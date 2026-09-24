# TB-J606F release reproducibility and flash-asset audit

Generated 2026-09-24T11:30:46.140172+00:00. Full digests, download URLs, and HDD paths:
[JSON report](release-reproducibility-audit.json).

## Scope and exact counts

The live [release index](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases) contains **57 releases
with 250 downloadable asset records**. All 57
release tag names resolve locally, but they identify only **54
distinct source commits**. GitHub supplies a SHA256 digest for all
250 assets (missing: 0). The API reports
metadata and asset digests; this audit did not download and rehash 250 assets or
all approximately 180 MB source tarballs.

- **54 source-and-metadata-only releases**:
  each has only a source tar.gz, VERSION.txt, commit-stat.txt and SHA256SUMS.
  Their public downloads contain **zero directly deployable kernel/boot images**.
- **1 public kernel+ABI release (v1)**: raw Image/Image.gz, exact config,
  Module.symvers, System.map, compatibility module and checksums.
- **1 installer-only release (v2)**: install.sh, documentation, bundle and
  checksums; **no kernel Image**. The release ZIP/tar archive filename contains
  the published spelling tbj6066f, preserved as historical evidence.
- **1 source-matched bundle (v3)**: the same validated v1 kernel bytes and
  compatibility module, plus boot/vendor reconstruction scripts and manifests.
  Published v3 installer and guide hashes match the v3 *Git tag* blobs.

- **0 GitHub releases with a ready-to-flash OEM boot.img, vendor.img or Android
  GSI**. An arm64 raw Image is a kernel payload; flashing it to boot_a
  would not constitute a valid repacked boot image.

The older [GitHub catalog](github-release-catalog.json) was generated at
2026-09-24T10:57:21.628046+00:00 with **56 releases and
229 assets**, before v3 appeared. This report queries GitHub
live and retains that older snapshot as historical evidence.

## Source archive is not a reproducible build

The 54 old source tarballs and Git tags
preserve source checkpoints, and their GitHub SHA256 metadata makes the
downloaded tarballs identifiable. Neither existence of a snapshot nor a
filename containing tested proves that a matching, safe binary can be
rebuilt or booted. All **57** tag-to-commit relationships were
resolved against local annotated/lightweight Git refs. The independently
uploaded tar.gz contents have **not** been extracted and compared against
every Git tree, and all 250 asset payloads have **not** been rehashed
after download. Tag identity is not a device-test certificate.

The [HDD manifest](hdd-artifact-manifest.json) (captured
2026-09-24T10:54:07.334653+00:00) records **37 exact-tag release
folders** among the source-only releases with local Image, boot image,
config and Module.symvers. **17**
source-only releases lack that exact four-file local set in the recorded
release directories. These files were never attached to those old GitHub
source-only releases. An unrelated top-level boot file or an experiments/
directory with a similar name is **not** silently attributed to a tag.
The manifest SHA256 values are hashes captured earlier, not fresh verification
of current HDD bytes and not evidence of an independent backup.

**Toolchain and build state:** the final hybrid stable local
REPRODUCE.txt records clang-r353983c and
aosp-aarch64-linux-android-4.9-android10 at kernel checkpoint
7124b9c09a48380a7b028104e17cac36b9b1a0af.
[The build helper](../../../tools/tbj606f/build-kernel.sh) requires
KERNEL_OUT, CLANG_DIR, CROSS_DIR and the Bengal defconfig/config fragment,
but does not bundle these toolchain binaries. The stable
[bring-up documentation](../android16-zui14-bringup.md) identifies
.config SHA256
36270e3c45eb9e663e71eef8579617f09ad25d7732d009d5d4c1ea96f55bf734
and Module.symvers SHA256
dc7acfa28137adf12a3d7fae68ed0c9fe80a71a675abeada5653cb6344b37b13,
which were separately reproduced for the **stable checkpoint**. That report
also explains that CONFIG_MODULE_SIG_ALL creates a local signing key:
source/config/ABI reproduction **does not imply byte-identical Image**.
The old 37 local config/ABI sets make later reconstruction more practical,
but this audit did not rebuild any of those historical tags or validate their
specific compiler binaries, signing keys, source-to-build mapping, boot
template, firmware or runtime logs.

## Deployment inventory and explicit cautions

GitHub has **20 release/asset digest records** whose SHA256 is found
in the older HDD manifest; this count includes identical v1 and v3 asset bytes
twice, not 20 unique independent backups. In particular, v1 and v3 have
identical published Image, Image.gz, kernel.config, Module.symvers, System.map,
p11_audio_compat.ko and TESTED-IMAGE-HASHES.txt SHA256. Only the v1/v3
releases publish the tested kernel binary; neither gives the owner a
complete proprietary OEM boot/vendor image or the separate Android GSI.
For the final hybrid, the saved HDD folder
releases/p11-a16-zui14-hybrid-stable-20260924 contains:

- privately preserved boot-z14-adsp-loader-stable1.img:
  SHA256 93f9e9518fc9a20691ab0b3579b0c628e23522674e827fc57b8867945aedd635;
- privately preserved vendor_a-zui14-vndk30-z12wifi-z12audio-v5-760MiB.img:
  SHA256 b0cca3012109d045122dccdbd22f2505327ec7550576daa37d4bde643a39d3dd;
- REPRODUCE.txt plus the runtime identity, sensorservice, Wi-Fi, audio,
  camera and persistent boot captures. They document the validated **final
  Android 16/ZUI14 hybrid**, not blanket validation of every old milestone.

The separate LineageOS 23.2 Android 16 EROFS GSI remains on the Mac, reported
SHA256 26cde4242d9b92fb917b8235c4908e88c5fa6b60db1c56e0c53561db61d333bd.
**Crucial boot-template reproducibility distinction:** the recorded original
ZUI14 14.0.147 stock boot.img (SHA256
7356b6ac6a791c9508778aa76fe0fe381ca73eb225c7f10831799ed64f0e67d4)
has a different DTB and ramdisk from the tested hybrid and repacking it did
**not** yield the verified boot image. Repacking the owner's previously
validated ZUI12-DTB/EROFS-ramdisk hybrid boot backup (SHA256
93f9e9518fc9a20691ab0b3579b0c628e23522674e827fc57b8867945aedd635)
with the v1 kernel Image reproduced that exact stable boot hash. There is
**no verified original stock ZUI14 boot -> tested hybrid boot reconstruction
recipe**. A first-time device owner lacking that private boot backup cannot
claim an equivalent boot merely from a public source tarball, Image, or kit.

The owner must also obtain exact ZUI14 14.0.147 vendor input and ZUI12
12.0.519 Wi-Fi/audio modules legally, reconstruct the hybrid and keep a
restore path. The firmware requirements, tested-template hash checks, slot
and temporary-boot limitations are in [installation.md](../installation.md):
system_a/vendor_a may already have changed before boot_a passes a temporary
boot check. No archive release should be flashed merely because a matching
source snapshot or staged local boot file exists.

## Historically successful, partial, failed or reversed milestones

The explicitly **failed** GPU 980 MHz experiment is
zui12-post157-gpu-oc15-980-failed-20260922. The early 65 Hz panel probe was
later reverted by zui12-4.19.96-60hz-tested-20260917. The GPU oc16 harness,
the F2FS compression core-off build and the EROFS built milestone are build
checkpoints, **not independently proven successful runtime boots**. The
separate EROFS LZ4 decoder source release expressly disclaims a full-system
boot claim; the ADSP/sensor tag records a partial stage rather than the final
validated hybrid. The EROFS built, tested and runtime-tested release tags
point to **one same source commit**, as do the KGSL and modernization aliases.
Do not count them as independent successful builds or distinct codebases.

Historic tested tags with an HDD VALIDATION note have additional local
provenance, but those notes are not new tests and are not universally complete
Wi-Fi/audio/sensor/boot reports. The clearest final integrated success is
the v1/v3-shared kernel with the known-good ZUI14/ZUI12 hybrid and saved
2026-09-24 runtime capture: 34 sensors, audio policy, Wi-Fi and persistent
slot-A boot. v3 packages v1-identical kernel bytes and deployment helpers;
it does **not** claim a newly performed full flash or a distinct validated
kernel build. See [development-history.md](../development-history.md),
[android16-zui14-bringup.md](../android16-zui14-bringup.md), and the v1/v3
release notes for the stated scope.

## All public releases (one row per tag)

The source SHA is a prefix of GitHub asset metadata, not an independent downloaded hash.
HDD local means the EXACT tag-named stage folder contains Image + boot image + config + Module.symvers.
All historical runtime classifications refer to archival claims, not new device tests.

| Release | Source commit | GitHub asset classification | Source SHA | Exact-tag HDD | Historical disposition |
|---|---|---|---|---|---|
| [`tbj606f-a16-zui14-public-v1`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/tbj606f-a16-zui14-public-v1) | [`3a5bd05145`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/3a5bd05145cdafb844c51aa4021186e87b8700f1) | kernel-abi-bundle (9) | — | no exact-tag complete set | validated kernel/ABI payload; owner must supply and repack boot |
| [`tbj606f-a16-zui14-public-v2`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/tbj606f-a16-zui14-public-v2) | [`c067a36017`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/c067a36017daf5cdfc0bf0f531e22f1fa2dde274) | installer-only (4) | — | no exact-tag complete set | installer/docs ONLY; get kernel payload from v1/v3 |
| [`zui12-audiofix-baseline-20260917`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-audiofix-baseline-20260917) | [`12dbd275a7`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/12dbd275a7bc3c0d2d80ed95a036ad2035e2f9a6) | source-and-metadata-only (4) | `35bbca2eafb7` | local Image/boot/config/ABI | historical tested tag + local validation note; no fresh device run |
| [`zui12-65hz-probe-20260917`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-65hz-probe-20260917) | [`398465020d`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/398465020ddc3c8e3065b4e45f696b411237469d) | source-and-metadata-only (4) | `6c6b86a05373` | no exact-tag complete set | 65 Hz probe; later reverted by 4.19.96 60 Hz tag; experiment |
| [`zui12-backport2-tested-20260917`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-backport2-tested-20260917) | [`8898aeffe6`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/8898aeffe6199b2f645cd27d30be1be7c6a553d6) | source-and-metadata-only (4) | `e6b254438f44` | no exact-tag complete set | historical tested tag label; no fresh device run |
| [`zui12-next-tested-20260917`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-next-tested-20260917) | [`f60b10e1fe`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/f60b10e1fe21b1c1f240f5f94a4cce89d158eb19) | source-and-metadata-only (4) | `752631c2ba3f` | no exact-tag complete set | 65 Hz probe lineage; subsequent revert means not retained 60 Hz baseline |
| [`zui12-4.19.96-60hz-tested-20260917`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-4.19.96-60hz-tested-20260917) | [`14549a61ac`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/14549a61ace84b751acbdb8009194b369368e3ce) | source-and-metadata-only (4) | `8528699fe020` | local Image/boot/config/ABI | historical tested tag label; no fresh device run |
| [`zui12-4.19.97-60hz-tested-20260917`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-4.19.97-60hz-tested-20260917) | [`de0feabe14`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/de0feabe14d023ff8aa2e55d908b586b5f189f12) | source-and-metadata-only (4) | `87127424339c` | local Image/boot/config/ABI | historical tested tag label; no fresh device run |
| [`zui12-4.19.98-60hz-tested-20260918`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-4.19.98-60hz-tested-20260918) | [`bd81c2a9c1`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/bd81c2a9c117b6a7874ffe1209cde1a030a19e5a) | source-and-metadata-only (4) | `a1186bf73d88` | local Image/boot/config/ABI | historical tested tag label; no fresh device run |
| [`zui12-4.19.99-60hz-tested-20260918`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-4.19.99-60hz-tested-20260918) | [`d8ef0fccc7`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/d8ef0fccc767ff012069c4aa06a48b4ad853a773) | source-and-metadata-only (4) | `67ebbbd94434` | local Image/boot/config/ABI | historical tested tag label; no fresh device run |
| [`zui12-4.19.110-60hz-tested-20260918`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-4.19.110-60hz-tested-20260918) | [`b326cd634e`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/b326cd634ecebef98e55613a84599d256cb780fb) | source-and-metadata-only (4) | `3770f9d68fa5` | local Image/boot/config/ABI | historical tested tag label; no fresh device run |
| [`zui12-4.19.113-60hz-tested-20260918`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-4.19.113-60hz-tested-20260918) | [`0e89886e70`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/0e89886e70b419d0fa0355ff62cc0c50efbf0e8c) | source-and-metadata-only (4) | `b71e9a23e6b5` | local Image/boot/config/ABI | historical tested tag label; no fresh device run |
| [`zui12-4.19.125-60hz-tested-20260918`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-4.19.125-60hz-tested-20260918) | [`e5deb74160`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/e5deb7416032b68cb0c1a9cd6b3279985c53d128) | source-and-metadata-only (4) | `42f86d9acb48` | local Image/boot/config/ABI | historical tested tag + local validation note; no fresh device run |
| [`zui12-4.19.136-60hz-tested-20260918`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-4.19.136-60hz-tested-20260918) | [`17dd80827d`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/17dd80827d9d606c313191163a4343a156890ae7) | source-and-metadata-only (4) | `405c2add100e` | local Image/boot/config/ABI | historical tested tag + local validation note; no fresh device run |
| [`zui12-4.19.146-60hz-tested-20260918`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-4.19.146-60hz-tested-20260918) | [`04675e238c`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/04675e238cf7f15f0a279c80afba4cbcf18593d1) | source-and-metadata-only (4) | `cf14581bcacd` | local Image/boot/config/ABI | historical tested tag + local validation note; no fresh device run |
| [`zui12-4.19.157-60hz-tested-20260918`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-4.19.157-60hz-tested-20260918) | [`75497879c4`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/75497879c4267c40192011e4ec2a928fb9c72827) | source-and-metadata-only (4) | `ad6f95bdedb9` | local Image/boot/config/ABI | historical tested tag label; no fresh device run |
| [`zui12-post157-dwc3fix1-tested-20260918`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-post157-dwc3fix1-tested-20260918) | [`075c3c4442`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/075c3c4442c665ea7c64bb791c6e09e8a47af50e) | source-and-metadata-only (4) | `92fd58eb83b5` | local Image/boot/config/ABI | historical tested tag label; no fresh device run |
| [`zui12-post157-dwc3fix2-tested-20260918`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-post157-dwc3fix2-tested-20260918) | [`7892720ae2`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/7892720ae26e0434dfa0987ab1c5319f5eef8380) | source-and-metadata-only (4) | `28df81eeb54f` | local Image/boot/config/ABI | historical tested tag label; no fresh device run |
| [`zui12-post157-dwc3fix3-tested-20260918`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-post157-dwc3fix3-tested-20260918) | [`13eb6312b8`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/13eb6312b87e67bf78f1ee94ada2a53a473e1392) | source-and-metadata-only (4) | `5ca2c511c4be` | local Image/boot/config/ABI | historical tested tag label; no fresh device run |
| [`zui12-post157-dwc3fix4-tested-20260918`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-post157-dwc3fix4-tested-20260918) | [`038bdb03b8`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/038bdb03b8ce89b1e23c883f44e4c99f37b52591) | source-and-metadata-only (4) | `97f4c128bf8a` | local Image/boot/config/ABI | historical tested tag label; no fresh device run |
| [`zui12-post157-dwc3fix5-tested-20260918`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-post157-dwc3fix5-tested-20260918) | [`ea2afcf795`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/ea2afcf79538d666c946b97f9a0be9515c7b42cd) | source-and-metadata-only (4) | `f72479b0cffd` | local Image/boot/config/ABI | historical tested tag label; no fresh device run |
| [`zui12-post157-ufsfix1-tested-20260918`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-post157-ufsfix1-tested-20260918) | [`733c5aaa50`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/733c5aaa50d05315064612cc8c66257287194098) | source-and-metadata-only (4) | `316d28dc0ad8` | local Image/boot/config/ABI | historical tested tag label; no fresh device run |
| [`zui12-post157-ufsfix2-tested-20260918`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-post157-ufsfix2-tested-20260918) | [`a0f3e8b971`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/a0f3e8b971857e28bb3827223861d40ade8a2a48) | source-and-metadata-only (4) | `c9d9a2027b2f` | local Image/boot/config/ABI | historical tested tag label; no fresh device run |
| [`zui12-post157-erofs1-tested-20260918`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-post157-erofs1-tested-20260918) | [`b8e305905a`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/b8e305905acc8182bd2821842dfba4ccabd887d4) | source-and-metadata-only (4) | `39d7d29506b3` | local Image/boot/config/ABI | historical tested tag + local validation note; no fresh device run |
| [`zui12-post157-f2fs1-tested-20260918`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-post157-f2fs1-tested-20260918) | [`3d943306af`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/3d943306af5e339a64928f35fa8a3d0f49a8e767) | source-and-metadata-only (4) | `f99603dd1d8b` | local Image/boot/config/ABI | historical tested tag + local validation note; no fresh device run |
| [`zui12-post157-f2fs2-tested-20260918`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-post157-f2fs2-tested-20260918) | [`e15161550d`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/e15161550d4ddca3576e13d055680c3ca76667df) | source-and-metadata-only (4) | `f845f7f367ba` | local Image/boot/config/ABI | historical tested tag + local validation note; no fresh device run |
| [`zui12-post157-f2fs3-tested-20260918`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-post157-f2fs3-tested-20260918) | [`307231b400`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/307231b4002e7e4701aecf956e956373814b7d96) | source-and-metadata-only (4) | `12c483f90346` | local Image/boot/config/ABI | historical tested tag + local validation note; no fresh device run |
| [`zui12-post157-f2fs-compression-core-off-build-20260918`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-post157-f2fs-compression-core-off-build-20260918) | [`d04f96a5e5`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/d04f96a5e5e90757f006cd82c0ebdb8a364d0c9b) | source-and-metadata-only (4) | `296e437207df` | no exact-tag complete set | compression core-off BUILD checkpoint; no enabled-runtime claim |
| [`zui12-post157-f2fs-compress-source-tested-20260919`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-post157-f2fs-compress-source-tested-20260919) | [`91909246ac`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/91909246ac5e657b24a32b8689a8b17dc13bb500) | source-and-metadata-only (4) | `939678dc9032` | local Image/boot/config/ABI | historical tested tag + local validation note; no fresh device run |
| [`zui12-post157-f2fs-compress-fixes1-enabled-tested-20260919`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-post157-f2fs-compress-fixes1-enabled-tested-20260919) | [`7cc5ceaef5`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/7cc5ceaef55ca9ef2de65a880845b1857661b648) | source-and-metadata-only (4) | `58be949a27e5` | local Image/boot/config/ABI | historical tested tag + local validation note; no fresh device run |
| [`zui12-post157-f2fs-compress-fixes2-enabled-tested-20260919`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-post157-f2fs-compress-fixes2-enabled-tested-20260919) | [`dfcb1cd5d4`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/dfcb1cd5d4728ea5d60fbf4ddcb0eb8dcdb3d6ce) | source-and-metadata-only (4) | `ffd13ef2045b` | local Image/boot/config/ABI | historical tested tag + local validation note; no fresh device run |
| [`zui12-post157-fs-fixes3-zstd-tested-20260919`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-post157-fs-fixes3-zstd-tested-20260919) | [`fb21dd9825`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/fb21dd98258d06cf9ca0d5c26fd07b1208163687) | source-and-metadata-only (4) | `f258c929a580` | local Image/boot/config/ABI | historical tested tag + local validation note; no fresh device run |
| [`zui12-post157-f2fs-compress-fixes4-enabled-tested-20260919`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-post157-f2fs-compress-fixes4-enabled-tested-20260919) | [`40963169bc`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/40963169bcb5a92ce63f71d0f06e3f8d2fa48088) | source-and-metadata-only (4) | `5a6806473da1` | local Image/boot/config/ABI | historical tested tag + local validation note; no fresh device run |
| [`zui12-post157-f2fs-compress-fixes5-enabled-tested-20260919`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-post157-f2fs-compress-fixes5-enabled-tested-20260919) | [`b16c916b2d`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/b16c916b2d9b65f8796eacaf25e27c71177e5e7f) | source-and-metadata-only (4) | `fea410211d2c` | local Image/boot/config/ABI | historical tested tag + local validation note; no fresh device run |
| [`zui12-post157-f2fs-compress-fixes6-enabled-tested-20260919`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-post157-f2fs-compress-fixes6-enabled-tested-20260919) | [`5295e4dfde`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/5295e4dfde99c6c5991d822747dcf6b97ad01b9c) | source-and-metadata-only (4) | `08bb8e43095c` | local Image/boot/config/ABI | historical tested tag + local validation note; no fresh device run |
| [`zui12-post157-mm-zsmalloc-fixes7-enabled-tested-20260919`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-post157-mm-zsmalloc-fixes7-enabled-tested-20260919) | [`5c3c5c63f2`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/5c3c5c63f228774d5145af571ebc730c83ddec53) | source-and-metadata-only (4) | `88e8f527102d` | local Image/boot/config/ABI | historical tested tag + local validation note; no fresh device run |
| [`zui12-post157-ufs-resume-fixes8-enabled-tested-20260919`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-post157-ufs-resume-fixes8-enabled-tested-20260919) | [`dc22d91e70`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/dc22d91e70a2ddad32756cc85aa45acb919ed4f0) | source-and-metadata-only (4) | `140bfbd70489` | local Image/boot/config/ABI | historical tested tag + local validation note; no fresh device run |
| [`zui12-post157-sched-walt-fixes9-enabled-tested-20260919`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-post157-sched-walt-fixes9-enabled-tested-20260919) | [`98c4683b7d`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/98c4683b7d5280ccfd90830f5743b7b8dc603ec3) | source-and-metadata-only (4) | `e837d251c817` | local Image/boot/config/ABI | historical tested tag + local validation note; no fresh device run |
| [`zui12-post157-ufs-sysfs-desc-fixes10-enabled-tested-20260919`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-post157-ufs-sysfs-desc-fixes10-enabled-tested-20260919) | [`e91beb08de`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/e91beb08de332d5c5702ac7ac9a199a11a21d9aa) | source-and-metadata-only (4) | `2c6bbc3bbac1` | local Image/boot/config/ABI | historical tested tag + local validation note; no fresh device run |
| [`zui12-post157-kgsl-fixes11-enabled-tested-20260919`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-post157-kgsl-fixes11-enabled-tested-20260919) | [`f739eee2dc`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/f739eee2dcc3187dca6c112c3324c41f7b65a524) | source-and-metadata-only (4) | `65b47057ba5c` | local Image/boot/config/ABI | historical tested tag + local validation note; no fresh device run |
| [`zui12-post157-modernization-batch-tested-20260919`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-post157-modernization-batch-tested-20260919) | [`f739eee2dc`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/f739eee2dcc3187dca6c112c3324c41f7b65a524) | source-and-metadata-only (4) | `0198da4bac6f` | no exact-tag complete set | historical tested tag label; no fresh device run |
| [`zui12-post157-latency-tuning-tested-20260919`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-post157-latency-tuning-tested-20260919) | [`a46c5177ab`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/a46c5177abea98d8ce49b1db81faefb913360614) | source-and-metadata-only (4) | `dbb78adc1c45` | local Image/boot/config/ABI | historical tested tag + local validation note; no fresh device run |
| [`zui12-post157-dt2w-gsi-tested-20260919`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-post157-dt2w-gsi-tested-20260919) | [`7f7e5bf3b3`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/7f7e5bf3b3f524a65a1cbf4748a2f6f6d6776d9b) | source-and-metadata-only (4) | `9002092f3f68` | local Image/boot/config/ABI | historical tested tag + local validation note; no fresh device run |
| [`zui12-post157-kgsl-ringalloc-opt13-tested-20260919`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-post157-kgsl-ringalloc-opt13-tested-20260919) | [`7cd6df94c9`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/7cd6df94c95c06daca3a1a80a70196111ca10750) | source-and-metadata-only (4) | `4cef82d9ba56` | local Image/boot/config/ABI | historical tested tag + local validation note; no fresh device run |
| [`zui12-post157-eas-idle-opt14-known-good-20260922`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-post157-eas-idle-opt14-known-good-20260922) | [`a9f8072bcf`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/a9f8072bcf54428cfe9362cf7232447eb1298cc8) | source-and-metadata-only (4) | `4549dfb386ae` | no exact-tag complete set | historical known-good scheduler checkpoint; no exact-tag HDD build set |
| [`zui12-post157-gpu-oc15-980-failed-20260922`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-post157-gpu-oc15-980-failed-20260922) | [`0d43e6f23a`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/0d43e6f23a2af10b568584fb07579d9dc5954d45) | source-and-metadata-only (4) | `0a2cf9e6d16e` | no exact-tag complete set | explicit FAILED 980 MHz GPU experiment; not a tested image |
| [`zui12-post157-gpu-oc16-harness-built-20260922`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-post157-gpu-oc16-harness-built-20260922) | [`68c534d08a`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/68c534d08a1892b366a13f2ff7b3078aad45373e) | source-and-metadata-only (4) | `67510201a4e8` | no exact-tag complete set | GPU override harness BUILT; not proof of runtime success |
| [`zui12-post157-gpu-oc17-native960-tested-20260922`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-post157-gpu-oc17-native960-tested-20260922) | [`c08047730b`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/c08047730bb95a9b7ed89a0a47618070d8ed63ba) | source-and-metadata-only (4) | `2b4fb047c69e` | no exact-tag complete set | historical guarded 960 MHz GPU opt-in; not default clock |
| [`zui12-post157-erofs-lineage23.2-built-20260922`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-post157-erofs-lineage23.2-built-20260922) | [`5cf633864b`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/5cf633864bedb3e9d05b36c692b1b0964cd262a9) | source-and-metadata-only (4) | `041f048fd25c` | no exact-tag complete set | BUILD checkpoint; shares commit with tested/runtime-tested tags |
| [`zui12-post157-erofs-lineage23.2-tested-20260922`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-post157-erofs-lineage23.2-tested-20260922) | [`5cf633864b`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/5cf633864bedb3e9d05b36c692b1b0964cd262a9) | source-and-metadata-only (4) | `1991fa7774ba` | no exact-tag complete set | historical tested label; shares commit with built/runtime-tested tags |
| [`zui12-post157-erofs-lineage23.2-runtime-tested-20260922`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/zui12-post157-erofs-lineage23.2-runtime-tested-20260922) | [`5cf633864b`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/5cf633864bedb3e9d05b36c692b1b0964cd262a9) | source-and-metadata-only (4) | `fbbf71bc1157` | no exact-tag complete set | historical EROFS runtime milestone; shares sibling commit |
| [`p11-zui14-adsp-fastrpc-sensors-tested-20260923`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/p11-zui14-adsp-fastrpc-sensors-tested-20260923) | [`5f4e15db5c`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/5f4e15db5c97c2c507935ac3cc52575efda00b07) | source-and-metadata-only (4) | `bd46e4cc7ee7` | no exact-tag complete set | partial ADSP/sensors milestone; not final validated hybrid |
| [`tbj606f-a16-zui14-kernel-stable-20260924`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/tbj606f-a16-zui14-kernel-stable-20260924) | [`7124b9c09a`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/7124b9c09a48380a7b028104e17cac36b9b1a0af) | source-and-metadata-only (4) | `a22b1ce54a9b` | no exact-tag complete set | stable kernel source; binaries later released in v1 |
| [`tbj606f-a16-zui14-opensource-20260924`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/tbj606f-a16-zui14-opensource-20260924) | [`62d8b441b6`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/62d8b441b64013a9714736234390d216b9164195) | source-and-metadata-only (4) | `d1d50073e466` | no exact-tag complete set | source/publication milestone; no GitHub kernel image |
| [`tbj606f-a16-zui14-published-20260924`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/tbj606f-a16-zui14-published-20260924) | [`8ea948339a`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/8ea948339a5c910e40ced880f338eeac279e4c1e) | source-and-metadata-only (4) | `634c2be0b73a` | no exact-tag complete set | source/publication milestone; no GitHub kernel image |
| [`tbj606f-erofs-lz4-v183-20260924`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/tbj606f-erofs-lz4-v183-20260924) | [`3d93df7748`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/3d93df7748a22962edc037670a0342246d7619a7) | source-and-metadata-only (4) | `26378c57495b` | no exact-tag complete set | LZ4 decoder source checkpoint; release explicitly disclaims full boot |
| [`tbj606f-a16-zui14-public-v3`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/tbj606f-a16-zui14-public-v3) | [`ed298bfdc8`](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/commit/ed298bfdc8393b1bda63daf9b1f38e2187810a25) | kernel-and-helper-bundle (21) | — | no exact-tag complete set | source-matched v1-identical kernel + helper bundle; no OEM images |

## Audit data

- 57 releases, 250 assets, 0 missing asset digests, 54 unique source commits.
- 54 source-only releases: 37 exact-tag local staged Image/boot/config/ABI sets, 17 without such a set.
- 20 release/asset digest records match the previous HDD SHA manifest (duplicates across v1/v3 counted separately).
- Old catalog: 56 releases / 229 assets at 2026-09-24T10:57:21.628046+00:00, predating v3.

Rebuild audit metadata with: `python3 tools/tbj606f/audit-releases.py`.
No firmware, flash device, deletion, or kernel build is performed.
