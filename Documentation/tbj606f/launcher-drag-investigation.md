# TB-J606F launcher drag jank — separate Android UI from GPU clock

Status: **diagnosis, not yet a validated fix**. Device serial HA1E02DA,
LineageOS 23.2 Android 16 GSI / hybrid ZUI14, stable persistent boot,
physical 1200×2000, 240 DPI, 60 Hz. Avoid GPU OC/980 MHz, forcing buffer
release or flashing old temporary test boots while prior half-screen red tint
and panel-off wake issues remain unresolved.

## New observation (2026-09-25)

The user's launcher drag feels much worse than the Android Easter egg
animation. Current `dumpsys gfxinfo` since launcher process start showed:

| Process | Frames | Janky | p50 app | p95 app | p95 GPU |
|---|---:|---:|---:|---:|---:|
| `com.android.launcher3` Quickstep | 659 | 166 / 25.19% | 15 ms | 48 ms | 11 ms |
| `com.android.egg` | 589 | 44 / 7.47% | 38 ms | 77 ms | Not reliably measured: 4950 ms overflow bucket |
| `com.android.systemui` | 362 | 119 / 32.87% | 34 ms | 97 ms | 25 ms |

These counters include unrelated activities since process startup; do not
claim they measure only icon dragging. The Easter egg may render at a
**different target cadence** (38 ms median), so its lower official deadline
miss rate does not prove a higher FPS. `Number High input latency` is high
in the Easter egg too, so that classifier alone does not isolate Launcher.

A later read-only sample from `gfxinfo framestats` held 240 Launcher and
119 Easter egg **recent** rows. Launcher phase p95: Vsync→Input 10.0 ms;
SyncQueued→SyncStart **19.1 ms**; IssueDrawCommandsStart→SwapBuffers
**19.9 ms**; total IntendedVsync→FrameCompleted 48.2 ms. This supports
investigating RenderThread synchronization / buffer acquisition and
compositor pressure, **not** claiming the raw GPU shader time is 48 ms.
It is only a sampled post-hoc aggregate, not a matched gesture trace.

Previous controlled Settings scroll: 2.6–4.36% deadline misses; SystemUI
QS 27.64–31.55%; SF/composer placement, kernel boost and GPU/CPU floor
experiments did not consistently help. UI buffer-release wait p95 ~25.9
ms in the archived SystemUI ATrace. A temporary 960×1600 display test cut
QS deadline misses to 15–19% but was restored; lowering the resolution is
**not** the production fix. Original data: HDD
`experiments/scroll-performance-20260924/boot-only/display-corruption-and-boost-20260924/README.md`.

## Qualcomm vendor scroll hints (live config inspected, not activated)

The installed ZUI14 hybrid vendor's `/vendor/etc/perf/perfboostsconfig.xml`
has `bengal` vertical/horizontal scroll resource `0x00001080`, with GPU/CPU
bandwidth and little/big CPU floor requests. This establishes that native
vendor support is configured; it does **not** establish whether Android 16
Quickstep icon dragging calls those Qualcomm scroll hints or whether this
specific vendor performance HAL actually applies them on a physical finger
movement. Do not duplicate the old 180 ms CPU-boost experiment based on
this XML alone. Also the live `debug.egl.buffcount` currently reads `4`, but
changing it without before/after gesture traces could trade latency for
jank or complicate the separate rendering-corruption investigation.

## First discriminating test: manual physical gestures

Mac attached to the **exact** TB-J606F serial, display already awake and
unlocked, target app in foreground; logs stay private on Mac:

```sh
export P11_TARGET_SERIAL=HA1E02DA
# Open the home screen with a free region for repeated finger drags.
bash tools/tbj606f/launcher-gesture-benchmark.sh launcher \
  /Users/heart/tmp/p11-launcher-physical-1 20
# Open the Android Easter egg and repeatedly interact with its animation.
bash tools/tbj606f/launcher-gesture-benchmark.sh easteregg \
  /Users/heart/tmp/p11-easteregg-physical-1 20
python3 tools/tbj606f/analyze-launcher-framestats.py \
  /Users/heart/tmp/p11-launcher-physical-1/gfx-after.txt \
  /Users/heart/tmp/p11-easteregg-physical-1/gfx-after.txt
```

Both scripts refuse absent/wrong devices and `Dozing` screen. They do not
wake/switch apps, change display size, flash, or modify persistent options;
only gfxinfo in-memory measurements are reset. Capture three iterations
per workload before A/B conclusions, with wallpaper/taskbar conditions
recorded. For a full trace use the existing Mac ATrace/Perfetto workflow
and correlate physical `input` with Launcher UI, RenderThread, buffer
release, SurfaceFlinger/HWC/present fences, CPU freq and KGSL. **Scripted
Android `input swipe` is not a substitute for evdev finger input** when
claiming effectiveness of the optional kernel input-boost handler.

A/B priority at native 1200×2000: home icon drag vs empty-home swipe vs
app drawer swipe vs Easter egg; launcher wallpaper/taskbar layer changes;
CPU/render queue waits vs HWC scanout. Only change one reversible variable
at a time, restore it afterward. Do not remove launcher data or launch
unverified GPU overclocks.

The Mac connection was observed while the screen reported `Dozing`, so no
physical-gesture test was run or fabricated in this checkpoint.

## 2026-09-25 color-corruption incident and safer-fence candidate

**Urgent accuracy distinction:** While testing a Taskbar Lineage settings key,
`system_server` crashed twice (device wall time 22:29:47.764 and 22:30:58.444;
`InputSettingsObserver.onChange(InputSettingsObserver.java:172)` null
`Consumer.accept`). The user reported seeing a display color glitch just after
those crashes. The captured ADB screencap at 22:31:29 displayed a normal
lockscreen, but the red pixels might have disappeared before capture. The
contemporaneous `SurfaceFlinger` dump lists hardware composition for all seven
visible layers; it does not prove a persistent HWC bug, especially during
system-service recovery. `PHH: Set surface flinger hwc overlay to true` at
22:31:24 is post-crash PHH service bootstrap, **not proven to cause the glitch**.
Do not repeat unsupported `content insert`/`delete` on the `lineagesettings`
provider for performance A/B, or treat the reboot-disturbed Taskbar samples
as evidence of a Taskbar optimization. The earlier original `enable_taskbar`
key was absent and was restored to absent via `DELETE_system` before stopping
this class of live experiments.

**Separately, a concrete static rendering-risk candidate:** original verified
hybrid v5 vendor SHA256
`b0cca3012109d045122dccdbd22f2505327ec7550576daa37d4bde643a39d3dd`
contains `/build.prop` with `debug.sf.latch_unsignaled=1`, and the *live*
property was also `1` before any SF setting was modified. Android's
[Unsignaled buffer latching documentation](https://source.android.com/docs/core/graphics/unsignaled-buffer-latch)
explicitly discourages `Always` (`=1`) due to broken sync transactions and
freezes; the Android 13+ `AutoSingleLayer` mode is more constrained. This is a
**risk candidate, not a reproduced root cause of the physical red event**;
acquire fences should still be honored downstream by a correct HWC and GPU.
The device additionally uses a proprietary older ZUI14 gralloc/HWC plus an
Android 16 GSI, and has `vendor.gralloc.disable_ubwc=0`. Do not change UBWC,
clock or memory format at the same time; avoid false attribution.

The reproducible `tools/tbj606f/make-safe-fence-vendor.sh` copies only the
verified original image and changes a single **logical SF policy**:

```properties
# Original vendor:
debug.sf.latch_unsignaled=1
# Independent unflashed candidate:
debug.sf.latch_unsignaled=0
debug.sf.auto_latch_unsignaled=1
```

It refuses an unexpected input SHA256, unshares only the new `/build.prop`
inode, restores `0600`/root:root/`u:object_r:vendor_file:s0`, verifies exact
readback and both original/new ext4 filesystems, and re-hashes the unchanged
source. Verified **on SSD, not on the device**: candidate SHA256
`5d6a849f1791b373f1b2d16aa09b86efbe4858175e601c49c009eaa1f07744f4`,
path `/root/p11-kernel-lab/build/scroll-perf/vendor-sf-autosingle-fence-20260925.img`,
796,917,760 bytes. Because SurfaceFlinger reads its latching mode at startup,
**do not infer that a hot `setprop` would constitute a valid A/B**. Current
working vendor, boot, GSI, user data and active performance output remain
unchanged. This candidate is not a production upgrade or confirmed color
corruption/jank fix; test only after screen stability, original partition
identity, verified rollback and matched awake physical-gesture traces.
