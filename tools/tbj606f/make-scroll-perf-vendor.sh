#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only
# Experimental, reversible TB-J606F A16 hybrid-vendor rendering scheduler fix.
set -euo pipefail

usage() {
  cat >&2 <<'USAGE'
Usage: make-scroll-perf-vendor.sh TESTED_HYBRID_VENDOR.img OUTPUT.img [--composer-too]

Derive a NEW ext4 vendor image from the SHA256-verified ZUI14/ZUI12 hybrid v5.
Override only A16 SurfaceFlinger's two cpuset task profiles via the supported
/vendor/etc/task_profiles.json overlay. Optional --composer-too also moves the
Qualcomm display composer service to the foreground cpuset.

Does not change the input image, flash any partition, or touch the GSI.
USAGE
  exit 2
}

[[ $# -eq 2 || $# -eq 3 ]] || usage
base=$1
out=$2
composer=0
if [[ $# -eq 3 ]]; then
  [[ $3 == --composer-too ]] || usage
  composer=1
fi

for tool in sha256sum debugfs e2fsck python3 mktemp cp cmp; do
  command -v "$tool" >/dev/null || { echo "missing tool: $tool" >&2; exit 1; }
done

[[ -f $base ]] || { echo "missing base image: $base" >&2; exit 1; }
[[ ! -e $out ]] || { echo "output already exists: $out" >&2; exit 1; }
[[ -d $(dirname -- "$out") ]] || { echo "missing output directory" >&2; exit 1; }
expected=b0cca3012109d045122dccdbd22f2505327ec7550576daa37d4bde643a39d3dd
actual=$(sha256sum -- "$base")
actual=${actual%% *}
[[ $actual == "$expected" ]] || {
  echo "unexpected base vendor SHA256: $actual (expected $expected)" >&2
  exit 1
}

# Active image editing stays on the SSD. Only the new, complete image is kept.
tmp_root=${TMPDIR:-/root}
[[ $tmp_root != *' '* ]] || { echo 'TMPDIR must contain no spaces' >&2; exit 1; }
tmp=$(mktemp -d "$tmp_root/tbj606f-scroll-perf.XXXXXXXX")
working="${out}.partial.$$"
cleanup() {
  rm -f -- "$working"
  rm -rf -- "$tmp"
}
trap cleanup EXIT

cp --reflink=auto -- "$base" "$working"

# The tested image is a clean ext4 filesystem with shared_blocks. Unsharing
# every deduplicated file exceeds the fixed 760 MiB partition capacity. Keep
# the existing payload intact, add only our new profile file, and check the
# *whole* private image before and after editing. debugfs writes here never
# overwrite any shared file blocks: our profile file is new, and the optional
# composer init rc is removed/recreated as a new inode before writing.
e2fsck -fn "$working" >"$tmp/base-fsck.log" 2>&1 || {
  cat "$tmp/base-fsck.log" >&2
  exit 1
}

# The tested image has no vendor task_profiles.json; retain other definitions
# when the helper is adapted to a compatible vendor image in future.
debugfs -R "dump /etc/task_profiles.json $tmp/original.json" "$working" >"$tmp/dump.log" 2>&1 || true
python3 - "$tmp/original.json" "$tmp/override.json" <<'PY'
import json
from pathlib import Path
import sys

original, output = map(Path, sys.argv[1:])
doc = json.loads(original.read_text()) if original.is_file() and original.stat().st_size else {"Profiles": []}
profiles = doc.setdefault("Profiles", [])
if not isinstance(profiles, list):
    raise SystemExit("unexpected vendor task profiles format")

for name in ("SFMainPolicy", "SFRenderEnginePolicy"):
    replacement = {
        "Name": name,
        "Actions": [{
            "Name": "JoinCgroup",
            "Params": {"Controller": "cpuset", "Path": "foreground"},
        }],
    }
    matches = [idx for idx, profile in enumerate(profiles) if profile.get("Name") == name]
    if len(matches) > 1:
        raise SystemExit(f"duplicate existing vendor profile: {name}")
    if matches:
        actions = profiles[matches[0]].get("Actions")
        if actions not in (replacement["Actions"], [{
            "Name": "JoinCgroup",
            "Params": {"Controller": "cpuset", "Path": "system-background"},
        }]):
            raise SystemExit(f"refusing to replace unfamiliar existing profile: {name}")
        profiles[matches[0]] = replacement
    else:
        profiles.append(replacement)

output.write_text(json.dumps(doc, indent=2) + "\n")
PY

cat >"$tmp/edit.debugfs" <<EOF
EOF
if [[ -s $tmp/original.json ]]; then
  printf 'rm /etc/task_profiles.json\n' >>"$tmp/edit.debugfs"
fi
cat >>"$tmp/edit.debugfs" <<EOF
write $tmp/override.json /etc/task_profiles.json
ea_set /etc/task_profiles.json security.selinux u:object_r:vendor_configs_file:s0
EOF

if (( composer )); then
  rc=/etc/init/vendor.qti.hardware.display.composer-service.rc
  debugfs -R "dump $rc $tmp/composer.original.rc" "$working" >"$tmp/composer.dump.log" 2>&1
  python3 - "$tmp/composer.original.rc" "$tmp/composer.rc" <<'PY'
from pathlib import Path
import sys

source, dest = map(Path, sys.argv[1:])
text = source.read_text()
old = "    writepid /dev/cpuset/system-background/tasks"
if text.count(old) != 1:
    raise SystemExit("expected one composer cpuset assignment; refusing unknown init layout")
dest.write_text(text.replace(old, "    writepid /dev/cpuset/foreground/tasks"))
PY
  cat >>"$tmp/edit.debugfs" <<EOF
rm $rc
write $tmp/composer.rc $rc
ea_set $rc security.selinux u:object_r:vendor_configs_file:s0
EOF
fi

debugfs -w -f "$tmp/edit.debugfs" "$working" >"$tmp/edit.log" 2>&1
debugfs -R "dump /etc/task_profiles.json $tmp/verify.json" "$working" >"$tmp/verify.log" 2>&1
cmp -s "$tmp/override.json" "$tmp/verify.json" || {
  cat "$tmp/edit.log" >&2
  echo 'failed to verify vendor task profile payload' >&2
  exit 1
}
if (( composer )); then
  debugfs -R "dump /etc/init/vendor.qti.hardware.display.composer-service.rc $tmp/composer.verify.rc" "$working" >/dev/null 2>&1
  cmp -s "$tmp/composer.rc" "$tmp/composer.verify.rc" || {
    echo 'failed to verify vendor composer init rc' >&2
    exit 1
  }
fi

e2fsck -fn "$working" >"$tmp/final-fsck.log" 2>&1 || {
  cat "$tmp/final-fsck.log" >&2
  exit 1
}
mv -- "$working" "$out"
echo "input SHA256 $expected"
sha256sum -- "$out"
echo "SurfaceFlinger profiles: foreground (0-7 on tested P11)"
echo "composer: $([[ $composer -eq 1 ]] && echo foreground || echo unchanged)"
echo 'No device was flashed. Validate the image and test before publishing a release.'
