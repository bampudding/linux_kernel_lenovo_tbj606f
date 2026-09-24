#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only
# Host-side capture only; never modifies Android settings or flash partitions.
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo 'Usage: P11_TARGET_SERIAL=YOUR_DEVICE_SERIAL capture-display-artifact.sh NEW_OUTPUT_DIRECTORY' >&2
  exit 2
fi

serial=${P11_TARGET_SERIAL:?set the exact intended Android device serial}
out=$1
[[ ! -e $out ]] || { echo "refusing existing output: $out" >&2; exit 1; }
[[ $(adb -s "$serial" get-serialno | tr -d '\r') == "$serial" ]] || exit 1
[[ $(adb -s "$serial" shell getprop ro.product.model | tr -d '\r') == 'Lenovo TB-J606F' ]] || exit 1
awake=$(adb -s "$serial" shell dumpsys power | grep -m1 'mWakefulness=')
[[ $awake == *'mWakefulness=Awake'* ]] || {
  echo "Display is not awake. Wait until the issue is visible, then retry: $awake" >&2
  exit 1
}

mkdir -p "$out"
date -u '+%Y-%m-%dT%H:%M:%SZ' > "$out/utc-time.txt"
adb -s "$serial" exec-out screencap -p > "$out/screenshot.png"
adb -s "$serial" shell logcat -b kernel -d > "$out/kernel.log"
adb -s "$serial" shell logcat -b main -b system -b crash -d > "$out/android.log"
adb -s "$serial" shell dumpsys SurfaceFlinger > "$out/surfaceflinger.txt"
adb -s "$serial" shell dumpsys display > "$out/display.txt"
{
  adb -s "$serial" shell 'getprop sys.boot_completed; getprop ro.boot.slot_suffix; uname -r; cat /dev/cpuset/system-background/cpus'
  adb -s "$serial" shell 'wm size; wm density; settings get global disable_window_blurs; getprop debug.hwui.renderer'
  adb -s "$serial" shell 'cat /sys/devices/system/cpu/cpu_boost/input_boost_ms; cat /sys/devices/system/cpu/cpu_boost/input_boost_freq'
} > "$out/state.txt"
{
  echo 'Boot/session kernel GPU/DSI/panel warnings (not necessarily associated with the visual incident):'
  grep -Ei '(kgsl|adreno|gpu|dsi|drm|smmu|iommu|sde|mdss|fence)' "$out/kernel.log" |
    grep -Ei '(error|fault|fail|timeout|underrun|overflow|crc|hang|recovery|WARN)' |
    tail -90 || true
} > "$out/kernel-display-warnings.txt"
if command -v shasum >/dev/null 2>&1; then
  (cd "$out" && shasum -a 256 screenshot.png kernel.log android.log surfaceflinger.txt display.txt state.txt > SHA256SUMS)
fi
echo "Captured host-only evidence in: $out"
echo 'Also take a CAMERA PHOTO of the physical panel immediately, at the same moment.'
echo 'Do not upload the full logs publicly without reviewing private data.'
