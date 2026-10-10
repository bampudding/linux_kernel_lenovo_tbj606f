# TB-J606F development history and provenance

This repository intentionally preserves the original project history instead of
publishing a squashed source dump.

## Upstream lineage

- Original repository: https://github.com/JulianDroske/linux_kernel_lenovo_tbj606f.git
- Lenovo source import: c0ac0ddae (official-kernel)
- Original device bring-up head: 88b3ba552 (dev)
- Android 16 / ZUI14 stable kernel checkpoint: 7124b9c09
- Public continuation branch: opensource/tbj606f-a16-zui14

Linux stable updates are retained as their original individual commits. Device
compatibility fixes and backports are also retained as separate commits.

## Original bring-up commits

| Commit | Date | Subject |
|---|---|---|
| 8e72bcc0e | 2024-12-13 | status: add repo description |
| e3c1cb54e | 2024-12-13 | driver: input: touchscreen: Import NT36523W driver as nt36xxxspi |
| 2632905ec | 2024-12-13 | driver: staging: Import QCACLD driver |
| 552406b36 | 2024-12-13 | status: Touchscreen and Wi-Fi are working |
| 88b3ba552 | 2024-12-13 | status: update |

## 2026 TB-J606F development commits

The following device-development commits are authored by the current
maintainer and are ancestors of the stable Android 16/ZUI14 line. Interleaved
upstream Linux stable commits remain present in the Git graph with their
original authorship.

| Commit | Date | Subject |
|---|---|---|
| 12dbd275a | 2026-09-17 | tb-j606f: restore ZUI12 touch and audio compatibility |
| 7438a0225 | 2026-09-17 | scsi: ufs: fix clk-gating hold dead loop |
| ecf0e8fe0 | 2026-09-17 | scsi: ufs: clear outstanding task on TM timeout |
| 67c4bb7b3 | 2026-09-17 | scsi: ufs: improve shared interrupt handling |
| 4ce5b8f3a | 2026-09-17 | scsi: ufs: clean up request completed without interrupt |
| afe4c2e5b | 2026-09-17 | mmc: block: fix RPMB release use-after-free |
| ba9ac6d80 | 2026-09-17 | USB: hub: clear connect change after reset-resume |
| ffd3a3cfa | 2026-09-17 | mmc: core: set CQE enabled only after successful enable |
| 8898aeffe | 2026-09-17 | mmc: core: retry clock scaling after prior failure |
| f60b10e1f | 2026-09-17 | display: tb-j606f: add conservative 65 Hz panel probe |
| 363ea846b | 2026-09-17 | stable: uplift Linux 4.19.95 to 4.19.96 |
| 14549a61a | 2026-09-17 | Revert "display: tb-j606f: add conservative 65 Hz panel probe" |
| de0feabe1 | 2026-09-17 | stable: uplift Linux 4.19.96 to 4.19.97 |
| 4b1c61ac2 | 2026-09-17 | stable: uplift Linux 4.19.97 to 4.19.98 |
| bd81c2a9c | 2026-09-18 | kabi: preserve ZUI12 queue_limits layout on 4.19.98 |
| d8ef0fccc | 2026-09-18 | stable: uplift Linux 4.19.98 to 4.19.99 with ZUI12 kABI preservation |
| 35193f93c | 2026-09-18 | arm64: adapt Lenovo memory hotremove to 4.19.100 API |
| 4782f0895 | 2026-09-18 | kabi: preserve ZUI12 tcf_proto_ops bind_class CRC |
| 32679a7e3 | 2026-09-18 | tb-j606f: fix stable110 conflict resolution fallout |
| b326cd634 | 2026-09-18 | Revert "cfg80211: Fix radar event during another phy CAC" |
| 2c9d5fb28 | 2026-09-18 | tb-j606f: preserve ZUI12 inode kABI after futex fix |
| 0e89886e7 | 2026-09-18 | tb-j606f: preserve ZUI12 phy_device kABI |
| b2a5e6b0d | 2026-09-18 | f2fs: update vendor xattr corruption logging |
| 39ab21cc8 | 2026-09-18 | tb-j606f: fix stable125 vendor API build fallout |
| 048f1d81f | 2026-09-18 | tb-j606f: preserve ZUI12 task_struct kABI across exec-id fix |
| e5deb7416 | 2026-09-18 | tb-j606f: preserve ZUI12 tty and arm64 capability kABI |
| 17dd80827 | 2026-09-18 | tb-j606f: preserve ZUI12 sock cgroup kABI |
| 075c3c444 | 2026-09-18 | usb: dwc3: harden cancelled request handling |
| 7892720ae | 2026-09-18 | usb: dwc3: harden ENDTRANSFER timeout recovery |
| 13eb6312b | 2026-09-18 | usb: dwc3: guard endpoint PM state |
| 038bdb03b | 2026-09-18 | usb: dwc3: fix control endpoint teardown |
| ea2afcf79 | 2026-09-18 | usb: dwc3: decode endpoint command timeout correctly |
| 733c5aaa5 | 2026-09-18 | scsi: ufs: balance clock ungate request blocking |
| a0f3e8b97 | 2026-09-18 | scsi: ufs: close LRB completion race before gating |
| b8e305905 | 2026-09-18 | arm64: bengal: enable built-in EROFS support |
| 19b8738c2 | 2026-09-18 | f2fs: adapt discard policy to cached command memory |
| ca27df35f | 2026-09-18 | f2fs: avoid periodic discard thread wakeups |
| 97cb38136 | 2026-09-18 | f2fs: fix cyclic writeback retry range |
| 271aff299 | 2026-09-18 | f2fs: flush checkpoint data while waiting for writeback |
| 3d943306a | 2026-09-18 | f2fs: drop stale writeback retry label |
| cb2cc4753 | 2026-09-18 | f2fs: avoid reclaim I/O from write-side page reads |
| e15161550 | 2026-09-18 | f2fs: use rwsem for GC serialization |
| 1e509e9ef | 2026-09-18 | f2fs: introduce a private bio pool |
| 8c12e60a8 | 2026-09-18 | f2fs: avoid __GFP_NOFAIL in bio allocation |
| 307231b40 | 2026-09-18 | f2fs: allow post-read teardown during init failure |
| d04f96a5e | 2026-09-18 | f2fs: backport filesystem compression core |
| fb3a85c3c | 2026-09-18 | f2fs: complete compression backend integration |
| 3bfa3419a | 2026-09-18 | f2fs: adapt compressed encryption to legacy fscrypt |
| 34d8f647a | 2026-09-18 | f2fs: keep ICE on compressed bio path |
| 91909246a | 2026-09-18 | f2fs: guard compression-only merge helper |
| dce55390d | 2026-09-19 | f2fs: fix potential deadlock on compressed quota file |
| f2ce11ad5 | 2026-09-19 | f2fs: safely disable directory compression flags |
| 7cc5ceaef | 2026-09-19 | f2fs: avoid post-read workqueue for normal clusters |
| 22737ef21 | 2026-09-19 | f2fs: introduce F2FS_IOC_GET_COMPRESS_BLOCKS |
| bf54b17f2 | 2026-09-19 | f2fs: fix compressed cluster block accounting |
| 55032ff71 | 2026-09-19 | f2fs: introduce F2FS_IOC_RELEASE_COMPRESS_BLOCKS |
| 08d7311a3 | 2026-09-19 | f2fs: introduce F2FS_IOC_RESERVE_COMPRESS_BLOCKS |
| db273310c | 2026-09-19 | f2fs: use mempool for compression intermediate pages |
| dfcb1cd5d | 2026-09-19 | f2fs: add modern data block address helpers |
| 3df792662 | 2026-09-19 | f2fs: show compression in statx |
| 54226d7b7 | 2026-09-19 | f2fs: add decompression context callbacks |
| fb21dd982 | 2026-09-19 | f2fs: add ZSTD compression backend |
| 1dd995d67 | 2026-09-19 | f2fs: avoid writeback use-after-free in compressed clusters |
| bf9e26355 | 2026-09-19 | f2fs: initialize block address for compressed mmap writes |
| 801a2454c | 2026-09-19 | f2fs: avoid decompress context UAF on read bio failure |
| 40963169b | 2026-09-19 | f2fs: avoid op-lock deadlock in compressed writeback |
| 5d8c948d2 | 2026-09-19 | f2fs: avoid compressed checkpoint serialization deadlock |
| b16c916b2 | 2026-09-19 | f2fs: avoid cp_rwsem recursion while flushing inline data |
| 9b5f9ff46 | 2026-09-19 | f2fs: keep f2fs_kmalloc kmalloc-only |
| bc3c2657c | 2026-09-19 | f2fs: stop retrying dirty nodes on close after cp error |
| 1b587538a | 2026-09-19 | f2fs: avoid cp_rwsem recursion for quota writeback |
| 5295e4dfd | 2026-09-19 | f2fs: serialize data allocation with checkpoint |
| 5c3c5c63f | 2026-09-19 | zsmalloc: make concurrent compaction accounting precise |
| dc22d91e7 | 2026-09-19 | scsi: ufs: tolerate resume race with error recovery |
| 549f7cc2e | 2026-09-19 | sched: fix for_each_cluster bounds handling |
| d46021a37 | 2026-09-19 | sched: core_ctl: avoid uninitialized boost trace state |
| 752b469ce | 2026-09-19 | sched: rt: avoid double accounting CPU utilization |
| 96a215a84 | 2026-09-19 | sched: walt: avoid rq lock on every IRQ update |
| 98c4683b7 | 2026-09-19 | sched: walt: defer unsafe window-size rollover |
| 31a6bbc31 | 2026-09-19 | scsi: ufs: runtime-resume before AHIT sysfs access |
| e91beb08d | 2026-09-19 | scsi: ufs: validate descriptor parameter bounds |
| 2522bb79e | 2026-09-19 | msm: kgsl: serialize active context detach |
| 77496ad0e | 2026-09-19 | msm: kgsl: avoid fault-handler recovery mutex race |
| 764ed0fda | 2026-09-19 | msm: kgsl: balance process ref in fault early-exit |
| f739eee2d | 2026-09-19 | msm: kgsl: preserve power control flags across recovery |
| a46c5177a | 2026-09-19 | tune: reduce burst latency on TB-J606F |
| c3e343a9a | 2026-09-19 | input: nt36xxxspi: restore GSI-safe double-tap wake |
| 7f7e5bf3b | 2026-09-19 | input: nt36xxxspi: defer panel PM transitions |
| 7cd6df94c | 2026-09-19 | msm: kgsl: use kvcalloc for ringbuffer submission |
| a9f8072bc | 2026-09-19 | sched: prefer shallow-idle CPU in EAS wake placement |
| 7da20d48b | 2026-09-23 | lib: support overlapping LZ4 in-place literals |
| 58dd0257f | 2026-09-23 | erofs: fix LZ4 in-place virtual buffer ordering |
| 7124b9c09 | 2026-09-23 | soc: qcom: add native ADSP loader for ZUI14 userspace |

## Android 16 / EROFS / ZUI14 stable milestones

| Commit | Subject |
|---|---|
| 5cf633864 | erofs: backport modern compressed image support |
| 56ddb54d1 | erofs: align modern compressed runtime with 4.19 |
| 3d93df774 | lib: backport LZ4 v1.8.3 decompressor for EROFS |
| 7da20d48b | lib: support overlapping LZ4 in-place literals |
| 58dd0257f | erofs: fix LZ4 in-place virtual buffer ordering |
| 7124b9c09 | soc: qcom: add native ADSP loader for ZUI14 userspace |

## Preserved experimental lines

These experiments remain as separate Git branches/commits and are not silently
folded into the stable line.

| Ref | Head | Subject |
|---|---|---|
| p11/zui12-post157-erofs-z14-fastrpc-experiment | 5f4e15db5 | drivers: adapt ZUI14 FastRPC wakeup API to 4.19 |
| p11/zui12-post157-erofs-z14-fastrpc-kabi1 | d3b58d64e | kernel: backport Android KABI layout for ZUI14 modules |
| p11/zui12-post157-erofs-z14-glink1 | ee298d4ab | soc: qcom: add native ADSP loader for ZUI14 userspace |
| p11/zui12-post157-erofs-lz4-inplacefix-zui14-fastrpc1 | 6dfb40576 | drivers: adapt ZUI14 FastRPC wakeup API to 4.19 |
| p11/zui12-post157-gpu-oc15 | f3543de60 | test: lock active GPU to top pwrlevel for OC validation |
| p11/zui12-post157-gpu-oc16-harness | 68c534d08 | debug: add GPU speed-bin boot override |
| p11/zui12-post157-erofs-lz4-v183-noinplace | d8df671ab | erofs: disable in-place compressed page reuse on 4.19 |
| p11/diag-recovery-permissive | be502c662 | lib: backport LZ4 v1.8.3 decompressor for EROFS |

## Publication rule

Push the public stable branch together with the preserved branch refs and tags
when the full research history is desired. Proprietary Lenovo firmware, vendor
images, signed DLKMs, extracted modem/DSP images, and user data are deliberately
not committed. The repository contains source and scripts that reconstruct the
tested hybrid from firmware obtained by the device owner.
