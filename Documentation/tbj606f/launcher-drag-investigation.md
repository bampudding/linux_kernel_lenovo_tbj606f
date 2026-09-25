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
