#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only
# Temporary-boot-only diagnostic image for the Lenovo TB-J606F.
set -euo pipefail

if (( $# != 3 && $# != 4 )); then
  echo 'Usage: make-temp-sf-boot.sh STABLE_BOOT.img EXPERIMENTAL_RAW_Image OUTPUT_BOOT.img [--all-sf|--sf-and-composer]' >&2
  exit 2
fi

stable=$1
kernel=$2
output=$3
self_dir=$(cd "$(dirname -- "$0")" && pwd)
mode=1
if (( $# == 4 )); then
  case $4 in
    --all-sf) mode=2 ;;
    --sf-and-composer) mode=3 ;;
    *) echo 'unknown experiment mode' >&2; exit 2 ;;
  esac
fi
[[ -f $stable && -s $kernel ]] || { echo 'boot template/kernel missing' >&2; exit 1; }
[[ ! -e $output ]] || { echo 'output already exists' >&2; exit 1; }

for cmd in python3 sha256sum gzip cmp mktemp; do
  command -v "$cmd" >/dev/null || { echo "missing $cmd" >&2; exit 1; }
done

base_hash=93f9e9518fc9a20691ab0b3579b0c628e23522674e827fc57b8867945aedd635
actual=$(sha256sum "$stable")
actual=${actual%% *}
[[ $actual == "$base_hash" ]] || { echo "unknown boot template SHA256: $actual" >&2; exit 1; }

tmp=$(mktemp -d "${TMPDIR:-/root}/p11-temp-boot.XXXXXXXX")
partial="${output}.partial.$$"
trap 'rm -rf "$tmp"; rm -f "$partial"' EXIT

args=$(python3 "$self_dir/unpack_bootimg.py" \
  --boot_img "$stable" --out "$tmp/base" --format=mkbootimg)
gzip -n -9 -c "$kernel" >"$tmp/base/kernel"

# The verified template and the local unpacker generate only mkbootimg flags.
eval "set -- $args"
options=("$@")
found=0
for (( i=0; i<${#options[@]}; i++ )); do
  if [[ ${options[i]} == --cmdline ]]; then
    [[ ${options[i+1]} != *p11tune.sf_bigcpus=* ]] || {
      echo 'boot template already carries the experimental flag' >&2
      exit 1
    }
    options[i+1]="${options[i+1]} p11tune.sf_bigcpus=$mode"
    found=1
  fi
done
(( found == 1 )) || { echo 'boot template missing cmdline' >&2; exit 1; }

python3 "$self_dir/mkbootimg.py" "${options[@]}" --output "$partial"
[[ $(stat -c %s "$partial") -le 100663296 ]] || {
  echo 'boot.img exceeds 96 MiB boot_a capacity' >&2
  exit 1
}
python3 "$self_dir/unpack_bootimg.py" \
  --boot_img "$partial" --out "$tmp/verify" --format=mkbootimg \
  >"$tmp/verify-args.txt"
cmp "$tmp/base/ramdisk" "$tmp/verify/ramdisk"
cmp "$tmp/base/dtb" "$tmp/verify/dtb"
cmp "$tmp/base/kernel" "$tmp/verify/kernel"
grep -q "p11tune.sf_bigcpus=$mode" "$tmp/verify-args.txt"

mv "$partial" "$output"
echo "stable boot: $base_hash"
sha256sum "$kernel" "$output"
echo 'ramdisk and DTB unchanged; experimental kernel cmdline flag confirmed'
echo 'This image is for fastboot -s SERIAL boot only; never flash an untested image.'
