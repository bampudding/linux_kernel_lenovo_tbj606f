#!/bin/sh
# SPDX-License-Identifier: GPL-2.0-only
set -eu

usage() {
	echo "Usage: repack-boot.sh TEMPLATE_BOOT RAW_IMAGE OUTPUT_BOOT MKBOOTIMG_DIR" >&2
	exit 2
}

[ "$#" -eq 4 ] || usage
TEMPLATE=$1
IMAGE=$2
OUTPUT=$3
MKBOOTIMG_DIR=$4

[ -f "$TEMPLATE" ] || { echo "missing template boot image: $TEMPLATE" >&2; exit 1; }
[ -f "$IMAGE" ] || { echo "missing raw kernel Image: $IMAGE" >&2; exit 1; }
[ -f "$MKBOOTIMG_DIR/unpack_bootimg.py" ] || { echo "missing unpack_bootimg.py" >&2; exit 1; }
[ -f "$MKBOOTIMG_DIR/mkbootimg.py" ] || { echo "missing mkbootimg.py" >&2; exit 1; }

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

args=$(python3 "$MKBOOTIMG_DIR/unpack_bootimg.py" \
	--boot_img "$TEMPLATE" --out "$tmp" --format=mkbootimg)

gzip -n -9 -c "$IMAGE" > "$tmp/kernel"

# unpack_bootimg.py emits shell-quoted mkbootimg arguments. They point at the
# files under $tmp, whose kernel was just replaced.
eval "set -- $args"
python3 "$MKBOOTIMG_DIR/mkbootimg.py" "$@" --output "$OUTPUT"

test -s "$OUTPUT"
python3 - "$IMAGE" "$tmp/kernel" "$OUTPUT" <<'PYHASH'
import hashlib
import sys
for label, path in zip(('raw Image', 'compressed kernel', 'boot image'), sys.argv[1:]):
    digest = hashlib.sha256()
    with open(path, 'rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    print(f'{label}: {digest.hexdigest()}  {path}')
PYHASH
