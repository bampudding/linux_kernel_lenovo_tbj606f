# TB-J606F tag inventory

Generated: 2026-09-24T09:20:25Z

| Tag | Commit | Subject |
|---|---|---|
| stock-full-20201217 | c0ac0ddae7 | Upload source code for TB-J606F from official website |
| 20241218 | 88b3ba552e | status: update |
| zui12-audiofix-baseline-20260917 | 12dbd275a7 | tb-j606f: restore ZUI12 touch and audio compatibility |
| zui12-65hz-probe-20260917 | 398465020d | display: tb-j606f: add conservative 65 Hz panel probe |
| zui12-backport2-tested-20260917 | 8898aeffe6 | mmc: core: retry clock scaling after prior failure |
| zui12-next-tested-20260917 | f60b10e1fe | display: tb-j606f: add conservative 65 Hz panel probe |
| zui12-4.19.96-60hz-tested-20260917 | 14549a61ac | Revert "display: tb-j606f: add conservative 65 Hz panel probe" |
| zui12-4.19.97-60hz-tested-20260917 | de0feabe14 | stable: uplift Linux 4.19.96 to 4.19.97 |
| zui12-4.19.98-60hz-tested-20260918 | bd81c2a9c1 | kabi: preserve ZUI12 queue_limits layout on 4.19.98 |
| zui12-4.19.99-60hz-tested-20260918 | d8ef0fccc7 | stable: uplift Linux 4.19.98 to 4.19.99 with ZUI12 kABI preservation |
| zui12-4.19.110-60hz-tested-20260918 | b326cd634e | Revert "cfg80211: Fix radar event during another phy CAC" |
| zui12-4.19.113-60hz-tested-20260918 | 0e89886e70 | tb-j606f: preserve ZUI12 phy_device kABI |
| zui12-4.19.125-60hz-tested-20260918 | e5deb74160 | tb-j606f: preserve ZUI12 tty and arm64 capability kABI |
| zui12-4.19.136-60hz-tested-20260918 | 17dd80827d | tb-j606f: preserve ZUI12 sock cgroup kABI |
| zui12-4.19.146-60hz-tested-20260918 | 04675e238c | Linux 4.19.146 |
| zui12-4.19.157-60hz-tested-20260918 | 75497879c4 | Linux 4.19.157 |
| zui12-post157-dwc3fix1-tested-20260918 | 075c3c4442 | usb: dwc3: harden cancelled request handling |
| zui12-post157-dwc3fix2-tested-20260918 | 7892720ae2 | usb: dwc3: harden ENDTRANSFER timeout recovery |
| zui12-post157-dwc3fix3-tested-20260918 | 13eb6312b8 | usb: dwc3: guard endpoint PM state |
| zui12-post157-dwc3fix4-tested-20260918 | 038bdb03b8 | usb: dwc3: fix control endpoint teardown |
| zui12-post157-dwc3fix5-tested-20260918 | ea2afcf795 | usb: dwc3: decode endpoint command timeout correctly |
| zui12-post157-ufsfix1-tested-20260918 | 733c5aaa50 | scsi: ufs: balance clock ungate request blocking |
| zui12-post157-ufsfix2-tested-20260918 | a0f3e8b971 | scsi: ufs: close LRB completion race before gating |
| zui12-post157-erofs1-tested-20260918 | b8e305905a | arm64: bengal: enable built-in EROFS support |
| zui12-post157-f2fs1-tested-20260918 | 3d943306af | f2fs: drop stale writeback retry label |
| zui12-post157-f2fs2-tested-20260918 | e15161550d | f2fs: use rwsem for GC serialization |
| zui12-post157-f2fs3-tested-20260918 | 307231b400 | f2fs: allow post-read teardown during init failure |
| zui12-post157-f2fs-compression-core-off-build-20260918 | d04f96a5e5 | f2fs: backport filesystem compression core |
| zui12-post157-f2fs-compress-source-tested-20260919 | 91909246ac | f2fs: guard compression-only merge helper |
| zui12-post157-f2fs-compress-fixes1-enabled-tested-20260919 | 7cc5ceaef5 | f2fs: avoid post-read workqueue for normal clusters |
| zui12-post157-f2fs-compress-fixes2-enabled-tested-20260919 | dfcb1cd5d4 | f2fs: add modern data block address helpers |
| zui12-post157-fs-fixes3-zstd-tested-20260919 | fb21dd9825 | f2fs: add ZSTD compression backend |
| zui12-post157-f2fs-compress-fixes4-enabled-tested-20260919 | 40963169bc | f2fs: avoid op-lock deadlock in compressed writeback |
| zui12-post157-f2fs-compress-fixes5-enabled-tested-20260919 | b16c916b2d | f2fs: avoid cp_rwsem recursion while flushing inline data |
| zui12-post157-f2fs-compress-fixes6-enabled-tested-20260919 | 5295e4dfde | f2fs: serialize data allocation with checkpoint |
| zui12-post157-mm-zsmalloc-fixes7-enabled-tested-20260919 | 5c3c5c63f2 | zsmalloc: make concurrent compaction accounting precise |
| zui12-post157-ufs-resume-fixes8-enabled-tested-20260919 | dc22d91e70 | scsi: ufs: tolerate resume race with error recovery |
| zui12-post157-sched-walt-fixes9-enabled-tested-20260919 | 98c4683b7d | sched: walt: defer unsafe window-size rollover |
| zui12-post157-ufs-sysfs-desc-fixes10-enabled-tested-20260919 | e91beb08de | scsi: ufs: validate descriptor parameter bounds |
| zui12-post157-kgsl-fixes11-enabled-tested-20260919 | f739eee2dc | msm: kgsl: preserve power control flags across recovery |
| zui12-post157-modernization-batch-tested-20260919 | f739eee2dc | msm: kgsl: preserve power control flags across recovery |
| zui12-post157-latency-tuning-tested-20260919 | a46c5177ab | tune: reduce burst latency on TB-J606F |
| zui12-post157-dt2w-gsi-tested-20260919 | 7f7e5bf3b3 | input: nt36xxxspi: defer panel PM transitions |
| zui12-post157-kgsl-ringalloc-opt13-tested-20260919 | 7cd6df94c9 | msm: kgsl: use kvcalloc for ringbuffer submission |
| zui12-post157-eas-idle-opt14-known-good-20260922 | a9f8072bcf | sched: prefer shallow-idle CPU in EAS wake placement |
| zui12-post157-gpu-oc15-980-failed-20260922 | 0d43e6f23a | test: default Bengal GPU to OEM 980 MHz bin |
| zui12-post157-gpu-oc16-harness-built-20260922 | 68c534d08a | debug: add GPU speed-bin boot override |
| zui12-post157-gpu-oc17-native960-tested-20260922 | c08047730b | gpu: add guarded TB-J606F 960 MHz opt-in |
| zui12-post157-erofs-lineage23.2-built-20260922 | 5cf633864b | erofs: backport modern compressed image support |
| zui12-post157-erofs-lineage23.2-tested-20260922 | 5cf633864b | erofs: backport modern compressed image support |
| zui12-post157-erofs-lineage23.2-runtime-tested-20260922 | 5cf633864b | erofs: backport modern compressed image support |
| p11-zui14-adsp-fastrpc-sensors-tested-20260923 | 5f4e15db5c | drivers: adapt ZUI14 FastRPC wakeup API to 4.19 |
| tbj606f-a16-zui14-kernel-stable-20260924 | 7124b9c09a | soc: qcom: add native ADSP loader for ZUI14 userspace |
| tbj606f-a16-zui14-opensource-20260924 | 62d8b441b6 | docs: update TB-J606F Android 16 ZUI14 status |
| tbj606f-a16-zui14-published-20260924 | 8ea948339a | docs: index published TB-J606F development refs |
| tbj606f-a16-zui14-public-v1 | 3a5bd05145 | docs: fix published TB-J606F ref index |
| tbj606f-a16-zui14-public-v2 | c067a36017 | docs: avoid self-pinning the published branch head |
