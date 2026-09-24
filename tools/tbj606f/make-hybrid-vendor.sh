#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only
set -euo pipefail

usage() {
	cat <<'EOF'
Usage:
  make-hybrid-vendor.sh BASE_VENDOR ZUI12_MODULE_DIR P11_AUDIO_COMPAT OUTPUT

Builds the TB-J606F Android 16/ZUI14 hybrid vendor image used by this tree.
No Lenovo binary is distributed by this repository. Supply modules extracted
from your own ZUI12/ZUI14 firmware images.

Requirements: debugfs, e2fsck, modinfo, modprobe, python3, sha256sum
EOF
}

[ "$#" -eq 4 ] || { usage >&2; exit 2; }
BASE=$1
Z12=$2
COMPAT=$3
OUT=$4

for tool in debugfs e2fsck modinfo modprobe python3 sha256sum; do
	command -v "$tool" >/dev/null || { echo "missing tool: $tool" >&2; exit 1; }
done
[ -f "$BASE" ] || { echo "missing base vendor: $BASE" >&2; exit 1; }
[ -d "$Z12" ] || { echo "missing ZUI12 module directory: $Z12" >&2; exit 1; }
[ -f "$COMPAT" ] || { echo "missing compat module: $COMPAT" >&2; exit 1; }

audio_modules=(
	audio_apr.ko
	audio_aw88258_4pa.ko
	audio_bolero_cdc.ko
	audio_machine_bengal.ko
	audio_mbhc.ko
	audio_native.ko
	audio_pinctrl_lpi.ko
	audio_platform.ko
	audio_pm2250_spmi.ko
	audio_q6.ko
	audio_q6_notifier.ko
	audio_q6_pdr.ko
	audio_rx_macro.ko
	audio_snd_event.ko
	audio_stub.ko
	audio_swr.ko
	audio_swr_ctrl.ko
	audio_tx_macro.ko
	audio_usf.ko
	audio_va_macro.ko
	audio_wcd937x.ko
	audio_wcd937x_slave.ko
	audio_wcd9xxx.ko
	audio_wcd_core.ko
	audio_wsa881x_analog.ko
)

for module in "${audio_modules[@]}" qca_cld3_wlan.ko; do
	[ -f "$Z12/$module" ] || { echo "missing required ZUI12 module: $module" >&2; exit 1; }
done

module_layout_crc() {
	modprobe --dump-modversions "$1" | awk '$2 == "module_layout" { print $1 }'
}

abi_crc=$(module_layout_crc "$Z12/qca_cld3_wlan.ko")
compat_crc=$(module_layout_crc "$COMPAT")
[ -n "$abi_crc" ] || { echo "cannot read ZUI12 module_layout CRC" >&2; exit 1; }
[ "$compat_crc" = "$abi_crc" ] || {
	echo "compat module ABI mismatch: compat=$compat_crc vendor=$abi_crc" >&2
	exit 1
}
for module in "${audio_modules[@]}"; do
	crc=$(module_layout_crc "$Z12/$module")
	[ "$crc" = "$abi_crc" ] || {
		echo "module ABI mismatch: $module has $crc, expected $abi_crc" >&2
		exit 1
	}
done

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cp --reflink=auto "$BASE" "$OUT"

cmdfile="$tmp/debugfs-replace.cmd"
: >"$cmdfile"
for module in "${audio_modules[@]}" qca_cld3_wlan.ko; do
	cat >>"$cmdfile" <<EOF
rm /lib/modules/$module
write $Z12/$module /lib/modules/$module
ea_set /lib/modules/$module security.selinux u:object_r:vendor_file:s0
EOF
done
cat >>"$cmdfile" <<EOF
write $COMPAT /lib/modules/p11_audio_compat.ko
ea_set /lib/modules/p11_audio_compat.ko security.selinux u:object_r:vendor_file:s0
EOF
debugfs -w -f "$cmdfile" "$OUT" >/dev/null

debugfs -R "dump /lib/modules/modules.load $tmp/modules.load" "$OUT" >/dev/null 2>&1
debugfs -R "dump /etc/init/hw/init.target.rc $tmp/init.target.rc" "$OUT" >/dev/null 2>&1

python3 - "$tmp/modules.load" "$tmp/init.target.rc" <<'PY'
from pathlib import Path
import sys

load_path = Path(sys.argv[1])
init_path = Path(sys.argv[2])

excluded_files = {
    "audio_adsp_loader.ko",
    "audio_rouleur.ko",
    "audio_rouleur_slave.ko",
    "p11_audio_compat.ko",
}
lines = []
seen = set()
for line in load_path.read_text().splitlines():
    line = line.strip()
    if not line or line in excluded_files or line in seen:
        continue
    seen.add(line)
    lines.append(line)
try:
    idx = lines.index("audio_machine_bengal.ko")
except ValueError:
    raise SystemExit("audio_machine_bengal.ko not present in modules.load")
lines.insert(idx, "p11_audio_compat.ko")
load_path.write_text("\n".join(lines) + "\n")

excluded_names = {
    "audio_adsp_loader",
    "audio_rouleur",
    "audio_rouleur_slave",
    "p11_audio_compat",
}
out = []
changed = False
for line in init_path.read_text().splitlines():
    if "/vendor/bin/modprobe -a -d /vendor/lib/modules" not in line:
        out.append(line)
        continue
    prefix, rest = line.split("/vendor/lib/modules", 1)
    names = [n for n in rest.split() if n not in excluded_names]
    if "audio_machine_bengal" not in names:
        raise SystemExit("audio_machine_bengal not present in early-init modprobe")
    names.insert(names.index("audio_machine_bengal"), "p11_audio_compat")
    out.append(prefix + "/vendor/lib/modules " + " ".join(names))
    changed = True
if not changed:
    raise SystemExit("early-init vendor modprobe command not found")
init_path.write_text("\n".join(out) + "\n")
PY

dump="$tmp/module-dump"
mkdir -p "$dump"
debugfs -R "rdump /lib/modules $dump" "$OUT" >/dev/null 2>&1

python3 - "$dump/modules" "$tmp/modules.dep" <<'PY'
from pathlib import Path
import subprocess
import sys

root = Path(sys.argv[1])
out = Path(sys.argv[2])
files = sorted(root.glob("*.ko"))
name_to_file = {}
meta = {}
for path in files:
    def field(name):
        try:
            return subprocess.check_output(
                ["modinfo", "-F", name, str(path)],
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
        except subprocess.CalledProcessError:
            return ""
    name = field("name")
    deps = [x for x in field("depends").split(",") if x]
    if name:
        name_to_file[name] = path.name
    meta[path.name] = deps

with out.open("w") as fp:
    for filename in sorted(meta):
        deps = [
            "/vendor/lib/modules/" + name_to_file[d]
            for d in meta[filename]
            if d in name_to_file
        ]
        suffix = (" " + " ".join(deps)) if deps else ""
        fp.write(f"/vendor/lib/modules/{filename}:{suffix}\n")
PY

cat >"$tmp/debugfs-metadata.cmd" <<EOF
rm /lib/modules/modules.load
write $tmp/modules.load /lib/modules/modules.load
ea_set /lib/modules/modules.load security.selinux u:object_r:vendor_file:s0
rm /lib/modules/modules.dep
write $tmp/modules.dep /lib/modules/modules.dep
ea_set /lib/modules/modules.dep security.selinux u:object_r:vendor_file:s0
rm /etc/init/hw/init.target.rc
write $tmp/init.target.rc /etc/init/hw/init.target.rc
ea_set /etc/init/hw/init.target.rc security.selinux u:object_r:vendor_configs_file:s0
EOF
debugfs -w -f "$tmp/debugfs-metadata.cmd" "$OUT" >/dev/null

echo "module_layout CRC: $abi_crc"
echo "machine dependency line:"
debugfs -R "cat /lib/modules/modules.dep" "$OUT" 2>/dev/null |
	grep '/audio_machine_bengal.ko:' || true
set +e
e2fsck -fy "$OUT"
fsck_rc=$?
set -e
if [ "$fsck_rc" -gt 1 ]; then
	exit "$fsck_rc"
fi
e2fsck -fn "$OUT"
sha256sum "$OUT"
