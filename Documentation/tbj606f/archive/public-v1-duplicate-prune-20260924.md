# Confirmed public-v1 duplicate removal — 2026-09-24

Nine byte-identical public-v1 extraction files were deleted from:

`/root/HDD/user0/P11/releases/github/tbj606f-a16-zui14-public-v1/bundle/`

Each current file matched SHA256 of its separate surviving parent-file and
an exact member of the published v1 tar.gz. The local tar SHA256 matched
GitHub's current release digest. Eight files also matched GitHub's separately
published assets; README.txt is part of the published tar. Historical manifest
hashes were checked before each removal, with a final survivor recheck.

- 9 duplicate files removed, 49,102,114 logical bytes.
- 49,045,504 allocated file bytes released, plus the empty 4 KiB directory.
- Nine canonical same-name files, v1 tar, release notes and checksums preserved.
- All other old releases, failed-boot logs, recoveries, firmware, the current
  scroll-performance experiment and its source were untouched.
- No ADB, Fastboot, flashing, or device change.

[Full file-by-file SHA256 and survivor ledger](public-v1-duplicate-prune-20260924.json).
The prior artifact manifest and cleanup readiness JSON are frozen pre-deletion
snapshots, not current filesystem claims. This ledger records the newer state.
No other old-work path has yet passed the case-by-case deletion gate.
