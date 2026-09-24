# TB-J606F Android 16 scrolling performance experiment

This is an **experimental**, source-reproducible vendor-image variant, not a
validated upgrade or a replacement for the archived hybrid v5. Do not add it
to a public stable release until a boot and runtime comparison is recorded.

## Measured problem (24 September 2026)

Target: the TB-J606F selected by `P11_TARGET_SERIAL` (set locally to its
exact adb serial). LineageOS 23.2 Android 16 EROFS, ZUI14 14.0.147 vendor,
custom kernel 4.19.157-perf+, display 1200×2000 at 60 Hz (16.67 ms budget).

On the live device, `/proc/1791/cpuset` and the SF main thread, RenderEngine,
HwcAsyncWorker and appSf reported `/system-background`, with
`Cpus_allowed_list: 0-3`; the ZUI14 display composer likewise reported 0-3.
`/dev/cpuset/system-background/cpus` was `0-3`, while foreground/top-app were
`0-7`. The little cluster tops out at 1804.8 MHz and the big cluster at
2016 MHz. Thus SF/composer cannot be scheduled on the big cluster even while
applications' RenderThreads can.

The initial SystemUI graphics dump reported 1,155/4,775 janky frames
(24.19%), frame-time median 29 ms, p90 53 ms. A controlled Settings benchmark
(20 alternating 300 ms swipes) recorded median 22–23 ms, p90 25–28 ms and
10/387–391 missed-deadline frames across three successive runs. The Android
`gfxinfo` jank percentage is deadline-based and does **not** replace a
frame-time/FPS comparison. The SurfaceFlinger missed counters are cumulative:
compare differences within each run, not their absolute values.

Thermal HAL severity was zero, cooling states zero, battery saver disabled;
`MemAvailable` was approximately 3.4 GiB. An A/B/A trial using the temporary
Android fixed-performance mode yielded Settings p50 **23 / 23 / 22 ms**.
The command was reset to `false` after the experiment; forcing high clocks is
not an evidenced solution.

The Android 16 GSI's `/system/etc/task_profiles.json` explicitly defines
`SFMainPolicy` and `SFRenderEnginePolicy` to join `system-background`.
`/system/etc/init/surfaceflinger.rc` uses `task_profiles HighPerformance`,
but that does not override the **cpuset** paths of those SF thread policies.
The ZUI14 composer init service explicitly writes its PID to
`/dev/cpuset/system-background/tasks`.

## Candidate fix: change the two SF profiles only

Android's documented vendor task-profile overlay overrides a system profile
with the same name without editing the GSI:

https://source.android.com/docs/core/perf/cgroups#per-api-level-task-profiles

Android 16 source confirms it loads `/vendor/etc/task_profiles.json` after
system/API profiles:

https://android.googlesource.com/platform/system/core/+/android16-qpr2-release/libprocessgroup/task_profiles.cpp

`tools/tbj606f/make-scroll-perf-vendor.sh` adds the following two definitions
to a **new** image's `/vendor/etc/task_profiles.json`:

```json
{
  "Profiles": [
    {"Name": "SFMainPolicy", "Actions": [{"Name": "JoinCgroup", "Params": {"Controller": "cpuset", "Path": "foreground"}}]},
    {"Name": "SFRenderEnginePolicy", "Actions": [{"Name": "JoinCgroup", "Params": {"Controller": "cpuset", "Path": "foreground"}}]}
  ]
}
```

It preserves any pre-existing vendor task profiles. **No clocks, GPU voltage,
thermals, memory policy, kernel ABI, DTB, EROFS GSI or system partition change.**
The optional `--composer-too` additionally changes only the vendor display
composer service's `writepid` cpuset assignment to `foreground`. Compare the
SF-only variant first, then this second variant if SF-only is insufficient.

## Reproduce on fedora-heart (SSD build output)

The base is the archived, **tested** hybrid vendor v5, with exact SHA256:
`b0cca3012109d045122dccdbd22f2505327ec7550576daa37d4bde643a39d3dd`.
This image is preserved on the HDD; it is copied into a new output on SSD.

```bash
cd /root/p11-kernel-lab/research/tbj606f-scroll-perf
BASE=/root/HDD/user0/P11/releases/p11-a16-zui14-hybrid-stable-20260924/vendor_a-zui14-vndk30-z12wifi-z12audio-v5-760MiB.img
OUTDIR=/root/p11-kernel-lab/build/scroll-perf
mkdir -p "$OUTDIR"
TMPDIR=/root tools/tbj606f/make-scroll-perf-vendor.sh \
  "$BASE" "$OUTDIR/vendor-sf-foreground.img"
TMPDIR=/root tools/tbj606f/make-scroll-perf-vendor.sh \
  "$BASE" "$OUTDIR/vendor-sf-composer-foreground.img" --composer-too
sha256sum "$BASE" "$OUTDIR"/*.img
debugfs -R 'cat /etc/task_profiles.json' "$OUTDIR/vendor-sf-foreground.img"
e2fsck -fn "$OUTDIR/vendor-sf-foreground.img"
```

The tool refuses an unexpected base SHA256, an existing output, and an
unfamiliar composer init assignment. `e2fsck` must pass before an output is
published. Keep the stable original as rollback, record both new hashes, and
add their manifest **only after** a device boot succeeds.

The archived base's `shared_blocks` feature is valid: a read-only `e2fsck -fn`
passes. The earlier attempt to unshare **all** files cannot fit within the
760 MiB image. This builder retains existing deduplicated payloads, creates
the new profile inode, and recreates the small composer rc inode only when
that variant is requested. Both results passed whole-image read-only fsck.

### Generated candidate artifacts (24 September 2026, untested on device)

Both images live **only on the SSD** at
`/root/p11-kernel-lab/build/scroll-perf/`; both are 796,917,760 bytes.

| Image | SHA256 | Read-only e2fsck |
|---|---|---|
| `vendor-sf-foreground.img` | `d4ffe1040e53a56159e49d3d9a9e4ee4a57b98e8ffd2361d942de8e7e57fc50c` | exit 0 |
| `vendor-sf-composer-foreground.img` | `86a170e0eb694a9b2a5ce2424505d2c7ea93a57bf2322047c34ea3ebb6024556` | exit 0 |

Each image's `/etc/task_profiles.json` was extracted with `debugfs` and
verified to contain the two `foreground` profiles with SELinux label
`u:object_r:vendor_configs_file:s0`. SF-only retains composer rc's
`system-background` assignment; the composer variant uses `foreground`.
The archived original v5 SHA256 remained unchanged after image generation.

## Runtime validation (not yet done)

The current device reported `ro.boot.flash.locked=1`,
`ro.boot.vbmeta.device_state=locked`, `ro.debuggable=0`, and has no `su`.
The adb shell cannot modify privileged cpusets or boot an unsigned image.
**Neither candidate has been installed or benchmarked on the device.** Do not
reboot to fastboot or attempt an unsigned flash while it is locked. Never
modify `system_a`, wipe userdata, move the GSI from the Mac or modify other
attached devices.

When the device is in a verified flash-capable, recoverable engineering state,
keep the current working vendor backup and test one candidate at a time using
the established project installation/rollback flow. Do not replace the stable
release's verified hash with an experiment's hash.

Run the benchmark **from the Mac**, with only the P11 serial:

```bash
P11_TARGET_SERIAL="$MY_P11_SERIAL" tools/tbj606f/scroll-benchmark.sh /Users/heart/tmp/p11-before
# After tested candidate boots:
P11_TARGET_SERIAL="$MY_P11_SERIAL" tools/tbj606f/scroll-benchmark.sh /Users/heart/tmp/p11-after-sf
```

Before each run, confirm the same display mode, app, battery saver, temperature,
interactive screen, and vendor variant. Inspect `device.txt` for the new SF
main and RenderEngine cpuset and `summary.txt` plus `settings-gfxinfo.txt` for
frame times and missed-deadline counts. Ideally record at least three runs on
each image and compare p50/p90/p95, SF missed-counter deltas, device heat and
idle drain. Check that Wi-Fi, Bluetooth, camera, audio, sensors, rotation and
sleep/wake still function. If there is no repeatable benefit or there is a
regression, revert to the original stable hybrid v5 vendor image.

One additional valid awake baseline (`p11-scroll-baseline-20260924-awake`) on
the unchanged working vendor reported **389 Settings frames, 36 deadline
misses (9.25%), p50 27 ms, p90 36 ms, p95 48 ms**. SurfaceFlinger cumulative
missed counters increased by 85 overall, 70 HWC, 46 GPU during that run. This
run was recorded after waking the previously Dozing display, so warm-up is a
possible source of variation; three repeated runs remain necessary. Two
attempts made while the display was Dozing produced zero frames and are
**invalid** performance evidence; `scroll-benchmark.sh` now rejects Dozing
and runs with fewer than 100 frames.
