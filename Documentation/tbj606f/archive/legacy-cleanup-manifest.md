# TB-J606F Legacy Cleanup Manifest

Preserve before HDD cleanup:
- Git history and tags
- GitHub Releases
- kernel Image/Image.gz
- configs and Module.symvers
- release checksums
- firmware provenance
- runtime logs

Verify before deletion:
- boot provenance
- vendor reconstruction inputs
- referenced experiments

The full SHA256/size/association records are in `hdd-artifact-manifest.json`;
published GitHub asset digests and tag source commits are in
`github-release-catalog.json`. See `README.md` for scope and exclusions.

Every candidate for removal needs a second independently retained copy of its
bytes, checked against the manifest. A matching hash in this repository is only
an identity record, not a backup. No experiment, firmware input, or release
artifact is approved for deletion by this document.
