# Native GPU floor rollback — 2026-09-25

**Status:** untested as a definitive fix for intermittent half-screen tint
or missed physical wakes, but source-level correctness bug confirmed.
This branch preserves the original `7124b9c09a48380a7b028104e17cac36b9b1a0af`
GPU power-level policy. It does NOT overclock or impose an active minimum.

## Original experimental-only diff

The GPU floor worktree inherited original stable source commit `7124b9c09`
with exactly **one** modified tracked file,
`drivers/gpu/msm/kgsl_pwrctrl.c` (+52 lines). The rest of the source,
including GPU `adreno.c` and DSI panel code, remained byte-identical to
that source. `.config` SHA256 for floor and stable-equivalent experiments:
`36270e3c45eb9e663e71eef8579617f09ad25d7732d009d5d4c1ea96f55bf734`.
Known-good archived boot SHA256:
`93f9e9518fc9a20691ab0b3579b0c628e23522674e827fc57b8867945aedd635`.
Two floor boots append ONLY `p11.f=465` or `p11.f=600`; stock cmdline
has neither. Stable and floor boot ramdisk and DTB are byte-identical.

`0b1243751` reconstructs the original uncommitted diagnostic change,
`35c7ba9fa` reverts it, preserving the exact experiment and a reviewable
fix. The resulting `kgsl_pwrctrl.c` is byte-identical to the archived
stable source. The original experimental worktree, boot images and HDD
archived stable boot were NOT overwritten.

## Specific correctness bug, independently audited

KGSL indexes faster GPU pwrlevels as lower numbers: index 4=600MHz,
5=465MHz, 6=320MHz. Experimental `_adjust_pwrlevel` unconditionally
constrains `min_pwrlevel` to index <=4 or <=5 whenever `p11.f` is used.
However stock KGSL `kgsl_pwrctrl_max_clock_set()` implements a requested
non-bin thermal limit by fractional cycling between neighboring levels:
`kgsl_thermal_cycle()` calls `kgsl_pwrctrl_pwrlevel_change()` for
`thermal_pwrlevel` and `thermal_pwrlevel + 1`. Under floor600 and a
requested 530MHz between 600/465, the newly installed index4 clamp
suppresses index5 and produces 600/600 instead of 600/465. At floor465
it likewise suppresses index6 for a 390MHz target. This breaks a
thermal-frequency limit, potentially increases power/heat and keeps
GPU/bus work busy when stock would downclock. POPP ordering presents
an additional inverted bound case, but exact user-visible tint causality
is not proven. **Do not retain this floor by moving its check into the
thermal-cycle timer: the global clamp affects more paths.**

## Rebuild and safe packaging

Build from this branch with Android clang r353983c and AOSP GCC 4.9,
`vendor/bengal-perf_defconfig`, the archived Android16 config fragment,
`ARCH=arm64`, `Image dtbs`. Use an SSD output directory. New build
will have a different `UTS_VERSION` timestamp; matching source/config is
not a claim of byte-identical archived boot.

`tools/tbj606f/make-safe-gpu-boot.sh VERIFIED_STABLE_BOOT.img BUILT_SAFE_Image NEW_BOOT.img`
requires exact source boot SHA256 and preserves its ramdisk/DTB, checks
that neither GPU floor nor 960MHz commandline option persists. This tool
**does not flash**. The simplest known-good rollback remains the exact
archived stock-hybrid boot itself, and live device remains on temporary
stable boot until an explicitly chosen persistent repair. Vendor v5
and existing stable public release remain unchanged.

## Build and temporary-boot validation, 2026-09-25

- Full clean SSD build succeeded with `JOBS=8`, Clang r353983c,
  AOSP GCC 4.9 and the same `.config` SHA256
  `36270e3c45eb9e663e71eef8579617f09ad25d7732d009d5d4c1ea96f55bf734`.
- Raw `Image` SHA256
  `9a10a645df3fec2da25c7230cb6ad048cd02303386c35c9b887853dfdff3e1ab`,
  generated boot SHA256
  `f1fa1adb8e5f834b7cd6b56b2aed6393e975ed6edcc5b7f63fd10b6f15774979`.
  Both are local **diagnostic** outputs, not old stable release replacements.
- Boot packer verified byte-identical ramdisk and DTB to known-good
  93f9 boot, no `p11.f=` nor `p11tune.gpu_top_freq=` in commandline.
- `fastboot -s HA1E02DA boot` accepted diagnostic boot with NO partition
  flash; Android `sys.boot_completed=1`, GPU top950MHz, boot build
  `#1 SMP PREEMPT Fri Sep 25 11:55:14 KST 2026`, same original hybrid
  vendor property `debug.sf.latch_unsignaled=1`.
- **6/6 ADB software display OFF→ON cycles passed**. These do not
  guarantee absence of intermittent physically visible panel tint/black
  screen; user physical confirmation and longer observation are essential.
- Host build folder: `/root/p11-kernel-lab/build/gpu-floor-safe-20260925/`.
  User original HDD boot, dirty historical GPU-floor experiment worktree,
  stable vendor and flash partitions were not modified. Currently the
  **temporary boot** can disappear after an ordinary reboot; do not claim
  persistence or final cure for display/timing issues.
