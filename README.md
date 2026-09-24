# Linux kernel for Lenovo Tab P11 (TB-J606F)

This project continues the TB-J606F kernel work originally published at
https://github.com/JulianDroske/linux_kernel_lenovo_tbj606f.

The Git history is intentionally preserved from the Lenovo source import and
the original 2024 device bring-up. The current development target is a stable
Linux 4.19.157 kernel for Android 16 EROFS GSIs while retaining Lenovo hardware
compatibility and selectively supporting newer ZUI14 vendor userspace.

## Current tested baseline

- Device: Lenovo Tab P11 TB-J606F Wi-Fi
- SoC / fastboot product: Qualcomm Bengal
- Kernel: Linux 4.19.157-perf+
- Stable kernel-code checkpoint: 7124b9c09
- Android: LineageOS 23.2 Android 16 EROFS GSI
- Vendor userspace: Lenovo ZUI 14.0.147 hybrid
- Persistent normal boot: verified
- Sensors / automatic rotation: working
- Wi-Fi 5 GHz / 802.11ac: working
- Audio primary speaker path: working
- Bluetooth: ON and enumerated
- Cameras: two devices enumerated

See [STATUS.md](./STATUS.md) for the validation matrix.

## Documentation

- [Android 16 / ZUI14 bring-up](Documentation/tbj606f/android16-zui14-bringup.md)
- [Development history and provenance](Documentation/tbj606f/development-history.md)
- [Optional Rouleur audio compatibility module](tools/tbj606f/audio-compat/README.md)

## Reproduction helpers

The repository includes source-only helpers for the complete tested workflow:

- tools/tbj606f/build-kernel.sh
- tools/tbj606f/repack-boot.sh
- tools/tbj606f/make-hybrid-vendor.sh
- tools/tbj606f/verify-runtime.sh
- tools/tbj606f/audio-compat/

The boot repacker preserves the known-good ramdisk and DTB while replacing only
the compressed kernel. The hybrid-vendor builder consumes firmware extracted
by the device owner and regenerates module dependency metadata for the mixed
ZUI14/ZUI12 module set.

## Proprietary firmware boundary

Lenovo vendor images, signed vendor DLKMs, modem/DSP images, OTAs, Google apps,
and other proprietary binaries are not added to this repository. The public
tree contains only source, patches already represented by Git commits, and
reproduction/verification tooling.

## Upstream and history

The original branches remain meaningful:

- official-kernel: Lenovo source import
- dev: original touchscreen/Wi-Fi device bring-up
- opensource/tbj606f-a16-zui14: current public continuation

Research branches for failed or superseded FastRPC, KABI, GLINK, GPU and EROFS
experiments are deliberately preserved rather than rewritten out of history.

## License

The kernel remains licensed under GPL-2.0 with the Linux syscall exception as
described by [COPYING](COPYING). Individual files may carry additional
SPDX-compatible licenses.
