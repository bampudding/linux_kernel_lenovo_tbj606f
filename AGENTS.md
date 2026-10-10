# TB-J606F kernel repository agent instructions

## Intent and preservation policy

This repository is **source-first**. Preserve an old kernel experiment as a
Git branch or immutable commit plus the actual `.config`/defconfig, relevant
patches, toolchain identity and exact build command. A Git tag or an old
binary alone does not prove a bit-for-bit rebuild. Never invent a matching
source commit from a similarly named HDD build folder; record unknowns.

The latest Android 16 / ZUI14 stable release is different: keep the existing
single verified flash-kit ZIP, its checksums, OEM-input hash guards, installer
and stable release tag. Do not replace that user-facing release with a pile
of historical binary assets. New experimental work is not automatically a
stable release. No historical boot-success claims without dated device tests.

## Scope and active work

The current performance-improvement source/worktrees, ongoing kernel builds,
measurements and device are outside legacy archival or cleanup tasks. Do not
traverse/modify the current perf experiment folder for archival purposes,
reset branches, touch the device, flash, delete, or repack a live boot image.
Old `workspace/` is not automatically an abandoned build tree; establish its
status before using it. Never delete original HDD artifacts solely because
source commits exist on GitHub.

## Build a historical experiment

1. Locate the branch or commit in
   `Documentation/tbj606f/archive/release-matrix.md` and the Git ref list.
   `legacy-build-recipes-20260925.json` records additional old build folders
   and **name-only candidates**, not proven build associations.
2. Obtain the saved `.config` and verify its SHA256 against the recorded
   archive. Historical toolchains must be identified rather than substituted
   silently; source+config without the correct toolchain is not an exact
   binary-reproducibility guarantee.
3. Build outside the source tree and current build directory. On the stable
   checkout the helper is `tools/tbj606f/build-kernel.sh` with `KERNEL_OUT`,
   `CLANG_DIR`, `CROSS_DIR`, optional `DEFCONFIG`, `CONFIG_FRAGMENT` and `JOBS`.
   **Do not use its default Android16 fragment for an older branch unless the
   old recipe requires it.** For archived exact `.config`, initialize the
   separate output with that file and use the matching historical toolchain.
4. Compare `Image`, `.config`, `Module.symvers` and optional `vmlinux` hashes
   to the historical record. If different, document the difference rather
   than claiming byte-identical reproduction. Mark unbootable experiments as
   unbootable/unknown, never as a flashable stable build.

## OEM-dependent variants and installation

If a branch needs hybrid ZUI14 vendor, ZUI12 audio/Wi-Fi modules, a different
DTB/ramdisk or a special installation step, document the exact version,
source and checksum of the user's own input. Use the existing
`tools/tbj606f/make-hybrid-vendor.sh`, `reconstruct-stable-boot.py`, and
`FLASH-ZIP-README.md` when applicable. Do not add proprietary firmware,
private runtime logs or device identifiers to public Git history. A plain
kernel-source branch needs no bespoke installer if it uses the same standard
build path. A variant-specific installer must have dry-run and exact device
checks before any flashing instructions.

## Publishing and audit

Push branch/commit and its recipe first. Create a release asset only for a
stable tested version, a genuinely required install/vendor dependency, or a
user-requested recovery artifact. Keep old public releases intact, but do
not keep creating redundant historic binary releases. Append a dated audit
rather than rewriting previous audit snapshots. Verify remote refs and
asset SHA256; do not mistake upload success for reproduction success.
