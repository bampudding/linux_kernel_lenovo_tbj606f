# TB-J606F release and archive preservation

This directory records what exists before any legacy cleanup. A hash and a
GitHub source snapshot identify an artifact; neither proves that the artifact's
bytes have been preserved somewhere other than the original HDD.

## Canonical inventories

| Record | Scope | Rebuild command on `fedora-heart` |
|---|---|---|
| `release-matrix.md` | Git milestone/tag to source commit | Review `git show-ref --tags` |
| `github-release-catalog.json` | Public release tag, exact source commit, release URL and published asset SHA256/size | `python3 tools/tbj606f/release-catalog.py` |
| `hdd-artifact-manifest.json` | Every regular file and symlink in HDD `releases/` and `experiments/`, plus selected original firmware inputs | `python3 tools/tbj606f/archive-inventory.py` |
| `legacy-archive-manifest.json` | Tracked/untracked-but-unignored helper/documentation SHA256 values, excluding itself | `python3 tools/tbj606f/source-inventory.py` |
| `artifact-inventory.txt` | Historical filename-only release/experiment inventory | Retained as an earlier snapshot; it is not the checksum authority |

Run the generators at the public kernel repository root. The HDD generator
reads `/root/HDD/user0/P11` and writes the manifest to this SSD checkout. It
does not follow symlinks, change source files, use device flashing tools, or
copy the GSI from the Mac. The larger unpacked/extracted firmware trees are
not included in the full-file inventory; selected original ZUI12, ZUI14 and
service firmware inputs are recorded separately inside the same manifest.

The `release_association` field is set only when a release folder corresponds
to an existing Git tag. A `null` association indicates that no reliable release
mapping was established; it must not be read as permission to discard the file.
The GitHub catalog's `single_commit_range` records the tag commit and its
first parent and is **not** a claim that the entire development milestone
consists of one commit. Source snapshots and the complete Git history retain
the actual intermediate changes.

## Support evidence and proprietary provenance

The stable hardware claims are backed by the saved runtime capture at
`releases/p11-a16-zui14-hybrid-stable-20260924/runtime/`, including
`sensorservice.txt`, `rotation.txt`, `wifi.txt`, `camera.txt`, `bluetooth.txt`,
`audio_policy.txt`, and `identity.txt`. On 2026-09-24 a fresh, serial-scoped,
read-only ADB check again observed Android 16, vendor build
`14.0.147_230414`, `4.19.157-perf+`, `sys.boot_completed=1`, and 34 hardware
sensors. Earlier sensor-failure logs belong to older experimental boots.

The tested LineageOS EROFS GSI stays at its existing Mac location. Its known
SHA256 is `26cde4242d9b92fb917b8235c4908e88c5fa6b60db1c56e0c53561db61d333bd`
and its byte size is `2255372288`. A hash does not authorize redistribution
of OEM boot/vendor images, DSP/modem firmware or extracted proprietary modules.

## Post-v5 cleanup readiness observation

The new [2026-09-24 read-only cleanup readiness report](cleanup-readiness-20260924.md)
with [full JSON digest-duplicate groups](cleanup-readiness-20260924.json)
records why the old HDD project was **not deleted**: live scroll-performance
experiments postdate the older manifest; large build and firmware trees remain
outside that manifest; the HDD is RAID0 (not a redundant backup). Re-run the
read-only scanner with `python3 tools/tbj606f/cleanup-readiness.py`.
The public v5 Git tag is unchanged by this later cleanup audit.

## Public-v1 duplicate extraction cleanup (2026-09-24)

The [actual cleanup ledger](public-v1-duplicate-prune-20260924.md) records
nine individually SHA-verified duplicate files removed from the extracted
public-v1 bundle; direct-parent copies and GitHub's published tar remain.
The earlier inventories remain historical pre-cleanup snapshots.
Current scroll-performance work and all other old material were untouched.

## Public legacy source and kernel preservation (2026-09-25)

See [verified 84 archive asset inventory](legacy-remote-preservation-20260925.md)
and [per-file SHA256 JSON](legacy-remote-preservation-20260925.json).
Source-only historic GitHub tags with HDD kernel stages have supplementary
kernel/config/ABI archives; loose old folder GPL components have a distinct
archival release. The old lineage19.1 source HEAD has a recovered GitHub
branch. Latest scroll-performance work and the current build environment were
excluded. OEM boot/vendor, old diagnostics, and large incomplete HDD archive
trees remain unbacked-up in a fully independent failure domain, so this is
**not authority to erase the old HDD**.

## Cleanup gate

No deletion of `experiments/` or `releases/` is authorized by these inventories.
Before considering an individual artifact for deletion, verify that its actual
bytes have an independently retained, readable copy; verify that copy against
its per-file SHA256; confirm the matching source tag and notes; check whether
any scripts or historical manifests refer to its original path; and retain
necessary build inputs and validation logs. Keep proprietary firmware inputs
available to their owner even when public metadata is complete.

Re-running an inventory after changes produces a new observation; commit it
with an explicit date. Do not rewrite old Git tags or pretend historical
release assets appeared in a tag that predates their source files.
