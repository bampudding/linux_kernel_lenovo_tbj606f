# TB-J606F release matrix

This file is the deletion checklist for legacy workspace cleanup.

## Public packages and source checkpoints

| Release | Source and artifact status | Purpose |
|---|---|---|
| `tbj606f-a16-zui14-public-v1` | Tested kernel binary bundle; kernel source checkpoint `7124b9c09a` | Android 16 EROFS + ZUI14 hybrid kernel, config and audio compatibility module |
| `tbj606f-a16-zui14-public-v2` | Installer/documents attached to release; the v2 **tag predates `install.sh`** | Historical deployment-package checkpoint; use the later tagged source for a reproducible script checkout |
| `tbj606f-a16-zui14-public-v3` | Source-matched installer, tested v1 kernel bytes and archive metadata | Historical complete tarball + components |
| `tbj606f-a16-zui14-public-v4` | One ZIP with tested kernel, compatibility module, installer, repacking tools, checksum validator and user guide | Historical ZIP requiring an already validated boot backup |
| `tbj606f-a16-zui14-public-v5` | v4 flash ZIP plus stock ZUI12 12.0.519 boot → exact stable hybrid boot reconstruction | Preferred non-proprietary first-installation ZIP |

## Development lineage

| Stage | Git reference | Preserved items |
|---|---|---|
| Original Lenovo/ZUI12 kernel baseline | upstream history | original GPL kernel history |
| EROFS compressed-image groundwork | `zui12-post157-erofs-lineage23.2-built-20260922` | EROFS backports and build milestone |
| LZ4 v1.8.3 decoder backport | `tbj606f-erofs-lz4-v183-20260924` | Historical source snapshot, diff metadata and hashes; not itself a complete boot-success claim |
| Android 16 runtime validation | `zui12-post157-erofs-lineage23.2-runtime-tested-20260922` | EROFS boot milestone source snapshot, logs indexed on HDD |
| ADSP/ZUI14 compatibility | `tbj606f-a16-zui14-kernel-stable-20260924` | Native ADSP loader and stable hybrid kernel checkpoint |
| Published tested binary | `tbj606f-a16-zui14-public-v1` | Image, config, Module.symvers, hashes |
| Installer publication | `tbj606f-a16-zui14-public-v3` | Tagged installer source, instructions, verified binary inputs and preservation metadata |

## Artifact retention policy

Every milestone release must retain:

- kernel source commit
- kernel `.config`
- `Image` or reproducible build instructions
- `Module.symvers` when external modules are involved
- validation logs
- SHA256 manifest
- hashes of proprietary images that cannot be redistributed

## Proprietary files

The following are never uploaded as public release assets unless licensing
allows redistribution:

- Lenovo boot images containing proprietary ramdisk content
- vendor images
- modem/DSP firmware
- extracted proprietary modules

Their SHA256 identities belong in release notes/manifests.

## Cleanup rule

A local legacy directory may be removed only after:

1. its commit exists on the public repository;
2. its tag exists;
3. its release manifest exists;
4. required binary/debug artifacts are attached or reproducible.

The exact existing bytes must also be present in an independently retained copy
whose SHA256 matches `archive/hdd-artifact-manifest.json`. A GitHub tag or a
checksum alone is insufficient to justify deleting local proprietary images
or unreleased diagnostics. See `archive/README.md`.
