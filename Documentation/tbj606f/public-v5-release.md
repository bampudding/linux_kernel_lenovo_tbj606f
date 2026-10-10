# TB-J606F Android 16 / ZUI14 public v5 — OEM-reproducible flash ZIP

**Download one file for the non-proprietary flashing toolkit:**
`tbj606f-a16-zui14-public-v5-flash-kit.zip`.
압축을 해제하고 `README-START-HERE.md`를 먼저 읽으세요.

## What changed since public v4

The previously missing first-install boot reconstruction is now independently
verified. `reconstruct-stable-boot.py` transforms the owner's original
**TB-J606F ZUI12 12.0.519** OEM `boot.img` (SHA256
`d4e86ef850d4109a8b2b7a87bec82dd2c60cc68a6f0e3709e7bec0f74ff982d8`)
and the released public-v1-identical Image into the **exact previously tested
hybrid boot** (14,286,848 bytes; SHA256
`93f9e9518fc9a20691ab0b3579b0c628e23522674e827fc57b8867945aedd635`).
The derived EROFS ramdisk itself matched the archived stable ramdisk byte for
byte. This was checked using the archived OEM QFIL boot input, the public
kernel, and the new script, without supplying the known-good final boot to
the script. A pure stock ZUI14 boot remains an invalid replacement for this
ZUI12-derived template.

The installer now accepts `--zui12-stock-boot` for this reproducible route;
`--stock-boot` remains supported for an owner who already has the exact
validated hybrid boot. `--offline` uses kernel and module from the ZIP.

## Package and installation

Contains `Image`, `Image.gz`, `p11_audio_compat.ko`, `kernel.config`,
`Module.symvers`, `System.map`, checksum manifest and verifier, installer,
ZUI12 boot reconstructor, boot/vendor helpers and documentation. Full GPL
source is available through this release's Git tag; a source tree is not
included in the flashing ZIP.

After extraction, run `python3 verify-package.py`, then follow
`README-START-HERE.md`. Example with user-prepared matching hybrid vendor:

```sh
bash ./install.sh --offline --dry-run \
  --serial HA1E02DA \
  --gsi /path/to/LineageOS-23.2-20260524-GAPPS-EROFS-GSI.img \
  --zui12-stock-boot /path/to/ZUI12-12.0.519/boot.img \
  --vendor-image /path/to/your-verified-hybrid-vendor.img
```

Only after validating your exact files and recovery access should you run
the command without `--dry-run`. The installation helper scopes all ADB and
Fastboot commands to the supplied serial; checks model/bootloader, hash,
partition capacity and active slot; and must successfully temporary-boot
before permanently flashing `boot_a`. `system_a` and `vendor_a` can have
changed before temporary boot. No userdata wipe, partition resize, modem/DSP
swap or unsolicited recovery flash is performed.

## Firmware and validation scope

OEM ZUI12 12.0.519 boot and Wi-Fi/audio modules, ZUI14 14.0.147 vendor
userspace source, rebuilt hybrid vendor and Android 16 EROFS GSI are
**not bundled**. Obtain them from lawful owner-supplied firmware. The installer
pins the tested GSI SHA256
`26cde4242d9b92fb917b8235c4908e88c5fa6b60db1c56e0c53561db61d333bd`.

Validation completed for v5: extracted ZIP internal SHA256 verification,
byte-identical OEM ZUI12 → stable boot reproduction, offline mocked serial-
scoped ADB `--dry-run`, shell/Python syntax checks and source/asset checksum
comparisons. No new full-device flash was performed for this release; the
historically saved Android 16/ZUI14 runtime boot is the tested integration
baseline. `public-v4` is retained as an immutable, earlier release.

The [historical release audit](archive/release-reproducibility-audit.md)
separates genuinely downloadable kernel/deployment artifacts from source-only
archival tags and failed experiments. Avoid treating a source-only milestone
as a ready-to-flash ROM.
