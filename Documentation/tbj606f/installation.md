# TB-J606F one-command installation and required firmware

This page defines the supported, tested starting point for the Android
16/ZUI14 hybrid and the inputs needed by `tools/tbj606f/install.sh`.

## Supported device

- Lenovo Tab P11 **TB-J606F Wi-Fi**
- Qualcomm bootloader product: `bengal`
- Lenovo product/vendor device: `J606F` / `m11_prc_wifi`
- unlocked bootloader
- installation target: slot **A**

Do not use the installer on TB-J606L/TB-J616 or another Bengal device.

## Tested starting firmware

The final stack was validated on **ZUI14 14.0.147** TB-J606F CN Wi-Fi vendor
userspace:

```text
Lenovo/m11_prc_wifi/J606F:12/SKQ1.220213.001/14.0.147_230414:user/release-keys
```

Preserved OTA used during development:

```text
08_TB-J606F_CN_WIFI_USER_ZUI_13.1.580_to_TB-J606F_CN_WIFI_USER_ZUI_14.0.147.zip
SHA256 05a94adee44146846542b5b1cdeb8e7faa694eccb6f461c306fbfee6ade15727
```

Its payload metadata identifies `J606F`, Android 12 / SDK 31 and
`14.0.147_230414`.

Exact extracted ZUI14 inputs used by the project:

```text
boot.img
SHA256 7356b6ac6a791c9508778aa76fe0fe381ca73eb225c7f10831799ed64f0e67d4

vendor.img
SHA256 7a73b5886e130cfeb1870e7f5855e1b6bf0010ff694783d2b0d0de553ba6758d

dtbo.img
SHA256 b96a76f4ad1f80bfd9419433115a138d9e1e6fcd75384f2ffbd5aabaa15fd6b7
```

The ZUI14 `boot.img` is used only as the ramdisk/DTB/container template. The
kernel payload is replaced by the released kernel.

### ZUI12 compatibility input

The working kernel preserves the ZUI12 module ABI. Wi-Fi and audio DLKMs come
from this exact TB-J606F firmware family:

```text
TB-J606F_CN_WIFI_USER_Q00016.0_Q_ZUI_12.0.519_ST_210130.zip
SHA256 db776ab8b7afe68467e0c853aafce3fb587a65f045dc33157b68a4a4e1547f62
```

Do not substitute the ZUI14 `qca_cld3_wlan.ko` or ZUI14 audio DLKMs. They
were not ABI-compatible with the stable custom kernel.

The repository does not redistribute Lenovo binaries. Extract the ZUI12
`/vendor/lib/modules` directory from firmware you are entitled to use.

## Android system image

Exact validated GSI:

```text
LineageOS-23.2-20260524-GAPPS-EROFS-GSI.img
SHA256 26cde4242d9b92fb917b8235c4908e88c5fa6b60db1c56e0c53561db61d333bd
size   2255372288 bytes
```

## Hybrid vendor

Final layout:

- ZUI14 14.0.147 userspace/HAL base
- ZUI12 12.0.519 `qca_cld3_wlan.ko`
- ZUI12 12.0.519 audio DLKMs
- ZUI14 `audio_adsp_loader.ko`, Rouleur and Rouleur-slave excluded from boot
- regenerated `modules.dep`
- GPL `p11_audio_compat.ko` loaded before `audio_machine_bengal`

Exact device-validated hybrid vendor:

```text
SHA256 b0cca3012109d045122dccdbd22f2505327ec7550576daa37d4bde643a39d3dd
size   796917760 bytes
```

It is not redistributed because it contains Lenovo/Qualcomm proprietary
payloads. `make-hybrid-vendor.sh` reconstructs it from user-supplied firmware.

## Firmware partitions intentionally not replaced

Do not blindly flash a complete ZUI14 modem/DSP set. A full ZUI14 modem swap
regressed/delayed boot during development, and DSP-only replacement did not
solve the original sensor failure.

The installer touches only:

- `system_a` unless `--skip-system`
- `vendor_a` unless `--skip-vendor`
- `boot_a`

It never wipes userdata and does not flash modem, DSP, recovery, dtbo or other
firmware partitions.

## Partition requirements

Validated minimum image sizes:

```text
system_a >= 2255372288 bytes
vendor_a >= 796917760 bytes
```

The installer checks capacities in fastbootd. It does not silently delete or
shrink other logical partitions to create space.

## One-command installation

With a prepared hybrid vendor:

```sh
./tools/tbj606f/install.sh \
  --serial YOUR_SERIAL \
  --gsi /path/to/LineageOS-23.2-20260524-GAPPS-EROFS-GSI.img \
  --stock-boot /path/to/zui14-14.0.147/boot.img \
  --vendor-image /path/to/vendor-hybrid.img
```

Or, on Linux, build the hybrid vendor during the same run:

```sh
./tools/tbj606f/install.sh \
  --serial YOUR_SERIAL \
  --gsi /path/to/LineageOS-23.2-20260524-GAPPS-EROFS-GSI.img \
  --stock-boot /path/to/zui14-14.0.147/boot.img \
  --zui14-vendor /path/to/zui14-14.0.147/vendor.img \
  --zui12-modules /path/to/zui12-12.0.519/vendor/lib/modules
```

Use `--dry-run` first to validate local inputs and the connected device.
Use `--yes` for unattended flashing after verifying the command.

The sequence is:

1. validate firmware/GSI/release hashes;
2. validate exact TB-J606F and ZUI14 14.0.147 vendor fingerprint;
3. verify unlocked `bengal` bootloader and select slot A;
4. enter fastbootd and verify logical partition sizes;
5. flash `system_a` and `vendor_a`;
6. temporarily boot the newly repacked kernel;
7. require Android boot completion, 34 sensors and AudioPolicyManager;
8. only then flash the same image to `boot_a`;
9. reboot without wiping userdata.

If temporary boot validation fails, `boot_a` is not modified.

## What must survive deletion of the old development workspace

GitHub Releases are the long-term archive for:

- each tagged source version;
- preserved kernel `Image` where one exists;
- exact config where one exists;
- `Module.symvers` where one exists;
- validation/source metadata;
- hashes for non-redistributed boot/recovery/vendor images.

Also retain or retain a legal reacquisition path for the two Lenovo firmware
packages above and the Android GSI. The repository cannot replace those
third-party inputs with redistributed copies.
