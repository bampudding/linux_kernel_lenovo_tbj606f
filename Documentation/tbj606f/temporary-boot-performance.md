# TB-J606F boot-only SurfaceFlinger performance experiment

Date: 2026-09-24. Device: Lenovo Tab P11 TB-J606F, Android 16
LineageOS 23.2 EROFS GSI, 4.19.157-perf+ kernel, ZUI14/ZUI12 hybrid v5
vendor. Target serial must be supplied explicitly to every Mac ADB/fastboot
command. Other connected Android devices were not accessed.

## Why a separate experimental boot kernel?

The preferred production candidate replaces two Android task profiles in a
new vendor image (`make-scroll-perf-vendor.sh`). However, `fastboot boot`
accepts a boot partition image, not a vendor filesystem. During the
temporary-boot-only phase, `p11tune.sf_bigcpus=1` enables a **diagnostic,
non-production** kernel cpuset exception for the SurfaceFlinger process main
thread and its `RenderEngine` thread while each is in `system-background`.
The full CPU0–7 mask is bounded by active CPUs and any explicit requested
affinity; the system-background cpuset itself remains CPU0–3. Other tasks,
including the Qualcomm composer, retain their stock CPU placement. The
exception is disabled when the command-line option is absent; the normal
stable boot image instantly restores default behavior on the next boot.

This test isolates display-side scheduling as a hypothesis. Kernel-level
cpuset exceptions are inappropriate as a permanent production solution;
after repeatable benefit is shown, use the Android vendor task-profile
solution and separately validate composer placement.

## Temporary boot gate confirmed

Android `ro.boot.flash.locked=1` and `ro.debuggable=0` were misleading about
the host fastboot transport: `fastboot -s "$MY_P11_SERIAL" getvar unlocked`
returned `yes`. The known-good boot image SHA256
`93f9e9518fc9a20691ab0b3579b0c628e23522674e827fc57b8867945aedd635`
was transferred to the Mac and `fastboot -s "$MY_P11_SERIAL" boot ...` returned
`Sending OKAY` and `Booting OKAY`; `sys.boot_completed=1` subsequently.

## Build/recreate the first experiment on fedora-heart SSD

From source branch `perf/tbj606f-temporary-boot-sf-cpuset`, use the full
tested kernel configuration in
`/root/p11-kernel-lab/build/zui12-post157-erofs-z14-adsp-loader-stable1/.config`
and the project's documented clang-r353983c and aarch64 toolchain. Build
`Image` with an isolated SSD `O=` directory; the stable kernel build's output
directory may be reflink-copied for incremental rebuilds. For example:

```bash
cd /root/p11-kernel-lab/research/tbj606f-scroll-perf
export PATH=/root/p11-kernel-lab/toolchains/clang-r353983c/bin:/root/p11-kernel-lab/toolchains/aosp-aarch64-linux-android-4.9-android10/bin:$PATH
make O=/root/p11-kernel-lab/build/scroll-perf/kernel-out \
  ARCH=arm64 CC=/root/p11-kernel-lab/toolchains/clang-r353983c/bin/clang \
  CROSS_COMPILE=aarch64-linux-android- CLANG_TRIPLE=aarch64-linux-gnu- \
  -j12 Image
TMPDIR=/root tools/tbj606f/make-temp-sf-boot.sh \
  /root/HDD/user0/P11/releases/p11-a16-zui14-hybrid-stable-20260924/boot-z14-adsp-loader-stable1.img \
  /root/p11-kernel-lab/build/scroll-perf/kernel-out/arch/arm64/boot/Image \
  /root/p11-kernel-lab/build/scroll-perf/boot-sf-bigcpus-temporary.img
```

The builder requires the exact archived stable boot SHA256 and checks that
the DTB, ramdisk, and compressed raw Image round-trip unchanged through
the packed Android v2 boot image. Only the replacement kernel and
`p11tune.sf_bigcpus=1` boot argument differ from the stable boot template.
Output must fit within the known 96 MiB `boot_a` capacity.

Experiment `Image` SHA256:
`989a5ab492cd7e944a2497de7cd95fe5260f015ffaf4b564e940a927233b9ee7`.
Temporary `boot.img` SHA256:
`ce789b91d0958675d2ad7cf8f4fa86c0451fd24121aaa1ca10be3abded781aee`.
Temporary `boot.img` size: 14,290,944 bytes.

On the Mac, copy the verified image to a local non-GSI path; then use only:

```bash
adb -s "$MY_P11_SERIAL" reboot bootloader
fastboot -s "$MY_P11_SERIAL" getvar unlocked
fastboot -s "$MY_P11_SERIAL" boot /path/to/boot-sf-bigcpus-temporary.img
adb -s "$MY_P11_SERIAL" shell getprop sys.boot_completed
```

No `fastboot flash`, permanent boot/recovery installation, GSI movement,
partition resize, userdata wipe, or ZUI firmware swap was performed.

## First run: boot and scheduling confirmed

The experimental `fastboot boot` returned `Sending OKAY` / `Booting OKAY`.
The device eventually appeared in ADB and returned `sys.boot_completed=1`
and `4.19.157-perf+`. SurfaceFlinger main TID1777 and RenderEngine TID1814
had `Cpus_allowed_list: 0-7` while still in `/system-background`.
HwcAsyncWorker, appSf and the Qualcomm composer remained `0-3`; global
`system-background/cpus` remained `0-3`. Thermal service severity was zero.
Device discovery may take about a minute during normal Android boot; a
fastboot `Booting OKAY` alone is not proof of completed OS boot.

## Settings UI scroll results: three runs per variant

Benchmark `scroll-benchmark.sh` starts Settings, resets its `gfxinfo`,
executes 20 alternating 300 ms swipes and captures SF cumulative counter
deltas, CPU masks and temperature. Screen must be awake and 100+ app frames
recorded; zero-frame runs are rejected. Conditions may still vary with the
current Settings page, background work and thermal history.

| Variant/run | Frames | Janky/deadline missed | p50 | p90 | p95 |
|---|---:|---:|---:|---:|---:|
| Known-good baseline A | 420 | 41 (9.76%) | 23ms | 42ms | 46ms |
| Known-good baseline B | 368 | 41 (11.14%) | 23ms | 44ms | 53ms |
| Known-good baseline C | 391 | 20 (5.12%) | 23ms | 36ms | 42ms |
| SF-only diagnostic A | 407 | 21 (5.16%) | 23ms | 32ms | 40ms |
| SF-only diagnostic B | 407 | 20 (4.91%) | 23ms | 30ms | 36ms |
| SF-only diagnostic C | 401 | 27 (6.73%) | 23ms | 28ms | 36ms |

The p90 mean decreased ~26%, from 40.7 to 30.0 ms. Deadline misses
were 102/1179 (~8.65%) baseline and 68/1215 (~5.60%) experimentally.
The median stayed 23ms. Thus this is evidence of improvement in the slow
tail but does not justify describing the experience as fully smooth or a
proven cure. Preserve raw logs and re-test unchanged stock boot to control
for run order before upgrading any stable release.

Logs/boot binaries for this experiment are archived on HDD in
`/root/HDD/user0/P11/experiments/scroll-performance-20260924/boot-only/`.
