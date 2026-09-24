# TB-J606F Android 16 / ZUI14 hybrid bring-up

This document describes the tested Lenovo Tab P11 TB-J606F (Wi-Fi, bengal)
configuration used with a LineageOS 23.2 Android 16 EROFS GSI.

## Tested software stack

- Kernel: Linux 4.19.157-perf+
- Stable kernel checkpoint: 7124b9c09
- Android: LineageOS 23.2 / Android 16
- GSI build: 23.2-20260524-GAPPS-EROFS-GSI
- GSI SHA256: 26cde4242d9b92fb917b8235c4908e88c5fa6b60db1c56e0c53561db61d333bd
- Vendor userspace base: Lenovo ZUI 14.0.147
- Wi-Fi DLKM: ZUI12 module matching the kernel's module ABI
- Audio DLKMs: ZUI12 modules matching the kernel's module ABI
- ADSP loader: built into the kernel by 7124b9c09
- Audio machine-link shim: tools/tbj606f/audio-compat

The repository does not distribute Lenovo firmware or vendor binaries. Extract
those from firmware that you are legally entitled to use.

## Why the hybrid is required

ZUI14 vendor userspace is newer than the public ZUI12-era kernel source, but
the complete stack is not independently interchangeable. The relevant chain is:

    framework -> vendor HAL/daemon -> kernel ABI -> DT -> DSP firmware

The final stable configuration keeps ZUI14 userspace while using kernel-module
components whose modversion ABI matches the custom kernel.

### Sensors

The ZUI14 sensor stack needs ADSP to be brought up through the vendor-visible
boot contract. Commit 7124b9c09 supplies a small in-kernel implementation of
the /sys/kernel/boot_adsp contract and calls subsystem_get("adsp").

The verified boot sequence contains:

- ADSP powered up
- FastRPC RPMSG channel opened for ADSP
- sensor_pd service registered
- sensor_pd reported up

No full ZUI14 FastRPC replacement is required on the stable line.

### Wi-Fi

The ZUI14 qca_cld3 module does not match the custom kernel's module ABI. The
ZUI12 qca_cld3_wlan.ko matches and is used instead.

### Audio

The ZUI12 audio DLKMs match the custom kernel ABI, but ZUI14 modules.dep data
must not be reused unchanged. It can force an unused Rouleur codec dependency.

tools/tbj606f/make-hybrid-vendor.sh regenerates modules.dep from the actual
module set and keeps the ZUI14 audio_adsp_loader, Rouleur, and Rouleur-slave
modules out of the boot load list.

The ZUI12 Bengal machine driver retains two optional Rouleur link references.
TB-J606F selects WCD937x/Bolero in DT, so those branches are not used at
runtime. tools/tbj606f/audio-compat supplies inert exports only for those two
link-time symbols.

## Reproducible build

Build the kernel on a fast local filesystem:

    export KERNEL_OUT=/path/to/out
    export CLANG_DIR=/path/to/clang/bin
    export CROSS_DIR=/path/to/aarch64-linux-android-4.9/bin
    ./tools/tbj606f/build-kernel.sh

Build the audio compatibility module against exactly the same output tree:

    export KERNEL_SRC=$PWD
    ./tools/tbj606f/audio-compat/build.sh

Repack a known-good boot template while keeping its ramdisk and DTB unchanged:

    ./tools/tbj606f/repack-boot.sh         stock-or-known-good-boot.img         "$KERNEL_OUT/arch/arm64/boot/Image"         boot-test.img         /path/to/mkbootimg

For the validated stable Image, the repacker reproduces the tested boot image
byte-for-byte.

Build a hybrid vendor image from firmware extracted by the device owner:

    ./tools/tbj606f/make-hybrid-vendor.sh         zui14-vendor-base.img         /path/to/zui12/modules         tools/tbj606f/audio-compat/p11_audio_compat.ko         vendor-hybrid.img

## Device testing

Always scope Android tools to the intended device serial.

First test a boot image without flashing it:

    fastboot -s SERIAL boot boot-test.img

After Android boots, capture runtime state:

    ./tools/tbj606f/verify-runtime.sh SERIAL runtime-check

Only after temporary boot succeeds should the matching boot image be installed
to the active boot slot. Do not wipe userdata as part of this bring-up.

## Verified final runtime

The 2026-09-24 stable checkpoint was verified after two consecutive normal
reboots with the persistent boot and vendor images installed.

- sys.boot_completed=1
- active slot: a
- root filesystem: EROFS
- kernel: Linux 4.19.157-perf+ #2
- hardware sensors: 34/34 enumerated
- Qualcomm Device Orientation sensor available
- Android WindowOrientationListener uses the orientation sensor
- Wi-Fi: 5 GHz, 802.11ac, connected
- machine_dlkm loaded
- AudioPolicyManager initialized
- primary speaker route present
- Bluetooth state ON
- camera service reports two devices
- battery and AC state reported

The previous sensor failures:

- apps_dev_init failed
- remote_handle_open failed
- Transport endpoint is not connected

were absent from the final persistent-boot validation.

## Known-good local artifact hashes

These identify the exact artifacts used for the final device validation. The
proprietary-containing vendor image is not distributed by this repository.

- boot image:
  93f9e9518fc9a20691ab0b3579b0c628e23522674e827fc57b8867945aedd635
- hybrid vendor image:
  b0cca3012109d045122dccdbd22f2505327ec7550576daa37d4bde643a39d3dd
- validated p11_audio_compat.ko:
  af7e14a238437b5fc7e29dc5fdf8453630d3981f0c4b7218f588ccf6aab08f40

## Firmware experiments that are not part of the stable recipe

A full ZUI14 modem swap was not demonstrated to be beneficial and caused a
boot regression/delay during testing. A ZUI14 DSP image alone did not restore
sensors. Neither is required by the final stable recipe.

The FastRPC, Android KABI, and GLINK experiments are retained as separate Git
branches for research and are listed in development-history.md.
