#!/bin/sh
# SPDX-License-Identifier: GPL-2.0-only
set -eu

SELF=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
KERNEL_SRC=${KERNEL_SRC:-$SELF}
: "${KERNEL_OUT:?set KERNEL_OUT to an SSD build directory}"
: "${CLANG_DIR:?set CLANG_DIR to the clang bin directory}"
: "${CROSS_DIR:?set CROSS_DIR to the aarch64-linux-android bin directory}"
DEFCONFIG=${DEFCONFIG:-vendor/bengal-perf_defconfig}
JOBS=${JOBS:-$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 8)}

mkdir -p "$KERNEL_OUT"
PATH="$CLANG_DIR:$CROSS_DIR:$PATH" \
make -C "$KERNEL_SRC" O="$KERNEL_OUT" ARCH=arm64 \
	CC="$CLANG_DIR/clang" \
	CROSS_COMPILE=aarch64-linux-android- \
	CLANG_TRIPLE=aarch64-linux-gnu- \
	"$DEFCONFIG"

PATH="$CLANG_DIR:$CROSS_DIR:$PATH" \
make -C "$KERNEL_SRC" O="$KERNEL_OUT" ARCH=arm64 \
	CC="$CLANG_DIR/clang" \
	CROSS_COMPILE=aarch64-linux-android- \
	CLANG_TRIPLE=aarch64-linux-gnu- \
	-j"$JOBS" Image dtbs

IMAGE="$KERNEL_OUT/arch/arm64/boot/Image"
test -s "$IMAGE"
sha256sum "$IMAGE"
strings "$IMAGE" | grep -m1 'Linux version 4.19.157' || true
