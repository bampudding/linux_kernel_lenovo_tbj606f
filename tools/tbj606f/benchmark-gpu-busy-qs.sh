#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only
# Private paired QS benchmark: graphics counters and GPU DVFS changes.
# Temporarily toggles statusbar and tracepoints, restores tracepoint.
set -euo pipefail
if [[ $# != 1 ]];then echo 'Usage: P11_TARGET_SERIAL=HA1E02DA benchmark-gpu-busy-qs.sh NEW_OUTPUT_DIRECTORY' >&2;exit 2;fi
S=${P11_TARGET_SERIAL:?Must select the exact device serial}
[[ $S == HA1E02DA ]] || { echo 'Not the verified TB-J606F serial' >&2;exit 1; }
P=$1
[[ ! -e $P ]] || { echo 'output already exists';exit 1; }
mkdir -p "$P"
[[ "$(adb -s "$S" shell getprop ro.product.device | tr -d '\r')" == J606F ]] || { echo 'Target device does not report J606F' >&2;exit 1; }
getprop=$(adb -s "$S" shell getprop sys.boot_completed | tr -d '\r')
[[ $getprop == 1 ]] || { echo 'boot incomplete';exit 1; }
awake=$(adb -s "$S" shell dumpsys power | grep -m1 mWakefulness= || :)
[[ $awake == *Awake* ]] || { echo 'screen asleep';exit 1; }
keyguard=$(adb -s "$S" shell dumpsys window policy | grep -m1 mIsShowing= || :)
[[ $keyguard != *mIsShowing=true* ]] || { echo 'KEYGUARD showing; abort';exit 1; }
{
 date
 adb -s "$S" shell 'uname -v;getprop sys.boot_completed;dumpsys thermalservice | grep -m1 "Thermal Status:";for d in /sys/class/thermal/cooling_device{0,1,15};do echo -n "$d ";cat "$d/cur_state";done'
} > "$P/state-before.txt" 2>&1
adb -s "$S" shell 'cmd statusbar collapse;cmd statusbar expand-settings;sleep .5;cmd statusbar collapse;sleep .5' > "$P/warmup.txt" 2>&1
adb -s "$S" shell dumpsys gfxinfo com.android.systemui reset > "$P/gfx-reset.txt"
adb -s "$S" shell 'dumpsys SurfaceFlinger | grep -E "Total missed frame count:|HWC missed frame count:|GPU missed frame count:" | head -3' > "$P/sf-before.txt"
trace_before=$(adb -s "$S" shell 'cat /sys/kernel/tracing/events/power/gpu_frequency/enable /sys/kernel/tracing/tracing_on' | tr -d '\r' | tr '\n' ',')
[[ $trace_before == 0,0, ]] || { echo "TRACING BUSY $trace_before";exit 1; }
trap 'adb -s "$S" shell "echo 0 > /sys/kernel/tracing/events/power/gpu_frequency/enable" >/dev/null 2>&1 || :' EXIT
adb -s "$S" shell 'echo 1 > /sys/kernel/tracing/events/power/gpu_frequency/enable'
(adb -s "$S" shell 'sleep 2;for n in 1 2 3 4 5 6 7 8 9 10;do cmd statusbar expand-settings;sleep .3;cmd statusbar collapse;sleep .3;done' > "$P/gestures.txt" 2>&1) & G=$!
adb -s "$S" shell atrace -z -b 32768 -t 16 gfx view input sched freq idle hal binder_driver thermal > "$P/atrace.txt" 2> "$P/atrace.err" || :
wait "$G"
adb -s "$S" shell 'echo 0 > /sys/kernel/tracing/events/power/gpu_frequency/enable'
trap - EXIT
adb -s "$S" shell dumpsys gfxinfo com.android.systemui > "$P/gfx-after.txt"
adb -s "$S" shell 'dumpsys SurfaceFlinger | grep -E "Total missed frame count:|HWC missed frame count:|GPU missed frame count:" | head -3' > "$P/sf-after.txt"
{
 date
 adb -s "$S" shell 'uname -v;getprop sys.boot_completed;dumpsys thermalservice | grep -m1 "Thermal Status:";for d in /sys/class/thermal/cooling_device{0,1,15};do echo -n "$d ";cat "$d/cur_state";done'
} > "$P/state-after.txt" 2>&1
python3 - "$P" <<'PY'
import sys,zlib,pathlib,re,collections
p=pathlib.Path(sys.argv[1]);b=(p/'atrace.txt').read_bytes(); i=b.find(b'TRACE:\n')
assert i>=0, 'missing atrace bytes'
s=zlib.decompress(b[i+7:]).decode(errors='replace')
(p/'atrace.decoded.txt').write_text(s)
f=[int(x) for x in re.findall(r'gpu_frequency: state=(\d+) gpu_id=0',s)]
g=(p/'gfx-after.txt').read_text()
summary='\n'.join(x for x in g.splitlines() if x.startswith(('Total frames rendered:','Janky frames:','50th percentile:','95th percentile:','50th gpu percentile:','95th gpu percentile:')))
print(p.name, 'GPU clock transitions (kHz)',collections.Counter(f),'Trace waits',s.count('waitForBufferRelease'))
print(summary)
(p/'summary.txt').write_text('GPU clock (kHz) '+repr(dict(collections.Counter(f)))+'\n'+summary+'\n')
PY
cat "$P/state-after.txt" | head -9
