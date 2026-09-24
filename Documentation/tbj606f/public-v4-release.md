# TB-J606F Android 16 / ZUI14 hybrid public v4 — unified flash kit

Download **one file**: `tbj606f-a16-zui14-public-v4-flash-kit.zip`.
This ZIP contains the validated Linux 4.19.157 kernel Image/Image.gz,
`p11_audio_compat.ko`, config/ABI files, installer, boot repacking and hybrid
vendor tools, SHA256SUMS, package validator and `README-START-HERE.md`.
The complete kernel source and development history remain in this repository
at the Git tag; the flashing ZIP itself has no source tree.

Extract the ZIP and start with `README-START-HERE.md`, then run:

```sh
python3 verify-package.py
```

The exact previously tested `Image` and compatibility module SHA256 values are
pinned by the installer; it uses the ZIP copies directly with `--offline`.
A dry run with the ZIP extracted and a user-supplied **previously validated
boot** was verified to produce the exact tested boot SHA256
`93f9e9518fc9a20691ab0b3579b0c628e23522674e827fc57b8867945aedd635`.
It used mocked ADB for TB-J606F serial HA1E02DA, and did not flash a device.

**Important prerequisite:** an unmodified stock ZUI14 boot.img did not produce
the validated boot. The working boot includes a ZUI12 DTB and EROFS-adjusted
ramdisk. Owners lacking the validated boot template must not assume this ZIP
alone recreates the original tested hybrid. No Lenovo/Qualcomm boot/vendor or
modem/DSP image, nor the third-party Android GSI, is included. The installer
checks hash and device identity and requires successful temporary boot before
permanently flashing boot_a; system_a/vendor_a may already have been flashed
before that runtime check. Do not wipe userdata or resize system_a.

The [historical reproducibility audit](archive/release-reproducibility-audit.md)
classifies 57 releases existing before public v4: 54 source/metadata-only, v1
kernel/ABI, v2 installer-only and v3 integrated kernel/helper tarball. It
separates publication of a source checkpoint from proven successful runtime or
byte-identical rebuild and identifies 37 historically staged local Image/boot/
config/ABI sets that were not attached to their respective source-only
GitHub releases. Failed development experiments remain archival, not recommended
flash versions.
