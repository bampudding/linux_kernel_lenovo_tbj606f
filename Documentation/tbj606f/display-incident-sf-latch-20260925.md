# 2026-09-25: intermittent half-screen tint + screen-off wake vs frame jank

## Facts observed before A/B

- Physical photos: a sharp approximately central vertical violet/teal divide
  across the lock screen, sometimes no visible image after screen off/on;
  user also observed successful intermittent wakes. The same 10:35 lock
  screen + power dialog in `adb exec-out screencap -p` did **not** show the
  same sharp divide. Screenshot was captured after the user photo and
  cannot prove simultaneous failure, but prioritizes HWC/DSI/panel output
  over a pure launcher software-painting or CPU scheduling diagnosis.
- Android 16 GSI with hybrid ZUI14 vendor and ZUI12 DTB/kernel. Old user
  space and kernel are not a matched display BSP. Current test boot at
  onset was kernel `#10 SMP PREEMPT Fri Sep 25 00:57:00 KST 2026`, matching
  active experimental GPU-floor build; archived stable kernel compiled
  `#2 SMP PREEMPT Wed Sep 23 20:29:56 KST 2026`.
- Native KGSL speedbin `0xc8` has top **950 MHz**; experimental `p11.f`
  restricts active GPU minimum to 465 or 600 MHz but retains top 950.
  Historical 980MHz modified speed-bin caused faults, do not reenable.
  No incident-correlated KGSL reset or DSI underrun proven. The
  boot-only current experimental option could not be read because shell
  is denied `/proc/cmdline` and GPU sysfs; only compiled build is matched.
- The *exact archived* hybrid vendor image
  `b0cca3012109d045122dccdbd22f2505327ec7550576daa37d4bde643a39d3dd`
  embeds `/build.prop` `debug.sf.latch_unsignaled=1`, and live Android
  `getprop debug.sf.latch_unsignaled` is `1`, while
  `vendor.gralloc.disable_ubwc=0` and `debug.sf.hw=0`. The `/system/etc/init/vndk.rc`
  trigger for `vendor.debug.sf.latch_unsignaled` does not explain this
  because that vendor-specific property was empty. PHH on-boot service
  also recorded `Set surface flinger hwc overlay to true`.
- AOSP explicitly documents `debug.sf.latch_unsignaled=true` as **Always**,
  with a risk of disrupting synchronized transactions and freezing
  display. Android 13+ adds narrower AutoSingleLayer mode; all-unsignaled
  legacy vendor setting overrides the narrower mode.
  https://source.android.com/docs/core/graphics/unsignaled-buffer-latch
- A separate existing launcher framerate check showed RenderThread sync
  p95 19.1ms and IssueDrawCommandsStart→SwapBuffers p95 19.9ms. This
  suggests buffer backpressure but does NOT causally link the display
  tint or frame jank to the above prop without controlled comparison.

## Isolated test artifact, NOT a released firmware

`tools/tbj606f/make-safe-sf-latch-vendor.py` requires the SHA-pinned,
796,917,760-byte previously validated hybrid vendor ext4 image, copies it
under a new path, replaces the **single byte** for `latch_unsignaled=1`
with `0`, verifies source and target `/build.prop` differ only by that
byte, byte-compares entire image and prints SHA256. Unlike filesystem
`rm`/`write`, a same-length data-byte replacement preserves the property
inode, SELinux label, ownership, other proprietary graphics components,
and ext4 structure.

Private output from 2026-09-25:
`/root/p11-kernel-lab/build/sf-latch-test/vendor_a-zui14-v5-latch-safe.img`,
SHA256 `1c304df1388b765f85bb07c980763dab159e271cc690f70850da36b483b4f5b1`.
`e2fsck -fn` passed all 5 passes. Do **not** commit/share private vendor
image, claim a fix before same-device A/B or alter stable v5 public release.

For comparison the exact known-good archived boot is SHA256
`93f9e9518fc9a20691ab0b3579b0c628e23522674e827fc57b8867945aedd635`.
Temporary `fastboot boot` stable ran Android 16 and 6 automated display
sleep/wake cycles returned software `mScreenState=ON` and
`mWakefulness=Awake`. Physically visible panel correctness is **not**
validated by these ADB states. Physical user photos plus near-simultaneous
screencap are required when the fault recurs.

## Safety/decision order

1. Keep original stable boot, original hybrid vendor and stock image backed
   up; never change DTB/DTBO, persist, GSI partitions or Wi-Fi modules
   simultaneously. Never mix ZUI14 DTB alone into ZUI12 kernel.
2. Run known-good temporary stable boot and compare actual display/wake.
3. Test ONLY the same-ABI hybrid vendor property change when rollback is
   concrete and current target slot verified; SurfaceFlinger reads the flag
   at startup, so late `setprop` cannot reliably test it.
4. Compare physical photo/screencap and matched launcher/SystemUI traces at
   1200x2000, 60Hz. If no improvement, restore original vendor and inspect
   matched OEM display/BSP and DSI reset plus UBWC/HWC composition.

The property change is a **plausible, source-backed compatibility fix to
probe**, not yet a proven root cause of tint or jank.
