# Published development refs

This file records the branch and tag heads published with the TB-J606F
Android 16/ZUI14 open-source continuation on 2026-09-24.

The original repository is .
The continuation is published as the fork
.

Branches preserve successful milestones, intermediate modernization work,
and failed/diagnostic experiments. They are intentionally not squashed.

## Branches

| Branch | Commit | Subject |
|---|---|---|
|  |  | official-kernel |
|  |  | c0ac0ddae |
|  |  | Upload source code for TB-J606F from official website |
|  |  | opensource/tbj606f-a16-zui14 |
|  |  | 62d8b441b |
|  |  | docs: update TB-J606F Android 16 ZUI14 status |
|  |  | p11/diag-recovery-permissive |
|  |  | be502c662 |
|  |  | lib: backport LZ4 v1.8.3 decompressor for EROFS |
|  |  | p11/zui12-65hz |
|  |  | 398465020 |
|  |  | display: tb-j606f: add conservative 65 Hz panel probe |
|  |  | p11/zui12-audiofix |
|  |  | 12dbd275a |
|  |  | tb-j606f: restore ZUI12 touch and audio compatibility |
|  |  | p11/zui12-backport1 |
|  |  | 8898aeffe |
|  |  | mmc: core: retry clock scaling after prior failure |
|  |  | p11/zui12-bringup |
|  |  | 88b3ba552 |
|  |  | status: update |
|  |  | p11/zui12-next |
|  |  | f60b10e1f |
|  |  | display: tb-j606f: add conservative 65 Hz panel probe |
|  |  | p11/zui12-post157-dt2w-gsi |
|  |  | 7f7e5bf3b |
|  |  | input: nt36xxxspi: defer panel PM transitions |
|  |  | p11/zui12-post157-eas-idle-opt14 |
|  |  | a9f8072bc |
|  |  | sched: prefer shallow-idle CPU in EAS wake placement |
|  |  | p11/zui12-post157-erofs-lineage23.2 |
|  |  | 5cf633864 |
|  |  | erofs: backport modern compressed image support |
|  |  | p11/zui12-post157-erofs-lz4-inplacefix |
|  |  | 58dd0257f |
|  |  | erofs: fix LZ4 in-place virtual buffer ordering |
|  |  | p11/zui12-post157-erofs-lz4-inplacefix-zui14-fastrpc1 |
|  |  | 6dfb40576 |
|  |  | drivers: adapt ZUI14 FastRPC wakeup API to 4.19 |
|  |  | p11/zui12-post157-erofs-lz4-v183 |
|  |  | 3d93df774 |
|  |  | lib: backport LZ4 v1.8.3 decompressor for EROFS |
|  |  | p11/zui12-post157-erofs-lz4-v183-noinplace |
|  |  | d8df671ab |
|  |  | erofs: disable in-place compressed page reuse on 4.19 |
|  |  | p11/zui12-post157-erofs-v54compat |
|  |  | 56ddb54d1 |
|  |  | erofs: align modern compressed runtime with 4.19 |
|  |  | p11/zui12-post157-erofs-z14-adsp-loader-stable |
|  |  | 7124b9c09 |
|  |  | soc: qcom: add native ADSP loader for ZUI14 userspace |
|  |  | p11/zui12-post157-erofs-z14-fastrpc-experiment |
|  |  | 5f4e15db5 |
|  |  | drivers: adapt ZUI14 FastRPC wakeup API to 4.19 |
|  |  | p11/zui12-post157-erofs-z14-fastrpc-kabi1 |
|  |  | d3b58d64e |
|  |  | kernel: backport Android KABI layout for ZUI14 modules |
|  |  | p11/zui12-post157-erofs-z14-glink1 |
|  |  | ee298d4ab |
|  |  | soc: qcom: add native ADSP loader for ZUI14 userspace |
|  |  | p11/zui12-post157-f2fs-compress |
|  |  | 91909246a |
|  |  | f2fs: guard compression-only merge helper |
|  |  | p11/zui12-post157-f2fs-compress-fixes1 |
|  |  | 7cc5ceaef |
|  |  | f2fs: avoid post-read workqueue for normal clusters |
|  |  | p11/zui12-post157-f2fs-compress-fixes2 |
|  |  | dfcb1cd5d |
|  |  | f2fs: add modern data block address helpers |
|  |  | p11/zui12-post157-f2fs-compress-fixes4 |
|  |  | 40963169b |
|  |  | f2fs: avoid op-lock deadlock in compressed writeback |
|  |  | p11/zui12-post157-f2fs-compress-fixes5 |
|  |  | b16c916b2 |
|  |  | f2fs: avoid cp_rwsem recursion while flushing inline data |
|  |  | p11/zui12-post157-f2fs-compress-fixes6 |
|  |  | 5295e4dfd |
|  |  | f2fs: serialize data allocation with checkpoint |
|  |  | p11/zui12-post157-f2fs1 |
|  |  | 3d943306a |
|  |  | f2fs: drop stale writeback retry label |
|  |  | p11/zui12-post157-f2fs2 |
|  |  | e15161550 |
|  |  | f2fs: use rwsem for GC serialization |
|  |  | p11/zui12-post157-f2fs3 |
|  |  | 307231b40 |
|  |  | f2fs: allow post-read teardown during init failure |
|  |  | p11/zui12-post157-fs-fixes3 |
|  |  | fb21dd982 |
|  |  | f2fs: add ZSTD compression backend |
|  |  | p11/zui12-post157-gpu-oc15 |
|  |  | f3543de60 |
|  |  | test: lock active GPU to top pwrlevel for OC validation |
|  |  | p11/zui12-post157-gpu-oc16-harness |
|  |  | 68c534d08 |
|  |  | debug: add GPU speed-bin boot override |
|  |  | p11/zui12-post157-gpu-oc17-native960-final |
|  |  | c08047730 |
|  |  | gpu: add guarded TB-J606F 960 MHz opt-in |
|  |  | p11/zui12-post157-iohot1 |
|  |  | 307231b40 |
|  |  | f2fs: allow post-read teardown during init failure |
|  |  | p11/zui12-post157-kgsl-fixes11 |
|  |  | f739eee2d |
|  |  | msm: kgsl: preserve power control flags across recovery |
|  |  | p11/zui12-post157-kgsl-ringalloc-opt13 |
|  |  | 7cd6df94c |
|  |  | msm: kgsl: use kvcalloc for ringbuffer submission |
|  |  | p11/zui12-post157-latency-tuning-final |
|  |  | a46c5177a |
|  |  | tune: reduce burst latency on TB-J606F |
|  |  | p11/zui12-post157-mm-zsmalloc-fixes7 |
|  |  | 5c3c5c63f |
|  |  | zsmalloc: make concurrent compaction accounting precise |
|  |  | p11/zui12-post157-qcomfixes |
|  |  | b8e305905 |
|  |  | arm64: bengal: enable built-in EROFS support |
|  |  | p11/zui12-post157-sched-walt-fixes9 |
|  |  | 98c4683b7 |
|  |  | sched: walt: defer unsafe window-size rollover |
|  |  | p11/zui12-post157-ufs-resume-fixes8 |
|  |  | dc22d91e7 |
|  |  | scsi: ufs: tolerate resume race with error recovery |
|  |  | p11/zui12-post157-ufs-sysfs-desc-fixes10 |
|  |  | e91beb08d |
|  |  | scsi: ufs: validate descriptor parameter bounds |
|  |  | p11/zui12-stable100 |
|  |  | 35193f93c |
|  |  | arm64: adapt Lenovo memory hotremove to 4.19.100 API |
|  |  | p11/zui12-stable101 |
|  |  | 4782f0895 |
|  |  | kabi: preserve ZUI12 tcf_proto_ops bind_class CRC |
|  |  | p11/zui12-stable110 |
|  |  | b326cd634 |
|  |  | Revert "cfg80211: Fix radar event during another phy CAC" |
|  |  | p11/zui12-stable113 |
|  |  | 0e89886e7 |
|  |  | tb-j606f: preserve ZUI12 phy_device kABI |
|  |  | p11/zui12-stable125 |
|  |  | e5deb7416 |
|  |  | tb-j606f: preserve ZUI12 tty and arm64 capability kABI |
|  |  | p11/zui12-stable136 |
|  |  | 17dd80827 |
|  |  | tb-j606f: preserve ZUI12 sock cgroup kABI |
|  |  | p11/zui12-stable146 |
|  |  | 04675e238 |
|  |  | Linux 4.19.146 |
|  |  | p11/zui12-stable157 |
|  |  | 75497879c |
|  |  | Linux 4.19.157 |
|  |  | p11/zui12-stable96 |
|  |  | 14549a61a |
|  |  | Revert "display: tb-j606f: add conservative 65 Hz panel probe" |
|  |  | p11/zui12-stable97 |
|  |  | de0feabe1 |
|  |  | stable: uplift Linux 4.19.96 to 4.19.97 |
|  |  | p11/zui12-stable98 |
|  |  | bd81c2a9c |
|  |  | kabi: preserve ZUI12 queue_limits layout on 4.19.98 |
|  |  | p11/zui12-stable99 |
|  |  | f60b10e1f |
|  |  | display: tb-j606f: add conservative 65 Hz panel probe |
|  |  | p11/zui12-stable99-step |
|  |  | d8ef0fccc |
|  |  | stable: uplift Linux 4.19.98 to 4.19.99 with ZUI12 kABI preservation |
|  |  | p11/zui12-tune-inputboost-80ms |
|  |  | 13dd7fc5d |
|  |  | cpufreq: cap touch input boost at 80 ms |
|  |  | p11/zui12-tuning-harness |
|  |  | 8960a3a1b |
|  |  | debug: add swap page-cluster tuning override |

## Tags

| Tag | Target | Subject |
|---|---|---|
|  |  | 20241218 |
|  |  | 88b3ba552eae9f322e1c0fcbf14ea3de5d5976e8 |
|  |  | status: update |
|  |  | p11-zui14-adsp-fastrpc-sensors-tested-20260923 |
|  |  | 5f4e15db5c97c2c507935ac3cc52575efda00b07 |
|  |  | drivers: adapt ZUI14 FastRPC wakeup API to 4.19 |
|  |  | stock-full-20201217 |
|  |  | c0ac0ddae71ac66a4fbe1fe6dd127e608ddc1949 |
|  |  | Upload source code for TB-J606F from official website |
|  |  | tbj606f-a16-zui14-kernel-stable-20260924 |
|  |  | 7124b9c09a48380a7b028104e17cac36b9b1a0af |
|  |  | soc: qcom: add native ADSP loader for ZUI14 userspace |
|  |  | tbj606f-a16-zui14-opensource-20260924 |
|  |  | 62d8b441b64013a9714736234390d216b9164195 |
|  |  | docs: update TB-J606F Android 16 ZUI14 status |
|  |  | zui12-4.19.110-60hz-tested-20260918 |
|  |  | b326cd634ecebef98e55613a84599d256cb780fb |
|  |  | Revert "cfg80211: Fix radar event during another phy CAC" |
|  |  | zui12-4.19.113-60hz-tested-20260918 |
|  |  | 0e89886e70b419d0fa0355ff62cc0c50efbf0e8c |
|  |  | tb-j606f: preserve ZUI12 phy_device kABI |
|  |  | zui12-4.19.125-60hz-tested-20260918 |
|  |  | e5deb7416032b68cb0c1a9cd6b3279985c53d128 |
|  |  | tb-j606f: preserve ZUI12 tty and arm64 capability kABI |
|  |  | zui12-4.19.136-60hz-tested-20260918 |
|  |  | 17dd80827d9d606c313191163a4343a156890ae7 |
|  |  | tb-j606f: preserve ZUI12 sock cgroup kABI |
|  |  | zui12-4.19.146-60hz-tested-20260918 |
|  |  | 04675e238cf7f15f0a279c80afba4cbcf18593d1 |
|  |  | Linux 4.19.146 |
|  |  | zui12-4.19.157-60hz-tested-20260918 |
|  |  | 75497879c4267c40192011e4ec2a928fb9c72827 |
|  |  | Linux 4.19.157 |
|  |  | zui12-4.19.96-60hz-tested-20260917 |
|  |  | 14549a61ace84b751acbdb8009194b369368e3ce |
|  |  | Revert "display: tb-j606f: add conservative 65 Hz panel probe" |
|  |  | zui12-4.19.97-60hz-tested-20260917 |
|  |  | de0feabe14d023ff8aa2e55d908b586b5f189f12 |
|  |  | stable: uplift Linux 4.19.96 to 4.19.97 |
|  |  | zui12-4.19.98-60hz-tested-20260918 |
|  |  | bd81c2a9c117b6a7874ffe1209cde1a030a19e5a |
|  |  | kabi: preserve ZUI12 queue_limits layout on 4.19.98 |
|  |  | zui12-4.19.99-60hz-tested-20260918 |
|  |  | d8ef0fccc767ff012069c4aa06a48b4ad853a773 |
|  |  | stable: uplift Linux 4.19.98 to 4.19.99 with ZUI12 kABI preservation |
|  |  | zui12-65hz-probe-20260917 |
|  |  | 398465020ddc3c8e3065b4e45f696b411237469d |
|  |  | display: tb-j606f: add conservative 65 Hz panel probe |
|  |  | zui12-audiofix-baseline-20260917 |
|  |  | 12dbd275a7bc3c0d2d80ed95a036ad2035e2f9a6 |
|  |  | tb-j606f: restore ZUI12 touch and audio compatibility |
|  |  | zui12-backport2-tested-20260917 |
|  |  | 8898aeffe6199b2f645cd27d30be1be7c6a553d6 |
|  |  | mmc: core: retry clock scaling after prior failure |
|  |  | zui12-next-tested-20260917 |
|  |  | f60b10e1fe21b1c1f240f5f94a4cce89d158eb19 |
|  |  | display: tb-j606f: add conservative 65 Hz panel probe |
|  |  | zui12-post157-dt2w-gsi-tested-20260919 |
|  |  | 7f7e5bf3b3f524a65a1cbf4748a2f6f6d6776d9b |
|  |  | input: nt36xxxspi: defer panel PM transitions |
|  |  | zui12-post157-dwc3fix1-tested-20260918 |
|  |  | 075c3c4442c665ea7c64bb791c6e09e8a47af50e |
|  |  | usb: dwc3: harden cancelled request handling |
|  |  | zui12-post157-dwc3fix2-tested-20260918 |
|  |  | 7892720ae26e0434dfa0987ab1c5319f5eef8380 |
|  |  | usb: dwc3: harden ENDTRANSFER timeout recovery |
|  |  | zui12-post157-dwc3fix3-tested-20260918 |
|  |  | 13eb6312b87e67bf78f1ee94ada2a53a473e1392 |
|  |  | usb: dwc3: guard endpoint PM state |
|  |  | zui12-post157-dwc3fix4-tested-20260918 |
|  |  | 038bdb03b8ce89b1e23c883f44e4c99f37b52591 |
|  |  | usb: dwc3: fix control endpoint teardown |
|  |  | zui12-post157-dwc3fix5-tested-20260918 |
|  |  | ea2afcf79538d666c946b97f9a0be9515c7b42cd |
|  |  | usb: dwc3: decode endpoint command timeout correctly |
|  |  | zui12-post157-eas-idle-opt14-known-good-20260922 |
|  |  | a9f8072bcf54428cfe9362cf7232447eb1298cc8 |
|  |  | sched: prefer shallow-idle CPU in EAS wake placement |
|  |  | zui12-post157-erofs-lineage23.2-built-20260922 |
|  |  | 5cf633864bedb3e9d05b36c692b1b0964cd262a9 |
|  |  | erofs: backport modern compressed image support |
|  |  | zui12-post157-erofs-lineage23.2-runtime-tested-20260922 |
|  |  | 5cf633864bedb3e9d05b36c692b1b0964cd262a9 |
|  |  | erofs: backport modern compressed image support |
|  |  | zui12-post157-erofs-lineage23.2-tested-20260922 |
|  |  | 5cf633864bedb3e9d05b36c692b1b0964cd262a9 |
|  |  | erofs: backport modern compressed image support |
|  |  | zui12-post157-erofs1-tested-20260918 |
|  |  | b8e305905acc8182bd2821842dfba4ccabd887d4 |
|  |  | arm64: bengal: enable built-in EROFS support |
|  |  | zui12-post157-f2fs-compress-fixes1-enabled-tested-20260919 |
|  |  | 7cc5ceaef55ca9ef2de65a880845b1857661b648 |
|  |  | f2fs: avoid post-read workqueue for normal clusters |
|  |  | zui12-post157-f2fs-compress-fixes2-enabled-tested-20260919 |
|  |  | dfcb1cd5d4728ea5d60fbf4ddcb0eb8dcdb3d6ce |
|  |  | f2fs: add modern data block address helpers |
|  |  | zui12-post157-f2fs-compress-fixes4-enabled-tested-20260919 |
|  |  | 40963169bcb5a92ce63f71d0f06e3f8d2fa48088 |
|  |  | f2fs: avoid op-lock deadlock in compressed writeback |
|  |  | zui12-post157-f2fs-compress-fixes5-enabled-tested-20260919 |
|  |  | b16c916b2d9b65f8796eacaf25e27c71177e5e7f |
|  |  | f2fs: avoid cp_rwsem recursion while flushing inline data |
|  |  | zui12-post157-f2fs-compress-fixes6-enabled-tested-20260919 |
|  |  | 5295e4dfde99c6c5991d822747dcf6b97ad01b9c |
|  |  | f2fs: serialize data allocation with checkpoint |
|  |  | zui12-post157-f2fs-compress-source-tested-20260919 |
|  |  | 91909246ac5e657b24a32b8689a8b17dc13bb500 |
|  |  | f2fs: guard compression-only merge helper |
|  |  | zui12-post157-f2fs-compression-core-off-build-20260918 |
|  |  | d04f96a5e5e90757f006cd82c0ebdb8a364d0c9b |
|  |  | f2fs: backport filesystem compression core |
|  |  | zui12-post157-f2fs1-tested-20260918 |
|  |  | 3d943306af5e339a64928f35fa8a3d0f49a8e767 |
|  |  | f2fs: drop stale writeback retry label |
|  |  | zui12-post157-f2fs2-tested-20260918 |
|  |  | e15161550d4ddca3576e13d055680c3ca76667df |
|  |  | f2fs: use rwsem for GC serialization |
|  |  | zui12-post157-f2fs3-tested-20260918 |
|  |  | 307231b4002e7e4701aecf956e956373814b7d96 |
|  |  | f2fs: allow post-read teardown during init failure |
|  |  | zui12-post157-fs-fixes3-zstd-tested-20260919 |
|  |  | fb21dd98258d06cf9ca0d5c26fd07b1208163687 |
|  |  | f2fs: add ZSTD compression backend |
|  |  | zui12-post157-gpu-oc15-980-failed-20260922 |
|  |  | 0d43e6f23a2af10b568584fb07579d9dc5954d45 |
|  |  | test: default Bengal GPU to OEM 980 MHz bin |
|  |  | zui12-post157-gpu-oc16-harness-built-20260922 |
|  |  | 68c534d08a1892b366a13f2ff7b3078aad45373e |
|  |  | debug: add GPU speed-bin boot override |
|  |  | zui12-post157-gpu-oc17-native960-tested-20260922 |
|  |  | c08047730bb95a9b7ed89a0a47618070d8ed63ba |
|  |  | gpu: add guarded TB-J606F 960 MHz opt-in |
|  |  | zui12-post157-kgsl-fixes11-enabled-tested-20260919 |
|  |  | f739eee2dcc3187dca6c112c3324c41f7b65a524 |
|  |  | msm: kgsl: preserve power control flags across recovery |
|  |  | zui12-post157-kgsl-ringalloc-opt13-tested-20260919 |
|  |  | 7cd6df94c95c06daca3a1a80a70196111ca10750 |
|  |  | msm: kgsl: use kvcalloc for ringbuffer submission |
|  |  | zui12-post157-latency-tuning-tested-20260919 |
|  |  | a46c5177abea98d8ce49b1db81faefb913360614 |
|  |  | tune: reduce burst latency on TB-J606F |
|  |  | zui12-post157-mm-zsmalloc-fixes7-enabled-tested-20260919 |
|  |  | 5c3c5c63f228774d5145af571ebc730c83ddec53 |
|  |  | zsmalloc: make concurrent compaction accounting precise |
|  |  | zui12-post157-modernization-batch-tested-20260919 |
|  |  | f739eee2dcc3187dca6c112c3324c41f7b65a524 |
|  |  | msm: kgsl: preserve power control flags across recovery |
|  |  | zui12-post157-sched-walt-fixes9-enabled-tested-20260919 |
|  |  | 98c4683b7d5280ccfd90830f5743b7b8dc603ec3 |
|  |  | sched: walt: defer unsafe window-size rollover |
|  |  | zui12-post157-ufs-resume-fixes8-enabled-tested-20260919 |
|  |  | dc22d91e70a2ddad32756cc85aa45acb919ed4f0 |
|  |  | scsi: ufs: tolerate resume race with error recovery |
|  |  | zui12-post157-ufs-sysfs-desc-fixes10-enabled-tested-20260919 |
|  |  | e91beb08de332d5c5702ac7ac9a199a11a21d9aa |
|  |  | scsi: ufs: validate descriptor parameter bounds |
|  |  | zui12-post157-ufsfix1-tested-20260918 |
|  |  | 733c5aaa50d05315064612cc8c66257287194098 |
|  |  | scsi: ufs: balance clock ungate request blocking |
|  |  | zui12-post157-ufsfix2-tested-20260918 |
|  |  | a0f3e8b971857e28bb3827223861d40ade8a2a48 |
|  |  | scsi: ufs: close LRB completion race before gating |
