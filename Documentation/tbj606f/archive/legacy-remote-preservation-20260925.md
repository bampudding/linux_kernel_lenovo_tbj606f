# TB-J606F legacy remote preservation — 2026-09-25

**Public Linux kernel files and source references archived. Full HDD deletion is NOT yet safe.**

## Verified public result

| Scope | Completed | Evidence |
|---|---:|---|
| Original remote branches | 65 | Own GH repo; includes newly recovered early lineage19.1 source branch |
| Original remote tags (including new archival tag) | 62 | Git refs; does not alter pre-existing tags |
| Source-only historical release tags with exact HDD stage | 37/54 | 37 source-tag GitHub releases augmented with `Image`, `kernel.config`, `Module.symvers`, checksum and source commit tarball |
| Legacy loose release/experiment groups assessed | 63 | Original 43 unmatched release dirs + 20 experiment dirs; most recent stable folder and current performance excluded |
| Loose groups with GPL kernel/code assets published | 47 | [Archival GitHub Release](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/tbj606f-legacy-gpl-stages-20260925) |
| Groups without independently redistributable archive | 16 | Original contents remain on HDD; no false empty archives |
| New external archive bytes (37 + 47) | 1,049,596,223 | GitHub SHA256/size verified for all 84 tar.gz assets |

Historical baseline source: [archive/lineage19.1-baseline-20260914](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/tree/archive/lineage19.1-baseline-20260914), exact commit `23f0307a69093cf287335a09ef88d73870e9120a`.

The 37 source-tag release notes were appended with a dated **supplemental**-asset notice, preserving the original notes and source commits. Recovered binaries should not be mistaken for new clean rebuilds or newly successful device tests. The 47 untagged artifacts are versioned by their original named HDD directory in one archival GitHub release, not assigned speculative source commits. [Full public inventory and per-asset SHA256](legacy-remote-preservation-20260925.json).

## Scope not safe to delete or upload in public kernel repository

- Original Lenovo/third-party `boot.img` payloads and modifications, stock recovery, hybrid vendor and proprietary firmware; excluded from public release bytes. Historical tagged boots alone are 37 distinct images totaling 3,724,541,952 bytes; GitHub kernel tarballs do **not** preserve those bytes.
- 22 loose old boot images in HDD `releases/`, old `experiments/` boots/ramdisks, vendor and product system images, old runtime/dmesg/logcat evidence and the newest stable hybrid inputs.
- Large unmanifested legacy trees: `build-archive/`, `dev-archive/`, `workspace/`, `p11-kernel-tests/`, `reference/`, `scratch-archive/` and the full firmware tree. Prior independent stat-only scan found ~526,532 old regular files without per-file archival hashes.
- Three locally unpushed diagnostic branches beginning `perf/` are excluded as ongoing performance work, not missing historical release branches.
- `/root/HDD` spans RAID0 on sdb and sdc, with **no independent disk redundancy**. Duplicates or hardlinks on it are not backups.

**No additional HDD files were deleted in this publication run.** To retire the old HDD in full, preserve and restore-check all excluded original byte sequences to an independent owned drive/private encrypted archive. Also retain exact toolchains/configs when bit-for-bit historical builds matter. Do not assume a Git source tag itself recreates OEM-containing old boot images.

## Restore public kernel files

For a named tagged release, download `tbj606f-legacy-kernel-<release-tag>.tar.gz` from that existing GitHub release; check the asset SHA in the JSON and embedded `SHA256SUMS`, then extract `Image`, `Module.symvers` and `kernel.config`. The source is the same existing Git tag/commit. For an untagged former folder, use the asset `tbj606f-old-releases-<folder>.tar.gz` or `tbj606f-old-experiments-<folder>.tar.gz` on the archival release; its `BUILD-PROVENANCE.json` explicitly records source as unknown. Neither package is a universal flash ZIP.

## Relevant scripts and dated snapshots

- `tools/tbj606f/publish-legacy-kernel-assets.py` — stage-complete source tag packaging, exact SHA provenance and safe idempotent upload.
- `tools/tbj606f/publish-legacy-untagged-artifacts.py` — loose historical GPL stage packaging, 63-group classification and current-work exclusion.
- `tools/tbj606f/annotate-legacy-release-assets.py` — append explanatory dated addenda without overwriting historical release notes.
- Existing `release-reproducibility-audit.json` is an **earlier snapshot** of before 2026-09-25 supplementary artifacts and should not be used as current GitHub asset count.
