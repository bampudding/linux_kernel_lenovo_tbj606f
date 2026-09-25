# TB-J606F Android 17 GSI bring-up — source-first, no Android 16 regression

**Status (2026-09-25): real P11-only compatibility source patches built and
static-tested. No Android 17 system.img was available inside P11's permitted
workspace, and no Android 17 image was flashed or boot-confirmed. Kernel
4.19.325 is a separate isolated port, not proof of Android 17 support.**

## Immutable baseline and real device evidence

- P11 Android 16 known stable: `/root/p11-kernel-lab/research/julian-zui12-stable100`
  at `62e502146a135e40893d536a31468096cf698f75`, 4.19.157,
  public `opensource/tbj606f-a16-zui14`. No stable source edits.
- Current `vendor/etc/selinux/plat_sepolicy_vers.txt`: **30.0**;
  live `ro.vndk.version=30`, `ro.vendor.build.version.sdk=30`,
  `ro.product.first_api_level=29`, `ro.board.first_api_level=30`;
  ZUI14 hybrid manifest FCM target-level **5**. This is about the
  *actual vendor* and never guessed from Snapdragon model.
- Android 16 control GSI (`LineageOS-23.2-20260524...EXT4-GSI.img`)
  has a **real** `/system/etc/selinux/mapping/30.0.cil` (126,277B,
  1,084 ABI-30 symbol references), plus system_ext/product 30.0 files.
  Tested by `preflight_gsi.py` against P11's extracted vendor.
- Android 17 AOSP `system/sepolicy` release 1 (SHA
  `e066568e98d86db31a9346d30977f3632fa7073c`) begins its
  generated mapping modules at **31.0**, no 30.0 API snapshot or
  30.0 private compatibility sources. Ordinary vendor30 policy loading
  therefore requires genuine mapping support. **Never rename 31.0.cil
  to 30.0.cil**: suffixes and public types differ.

## Source patch 1: genuine sepolicy 30.0 mapping chain

File: `aosp17-sepolicy-compat30.patch` (AOSP Apache 2.0 source).
Applied to exact AOSP17 `platform/system/sepolicy` tag
`android-17.0.0_r1`; private 30.0 bridge and 30.0 public API snapshot
imported byte-for-byte from exact AOSP16 `android-16.0.0_r1`
(SHA `d4a7f392598cee96d9479a8ac0f84259c19b043a`).

Reestablishes **11 Soong compat modules** linking 30.0 to the existing
31.0→32.0→33.0→34.0→202404→newer compatibility chain;
platform, system_ext and product mapping targets and platform/system_ext
`*.compat.cil` modules, plus original public version 30 policy API.
All relevant AOSP17 `Android.bp` packaging dependencies restored.
The source patch was replay/undo-checked and its A16 bridge file
SHA256s verified. It has **NOT** been built with a complete AOSP17
Soong tree; an actual compiled system image and secilc/vendor policy
merge are still necessary for final acceptance.

## Source patch 2: restore Android 11-era VINTF FCM5 fragment

Actual P11 ZUI14 hybrid vendor declares VINTF FCM target level **5**.
The official Android17 `hardware/interfaces` compatibility-matrix source
(tag `android-17.0.0_r1`, SHA
`0162af698935100a590b7359581ac8b1b80693e5`) only packages FCM
7/8 and 202404/202504/202604: it omits FCM5 and FCM6 present in
this P11's booted Android16 Lineage GSI. The A17 `libvintf` source
still recognizes FCM level 5 and combines any higher FCM matrices
as optional fragments, but the source bundle's supported-version list
is a separate concrete mismatch worth fixing.

`aosp17-fcm5-p11.patch` restores the **byte-identical** 295-byte A16
FCM5 compatibility matrix placeholder and the A17 Soong module/
`SYSTEM_MATRIX_DEPS_A17` packaging. FCM5 was already formally
deprecated in A16 and is a placeholder, **not** a complete historical
HAL contract or permission to suppress VINTF incompatibilities.
The missing FCM6 kernel-config map is not blindly recreated because its
build dependencies were removed; full target-level5 device VINTF
compatibility still requires generated Android17 framework matrices
and the actual P11 device manifest to be checked together.

`verify_fcm5_source.py` confirms target5, byte-identical upstream A16
snapshot and exactly one A17 Soong module/packaging entry. A17 source
commit `8ef0c22e3cbd902f376aae2af7b3f03a54ca4d5f`, based on
`0162af698935100a590b7359581ac8b1b80693e5`.

## Source patch 3: P11-only Android17 BPF version gate

**Critical newly confirmed independent blocker**: AOSP17
`packages/modules/Connectivity/bpf/loader/NetBpfLoad.cpp` tag
`android-17.0.0_r1`, SHA
`347fbd34b368d19f0d87e908ea101eed3601a731`, returns error 6 if
`25Q2+` runs with kernel below **5.4**, then error 7 if `25Q4+` runs
below **5.10**. Android 17 26Q2 satisfies both conditions.
`netbpfload.rc` synchronously waits for `bpf.progs_loaded=1`, so an
unmodified AOSP17 Tethering APEX can stop boot even on **4.19.325**.
This is unrelated to ColorOS/Oplus-specific qspmhal and Wi-Fi overlay.

File: `aosp17-connectivity-p11-bpf419.patch`. Allows passing **only
these two version guards** when the *actual* vendor device is J606F,
platform Bengal, vendor SDK 30, kernel exactly 4.19.x and at least
4.19.325. Logs a prominent warning. This does **not** change uname,
pretend missing BPF helpers exist, disable loader, force the
`bpf.progs_loaded` property or exempt other devices from the minimum
checks. Any real unsupported eBPF program/helper/API must still fail,
and must be fixed with verified, minimal backports or a P11-specific
BPF program compatibility change after obtaining logs. The patch
requires a full matching Tethering APEX rebuild. Patching only
system.img file names will not change the APEX binary.

## Reproduce the AOSP source changes, HDD only

```bash
BASE=/root/HDD/user0/P11/android17-gsi-compat
# The exact pinned source checkouts already exist on this machine:
#   $BASE/system-sepolicy        branch p11/android17-compat30
#   $BASE/aosp17-connectivity    branch p11/android17-legacy419-bpf
# Alternatively, fresh clones of these *specific AOSP17 tags*:
git clone --depth=1 --branch android-17.0.0_r1 \
  https://android.googlesource.com/platform/system/sepolicy "$BASE/sepolicy-clean"
git -C "$BASE/sepolicy-clean" apply --check \
  /root/HDD/user0/P11/android17-gsi-compat/kernel-worktree/Documentation/tbj606f/android17/aosp17-sepolicy-compat30.patch
# The patch needs an actual apply and Soong build in a full matching
# Android17 AOSP source tree; it does not modify current vendor or GSI.
```

Build/review the `plat_30.0.cil`, `system_ext_30.0.cil`,
`product_30.0.cil` plus `30.0.compat.cil` modules and the combined
SELinux policy with the exact hybrid vendor `vendor_sepolicy.cil` and
`plat_pub_versioned.cil`, then rebuilt Tethering APEX binary with the
P11-only BPF patch. Vendor proprietary files remain private.

## Verification commands

```bash
W=/root/HDD/user0/P11/android17-gsi-compat/kernel-worktree
R=/root/HDD/user0/P11/android17-gsi-compat
V=/root/HDD/user0/P11/scratch-archive/20260923/vendor-upgrade-audit-20260923/z14/etc
python3 "$W/tools/tbj606f/android17/verify_compat30_source.py" \
  --a17-sepolicy "$R/system-sepolicy" --p11-vendor-etc "$V"
python3 "$W/tools/tbj606f/android17/verify_bpf_guard.py" \
  --connectivity-source "$R/aosp17-connectivity"
python3 "$W/tools/tbj606f/android17/verify_fcm5_source.py" \
  --a17-hardware-interfaces "$R/hardware-interfaces" \
  --a16-hardware-interfaces "$R/hardware-interfaces-a16" \
  --p11-vendor-etc "$V"
# When an Android17 ARM64 GSI system.img exists in P11's HDD directory:
python3 "$W/tools/tbj606f/android17/preflight_gsi.py" \
  --vendor-dir "$V" --scratch-dir "$R" \
  --system-img "$R/accepted-official-android17/system.img"
```

Preflight accepts raw ext4 and Android sparse images and is read-only;
all sparse decoding happens temporarily on the HDD, not small `/root`.
It requires SDK37 (Android17) by default, rejects Android16 controls
unless explicitly run with `--require-sdk 36`, rejects absent/wrong
platform 30.0 mapping and notes system_ext, product, LLNDK/VNDK checks
that may require other partition images.
The shipped Android16 control passes; malformed images are rejected.
`preflight_gsi.py` does **not** claim that a mapping exists in an
Android17 GSI not supplied for P11.

## Existing LineageOS 16 combined-policy caveat, experimentally tested

As a negative control, the **already-running P11 Android16** LineageOS
system image was read via debugfs (no mounts or image edits) and
`secilc -m -M true -G -c 31` was run with its platform policy, genuine
30.0 mapping/compat CIL, system_ext CIL and the actual ZUI14 hybrid
vendor's `plat_pub_versioned.cil` + `vendor_sepolicy.cil`. With
neverallow checks **enabled**, this independent source-level recompilation
failed due preexisting Lineage PHH `phhsu_daemon` broad `property_type`
set rules and vendor exported property assignments. Its log is at
`/root/HDD/user0/P11/android17-gsi-compat/a16-control-merge/secilc.log`
(HDD only). The installed Android16 combination still boots, so the
standalone test is not equivalent to its precompiled policy, build-time
exemptions, or actual init's policy assembly. This is **not evidence
of an Android17-specific regression**, nor permission to suppress
neverallows in a replacement SELinux policy. A matching A17 build must
be checked with the complete build policy, no arbitrary permissive
or `-N` workaround. The control makes the acceptance criterion more
precise than simply checking 30.0 mapping file presence.

## First flash-free checks once the image exists

1. Verify the official ZIP SHA256 (not just the `.img` digest), file
   format, device partition size, rollback source images and module
   ABI. Official Android17 GSI distribution requires license acceptance;
   none was accepted on behalf of the user in this work.
2. Check generated 30.0 mappings and combine all relevant
   plat, mapping, vendor, system_ext and product policies with `secilc`
   at the device's supported policy version; do not bypass neverallows.
3. Verify FCM5 device manifest vs Android17 framework compatibility
   matrix, old VNDK30 availability and actual HAL binaries.
4. Confirm 4.19.325 boot Image + dtb is structurally valid and vendor
   Wi-Fi/audio/display module ABI remains matched; no boot from an
   uncompiled source tree.
5. After separate rollback-capable device approval and verified image,
   use GSI installation procedure; `fastboot boot` only boots boot.img,
   **not** a replacement Android system partition. Capture first-stage
   init, SELinux merge, bpfloader, VINTF and zygote logs; restore stable
   Android16 if anything fails. There was **no such Android17 attempt**
   performed by this source-only checkpoint.

No TB371FC source, image, experiment or running device was modified or
used as a substitute for an Android17 image dedicated to P11.
