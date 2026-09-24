# TB-J606F temporary boot experiment 2: all SurfaceFlinger threads

2026-09-24. Branch `perf/tbj606f-temporary-boot-sf-all` builds on
`perf/tbj606f-temporary-boot-sf-cpuset`.

With `p11tune.sf_bigcpus=1`, only the SurfaceFlinger main and RenderEngine
threads receive active CPU0–7 while in Android's `system-background`
cpuset. With `p11tune.sf_bigcpus=2`, **all threads of that one
SurfaceFlinger thread group** receive active CPU0–7 while in
`system-background`, bounded by explicitly requested CPU affinity.
The Qualcomm vendor composer and unrelated background processes remain
CPU0–3. The flag is disabled by default. This is an isolated, temporary
boot diagnostic, not a recommended production kernel change.

## Reproduction

Build the exact source/config/toolchain specified in
`temporary-boot-performance.md`, preserving the stable DTB and ramdisk,
then:

```bash
TMPDIR=/root tools/tbj606f/make-temp-sf-boot.sh \
  /root/HDD/user0/P11/releases/p11-a16-zui14-hybrid-stable-20260924/boot-z14-adsp-loader-stable1.img \
  /root/p11-kernel-lab/build/scroll-perf/kernel-out/arch/arm64/boot/Image \
  /root/p11-kernel-lab/build/scroll-perf/boot-sf-all-temporary.img --all-sf
```

Kernel Image SHA256:
`064d93f69c5f2115afb91469d36c1807db27f1322e5961dde453f6d62da4bc78`.

Boot image SHA256:
`872a8cbfed4579a728e78a90ab3f4d8308e18f709b494104b7cac93a82ef7631`.
Size: 14,290,944 bytes. Re-packed ramdisk and DTB compared byte-for-byte
against the stable boot source; the target `p11tune.sf_bigcpus=2` option
was verified in the boot image's command line. The Mac copy matched SHA256.

The serial-scoped `fastboot boot` operation returned `Booting OKAY`.
Android returned `sys.boot_completed=1` and kernel `4.19.157-perf+`.
SurfaceFlinger main, RenderEngine, HwcAsyncWorker, app/appSf,
RegionSampling, TouchTimer and auxiliary surfaceflinger threads reported
`Cpus_allowed_list: 0-7`, while Qualcomm composer remained `0-3` and
`/dev/cpuset/system-background/cpus` remained `0-3`. Thermal severity=0.

## Same 20 alternating Settings swipes: initial and warmed runs

| Run | Frames | Janky/deadline missed | p50 | p90 | p95 |
|---|---:|---:|---:|---:|---:|
| A (post-boot first run) | 406 | 42 (10.34%) | 24ms | 42ms | 53ms |
| B | 391 | 12 (3.07%) | 23ms | 29ms | 31ms |
| C | 390 | 11 (2.82%) | 23ms | 24ms | 25ms |
| D | 390 | 12 (3.08%) | 23ms | 31ms | 32ms |
| E | 388 | 13 (3.35%) | 23ms | 30ms | 32ms |

SurfaceFlinger total missed counter deltas in runs A–E were 89, 2, 3, 4,
5 respectively. The poor first run and unchanged p50 are unresolved;
warm-only results must not be represented as guaranteed cold-boot
performance. The five raw benchmark directories and image/kernel hashes are
preserved under HDD `experiments/scroll-performance-20260924/boot-only/sf-all`.
Next diagnostics should compare stable return boot and test vendor composer
separately before declaring this fixed.

No vendor/system image was applied, no flash command executed, no userdata
wiped, and no other attached device used. Original stable boot stays the
reversion path through serial-scoped `fastboot boot` or a normal reboot.
