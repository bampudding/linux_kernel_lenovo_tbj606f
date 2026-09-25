#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only
# Known-good source boot, kernel shared between control/wake465 images;
# private temporary fastboot boot experiment only. No partition writes.
set -euo pipefail
if [[ $# != 4 || ( ${4:-} != stock && ${4:-} != 465 ) ]];then
  echo 'Usage: make-gpu-wake-boot.sh VERIFIED_STABLE_BOOT.img Image OUTPUT_BOOT.img stock|465' >&2
  exit 2
fi
stable=$1; kernel=$2; out=$3; mode=$4
base_hash=93f9e9518fc9a20691ab0b3579b0c628e23522674e827fc57b8867945aedd635
[[ -s $stable && -s $kernel && ! -e $out ]] || { echo 'missing input or existing output' >&2; exit 1; }
[[ $(sha256sum "$stable" | cut -d' ' -f1) == "$base_hash" ]] || { echo 'source boot SHA mismatch' >&2; exit 1; }
[[ $(stat -c %s "$kernel") -gt 30000000 && $(stat -c %s "$kernel") -lt 37000000 ]] || { echo 'raw Image size mismatch' >&2; exit 1; }
self_dir=$(cd -- "$(dirname -- "$0")" && pwd)
tmp=$(mktemp -d "${TMPDIR:-/tmp}/p11-gpuwake.XXXXXXXX")
partial="$out.partial.$$"
trap 'rm -rf "$tmp"; rm -f "$partial"' EXIT
args=$(python3 "$self_dir/unpack_bootimg.py" --boot_img "$stable" --out "$tmp/base" --format=mkbootimg)
gzip -n -9 -c "$kernel" >"$tmp/base/kernel"
eval "set -- $args"
options=("$@")
found=0
for ((i=0; i<${#options[@]};i++));do
  if [[ ${options[i]} == --cmdline ]];then
    [[ ${options[i+1]} != *p11.f=* && ${options[i+1]} != *p11.gw=* && ${options[i+1]} != *p11tune.gpu_top_freq=* ]] || { echo 'unsafe experiment already in source boot cmdline' >&2;exit 1; }
    if [[ $mode == 465 ]];then options[i+1]="${options[i+1]} p11.gw=465";fi
    found=1
  fi
done
((found==1)) || { echo 'no boot cmdline found' >&2;exit 1; }
python3 "$self_dir/mkbootimg.py" "${options[@]}" --output "$partial"
[[ $(stat -c %s "$partial") -le 100663296 ]] || { echo 'boot exceeds 96MiB' >&2;exit 1; }
verified=$(python3 "$self_dir/unpack_bootimg.py" --boot_img "$partial" --out "$tmp/check" --format=mkbootimg)
cmp "$tmp/base/kernel" "$tmp/check/kernel"
cmp "$tmp/base/ramdisk" "$tmp/check/ramdisk"
cmp "$tmp/base/dtb" "$tmp/check/dtb"
[[ $verified != *p11.f=* && $verified != *p11tune.gpu_top_freq=* ]] || { echo 'unsafe floor or OC flag' >&2;exit 1; }
if [[ $mode == 465 ]];then
 [[ $verified == *p11.gw=465* ]] || { echo 'wake option absent' >&2;exit 1; }
else
 [[ $verified != *p11.gw=* ]] || { echo 'unexpected wake option' >&2;exit 1; }
fi
mv "$partial" "$out"
sha256sum "$out"
echo "TEMPORARY boot diagnostic: $mode, stock DTB/ramdisk verified; no flash."
