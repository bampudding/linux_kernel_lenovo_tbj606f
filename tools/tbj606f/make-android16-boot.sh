#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only
set -euo pipefail

usage() {
  echo "Usage: make-android16-boot.sh ZUI12_BOOT RAW_IMAGE OUTPUT_BOOT [MKBOOTIMG_DIR]" >&2
  exit 2
}

[ "$#" -ge 3 ] && [ "$#" -le 4 ] || usage
TEMPLATE=$1
IMAGE=$2
OUTPUT=$3
SELF_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
MKBOOTIMG_DIR=${4:-$SELF_DIR}

for x in python3 gzip cpio find sort; do
  command -v "$x" >/dev/null 2>&1 || { echo "missing tool: $x" >&2; exit 1; }
done
[ -f "$TEMPLATE" ] || { echo "missing ZUI12 boot template" >&2; exit 1; }
[ -f "$IMAGE" ] || { echo "missing raw kernel Image" >&2; exit 1; }
[ -f "$MKBOOTIMG_DIR/unpack_bootimg.py" ] || { echo "missing unpack_bootimg.py" >&2; exit 1; }
[ -f "$MKBOOTIMG_DIR/mkbootimg.py" ] || { echo "missing mkbootimg.py" >&2; exit 1; }

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
unpack="$tmp/unpack"
root="$tmp/ramdisk-root"
mkdir -p "$unpack" "$root"

args=$(python3 "$MKBOOTIMG_DIR/unpack_bootimg.py" --boot_img "$TEMPLATE" --out "$unpack" --format=mkbootimg)

(
  cd "$root"
  gzip -dc "$unpack/ramdisk" | cpio -idm --quiet
)

python3 - "$root/fstab.qcom" <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1])
text=p.read_text()
old="system                                                  /system                   ext4    ro,barrier=1,discard                                 wait,slotselect,avb=vbmeta_system,logical,first_stage_mount,avb_keys=/avb/q-gsi.avbpubkey:/avb/r-gsi.avbpubkey:/avb/s-gsi.avbpubkey"
new="system                                                  /system                   erofs   ro                                                   wait,slotselect,logical,first_stage_mount"
if old not in text:
    raise SystemExit("expected ZUI12 system fstab entry not found")
p.write_text(text.replace(old,new,1))
PY

(
  cd "$root"
  LC_ALL=C find . -print | LC_ALL=C sort | cpio -o -H newc --quiet | gzip -n -9 > "$unpack/ramdisk.new"
)
mv "$unpack/ramdisk.new" "$unpack/ramdisk"
gzip -n -9 -c "$IMAGE" > "$unpack/kernel"

eval "set -- $args"
python3 "$MKBOOTIMG_DIR/mkbootimg.py" "$@" --output "$OUTPUT"

test -s "$OUTPUT"
echo "raw Image:"
sha256sum "$IMAGE" 2>/dev/null || shasum -a 256 "$IMAGE"
echo "boot image:"
sha256sum "$OUTPUT" 2>/dev/null || shasum -a 256 "$OUTPUT"
