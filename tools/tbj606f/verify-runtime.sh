#!/bin/sh
set -eu
SERIAL=$1
OUT=${2:-tbj606f-runtime-$(date +%Y%m%d-%H%M%S)}
mkdir -p "$OUT"
adb -s "$SERIAL" wait-for-device
adb -s "$SERIAL" shell getprop sys.boot_completed > "$OUT/boot_completed.txt"
adb -s "$SERIAL" shell getprop ro.boot.slot_suffix > "$OUT/slot.txt"
adb -s "$SERIAL" shell uname -a > "$OUT/uname.txt"
adb -s "$SERIAL" shell dumpsys sensorservice > "$OUT/sensorservice.txt"
adb -s "$SERIAL" shell dumpsys wifi > "$OUT/wifi.txt"
adb -s "$SERIAL" shell dumpsys media.audio_policy > "$OUT/audio_policy.txt"
adb -s "$SERIAL" shell dumpsys media.audio_flinger > "$OUT/audio_flinger.txt"
adb -s "$SERIAL" shell cat /proc/modules > "$OUT/modules.txt"
