# TB-J606F optional Rouleur compatibility module

The ZUI12 Bengal ASoC machine module contains unresolved link-time references
to `rouleur_info_create_codec_entry()` and `rouleur_mbhc_hs_detect()` even when
the board uses the WCD937x/Bolero codec path.

TB-J606F's device tree selects WCD937x/Bolero. The Rouleur runtime branches
are therefore not used on this tablet, but the symbols still have to exist for
`machine_dlkm` to load. This small GPL module exports inert implementations
that return success.

It must be built against the exact kernel build output used for the boot image.
For the Android 16/ZUI14 compatibility baseline the expected `module_layout`
CRC is `0xd97eab43`.

Example:

```sh
export KERNEL_SRC=/path/to/linux_kernel_lenovo_tbj606f
export KERNEL_OUT=/path/to/kernel-out
export CLANG_DIR=/path/to/clang/bin
export CROSS_DIR=/path/to/aarch64-linux-android-4.9/bin
./tools/tbj606f/audio-compat/build.sh
```

Do not use this shim on a device whose DT actually selects the Rouleur codec.
