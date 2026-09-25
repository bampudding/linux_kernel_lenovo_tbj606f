#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only
# Manually reproduce a physical-touch launcher drag (or a comparison workload).
# The device must already be awake and showing the chosen app. No boot, vendor,
# display, launcher preference or filesystem settings are changed by this test.
set -euo pipefail
usage() {
  echo 'Usage: P11_TARGET_SERIAL=HA1E02DA launcher-gesture-benchmark.sh launcher|easteregg|settings OUTPUT_DIRECTORY [SECONDS]' >&2
  echo 'Before invocation, open the selected app and keep the display awake. During the timed window, repeat physical-finger dragging or scrolling.' >&2
  exit 2
}
(( $# == 2 || $# == 3 )) || usage
mode=$1
out=$2
seconds=${3:-20}
case "$mode" in
  launcher) pkg=com.android.launcher3 ;;
  easteregg) pkg=com.android.egg ;;
  settings) pkg=com.android.settings ;;
  *) usage ;;
esac
[[ $seconds =~ ^[0-9]+$ ]] && ((seconds >= 10 && seconds <= 120)) || usage
[[ ! -e $out ]] || { echo "Output exists: $out" >&2; exit 1; }
command -v adb >/dev/null || { echo 'adb required' >&2; exit 1; }
serial=${P11_TARGET_SERIAL:?Set P11_TARGET_SERIAL to the exact serial}
[[ $serial == HA1E02DA ]] || { echo 'Only the verified TB-J606F serial is supported' >&2; exit 1; }
run() { adb -s "$serial" "$@"; }
[[ $(run get-serialno | tr -d '\r') == "$serial" ]] || { echo 'Target device not connected' >&2; exit 1; }
[[ $(run shell getprop ro.product.device | tr -d '\r') == J606F ]] || { echo 'Target model mismatch' >&2; exit 1; }
awake=$(run shell dumpsys power | grep -m 1 'mWakefulness=' | tr -d '\r')
[[ $awake == *mWakefulness=Awake* ]] || { echo "Device display not awake: $awake" >&2; exit 1; }
focus=$(run shell dumpsys window | grep -m1 'mFocusedApp=' | tr -d '\r' || :)
[[ $focus == *"$pkg"* ]] || { echo "Foreground app does not match $pkg: $focus" >&2; exit 1; }
mkdir -p -- "$out"
{
  echo "time_utc=$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  echo "mode=$mode package=$pkg interval=$seconds target=$serial"
  run shell 'getprop sys.boot_completed; getprop ro.boot.slot_suffix; uname -r; wm size; wm density; getprop debug.egl.buffcount; settings get global disable_window_blurs; dumpsys thermalservice | grep "Thermal Status:"'
  run shell 'for p in $(pidof com.android.launcher3) $(pidof com.android.egg) $(pidof surfaceflinger) $(pidof vendor.qti.hardware.display.composer-service); do [ -e /proc/$p/status ] || continue; echo "PID:$p"; cat /proc/$p/comm /proc/$p/cpuset 2>/dev/null || :; grep Cpus_allowed_list /proc/$p/status; done'
} > "$out/device.txt"
run shell 'dumpsys SurfaceFlinger | grep -E "Total missed frame count:|HWC missed frame count:|GPU missed frame count:" | head -3' > "$out/sf-before.txt"
run shell dumpsys gfxinfo "$pkg" reset > "$out/gfx-pre-reset.txt"
printf 'CAPTURE START: repeat physical gestures in %s for %s seconds. Do not switch apps.\n' "$pkg" "$seconds"
sleep "$seconds"
run shell dumpsys gfxinfo "$pkg" > "$out/gfx-after.txt"
run shell 'dumpsys SurfaceFlinger | grep -E "Total missed frame count:|HWC missed frame count:|GPU missed frame count:" | head -3' > "$out/sf-after.txt"
{
  grep -E 'Total frames rendered:|Janky frames:|50th percentile:|90th percentile:|95th percentile:|99th percentile:|Number High input latency:|Number Slow UI thread:|Number Slow issue draw commands:|Number Frame deadline missed:' "$out/gfx-after.txt" | head -11 || :
  printf 'SurfaceFlinger before:\n';cat "$out/sf-before.txt"
  printf 'SurfaceFlinger after:\n';cat "$out/sf-after.txt"
} | tee "$out/summary.txt"
frames=$(sed -n 's/^Total frames rendered: \([0-9][0-9]*\)$/\1/p' "$out/gfx-after.txt" | head -1)
[[ $frames =~ ^[0-9]+$ ]] && ((frames >= 40)) || { echo "INCONCLUSIVE: only ${frames:-unknown} frames; review foreground/finger activity" >&2; exit 1; }
echo "CAPTURE COMPLETE (private diagnostic, do not publish raw device info): $out"
