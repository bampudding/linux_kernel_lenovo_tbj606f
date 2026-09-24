# TB-J606F one-command installation and required firmware

This page defines the supported, tested starting point for the Android
16/ZUI14 hybrid and the inputs needed by `tools/tbj606f/install.sh`.
For end users, download the single `tbj606f-a16-zui14-public-v4-flash-kit.zip`
from the public-v4 GitHub Release, extract it, then follow `README-START-HERE.md`.
The extracted installer uses the bundled tested kernel `Image` and
`p11_audio_compat.ko` directly (no second download); in a source-only checkout
it can download exactly those two pinned binaries from public v1. The hybrid
vendor builder was added in the public-v2 lineage; public v4 is the unified
non-proprietary flashing kit. Historical source-only releases are documented
separately in `archive/release-reproducibility-audit.md`.

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

The stock ZUI14 `boot.img` is a recorded provenance input but **must not** be
passed directly as the validated boot template: its DTB and ramdisk differ from
the stable ZUI12-DTB/EROFS-ramdisk hybrid. The installer requires the user's
owner-provided validated boot backup (SHA256
`93f9e9518fc9a20691ab0b3579b0c628e23522674e827fc57b8867945aedd635`)
and replaces only its kernel. Repacking the exact stable backup with the
published Image was independently reproduced byte-for-byte. The validated
boot contains Lenovo content and is not distributed in the ZIP. No general
original-stock-to-stable boot reconstruction recipe has yet been proven;
therefore a first-time installer without the validated boot backup cannot
claim to reproduce the tested boot from stock ZUI14 alone. `--allow-other-boot`
is an unvalidated research override, not a supported installation method.

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

When building this image locally, `make-hybrid-vendor.sh` requires the ZUI12
Wi-Fi module and all 25 expected ZUI12 audio modules, and checks their
`module_layout` CRC against the released compatibility module. A supplied
prebuilt hybrid vendor is verified against the tested SHA256 instead. The
installer later checks that `p11_audio_compat` and `machine_dlkm` actually
loaded during its temporary boot; this is not a complete Wi-Fi/audio playback
test.

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

The installer checks **both** required capacities in fastbootd before it
changes the active slot or flashes either partition. It does not delete,
resize or shrink other logical partitions to create space.

## One-command installation

With a prepared hybrid vendor:

```sh
./install.sh --offline \
  --serial HA1E02DA \
  --gsi /path/to/LineageOS-23.2-20260524-GAPPS-EROFS-GSI.img \
  --stock-boot /path/to/your-validated-boot-template.img \
  --vendor-image /path/to/vendor-hybrid.img
```

Or, on Linux, build the hybrid vendor during the same run:

```sh
./install.sh --offline \
  --serial HA1E02DA \
  --gsi /path/to/LineageOS-23.2-20260524-GAPPS-EROFS-GSI.img \
  --stock-boot /path/to/your-validated-boot-template.img \
  --zui14-vendor /path/to/zui14-14.0.147/vendor.img \
  --zui12-modules /path/to/zui12-12.0.519/vendor/lib/modules
```

When using the ZIP, run these commands from its extracted folder; in a source
checkout use `./tools/tbj606f/install.sh` instead. Use `python3
verify-package.py` in the extracted ZIP to verify all 16 bundled files, then
add `--dry-run` to the installation command to validate inputs and the
connected device.
It checks hashes, constructs the hybrid vendor when requested, repacks the boot
image, and checks the connected Android device identity and vendor fingerprint.
It does not reboot the device or check bootloader unlock status, fastboot product,
or partition capacities; these require entering fastboot/fastbootd in the normal
installation flow. `--skip-system` omits the GSI argument, and `--skip-vendor`
omits the hybrid vendor argument when a compatible hybrid vendor is already
installed. Use `--yes` for unattended flashing after verifying the command.

The sequence is:

1. validate firmware/GSI/release hashes and repack the tested boot image;
2. validate exact TB-J606F and ZUI14 14.0.147 vendor fingerprint over ADB;
3. verify unlocked `bengal` bootloader;
4. enter fastbootd and verify **both** logical partition sizes before any flash;
5. select and confirm slot A, then flash `system_a` and `vendor_a` unless skipped;
6. temporarily boot the newly repacked kernel using those flashed partitions;
7. require Android boot completion on slot A, 34 sensors, AudioPolicyManager,
   and both the compatibility and machine audio modules loaded;
8. only then flash the same image to `boot_a`;
9. reboot without wiping userdata.

**The temporary boot protects `boot_a` from being persistently flashed before
runtime validation.** Full Android 16/hybrid-vendor validation needs the new
system and vendor partitions, so those partitions are flashed *before* the
runtime test. If that test fails, `boot_a` remains unchanged, but `system_a`
and/or `vendor_a` may already have changed and the device may require recovery.
Have known-good firmware and a restore path available before installation.
The script does not wipe userdata or perform logical partition resizing.

The published `public-v1` Image/compatibility-module release used by the
`public-v4` flash ZIP is pinned by
SHA256, along with the known-good GSI, validated boot template and hybrid vendor.
`--allow-other-gsi`, `--allow-other-boot` and `--allow-other-vendor` bypass
specific tested-image comparisons and make that combination unverified;
`--release-tag` does not bypass the released Image/module hash checks.

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
