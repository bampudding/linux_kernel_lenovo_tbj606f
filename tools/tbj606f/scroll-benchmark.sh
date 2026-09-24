#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only
# Run on the Mac with the TB-J606F attached, before and after a vendor change.
set -euo pipefail

usage() {
  echo 'Usage: scroll-benchmark.sh OUTPUT_DIRECTORY' >&2
  echo 'Records a controlled Settings scroll plus CPU placement and thermal state.' >&2
  exit 2
}

[[ $# -eq 1 ]] || usage
out=$1
[[ ! -e $out ]] || { echo "refusing existing output directory: $out" >&2; exit 1; }
command -v adb >/dev/null || { echo 'adb is required' >&2; exit 1; }

serial=${P11_TARGET_SERIAL:?set P11_TARGET_SERIAL to the exact TB-J606F adb serial}
device=$(adb -s "$serial" get-serialno | tr -d '\r')
[[ $device == "$serial" ]] || { echo "wrong/absent device: $device" >&2; exit 1; }
model=$(adb -s "$serial" shell getprop ro.product.model | tr -d '\r')
[[ $model == 'Lenovo TB-J606F' ]] || { echo "wrong model: $model" >&2; exit 1; }
android=$(adb -s "$serial" shell getprop ro.build.version.release | tr -d '\r')
[[ $android == 16 ]] || { echo "expected Android 16, found $android" >&2; exit 1; }
awake=$(adb -s "$serial" shell dumpsys power | grep -m 1 'mWakefulness=' | tr -d '\r')
[[ $awake == *'mWakefulness=Awake'* ]] || {
  echo "display must be awake and unlocked for scrolling: $awake" >&2
  exit 1
}

mkdir -p -- "$out"
{
  echo "UTC: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  echo "Serial: $serial"
  echo "Model: $model"
  echo "Android: $android"
  adb -s "$serial" shell 'uname -r; getprop ro.vendor.build.fingerprint; getprop ro.boot.slot_suffix; getprop ro.boot.flash.locked'
  adb -s "$serial" shell 'for p in $(pidof surfaceflinger) $(pidof vendor.qti.hardware.display.composer-service); do echo "pid=$p"; cat /proc/$p/comm /proc/$p/cpuset; grep Cpus_allowed_list /proc/$p/status; done'
  adb -s "$serial" shell 'for n in /sys/devices/system/cpu/cpufreq/policy*; do echo "$n"; cat "$n/scaling_governor" "$n/scaling_min_freq" "$n/scaling_max_freq"; done'
  adb -s "$serial" shell 'dumpsys thermalservice | grep -E "Thermal Status:|mName=GPU|mName=skin|thermal-cpufreq" | head -15'
} >"$out/device.txt"

adb -s "$serial" shell am start -a android.settings.SETTINGS >"$out/activity.txt" 2>&1
sleep 1
adb -s "$serial" shell 'dumpsys SurfaceFlinger | grep -E "Total missed frame count:|HWC missed frame count:|GPU missed frame count:" | head -3' >"$out/sf-before.txt"
adb -s "$serial" shell dumpsys gfxinfo com.android.settings reset >"$out/settings-pre-reset.txt"

# Twenty alternating gestures, confined to Settings; never wipes or changes
# the Android system, persistent settings, boot state, or another device.
adb -s "$serial" shell 'for n in 1 2 3 4 5 6 7 8 9 10; do input swipe 600 1580 600 450 300; input swipe 600 470 600 1570 300; done'
adb -s "$serial" shell dumpsys gfxinfo com.android.settings >"$out/settings-gfxinfo.txt"
adb -s "$serial" shell 'dumpsys SurfaceFlinger | grep -E "Total missed frame count:|HWC missed frame count:|GPU missed frame count:" | head -3' >"$out/sf-after.txt"

frames=$(sed -n 's/^Total frames rendered: \([0-9][0-9]*\)$/\1/p' "$out/settings-gfxinfo.txt" | head -1)
if [[ ! $frames =~ ^[0-9]+$ ]] || (( frames < 100 )); then
  echo "invalid scroll run: only ${frames:-unknown} Settings frames; wake/unlock the display and retry using a NEW output directory" >&2
  exit 1
fi

{
  grep -E 'Total frames rendered:|Janky frames:|50th percentile:|90th percentile:|95th percentile:|99th percentile:|Number Slow UI thread:|Number Slow issue draw commands:|Number Frame deadline missed:' "$out/settings-gfxinfo.txt" | head -11
  echo 'SurfaceFlinger cumulative counters before:'
  cat "$out/sf-before.txt"
  echo 'SurfaceFlinger cumulative counters after:'
  cat "$out/sf-after.txt"
} | tee "$out/summary.txt"

echo "Saved: $out"
