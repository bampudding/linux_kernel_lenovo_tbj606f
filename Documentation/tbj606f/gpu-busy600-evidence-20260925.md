# TB-J606F: native GPU busy-sample headroom, controlled A/B, 2026-09-25

Status: measured PARTIAL improvement. Not a complete solution to physical
finger dragging or display corruption. Do not merge into current stable yet.

The user's ~22s / 24fps camera video shows notification-panel gestures
with inconsistent visible response. Camera encoding is not tablet FPS.
The private video and Android traces MUST NOT be uploaded to GitHub.

## Evidence that motivated the scoped fix

Previous native-resolution, no-floor boot: QS 328 frames, 114 misses
(34.76%); RenderThread buffer-release wait p95 23.76ms; scheduler
wakeup-to-run p90 0.4ms SF / 0.55ms RenderThread. Current Android
thermal GPU and CPU cooling cur_state=0; there was later Android skin
severity3 during repeated runs, NOT CPU/GPU throttling. CPU scheduling
and GPU/SDM/bus remain separate contributing factors.

Kernel power/gpu_frequency ftrace joined with Android graphics ATrace
during a repeated QS action showed only 320<->465 MHz and GPU off,
with buffer-return waits to 32ms while 465MHz. Later same-kernel
controls reached 600MHz only briefly (~0.5-0.8s/capture), and mostly
ran at 465MHz. This is a correlation between weak devfreq response
and slow buffers, NOT a proof that every buffer wait is GPU-bound.

The stock selected speedbin 0xc8 supports precisely
950/900/820/745/600/465/320 MHz. Stock qcom,initial-pwrlevel=6
corresponds to 320MHz. The earlier global p11.f=465/600 experiment
incorrectly clamped KGSL thermal fractional cycling and stays REMOVED.

## Change and conservative guards

Kernel drivers/devfreq/governor_msm_adreno_tz.c accepts only the
optional boot argument p11.gb=600. Enable only when all seven exact
native speed-bin frequencies match. TZ makes its normal decision first.
If the accumulated sample has at least 3ms GPU-busy time and at
least 40% busy over the governor's minimum 5ms sample, and TZ
would otherwise return index 5/6 (465/320MHz), use native index4
(600MHz) for the NEXT work batch. Original TZ higher votes win.
Idle/low busy still permits native 320MHz and slumber. No changes
to thermal cap, min/max, GMU, OPP, bus table, panel or stock 950MHz.
KGSL pwrlevel adjustment still enforces all thermal/bounds decisions.
This may increase power/skin temperature during actual GPU demand.

Build with Clang r353983c, GCC4.9, archived Android16 fragment and
vendor/bengal-perf_defconfig. .config SHA256:
36270e3c45eb9e663e71eef8579617f09ad25d7732d009d5d4c1ea96f55bf734
Raw Image SHA256:
c13a6fdc4b741d1a1ba597441fb71a4066af225c76c76884d9fd652ded1af764
Control boot SHA256:
5755419bdc88bb0ad7d579dbf03d28459f9059dd47ed2529a8e44818da068fb2
Opt-in test boot SHA256:
3a524d8154b7465e31f0dfb33730fe7964701a67b15d3c7d06286b35d08399df
Both have same Image, ramdisk and DTB: only commandline differs.
Exact source stock boot SHA93f9e9518fc9a20691ab0b3579b0c628e23522674e827fc57b8867945aedd635.
Both fastboot boot accepted; NEVER flashed. Test boot kernel log
states p11: native GPU busy600 enabled (governor+thermal intact).

## Actual A/B/A, SystemUI QS at 1200x2000 and 60Hz

After every boot unlocked the swipe-only keyguard, warmed QS, reset
gfxinfo and ran ten identical statusbar expand-settings/collapse pairs
under same 16s graphics/scheduler/frequency trace. Zero-frame locked
tests were excluded. Local-only Mac raw data:
 /Users/heart/tmp/p11-gpu-busy600-20260925/{control-1,exp-1,exp-2,exp-3,control-2,control-3}

| Mode/run | Frames | Missed deadline | Buffer release p95 | 600MHz residency |
|---|---:|---:|---:|---:|
| Control 1 | 312 | 135 (43.27%) | 26.24ms | 0.80s |
| Busy600 1 | 328 | 109 (33.23%) | 24.25ms | 5.08s |
| Busy600 2 | 329 | 121 (36.78%) | 23.95ms | 5.27s |
| Busy600 3 | 325 | 117 (36.00%) | 24.46ms | 5.27s |
| Control 2 | 330 | 125 (37.88%) | 25.58ms | 0.51s |
| Control 3 | 308 | 133 (43.18%) | 26.11ms | 0.65s |

Three-run averages: control 41.44% vs test 35.34% misses;
buffer release p95 control ~25.98ms vs test ~24.22ms.
Control GPU p95 25ms/23ms where valid, all tests 19ms. Control 2
reported an invalid/overflow 4950ms GPU p95, so do not aggregate it.
Short scripted transitions are NOT identical to real finger drags;
three trials are insufficient to establish statistical certainty.
Thermal CPU/GPU coolers remained state0 at every sample end.
Some later HAL skin severity3 values occurred.

## Follow-up

User physical video and response A/B still needed on the temporary
test boot. Residual ~35% missed deadlines means further investigate
native fullscreen 1200x2000 HWC/SDM + Taskbar layers, present fences,
bus bandwidth and release callbacks. The Bengal Drag performance hint
lacks CPUBW that native Scroll has, but its actual GSI->Qualcomm
trigger is NOT demonstrated; do not flash hypothetical vendor XML.

The user device is left in temporarily booted busy600 mode;
normal restart returns to installed boot. The current official
stable ZIP, vendor image, partition layout and audio paths are
not changed. Do not publish proprietary boot/vendor binary.
