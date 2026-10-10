#!/bin/sh
# SPDX-License-Identifier: GPL-2.0-only
set -eu

SELF_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
: "${KERNEL_SRC:?set KERNEL_SRC to the TB-J606F kernel source tree}"
: "${KERNEL_OUT:?set KERNEL_OUT to the matching kernel build output}"
: "${CLANG_DIR:?set CLANG_DIR to the clang bin directory}"
: "${CROSS_DIR:?set CROSS_DIR to the aarch64-linux-android bin directory}"

PATH="$CLANG_DIR:$CROSS_DIR:$PATH" \
make -C "$KERNEL_SRC" \
	O="$KERNEL_OUT" \
	M="$SELF_DIR" \
	ARCH=arm64 \
	CC="$CLANG_DIR/clang" \
	CROSS_COMPILE=aarch64-linux-android- \
	CLANG_TRIPLE=aarch64-linux-gnu- \
	modules

printf 'built: %s\n' "$SELF_DIR/p11_audio_compat.ko"
modinfo "$SELF_DIR/p11_audio_compat.ko" | grep -E '^(name|vermagic|depends|signer):' || true
modprobe --dump-modversions "$SELF_DIR/p11_audio_compat.ko" | grep module_layout || true
