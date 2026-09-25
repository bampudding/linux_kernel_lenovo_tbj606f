#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only
# Diagnostic ONLY: switch exactly one SurfaceFlinger fence-latching policy
# from vendor's `Always` to the Android 13+ safer `AutoSingleLayer` mode.
# Does not flash or change the currently attached device.
set -euo pipefail
usage() {
  echo "Usage: make-safe-fence-vendor.sh VERIFIED_HYBRID_V5_VENDOR.img NEW_OUTPUT.img" >&2
  echo 'The original verified hybrid vendor is never modified. Experimental output only.' >&2
  exit 2
}
[[ $# -eq 2 ]] || usage
base=$1
out=$2
for t in sha256sum debugfs e2fsck python3 mktemp cp cmp;do command -v "$t" >/dev/null || { echo "required: $t" >&2;exit 1;};done
[[ -f "$base" && ! -e "$out" && -d "$(dirname -- "$out")" ]] || usage
expected=b0cca3012109d045122dccdbd22f2505327ec7550576daa37d4bde643a39d3dd
actual=$(sha256sum -- "$base");actual=${actual%% *}
[[ $actual == "$expected" ]] || { echo "Unexpected base vendor: $actual" >&2;exit 1; }
tmp=$(mktemp -d "${TMPDIR:-/root}/tbj606f-safe-fence.XXXXXXXX")
working="$out.partial.$$"
cleanup() { rm -f -- "$working";rm -rf -- "$tmp"; }
trap cleanup EXIT
# Validate the original *before* copying, so no damaged partition is derived.
e2fsck -fn "$base" >"$tmp/original-fsck.txt" 2>&1 || { cat "$tmp/original-fsck.txt" >&2;exit 1; }
debugfs -R "dump /build.prop $tmp/original.prop" "$base" >/dev/null 2>&1
python3 - "$tmp/original.prop" "$tmp/patched.prop" <<'PY'
import pathlib,sys
original, output=map(pathlib.Path,sys.argv[1:])
p=original.read_bytes()
old=b'debug.sf.latch_unsignaled=1\n'
assert p.count(old)==1,'expected exactly one Always mode setting'
assert b'debug.sf.auto_latch_unsignaled=' not in p,'refusing a second existing mode setting'
# This is one logical policy change, not a GPU clock or gralloc/UBWC tweak.
out=p.replace(old,b'debug.sf.latch_unsignaled=0\ndebug.sf.auto_latch_unsignaled=1\n')
assert out!=p
output.write_bytes(out)
PY
cp --reflink=auto -- "$base" "$working"
# shared_blocks means do not overwrite a deduplicated original in place.
# Remove the build.prop inode and create a fresh inode with the same path,
# ownership, mode 0600 and SELinux security label as the verified base.
cat >"$tmp/edit.debugfs" <<EOF
rm /build.prop
write $tmp/patched.prop /build.prop
sif /build.prop mode 0100600
ea_set /build.prop security.selinux u:object_r:vendor_file:s0
EOF
debugfs -w -f "$tmp/edit.debugfs" "$working" >"$tmp/edit.log" 2>&1
if grep -Ei 'error|not found|invalid' "$tmp/edit.log";then echo 'debugfs reported unexpected output' >&2;exit 1;fi
debugfs -R "dump /build.prop $tmp/verified.prop" "$working" >"$tmp/verify.log" 2>&1
cmp -- "$tmp/patched.prop" "$tmp/verified.prop" || { echo 'modified build.prop differs' >&2;exit 1; }
debugfs -R 'stat /build.prop' "$working" >"$tmp/stat.txt" 2>&1
grep -q 'Mode:  0600' "$tmp/stat.txt" || { cat "$tmp/stat.txt" >&2;exit 1; }
grep -q 'User:     0   Group:     0' "$tmp/stat.txt" || { cat "$tmp/stat.txt" >&2;exit 1; }
grep -q 'u:object_r:vendor_file:s0' "$tmp/stat.txt" || { cat "$tmp/stat.txt" >&2;exit 1; }
e2fsck -fn "$working" >"$tmp/final-fsck.txt" 2>&1 || { cat "$tmp/final-fsck.txt" >&2;exit 1; }
[[ $(stat -c %s -- "$base") == "$(stat -c %s -- "$working")" ]] || { echo 'image size changed' >&2;exit 1; }
# Verify original source is still same byte-for-byte.
post=$(sha256sum -- "$base");post=${post%% *}
[[ $post == "$expected" ]] || { echo 'Original source changed unexpectedly' >&2;exit 1; }
mv -- "$working" "$out"
echo 'PASS: original unchanged, new output read-only filesystem check, exact config/mode/SELinux verified.'
sha256sum -- "$out"
echo 'NOT FLASHED: Do not call this validated as fixing jank/color until controlled device A/B and recovery.'
