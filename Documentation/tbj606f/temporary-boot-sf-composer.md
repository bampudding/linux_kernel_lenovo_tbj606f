# TB-J606F temporary boot experiment 3: SF and Qualcomm composer

2026-09-24. Branch `perf/tbj606f-temporary-boot-sf-composer` builds on
`perf/tbj606f-temporary-boot-sf-all`.

The boot-only diagnostic `p11tune.sf_bigcpus=3` expands CPU availability
for the SurfaceFlinger process and Qualcomm composer process, each only
while belonging to `system-background`. The match is to the group leader
`surfaceflinger` or the observed 15-character Linux comm
`composer-servic` (the full process is
`/vendor/bin/hw/vendor.qti.hardware.display.composer-service`). No
unrelated background process is widened, and the cpuset configuration
itself is preserved. The diagnostic is **disabled by default** and is not
a production kernel proposal.

The only binary changes to the archived stable boot are its kernel and
`p11tune.sf_bigcpus=3` boot argument. Ramdisk and DTB round-trip as exact
copies. It was built by:

```bash
TMPDIR=/root tools/tbj606f/make-temp-sf-boot.sh \
  /root/HDD/user0/P11/releases/p11-a16-zui14-hybrid-stable-20260924/boot-z14-adsp-loader-stable1.img \
  /root/p11-kernel-lab/build/scroll-perf/kernel-out/arch/arm64/boot/Image \
  /root/p11-kernel-lab/build/scroll-perf/boot-sf-composer-temporary.img --sf-and-composer
```

Kernel Image SHA256:
`df33903053e3aa1bd19a4d6c5e7e5cbf60c49c9af33799399394b971263c02cf`.

Boot image SHA256:
`a37aa5e90542776246551f5e85f0edf03f8092014ff8b8f796c8e3de81b43187`.
Size: 14,290,944 bytes; the Mac copy matched this SHA256. `fastboot
-s "$MY_P11_SERIAL" boot /path/to/boot-sf-composer-temporary.img` returned
`Sending OKAY` and `Booting OKAY`. Android subsequently returned
`sys.boot_completed=1`, `4.19.157-perf+` and active slot `_a`.
All observed SurfaceFlinger internal threads and all ten observed vendor
composer threads (main, HWC uevent, Binder/HwBinder, SDM event, DPPS)
reported allowed CPUs `0-7`; the system-background cpuset remained `0-3`.
Thermal service severity remained 0.

## Same Settings benchmark (20 alternating swipes)

| Run | Frames | Janky/deadline missed | p50 | p90 | p95 |
|---|---:|---:|---:|---:|---:|
| A, first after boot | 393 | 45 (11.45%) | 23ms | 42ms | 57ms |
| B | 392 | 12 (3.06%) | 23ms | 24ms | 26ms |
| C | 388 | 11 (2.84%) | 23ms | 24ms | 25ms |
| D | 387 | 10 (2.58%) | 23ms | 24ms | 26ms |
| E | 392 | 10 (2.55%) | 23ms | 24ms | 25ms |

SurfaceFlinger missed-frame counter deltas A–E were 57, 4, 2, 0, 3.
The SF-all-only preceding experiment recorded warm p90 29/24/31/30ms
and jank 3.07/2.82/3.08/3.35%. This composer mode may improve the
slow tail modestly, but controlled cross-boot ordering remains insufficient
to isolate a composer-only effect. The **first** run after boot was still
poor and the median remains 23ms, so this experiment does not establish
fully smooth scrolling or justify a stable kernel tuning claim.

Use additional A/B tests with the same Settings screen, boot age, thermal
state and workload before selecting a production vendor task profile fix.
Once a validated release exists, remove the kernel-level exception in
favor of the original stock kernel semantics and Android vendor profiles.

Archive:
`/root/HDD/user0/P11/experiments/scroll-performance-20260924/boot-only/sf-composer/`.

No flash/wipe/resize/GSI movement, and no commands targeted other devices.
