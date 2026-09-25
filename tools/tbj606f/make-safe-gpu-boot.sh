#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only
# Rebuild boot using the known-good ramdisk/DTB and a kernel with GPU floor
# experiment reverted. Never flash here: explicit output file only.
set -euo pipefail
if [[ $# != 3 ]]; then
  echo 'Usage: make-safe-gpu-boot.sh VERIFIED_STABLE_BOOT.img BUILT_SAFE_Image NEW_BOOT.img' >&2
  exit 2
fi
stable=$1
kernel=$2
out=$3
self_dir=$(cd -- "$(dirname -- "$0")" && pwd)
base_hash=93f9e9518fc9a20691ab0b3579b0c628e23522674e827fc57b8867945aedd635
[[ -s "$stable" && -s "$kernel" && ! -e "$out" ]] || { echo 'missing input or output already exists' >&2; exit 1; }
[[ $(sha256sum "$stable" | cut -d' ' -f1) == "$base_hash" ]] || { echo 'source boot hash mismatch' >&2; exit 1; }
[[ $(stat -c %s "$kernel") -gt 30000000 && $(stat -c %s "$kernel") -lt 37000000 ]] || { echo 'unexpected raw kernel Image size' >&2; exit 1; }
tmp=$(mktemp -d "${TMPDIR:-/tmp}/p11-gpu-rollback.XXXXXXXX")
partial="$out.partial.$$"
trap 'rm -rf "$tmp"; rm -f "$partial"' EXIT
args=$(python3 "$self_dir/unpack_bootimg.py" --boot_img "$stable" --out "$tmp/stable" --format=mkbootimg)
gzip -n -9 -c "$kernel" >"$tmp/stable/kernel"
eval "set -- $args"
options=("$@")
for ((i=0; i<${#options[@]}; i++)); do
  if [[ ${options[i]} == --cmdline ]]; then
    [[ ${options[i+1]} != *p11.f=* && ${options[i+1]} != *p11tune.gpu_top_freq=* ]] || {
      echo 'base boot contains unsupported GPU experiment option' >&2; exit 1;
    }
  fi
done
python3 "$self_dir/mkbootimg.py" "${options[@]}" --output "$partial"
[[ $(stat -c %s "$partial") -le 100663296 ]] || { echo 'boot exceeds 96 MiB' >&2; exit 1; }
verify=$(python3 "$self_dir/unpack_bootimg.py" --boot_img "$partial" --out "$tmp/check" --format=mkbootimg)
cmp "$tmp/stable/kernel" "$tmp/check/kernel"
cmp "$tmp/stable/ramdisk" "$tmp/check/ramdisk"
cmp "$tmp/stable/dtb" "$tmp/check/dtb"
[[ $verify != *p11.f=* && $verify != *p11tune.gpu_top_freq=* ]] || {
  echo 'stale GPU floor/OC boot flag persists' >&2; exit 1;
}
mv "$partial" "$out"
sha256sum "$out"
echo 'Verified stock ramdisk+DTB and no GPU floor or OC. Not flashed.'
