# Kernel for Lenovo Tab P11 (TB-J606F)

Linux 4.19 kernel development for the Lenovo Tab P11 TB-J606F (`bengal` /
`m11_prc_wifi`), continuing the original work by
[JulianDroske](https://github.com/JulianDroske/linux_kernel_lenovo_tbj606f).

This repository preserves the original Git history and continues it with the
device bring-up, Linux 4.19 stable uplift, Android 16 EROFS support, runtime
fixes, and ZUI14 vendor compatibility work used on the TB-J606F.

## Current tested baseline

The current public baseline is tested with:

- Lenovo Tab P11 TB-J606F Wi-Fi
- Linux `4.19.157-perf+`
- LineageOS 23.2 Android 16 EROFS GSI
- ZUI14 `14.0.147` vendor userspace
- ZUI12-compatible Wi-Fi and audio DLKMs where the newer ZUI14 modules do not
  match the preserved kernel ABI

Verified on the current stable checkpoint:

- Android boot completion
- EROFS root filesystem
- touchscreen
- Wi-Fi, including 5 GHz / 802.11ac
- Bluetooth
- cameras
- charging/battery reporting
- Qualcomm sensor DSP / FastRPC path
- 34 hardware sensors
- automatic rotation
- primary speaker audio path

The stable kernel checkpoint is `7124b9c09` plus the public userspace/vendor
reproduction helpers on branch `opensource/tbj606f-a16-zui14`.

## Download / installation

**[Download public v4 flash kit ZIP](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/tbj606f-a16-zui14-public-v4)**.
Download the single `tbj606f-a16-zui14-public-v4-flash-kit.zip`, extract it,
read `README-START-HERE.md`, and run `python3 verify-package.py`. This includes
the validated kernel, compatibility module, installer, boot/vendor construction
helpers, build ABI files and SHA256 manifest without requiring Git or a
second kernel download.

The ZIP does not redistribute Lenovo/Qualcomm proprietary boot/vendor images
or the Android GSI. It requires an **owner-supplied validated boot backup**,
not an unmodified stock ZUI14 boot.img: the final working boot uses a ZUI12
DTB and EROFS-modified ramdisk. The validated boot backup SHA256 is
`93f9e9518fc9a20691ab0b3579b0c628e23522674e827fc57b8867945aedd635`.
A fully verified stock-OEM-to-stable boot reconstruction recipe is still
missing. The installer refuses an unverified boot template by default.

The original kernel binary release is [public v1](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/tbj606f-a16-zui14-public-v1).
See [installation instructions](Documentation/tbj606f/installation.md) and
[the per-release reproducibility audit](Documentation/tbj606f/archive/release-reproducibility-audit.md)
before using historical tags: many historical releases preserve source only.

## Reproducing the Android 16 / ZUI14 hybrid

No Lenovo firmware image, proprietary vendor image, modem/DSP image, or signed
vendor module is distributed in this repository.

The scripts under [`tools/tbj606f`](tools/tbj606f) reproduce the tested setup
from firmware supplied by the device owner:

- `build-kernel.sh` - build the kernel in a separate output directory.
- `repack-boot.sh` - repack a known-good boot template with the new kernel.
- `audio-compat/` - build the optional Rouleur link compatibility shim needed
  by the ZUI12 Bengal machine driver on this WCD937x/Bolero device.
- `make-hybrid-vendor.sh` - construct the ZUI14/ZUI12 hybrid vendor image from
  locally supplied firmware files.
- `verify-runtime.sh` - collect scoped runtime validation from one explicitly
  selected Android serial.

See:

- [`Documentation/tbj606f/development-history.md`](Documentation/tbj606f/development-history.md)
- [`Documentation/tbj606f/android16-zui14-bringup.md`](Documentation/tbj606f/android16-zui14-bringup.md)
- [`STATUS.md`](STATUS.md)

for provenance, milestones, failed experiment branches, and the current
hardware status.

## Original project background

The original project imported Lenovo source from the
[Lenovo Open Source Portal](https://support.lenovo.com/us/en/solutions/ht511330-lenovo-open-source-portal)
and brought up the NT36523W touchscreen and Qualcomm WLAN support for AOSP and
Linux Mobile use.

The original repository is retained as the upstream remote and its commits are
kept intact rather than squashed.

## Build notes

The Lenovo-era baseline used Android clang based on `r353983c` and the
aarch64 Android 4.9 binutils toolchain. The public helper scripts intentionally
take toolchain paths through environment variables instead of embedding local
machine paths.

Example:

```sh
export KERNEL_OUT=/path/to/ssd/kernel-out
export CLANG_DIR=/path/to/clang/bin
export CROSS_DIR=/path/to/aarch64-linux-android/bin
./tools/tbj606f/build-kernel.sh
```

The Android 16 / ZUI14 hybrid has been validated only on TB-J606F. Do not
assume compatibility with other TB-J606 variants without verifying their DTB,
vendor modules, firmware, and kernel ABI first.

## License

The kernel follows the license terms already present in the source tree. See
[`COPYING`](COPYING). New helper code added by this continuation carries its
own SPDX identifier where applicable.
