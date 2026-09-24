# TB-J606F old-work cleanup readiness — NO FILES DELETED

Observed 2026-09-24T12:10:07.874381+00:00. Older source snapshot: `2026-09-24T10:54:07.334653+00:00`.

## Decision

**Do not purge the old HDD project en masse.** The ongoing SurfaceFlinger/scroll
performance work is excluded. Failed-to-boot experiments are archival negative
evidence; their raw boots and pstore/logs are not inferred rebuildable from their
source tags. The existing manifest proves a file existed, not an off-disk backup.
**This read-only audit deleted zero files and freed zero bytes.**
The whole P11 HDD project occupied approximately **168,402,071,552**
allocated bytes at this observation (hardlink-aware filesystem `du`).

## Evidence from the existing checked-in file manifest

- Snapshot: 2,492 entries; 1,703 regular files,
  789 symlinks; 46,252,195,265 logical regular-file bytes.
- Scope: `releases/`, then-existing `experiments/`, and **six selected**
  firmware input files, not a full HDD filesystem inventory.
- SHA256 duplicate groups: **285** covering
  **1,103** entries; at most
  **4,588,967,170 logical bytes** potentially duplicated.
  This is a *snapshot theoretical upper bound*, not proven safe/deletable
  disk blocks; some entries may be needed by experiments or build scripts.
- Actual same-inode/hardlink groups in live releases/experiments: 0.
- Current listed entries in these two trees: 2,635;
  **149 post-snapshot entries** newly appeared.
- All new entries under live scroll-performance experiment: True.
- Old entries missing / changed size / modified since snapshot: 0 / 0 / 0.
- Dangling extracted-recovery symlink references: 64
  (do not follow or classify them as duplicated file content).

## Protected active work and original recovery material

- `/root/p11-kernel-lab/research/tbj606f-scroll-perf` (SSD source tree).
- `/root/HDD/user0/P11/experiments/scroll-performance-20260924` (new baselines, SF-only and composer temporary boot/results).
- Original ZUI12/ZUI14 firmware including QFIL boot/vendor, the final hybrid
  stable boot/vendor, recovery images, failed boot logs and performance measurements.
- The tested Android 16 GSI stays on its Mac source path; no copying or deletion.

## Verified separate-disk bytes vs. merely matching historic hashes

- Freshly SHA256-checked local SSD package files that match frozen HDD digest entries: **7**.
  These are the released kernel Image, Image.gz, exact config, Module.symvers,
  System.map, p11_audio_compat.ko and TESTED-IMAGE-HASHES.txt.
- Frozen HDD manifest paths whose SHA matches some published GitHub asset: **25**.
  Public published assets include duplicates across v1 and v3; these matches
  do **not** imply the original HDD paths are no longer referenced or that
  all historic executable images are publicly available.
- Copies in different folders **on /root/HDD** are not independent backup.
- `/root/HDD` is Linux md0 **RAID0** (sdb+sdc; no disk redundancy): True.
- Confirmed same-inode example outside manifest: stock super_2.img (~3.29GB)
  under `reference/...` and `firmware/...` is a hardlink pair, **one** byte object.

## Larger excluded legacy trees — separate inventory and backup required

A separate stat-only scan of paths outside releases/experiments found
**526,538 regular files** (148,884,632,714 logical bytes) and
**5,306 symlinks**. Only six selected files are in the old SHA
manifest: **526,532 regular files lack a per-file checksum audit**.
This is a metadata count, not an independently backed-up or hashed set.
The legacy checksum manifest cannot authorize cleanup of `build-archive/`,
`dev-archive/`, `workspace/`, `p11-kernel-tests/`, `scratch-archive/`,
`reference/`, full `firmware/`, extracted proprietary inputs, or other
top-level directories. Their unverified build directories may contain
non-reconstructable compiler output or logs. Sample top-level apparent
sizes from a fresh stat-only `du` (GB decimal): build-archive ~33.6,
firmware ~31.5, dev-archive ~21.8, workspace ~18.8, p11-kernel-tests
~19.4, reference ~11.3, scratch-archive ~6.5.

## Top snapshot duplicate groups (NOT deletion permission)

| Copies | File size (bytes) | Theoretical redundant bytes | SHA256 prefix | Examples |
|---:|---:|---:|---|---|
| 10 | 100,663,296 | 905,969,664 | `7356b6ac6a791c95` | `releases/p11-debug-gnu-postbasic-20260916/work/boot.img`<br>`releases/p11-debug-gnu-prerest-20260916/work/boot.img` |
| 2 | 796,917,760 | 796,917,760 | `40e5158f4fa9844e` | `experiments/zui14-vendor-hybrid-20260923/vendor_a-zui14-vndk30-gsi-fstab-760MiB.img`<br>`experiments/zui14-vendor-hybrid-20260923/vendor_a-zui14-vndk30-z12wifi-sensors-760MiB.img` |
| 4 | 100,663,296 | 301,989,888 | `ede1baffbaf3d1e1` | `releases/p11-debug-gnu-postbasic-20260916/boot-gnu-postbasic-marker.img`<br>`releases/p11-debug-gnu-postbasic-20260916/work/new-boot.img` |
| 3 | 103,800,832 | 207,601,664 | `02ce04c37915d11c` | `experiments/vndk29-product-20260923/extracted-v29.apex`<br>`experiments/vndk29-vendor-20260923/extracted-v29-apexlabel.apex` |
| 3 | 100,663,296 | 201,326,592 | `27e8d4d15cfc479c` | `releases/p11-debug-gnu-prerest-20260916/boot-gnu-prerest-marker.img`<br>`releases/p11-debug-gnu-prerest-20260916/work/new-boot.img` |
| 4 | 34,290,176 | 102,870,528 | `86388e3431b01b42` | `releases/p11-debug-gnu-postbasic-20260916/Image`<br>`releases/p11-debug-gnu-postbasic-20260916/work/kernel` |
| 2 | 100,663,296 | 100,663,296 | `caacb892eaf1aa49` | `experiments/custom-recovery-20260922/P11Diag-recovery-v7-fallback.img`<br>`experiments/erofs-lineage23.2-20260922/diag-20260923/P11Diag-recovery-v7-fallback.img` |
| 2 | 100,663,296 | 100,663,296 | `a2de31f8d7c52a29` | `experiments/custom-recovery-20260922/P11Diag-recovery-v7.img`<br>`experiments/erofs-lineage23.2-20260922/diag-20260923/P11Diag-recovery-v7.img` |
| 2 | 100,663,296 | 100,663,296 | `655441bd242211c2` | `experiments/gpu-oc15-failure-20260922/boot-zui12-eas-idle-opt14.img`<br>`releases/zui12-post157-eas-idle-opt14-candidate-20260919/boot.img` |
| 2 | 100,663,296 | 100,663,296 | `44302e973fa0f20d` | `experiments/gpu-oc15-failure-20260922/boot-zui12-gpu-oc15-980-toplock.img`<br>`releases/zui12-post157-gpu-oc15-980-candidate-20260919/boot.img` |
| 2 | 100,663,296 | 100,663,296 | `804273c867cb5c9d` | `experiments/gpu-oc15-failure-20260922/boot-zui12-gpu-oc15-980.img`<br>`releases/zui12-final-pre-next-kernel-20260920/boot.img` |
| 2 | 100,663,296 | 100,663,296 | `29191c98d8d1ce4e` | `releases/boot-julian-zui12-audiofix2.img`<br>`releases/zui12-audiofix-baseline-20260917/boot.img` |
| 2 | 100,663,296 | 100,663,296 | `f2b4b6383a4448e0` | `releases/boot-julian-zui12-stockhybrid.img`<br>`releases/p11-zui12-julian-stockhybrid-20260917/boot-julian-dev-zui12-stockhybrid.img` |
| 2 | 100,663,296 | 100,663,296 | `1cef5482dfee45eb` | `releases/boot-zui12-4.19.110-60hz.img`<br>`releases/zui12-4.19.110-60hz-tested-20260918/boot.img` |

## Gate for *each* future deletion

1. Freeze the specific historical subtree, ensure no active performance or
   experimental process writes to it, and refresh its live inventory/hash.
2. Produce a readable **independent disk/off-host copy** for every unique
   file, symlink target/metadata, failed boot log, image and firmware input.
   For large build trees also preserve their exact toolchain/config/ABI
   or explicitly agree to lose bit-for-bit build reproductions.
3. Restore-test samples and verify SHA256 source-to-copy, check all path
   references and original release tags, and keep a deletion ledger.
4. Delete only individually whitelisted paths after those tests, then
   re-run inventory and verify surviving kernel sources, GitHub assets,
   stable boot/vendor and device recovery material.

Full groups and path lists: [JSON record](cleanup-readiness-20260924.json).
This tool never invokes `rm`, ADB or Fastboot.
