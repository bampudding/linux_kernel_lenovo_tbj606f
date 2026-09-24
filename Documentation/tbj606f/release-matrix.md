# TB-J606F release matrix

This file is the deletion checklist for legacy workspace cleanup.

## Current supported release

| Release | Status | Purpose |
|---|---|---|
| tbj606f-a16-zui14-public-v2 | stable | Android 16 EROFS + ZUI14 vendor hybrid kernel release |

## Development lineage

| Stage | Git reference | Preserved items |
|---|---|---|
| Original Lenovo/ZUI12 kernel baseline | upstream history | original GPL kernel history |
| EROFS bring-up | `tbj606f-a16-zui14-public-v1` lineage | EROFS backports, LZ4 changes, configs |
| Android 16 runtime validation | `tbj606f-a16-zui14-public-v1` | Image, config, Module.symvers, hashes |
| ZUI14 vendor compatibility | `tbj606f-a16-zui14-public-v2` | hybrid vendor scripts, installation docs |

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
