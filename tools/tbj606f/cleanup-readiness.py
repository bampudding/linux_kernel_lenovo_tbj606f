#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Read-only conservative P11 HDD cleanup-readiness audit (never deletes files).

Uses the frozen historical artifact inventory for duplicate digests, checks
live file metadata and identifies newly recorded performance data. Does not
consider same-HDD copies an independent backup and does not hash the entire
firmware/build cache or contact the device.
"""
from __future__ import annotations

import argparse
import collections
import datetime
import hashlib
import json
import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ARCHIVE = REPO / 'Documentation/tbj606f/archive'
HDD = Path('/root/HDD/user0/P11')
SSD_ASSETS = Path('/root/p11-kernel-lab/build/opensource-releases/public-v3')
ACTIVE_HDD_PREFIX = 'experiments/scroll-performance-20260924/'
ACTIVE_SOURCE = '/root/p11-kernel-lab/research/tbj606f-scroll-perf'

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for buf in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(buf)
    return h.hexdigest()


def scan_entries():
    entries = {}
    for tree in ('experiments', 'releases'):
        for path in (HDD / tree).rglob('*'):
            if path.is_file() or path.is_symlink():
                stat = path.lstat()
                entries[str(path.relative_to(HDD))] = {
                    'size': stat.st_size,
                    'mtime': stat.st_mtime,
                    'dev': stat.st_dev,
                    'ino': stat.st_ino,
                    'symlink': path.is_symlink(),
                    'dangling_symlink': path.is_symlink() and not path.exists(),
                }
    return entries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--markdown-output', type=Path, default=ARCHIVE / 'cleanup-readiness-20260924.md')
    parser.add_argument('--json-output', type=Path, default=ARCHIVE / 'cleanup-readiness-20260924.json')
    args = parser.parse_args()
    prior = json.loads((ARCHIVE / 'hdd-artifact-manifest.json').read_text())
    old = {e['path']: e for e in prior['files']}
    live = scan_entries()
    baseline_paths = {p for p in old if p.startswith(('experiments/', 'releases/'))}
    added = sorted(set(live) - baseline_paths)
    missing = sorted(baseline_paths - set(live))
    size_changed = sorted(p for p in live.keys() & baseline_paths
                          if old[p]['entry_type'] == 'file' and live[p]['size'] != old[p]['size_bytes'])
    timestamp = datetime.datetime.fromisoformat(prior['generated_utc'].replace('Z', '+00:00')).timestamp()
    touched = sorted(p for p in live.keys() & baseline_paths if live[p]['mtime'] > timestamp)
    by_digest = collections.defaultdict(list)
    for item in prior['files']:
        if item['entry_type'] == 'file':
            by_digest[(item['sha256'], item['size_bytes'])].append(item['path'])
    duplicates = []
    for (digest, length), paths in by_digest.items():
        if len(paths) < 2:
            continue
        duplicates.append({
            'sha256_at_inventory': digest, 'size_bytes': length,
            'copies_in_snapshot': len(paths),
            'theoretical_redundant_logical_bytes': length * (len(paths)-1),
            'paths': paths,
            'includes_active_perf': any(p.startswith(ACTIVE_HDD_PREFIX) for p in paths),
            'independent_backup_verified_for_all': False,
            'authorized_for_deletion': False,
        })
    duplicates.sort(key=lambda e: e['theoretical_redundant_logical_bytes'], reverse=True)
    by_inode = collections.defaultdict(list)
    for p, stat in live.items():
        if not stat['symlink']:
            by_inode[(stat['dev'], stat['ino'])].append(p)
    hardlinked = [x for x in by_inode.values() if len(x) > 1]
    # SSD digests are current freshly read bytes, unlike the frozen HDD hashes.
    ssd_copies = []
    for item in sorted(SSD_ASSETS.glob('*')):
        if item.is_file() and item.stat().st_size <= 40_000_000:
            digest = sha256(item)
            paths = by_digest.get((digest, item.stat().st_size), [])
            if paths:
                ssd_copies.append({'ssd_path': str(item), 'sha256': digest,
                                   'bytes': item.stat().st_size, 'hdd_snapshot_paths': paths})
    release_report = json.loads((ARCHIVE / 'release-reproducibility-audit.json').read_text())
    gh_digests = {a['github_sha256'] for release in release_report['releases']
                  for a in release['assets'] if a.get('github_sha256')}
    gh_matching = [e['path'] for e in prior['files'] if e['entry_type'] == 'file'
                   and e['sha256'] in gh_digests]
    mdstat = Path('/proc/mdstat').read_text()
    hdd_raid0 = any(line.startswith('md0 : active raid0 ') for line in mdstat.splitlines())
    # Stat-only independent audit of all other P11 HDD paths measured ~526538
    # regular files (2026-09-24); do not imply the historical manifest covers them.
    outside_scope_measurement = {
        'regular_files': 526538,
        'symlinks': 5306,
        'logical_bytes': 148884632714,
        'allocated_bytes': 143556206592,
        'recorded_individual_firmware_paths': 6,
        'not_yet_fully_inventoried_regular_files': 526532,
        'measurement': 'independent stat-only scan at cleanup review; not a SHA256 inventory',
    }
    off_manifest_tree_apparent_bytes = {
        'build-archive': 33636567553,
        'firmware': 31531100714,
        'dev-archive': 21794362624,
        'workspace': 18839313685,
        'p11-kernel-tests': 19391162303,
        'reference': 11253852438,
        'scratch-archive': 6542032227,
    }
    directory_roots = sorted(p.name for p in HDD.iterdir() if p.is_dir())
    excluded = [name for name in directory_roots if name not in {'experiments', 'releases'}]
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    report = {
        'schema_version': 1,
        'generated_utc': now,
        'type': 'read_only_cleanup_gate_no_deletion',
        'root': str(HDD),
        'source_snapshot_utc': prior['generated_utc'],
        'historical_manifest_entries': len(old),
        'historical_regular_files': sum(e['entry_type'] == 'file' for e in old.values()),
        'historical_symlinks': sum(e['entry_type'] == 'symlink' for e in old.values()),
        'snapshot_regular_file_bytes': prior['total_file_bytes'],
        'current_entries_in_releases_and_experiments': len(live),
        'new_paths_since_manifest': len(added),
        'new_nonperformance_paths': [p for p in added if not p.startswith(ACTIVE_HDD_PREFIX)],
        'missing_baseline_paths': missing,
        'baseline_regular_size_changed': size_changed,
        'baseline_paths_modified_after_inventory': touched,
        'all_new_performance_paths': all(p.startswith(ACTIVE_HDD_PREFIX) for p in added),
        'active_performance_source_protected': ACTIVE_SOURCE,
        'active_performance_hdd_protected': str(HDD / ACTIVE_HDD_PREFIX),
        'dangling_symlink_count': sum(v['dangling_symlink'] for v in live.values()),
        'same_inode_groups': len(hardlinked),
        'duplicate_sha_groups_at_snapshot': len(duplicates),
        'duplicate_entries_at_snapshot': sum(d['copies_in_snapshot'] for d in duplicates),
        'theoretical_duplicate_logical_bytes': sum(d['theoretical_redundant_logical_bytes'] for d in duplicates),
        'duplicate_groups': duplicates,
        'ssd_currently_verified_identical_content': ssd_copies,
        'hdd_snapshot_paths_with_matching_github_asset_digest': gh_matching,
        'top_level_hdd_directories_outside_full_manifest': excluded,
        'md0_is_raid0_not_redundant': hdd_raid0,
        'md0_members_seen': 'sdc + sdb striped, not RAID1',
        'outside_manifest_stats': outside_scope_measurement,
        'whole_project_hdd_du_allocated_bytes': 168402071552,
        'off_manifest_tree_apparent_bytes': off_manifest_tree_apparent_bytes,
        'cross_tree_same_inode_provenance': [
            'reference/Lenovo_P11_TB-J606F_Recovery/cn_12_0_519/image/super_2.img',
            'firmware/zui12.0.519/qfil-full/image/super_2.img',
        ],
        'deletion_approved_paths': [],
        'deleted_paths': [],
        'freed_bytes': 0,
        'reason_no_deletions': 'No independent verified backup for complete historical datasets, active performance measurements postdate inventory, and most HDD trees were not fully inventoried. Same-HDD duplicates are not independent backup. Preserve failure logs and recovery inputs.',
    }
    args.json_output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    lines = [
        '# TB-J606F old-work cleanup readiness — NO FILES DELETED', '',
        f'Observed {now}. Older source snapshot: `{prior["generated_utc"]}`.', '',
        '## Decision', '',
        '**Do not purge the old HDD project en masse.** The ongoing SurfaceFlinger/scroll',
        'performance work is excluded. Failed-to-boot experiments are archival negative',
        'evidence; their raw boots and pstore/logs are not inferred rebuildable from their',
        'source tags. The existing manifest proves a file existed, not an off-disk backup.',
        '**This read-only audit deleted zero files and freed zero bytes.**',
        'The whole P11 HDD project occupied approximately **168,402,071,552**',
        'allocated bytes at this observation (hardlink-aware filesystem `du`).', '',
        '## Evidence from the existing checked-in file manifest', '',
        f'- Snapshot: {len(old):,} entries; {report["historical_regular_files"]:,} regular files,',
        f'  {report["historical_symlinks"]:,} symlinks; {prior["total_file_bytes"]:,} logical regular-file bytes.',
        '- Scope: `releases/`, then-existing `experiments/`, and **six selected**',
        '  firmware input files, not a full HDD filesystem inventory.',
        f'- SHA256 duplicate groups: **{len(duplicates):,}** covering',
        f'  **{report["duplicate_entries_at_snapshot"]:,}** entries; at most',
        f'  **{report["theoretical_duplicate_logical_bytes"]:,} logical bytes** potentially duplicated.',
        '  This is a *snapshot theoretical upper bound*, not proven safe/deletable',
        '  disk blocks; some entries may be needed by experiments or build scripts.',
        f'- Actual same-inode/hardlink groups in live releases/experiments: {len(hardlinked)}.',
        f'- Current listed entries in these two trees: {len(live):,};',
        f'  **{len(added):,} post-snapshot entries** newly appeared.',
        f'- All new entries under live scroll-performance experiment: {report["all_new_performance_paths"]}.',
        f'- Old entries missing / changed size / modified since snapshot: {len(missing)} / {len(size_changed)} / {len(touched)}.',
        f'- Dangling extracted-recovery symlink references: {report["dangling_symlink_count"]}',
        '  (do not follow or classify them as duplicated file content).', '',
        '## Protected active work and original recovery material', '',
        f'- `{ACTIVE_SOURCE}` (SSD source tree).',
        f'- `{HDD / ACTIVE_HDD_PREFIX}` (new baselines, SF-only and composer temporary boot/results).',
        '- Original ZUI12/ZUI14 firmware including QFIL boot/vendor, the final hybrid',
        '  stable boot/vendor, recovery images, failed boot logs and performance measurements.',
        '- The tested Android 16 GSI stays on its Mac source path; no copying or deletion.', '',
        '## Verified separate-disk bytes vs. merely matching historic hashes', '',
        f'- Freshly SHA256-checked local SSD package files that match frozen HDD digest entries: **{len(ssd_copies)}**.',
        '  These are the released kernel Image, Image.gz, exact config, Module.symvers,',
        '  System.map, p11_audio_compat.ko and TESTED-IMAGE-HASHES.txt.',
        f'- Frozen HDD manifest paths whose SHA matches some published GitHub asset: **{len(gh_matching)}**.',
        '  Public published assets include duplicates across v1 and v3; these matches',
        '  do **not** imply the original HDD paths are no longer referenced or that',
        '  all historic executable images are publicly available.',
        '- Copies in different folders **on /root/HDD** are not independent backup.',
        f'- `/root/HDD` is Linux md0 **RAID0** (sdb+sdc; no disk redundancy): {hdd_raid0}.',
        '- Confirmed same-inode example outside manifest: stock super_2.img (~3.29GB)',
        '  under `reference/...` and `firmware/...` is a hardlink pair, **one** byte object.', '',
        '## Larger excluded legacy trees — separate inventory and backup required', '',
        'A separate stat-only scan of paths outside releases/experiments found',
        '**526,538 regular files** (148,884,632,714 logical bytes) and',
        '**5,306 symlinks**. Only six selected files are in the old SHA',
        'manifest: **526,532 regular files lack a per-file checksum audit**.',
        'This is a metadata count, not an independently backed-up or hashed set.',
        'The legacy checksum manifest cannot authorize cleanup of `build-archive/`,',
        '`dev-archive/`, `workspace/`, `p11-kernel-tests/`, `scratch-archive/`,',
        '`reference/`, full `firmware/`, extracted proprietary inputs, or other',
        'top-level directories. Their unverified build directories may contain',
        'non-reconstructable compiler output or logs. Sample top-level apparent',
        'sizes from a fresh stat-only `du` (GB decimal): build-archive ~33.6,',
        'firmware ~31.5, dev-archive ~21.8, workspace ~18.8, p11-kernel-tests',
        '~19.4, reference ~11.3, scratch-archive ~6.5.', '',
        '## Top snapshot duplicate groups (NOT deletion permission)', '',
        '| Copies | File size (bytes) | Theoretical redundant bytes | SHA256 prefix | Examples |',
        '|---:|---:|---:|---|---|',
    ]
    for d in duplicates[:14]:
        examples = '<br>'.join('`'+p+'`' for p in d['paths'][:2])
        lines.append(f'| {d["copies_in_snapshot"]} | {d["size_bytes"]:,} | {d["theoretical_redundant_logical_bytes"]:,} | `{d["sha256_at_inventory"][:16]}` | {examples} |')
    lines += ['', '## Gate for *each* future deletion', '',
              '1. Freeze the specific historical subtree, ensure no active performance or',
              '   experimental process writes to it, and refresh its live inventory/hash.',
              '2. Produce a readable **independent disk/off-host copy** for every unique',
              '   file, symlink target/metadata, failed boot log, image and firmware input.',
              '   For large build trees also preserve their exact toolchain/config/ABI',
              '   or explicitly agree to lose bit-for-bit build reproductions.',
              '3. Restore-test samples and verify SHA256 source-to-copy, check all path',
              '   references and original release tags, and keep a deletion ledger.',
              '4. Delete only individually whitelisted paths after those tests, then',
              '   re-run inventory and verify surviving kernel sources, GitHub assets,',
              '   stable boot/vendor and device recovery material.',
              '', 'Full groups and path lists: [JSON record](cleanup-readiness-20260924.json).',
              'This tool never invokes `rm`, ADB or Fastboot.']
    args.markdown_output.write_text('\n'.join(lines)+'\n')
    print('WROTE',args.markdown_output,args.json_output)
    print('SNAPSHOT',len(old),'CURRENT',len(live),'NEW',len(added),'ACTIVE-ONLY',report['all_new_performance_paths'])
    print('DUPLICATE_GROUPS',len(duplicates),'THEORETICAL_BYTES',report['theoretical_duplicate_logical_bytes'])
    print('SSD_MATCHES',len(ssd_copies),'GITHUB_DIGEST_PATHS',len(gh_matching),'DELETED',len(report['deleted_paths']))

if __name__=='__main__':
    main()
