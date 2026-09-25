# Historical TB-J606F experiments: source-first reproducibility

The historical archive is a **Git source/branch management task**, not a
requirement to attach every old object file or boot image to a release.
Stable Android 16/ZUI14 keeps the existing flash-kit ZIP and its validated
reconstruction/install process. Earlier branches can be experimental or
unbootable; only the exact matching commit, configuration, toolchain and
relevant OEM inputs together support a repeatable build.

- [Git branches](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/branches)
  and [existing source milestone matrix](release-matrix.md) are primary.
- [14 old build output folders](legacy-build-recipes-20260925.json) have saved
  `.config` and `vmlinux` hashes. Seven have *name-only candidate branches*;
  seven have no established branch association. None of these 14 has a
  newly demonstrated clean byte-identical rebuild, so don't discard their
  saved `.config` or original unique inputs on the strength of this map.
- For the stable source checkout, `tools/tbj606f/build-kernel.sh` documents
  required toolchain paths and builds `Image dtbs` in `KERNEL_OUT`.
- For the stable boot, `tools/tbj606f/reconstruct-stable-boot.py` takes the
  exact user-supplied ZUI12 OEM boot and the matching kernel Image.
- For the stable hybrid vendor, `tools/tbj606f/make-hybrid-vendor.sh` uses
  the user-supplied ZUI14 vendor and ZUI12 modules; proprietary inputs are
  **not** part of the Git source tree.
- `AGENTS.md` at repository root gives future agents explicit instructions
  to prioritize source, recipes and Git refs, not redundant binary uploads.

The 37 tagged historic kernel archives and 47 loose GPL artifacts already
published remain available as recovery evidence. An additional legacy build
output release was started before this policy clarification and stopped; it
is not the canonical way to track future experiments. No active performance
work or current build environment was changed for this source-first update.
