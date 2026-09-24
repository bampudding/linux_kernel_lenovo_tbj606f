#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only
set -euo pipefail

REPO="bampudding/linux_kernel_lenovo_tbj606f"
RELEASE_TAG="${TBJ606F_RELEASE_TAG:-tbj606f-a16-zui14-public-v1}"
BASE_URL="https://github.com/${REPO}/releases/download/${RELEASE_TAG}"

EXPECTED_IMAGE_SHA256="af0b7b6b81c4f6ba3c5c2fbb044972a1bf502453ec19effa6d3664c094fdb2f8"
EXPECTED_COMPAT_SHA256="af7e14a238437b5fc7e29dc5fdf8453630d3981f0c4b7218f588ccf6aab08f40"
EXPECTED_GSI_SHA256="26cde4242d9b92fb917b8235c4908e88c5fa6b60db1c56e0c53561db61d333bd"
EXPECTED_ZUI14_BOOT_SHA256="7356b6ac6a791c9508778aa76fe0fe381ca73eb225c7f10831799ed64f0e67d4"
EXPECTED_ZUI14_VENDOR_SHA256="7a73b5886e130cfeb1870e7f5855e1b6bf0010ff694783d2b0d0de553ba6758d"
EXPECTED_HYBRID_VENDOR_SHA256="b0cca3012109d045122dccdbd22f2505327ec7550576daa37d4bde643a39d3dd"
EXPECTED_TESTED_BOOT_SHA256="93f9e9518fc9a20691ab0b3579b0c628e23522674e827fc57b8867945aedd635"
EXPECTED_VENDOR_FINGERPRINT="Lenovo/m11_prc_wifi/J606F:12/SKQ1.220213.001/14.0.147_230414:user/release-keys"

SELF_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
MKBOOTIMG_DIR="$SELF_DIR"

SERIAL=""
GSI=""
STOCK_BOOT=""
VENDOR_IMAGE=""
ZUI14_VENDOR=""
ZUI12_MODULES=""
WORKDIR=""
YES=0
DRY_RUN=0
SKIP_SYSTEM=0
SKIP_VENDOR=0
ALLOW_OTHER_GSI=0
ALLOW_OTHER_BOOT=0
ALLOW_OTHER_VENDOR=0

usage() {
  cat <<'USAGE'
Usage:
  install.sh --serial SERIAL --stock-boot zui14-boot.img \
    [--gsi system.img | --skip-system] \
    [--vendor-image hybrid-vendor.img |
     --zui14-vendor zui14-vendor.img --zui12-modules DIR | --skip-vendor] [options]

Options:
  --yes
  --dry-run
  --skip-system
  --skip-vendor
  --workdir DIR
  --allow-other-gsi
  --allow-other-boot
  --allow-other-vendor
  --release-tag TAG

The script never wipes userdata. Every adb/fastboot command is scoped with
-s SERIAL and non-TB-J606F/bengal devices are rejected.
USAGE
}

die() { echo "ERROR: $*" >&2; exit 1; }
note() { echo "==> $*"; }

while [ "$#" -gt 0 ]; do
  case "$1" in
    --serial) SERIAL=${2:?}; shift 2 ;;
    --gsi) GSI=${2:?}; shift 2 ;;
    --stock-boot) STOCK_BOOT=${2:?}; shift 2 ;;
    --vendor-image) VENDOR_IMAGE=${2:?}; shift 2 ;;
    --zui14-vendor) ZUI14_VENDOR=${2:?}; shift 2 ;;
    --zui12-modules) ZUI12_MODULES=${2:?}; shift 2 ;;
    --workdir) WORKDIR=${2:?}; shift 2 ;;
    --yes) YES=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    --skip-system) SKIP_SYSTEM=1; shift ;;
    --skip-vendor) SKIP_VENDOR=1; shift ;;
    --allow-other-gsi) ALLOW_OTHER_GSI=1; shift ;;
    --allow-other-boot) ALLOW_OTHER_BOOT=1; shift ;;
    --allow-other-vendor) ALLOW_OTHER_VENDOR=1; shift ;;
    --release-tag) RELEASE_TAG=${2:?}; BASE_URL="https://github.com/${REPO}/releases/download/${2:?}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

[ -n "$SERIAL" ] || die "--serial is required"
if [ "$SKIP_SYSTEM" -eq 0 ]; then
  [ -f "$GSI" ] || die "--gsi file not found"
fi
[ -f "$STOCK_BOOT" ] || die "--stock-boot file not found"
if [ "$SKIP_VENDOR" -eq 0 ]; then
  if [ -n "$VENDOR_IMAGE" ]; then
    [ -f "$VENDOR_IMAGE" ] || die "--vendor-image file not found"
  else
    [ -f "$ZUI14_VENDOR" ] || die "provide --vendor-image or --zui14-vendor"
    [ -d "$ZUI12_MODULES" ] || die "--zui12-modules directory not found"
  fi
fi

for x in adb fastboot python3 curl gzip; do
  command -v "$x" >/dev/null 2>&1 || die "missing host tool: $x"
done

sha256_file() {
  python3 - "$1" <<'PY'
import hashlib, sys
h=hashlib.sha256()
with open(sys.argv[1],"rb") as f:
    for b in iter(lambda:f.read(1024*1024), b""):
        h.update(b)
print(h.hexdigest())
PY
}

size_file() {
  python3 - "$1" <<'PY'
import os, sys
print(os.path.getsize(sys.argv[1]))
PY
}

check_hash() {
  file=$1 expected=$2 label=$3 allow=$4
  got=$(sha256_file "$file")
  echo "$got  $file"
  if [ "$got" != "$expected" ] && [ "$allow" -ne 1 ]; then
    die "$label hash differs from the tested value"
  fi
}

if [ -z "$WORKDIR" ]; then
  WORKDIR=$(mktemp -d "${TMPDIR:-/tmp}/tbj606f-install.XXXXXX")
  CLEAN_WORKDIR=1
else
  mkdir -p "$WORKDIR"
  CLEAN_WORKDIR=0
fi
cleanup() {
  if [ "${CLEAN_WORKDIR:-0}" -eq 1 ]; then rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

note "validating local inputs"
if [ "$SKIP_SYSTEM" -eq 0 ]; then
  check_hash "$GSI" "$EXPECTED_GSI_SHA256" "GSI" "$ALLOW_OTHER_GSI"
fi
check_hash "$STOCK_BOOT" "$EXPECTED_ZUI14_BOOT_SHA256" "ZUI14 boot template" "$ALLOW_OTHER_BOOT"

download_asset() {
  name=$1 dest=$2
  if [ ! -s "$dest" ]; then
    note "downloading $name from $RELEASE_TAG"
    curl -fL --retry 3 -o "$dest" "$BASE_URL/$name"
  fi
}

KERNEL_IMAGE="$WORKDIR/Image"
COMPAT="$WORKDIR/p11_audio_compat.ko"
download_asset Image "$KERNEL_IMAGE"
download_asset p11_audio_compat.ko "$COMPAT"
check_hash "$KERNEL_IMAGE" "$EXPECTED_IMAGE_SHA256" "release Image" 0
check_hash "$COMPAT" "$EXPECTED_COMPAT_SHA256" "release compat module" 0

if [ "$SKIP_VENDOR" -eq 0 ] && [ -z "$VENDOR_IMAGE" ]; then
  [ "$(uname -s)" = Linux ] || die "hybrid vendor construction requires Linux; otherwise pass --vendor-image"
  check_hash "$ZUI14_VENDOR" "$EXPECTED_ZUI14_VENDOR_SHA256" "ZUI14 vendor base" 0
  for x in debugfs e2fsck modinfo modprobe; do
    command -v "$x" >/dev/null 2>&1 || die "missing vendor-build tool: $x"
  done
  VENDOR_IMAGE="$WORKDIR/vendor-hybrid.img"
  note "constructing hybrid vendor"
  "$SELF_DIR/make-hybrid-vendor.sh" "$ZUI14_VENDOR" "$ZUI12_MODULES" "$COMPAT" "$VENDOR_IMAGE"
fi

if [ "$SKIP_VENDOR" -eq 0 ]; then
  check_hash "$VENDOR_IMAGE" "$EXPECTED_HYBRID_VENDOR_SHA256" "hybrid vendor" "$ALLOW_OTHER_VENDOR"
fi

BOOT_IMAGE="$WORKDIR/boot-tbj606f-a16-zui14.img"
note "repacking boot image"
"$SELF_DIR/repack-boot.sh" "$STOCK_BOOT" "$KERNEL_IMAGE" "$BOOT_IMAGE" "$MKBOOTIMG_DIR"
BOOT_SHA=$(sha256_file "$BOOT_IMAGE")
echo "$BOOT_SHA  $BOOT_IMAGE"
if [ "$ALLOW_OTHER_BOOT" -eq 0 ] && [ "$BOOT_SHA" != "$EXPECTED_TESTED_BOOT_SHA256" ]; then
  die "repacked boot differs from tested boot; refusing to flash"
fi

note "checking Android device $SERIAL"
adb -s "$SERIAL" get-state >/dev/null
device=$(adb -s "$SERIAL" shell getprop ro.product.vendor.device 2>/dev/null | tr -d '\r')
[ "$device" = "J606F" ] || [ "$device" = "j606f" ] || die "device '$device' is not J606F"
fingerprint=$(adb -s "$SERIAL" shell getprop ro.vendor.build.fingerprint 2>/dev/null | tr -d '\r')
echo "vendor fingerprint: $fingerprint"
[ "$fingerprint" = "$EXPECTED_VENDOR_FINGERPRINT" ] || die "starting vendor is not tested ZUI14 14.0.147"

if [ "$DRY_RUN" -eq 1 ]; then
  note "dry-run complete; no device reboots or partitions modified"
  note "fastboot product, unlock state and partition capacities are checked before flashing in a normal run"
  exit 0
fi

if [ "$YES" -ne 1 ]; then
  cat <<EOF2
About to modify TB-J606F serial $SERIAL:
  slot:     A
  system_a: $([ "$SKIP_SYSTEM" -eq 1 ] && echo unchanged || echo "$GSI")
  vendor_a: $([ "$SKIP_VENDOR" -eq 1 ] && echo unchanged || echo "$VENDOR_IMAGE")
  boot_a:   $BOOT_IMAGE
  userdata: NEVER WIPED

Type exactly: FLASH J606F
EOF2
  read -r answer
  [ "$answer" = "FLASH J606F" ] || die "cancelled"
fi

wait_fastboot() {
  for _ in $(seq 1 90); do
    if fastboot -s "$SERIAL" getvar product 2>&1 | grep -q 'product:'; then return 0; fi
    sleep 1
  done
  return 1
}

note "entering bootloader"
adb -s "$SERIAL" reboot bootloader
wait_fastboot || die "device did not enter fastboot"
product=$(fastboot -s "$SERIAL" getvar product 2>&1 | sed -n 's/.*product: *//p' | tail -1 | tr -d '\r')
[ "$product" = bengal ] || die "fastboot product '$product' is not bengal"
unlocked=$(fastboot -s "$SERIAL" getvar unlocked 2>&1 | sed -n 's/.*unlocked: *//p' | tail -1 | tr -d '\r')
[ "$unlocked" = yes ] || die "bootloader is not unlocked"

note "entering fastbootd"
fastboot -s "$SERIAL" reboot fastboot
for _ in $(seq 1 90); do
  if fastboot -s "$SERIAL" getvar is-userspace 2>&1 | grep -q 'is-userspace: yes'; then break; fi
  sleep 1
done
fastboot -s "$SERIAL" getvar is-userspace 2>&1 | grep -q 'is-userspace: yes' || die "fastbootd did not start"

partition_bytes() {
  var=$1
  raw=$(fastboot -s "$SERIAL" getvar "partition-size:$var" 2>&1 | sed -n "s/.*partition-size:$var: *//p" | tail -1 | tr -d '\r')
  python3 - "$raw" <<'PY'
import sys
s=sys.argv[1].strip()
print(int(s,0) if s else 0)
PY
}

note "checking partition capacities before flashing"
if [ "$SKIP_SYSTEM" -eq 0 ]; then
  system_need=$(size_file "$GSI"); system_have=$(partition_bytes system_a)
  [ "$system_have" -ge "$system_need" ] || die "system_a=$system_have, GSI needs $system_need bytes; no partitions flashed"
fi
if [ "$SKIP_VENDOR" -eq 0 ]; then
  vendor_need=$(size_file "$VENDOR_IMAGE"); vendor_have=$(partition_bytes vendor_a)
  [ "$vendor_have" -ge "$vendor_need" ] || die "vendor_a=$vendor_have, vendor image needs $vendor_need bytes; no partitions flashed"
fi

note "selecting slot A"
fastboot -s "$SERIAL" --set-active=a
current_slot=$(fastboot -s "$SERIAL" getvar current-slot 2>&1 | sed -n 's/.*current-slot: *//p' | tail -1 | tr -d '\r')
[ "$current_slot" = a ] || die "fastboot active slot '$current_slot' is not A; no partitions flashed"

if [ "$SKIP_SYSTEM" -eq 0 ]; then
  note "flashing system_a"
  fastboot -s "$SERIAL" flash system_a "$GSI"
fi
if [ "$SKIP_VENDOR" -eq 0 ]; then
  note "flashing vendor_a"
  fastboot -s "$SERIAL" flash vendor_a "$VENDOR_IMAGE"
fi

note "temporary boot validation before persistent boot_a flash"
fastboot -s "$SERIAL" reboot bootloader
wait_fastboot || die "device did not return to bootloader"
fastboot -s "$SERIAL" boot "$BOOT_IMAGE"

boot_ok=0
for _ in $(seq 1 180); do
  if adb -s "$SERIAL" get-state >/dev/null 2>&1; then
    bc=$(adb -s "$SERIAL" shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')
    if [ "$bc" = 1 ]; then boot_ok=1; break; fi
  fi
  sleep 1
done
[ "$boot_ok" -eq 1 ] || die "temporary boot did not complete; boot_a was NOT flashed"
boot_slot=$(adb -s "$SERIAL" shell getprop ro.boot.slot_suffix 2>/dev/null | tr -d '\r')
[ "$boot_slot" = _a ] || die "temporary boot reached slot '$boot_slot', expected A; boot_a was NOT flashed"

sensor_line=$(adb -s "$SERIAL" shell dumpsys sensorservice 2>/dev/null | grep -m1 'Total .* h/w sensors' || true)
echo "sensor check: ${sensor_line:-missing}"
echo "$sensor_line" | grep -q 'Total 34 h/w sensors' || die "34-sensor validation failed; boot_a was NOT flashed"
audio_line=$(adb -s "$SERIAL" shell dumpsys media.audio_policy 2>/dev/null | grep -m1 'AudioPolicyManager Dump' || true)
[ -n "$audio_line" ] || die "audio validation failed; boot_a was NOT flashed"
module_lines=$(adb -s "$SERIAL" shell cat /proc/modules 2>/dev/null | tr -d '\r')
for module in p11_audio_compat machine_dlkm; do
  grep -q "^$module " <<< "$module_lines" || die "$module not loaded; boot_a was NOT flashed"
done
note "audio module check: p11_audio_compat and machine_dlkm loaded"

note "temporary boot validated; flashing boot_a"
adb -s "$SERIAL" reboot bootloader
wait_fastboot || die "device did not return to bootloader"
fastboot -s "$SERIAL" flash boot_a "$BOOT_IMAGE"
fastboot -s "$SERIAL" reboot
note "install complete; userdata was not wiped"
