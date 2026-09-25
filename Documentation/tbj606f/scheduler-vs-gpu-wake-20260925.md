# TB-J606F Android 16 system-wide UI latency: scheduler vs GPU power

2026-09-25; user reports more visible jank after removing the unsafe global
GPU active floor 465/600MHz. No assumption that the floor revert fixes jank.

## Evidence from the same device, native 1200×2000 / 60Hz

- On validated no-floor temporary boot, kernel thermal HAL severity **0**;
  cooling sysfs `thermal-cpufreq-0`, `thermal-cpufreq-4`, and
  `thermal-devfreq-0` all `cur_state=0` during 20 Settings scrolls and
  10 quick-settings expand/collapse pairs. CPU max frequencies remained
  native 1804800/2016000 kHz; no actual thermal throttle observed.
- Actual runtime governors were `schedutil`, both WALT PL=1, 0µs
  up/down rate limits; CPU big cluster frequency at normal governor
  minimum 1056000 kHz for 12.91/17.99 seconds in the traced QS sample,
  while active core activity and clock peaks to 2016000 kHz also appeared.
  A low frequency **between bursts** is a governor load decision, not
  evidence of a heat cap.
- Settings native 20 scripted swipes: 501 frames, 23 jank = **4.59%**;
  separately traced Settings run: 441 frames, 5 jank = 1.13% (run-to-run
  variability). QS sample: 328 frames, 114 jank = **34.76%**, app p50
  36ms/p90 61ms; GPU p50 8ms/p95 22ms. Prior multiple tests showed
  27–33% QS miss; low-resolution 960×1600 trial cut it to 15–19% but
  reduced sharpness and was reverted.
- Android tracing (`gfx view input sched freq idle hal binder_driver
  thermal`) in that QS sample: SurfaceFlinger sched_wakeup→scheduled
  p90 **0.402ms** (p99 .792), `RenderThread` p90 **0.552ms**
  (p99 3.393). Yet RenderThread `waitForBufferRelease` 275 occurrences,
  p95 **23.76ms**, generic `dequeueBuffer` 584 occurrences p95
  **20.59ms**, HWC present p95 ~7.17ms. CPU runqueue starvation cannot
  account for the majority of ~24ms wait; investigate GPU/HWC buffer
  release and full-resolution composition, including Taskbar's frequent
  redraw. This does not distinguish which GPU/SDM/bus stage causes the
  backpressure.
- Archived stable ZUI12 DTB for eFuse 0xc8 selects
  `qcom,initial-pwrlevel=<6>`: **320MHz** default wake, with 465MHz
  at index5, 600MHz at4, 950MHz max at0. Kernel
  `kgsl_pwrctrl_enable()` uses `default_pwrlevel` on normal GPU wake.
  A sustained active minimum/thermal limit clamp must NOT be reintroduced:
  the old floor blocked thermal 600↔465 fractional cycling.

Raw local-only traces/records:
`/Users/heart/tmp/p11-scheduler-diagnosis-20260925/settings-atrace.txt`,
`qs-atrace.txt`, their decoded summaries and CPU/thermal policy snapshots.
Do NOT publish entire Android logcat/screenshots: may contain private data.

## Very narrow wake-only experiment (NOT a production fix)

`drivers/gpu/msm/adreno.c`: optional short boot parameter `p11.gw=465` only
for exact native speedbin `0xc8`, table 8 entries, source top950 MHz,
startup index6=320 MHz, verified index5=465MHz. Sets `active_pwrlevel`
and `default_pwrlevel` to index5 at GPU probe; devfreq startup is also
based on default. It does NOT constrain `min_pwrlevel`, thermal, max,
OPP, or sustained GPU frequency. Existing governor may return to 320MHz.
Fallback without boot arg is source-level identical to earlier safe
branch. `make-gpu-wake-boot.sh` creates two byte-identical kernel/DTB/
ramdisk images differing *only* in boot cmdline, for matched temporary
`fastboot boot` A/B. Rebuild with original android16 config Clang9.

Build config SHA256
`36270e3c45eb9e663e71eef8579617f09ad25d7732d009d5d4c1ea96f55bf734`;
raw Image SHA256
`06448a7242653fe1da30f3fde409232ea27b06199459e011ed6d4cee4dcec3b9`;
private output `/root/p11-kernel-lab/build/gpu-wake465-20260925/`:
control boot SHA `ca335c91389cf1c56dd34f7233e50ace903c7308eeb95b905c09e74c0880c36a`,
465 boot SHA `488ab4ec32fb03afaa260895312eaffb399750f7bfca3665abdb4cc8bb8438fe`.

Both booted to `sys.boot_completed=1` using **temporary** `fastboot boot`;
465 version emits kernel message `p11: verified native GPU wake 320 ->
465MHz`. Both keep vendor and ramdisk/DTB untouched. Control QS after
boot and physical screen activity 343 frames/33.53% miss and
322 frames/38.82% miss; first only62 was discarded. **465 A/B is
INCONCLUSIVE**: screen was observed on lockscreen after test; window policy
reported `KeyguardStateMonitor.mIsShowing=true`, `mDreamingLockscreen=true`.
Noninteractive `cmd statusbar` produced 0 frames behind keyguard on both
465 and the safe rollback boot after return. Zero frames are invalid
rather than a GPU hang or a performance result. Human must physically
unlock after every temporary boot before rerunning; do not infer 465
performance benefit or failure. The device was returned by temporary
boot to the previous no-floor safe #1 kernel (build 11:55:14); no
partitions were flashed or permanent settings changed.

Next: after human unlock confirm `mIsShowing=false` and awake before EACH
run; alternate control-wake320, optin-wake465, then control again with
three native-resolution runs each. Test actual finger launcher drag and
QS separately, record thermal state and frame stats. If 465 has no
reproducible improvement, discard it; focus on HWC/GPU and vendor
memory-bandwidth requests rather than increasing global CPU/GPU floors.
