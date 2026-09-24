# TB-J606F boot-only scroll experiments and intermittent color artifact

2026-09-24. Status: diagnostic work only; **do not merge into stable or
flash these test images**. User reported intermittent half-screen red tint
in white UI regions and line-like artifacts. Cause is not established.

## Controls and measured results

Test device: TB-J606F, Android 16, LineageOS 23.2 GSI, hybrid ZUI14 vendor,
60 Hz 1200x2000 stock panel. Target only the explicitly selected serial.
Every boot experiment used `fastboot -s "$P11_TARGET_SERIAL" boot IMAGE`;
no permanent boot/vendor/system flash, userdata wipe, GSI relocation or
partition resize. All original stock images remain unchanged.

Settings scroll after warmup on persistent stable boot:
390 frames / 4.36% jank, 385 / 2.60%, 382 / 2.62%; median frame-duration
23/23/24 ms. A 23 ms Android gfxinfo duration is NOT by itself proof of
43 Hz actual panel presentation: panel hardware is 60 Hz.

SystemUI repeated quick-settings expand/collapse (10 pairs, 100+ frames):

| Boot / condition | Frame count | Missed deadlines | p50 | p90 |
|---|---:|---:|---:|---:|
| Stable baseline run, first exploratory | 521 | 144 (27.64%) | 38 ms | 61 ms |
| Stable baseline run, scripted | 504 | 159 (31.55%) | 40 ms | 61 ms |
| SF+composer CPU placement diagnostic | 511 / 528 / 516 | 28.57% / 24.81% / 31.59% | 40/40/42 ms | 65/61/65 ms |
| SF+composer + kernel input boost 180 ms, vendor native little floor | 515 / 525 / 503 | 28.93% / 29.90% / 33.00% | 40/40/40 ms | 65/65/65 ms |
| SF+composer + kernel input boost 180 ms, native little and big hispeed bins | 511 / 529 / 511 | 27.20% / 27.22% / 29.35% | 38/40/42 ms | 61/61/65 ms |
| Above, fixed-performance mode temporarily enabled | 511 | 31.90% | 40 ms | 61 ms |
| Above, blur temporarily disabled, then restored | 514 / 509 | 29.96% / 30.06% | 42/40 ms | 65/65 ms |
| Above, **960x1600 logical resolution + 192 DPI temporarily** | 576 / 560 | **15.28% / 18.93%** | 32/34 ms | 44/48 ms |

Resolution trial renders only 64% of full-resolution pixels and showed a
large performance improvement, **but sacrifices image sharpness**. It was
reset to physical 1200x2000, density 240 immediately afterward. No
resolution reduction was made permanent.

Important validity limit: `adb shell cmd statusbar expand-settings` and
`adb shell input swipe` inject at Android userspace and may bypass Linux
evdev. The opt-in kernel `input_boost_ms=180` was verified in sysfs, but
this scripted benchmark does **not prove the kernel input boost handler
fired**; results must not be generalized to physical-finger scrolling
without confirming input events. The first experimental boot with long
`p11tune.scroll_boost=` option was INVALID because the actual bootloader
truncated the kernel command line; v2 images use `p11.b=1/2` and their
runtime sysfs verified 180 ms / supported stock-bin floors.

An ATrace captured for the SF+composer image during QS transitions:
SystemUI RenderThread `waitForBufferRelease` (442 occurrences) p50 ~11.2
ms, p95 ~25.9 ms, max ~119 ms; its Drawing p50 ~5.4 ms; UI traversal
p50 ~12.7 ms. Buffer-release backpressure is confirmed, but by itself
does **not distinguish GPU, HWC or scanout as the root cause**. Forcing
early buffer release risks visual corruption and is not proposed.

## Display-artifact investigation and present safe state

The short-lived CPU input-boost kernel did not edit KGSL, Adreno, DSI,
panel/MDSS or DTB; it modified `drivers/cpufreq/cpu-boost.c` and retained
the previously tested opt-in SF/composer cpuset diagnostic. Both candidate
v2 `boot.img` files retain the archived stable ramdisk and DTB exactly.
The archived hybrid vendor retains stock ZUI14 graphics gralloc,
mapper, HWC, Adreno EGL and SDM libraries, with an older ZUI12-derived
kernel stack. Cross-generation graphics compatibility requires diagnosis,
but no cause is proven.

The user reported occasional half-screen red tint affecting white regions
and lines. Experiment and returned stable-boot kernel logs both show
identical *boot-time* panel parser errors for `Novatek36523W video mode
dsi boe panel`: `invalid vsync source selection`, `failed to parse
vregs`, `failed to parse power config rc=-22` and invalid ESD
configuration/status length. They may be existing nonfatal device-tree
warnings and **are not evidence that a visible artifact occurred at
those times**. No distinct GPU fault, timeout, DSI underrun or SMMU page
fault was found in the searched runtime log ranges. Historical forced
GPU speed-bin 980 MHz experiments produced KGSL faults; **never revive
that bin or run GPU overclocking during corruption diagnosis**.

A host-side `capture-display-artifact.sh` script records screenshot,
kernel, Android logs, SF/display state **when the physical symptom is
visible**, without changing the device. Pair it with a separate camera
photo of the same frame. If the red area appears in captured pixels, favor
render/graphics buffers; if visible only on the actual panel, investigate
HWC overlay/scanout/DSI/panel. A clean screenshot alone does not fully
exonerate display overlays. Also compare stable persistent boot and
test boot with the SAME vendor and content, and whether artifact occurs
in boot logo/recovery. Do not infer a defective panel solely from this.

The device was restored by normal `adb -s SERIAL reboot` from the
temporary test image. Verified afterward: `sys.boot_completed=1`,
slot `_a`, original `input_boost_ms=80`, original vendor little
`0:1017600` only, SF/composer CPU allowed `0-3`, no extra
`debug.hwui.renderer`, physical size 1200x2000, density 240, blur
setting restored `0`, thermal status `0`. No permanent flashes.

## Build outputs (UNTESTED AS FIX / never flash)

Source independent worktree
`/root/p11-kernel-lab/research/tbj606f-scroll-boost` from checkpoint
`7052a0d23`; source branch `perf/tbj606f-temporary-boot-scroll-boost`.
Built with archived stable config and specified Clang 9 toolchain.
Output dir: `/root/p11-kernel-lab/build/scroll-boost/`.

- Experimental raw Image SHA256:
  `8502f80b787506483f6319b222a053b847b9aa137e084905afebf8b5e1f55ae4`.
- v2 mode1 boot SHA256:
  `0fdeb6d0449a1d49a1a932f5f7fc469d9ba76b037992113ead88b47946be418b`.
- v2 mode2 boot SHA256:
  `d4b3909eac836454d80662cd1615cf8f592c995b3aacfbd85c99b429346ace8e`.

Their boot header options use `p11tune.sf_bigcpus=3 p11.b=1/2`
and were verified on-device (Android completed and mode 1/2 sysfs
readback). The earlier mode1/mode2 files with the long boot argument
are **invalid experiment variants** and must not be deployed.

All raw private device logs should remain in the HDD experiment archive,
NOT a public Git repository.
