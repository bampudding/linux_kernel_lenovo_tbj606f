#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Reproduce the tested hybrid boot from an owner's exact ZUI12 12.0.519 boot.

This regenerates the EROFS ramdisk from the caller's OEM boot and inserts the
validated redistributable kernel; it never includes or publishes OEM bytes.
"""
import argparse
import gzip
import hashlib
import pathlib
import shlex
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent
STOCK_SHA = 'd4e86ef850d4109a8b2b7a87bec82dd2c60cc68a6f0e3709e7bec0f74ff982d8'
IMAGE_SHA = 'af0b7b6b81c4f6ba3c5c2fbb044972a1bf502453ec19effa6d3664c094fdb2f8'
BOOT_SHA = '93f9e9518fc9a20691ab0b3579b0c628e23522674e827fc57b8867945aedd635'
RAMDISK_SHA = 'c5d9c256322550b3eb542046539e1aa2ac996f59c57e445cdbcc8dad5db99ce0'
DTB_SHA = '630d4d325b35c9f8975000d1945c3ee2bfbed6f18d250b64ee09c4ffa5c8b07a'
ORIGINAL = b'system                                                  /system                   ext4    ro,barrier=1,discard                                 wait,slotselect,avb=vbmeta_system,logical,first_stage_mount,avb_keys=/avb/q-gsi.avbpubkey:/avb/r-gsi.avbpubkey:/avb/s-gsi.avbpubkey'
EROFS = b'system                                                  /system                   erofs   ro                                                   wait,slotselect,logical,first_stage_mount'
RAMOOPS = ' ramoops.mem_address=0x64000000 ramoops.mem_size=0x100000 ramoops.record_size=0x40000 ramoops.console_size=0x40000 ramoops.ftrace_size=0 ramoops.pmsg_size=0x20000 ramoops.dump_oops=1'
ORDER = ('.', 'sys', 'proc', 'mnt', 'init', 'fstab.qcom', 'dev', 'debug_ramdisk',
         'avb', 'avb/s-gsi.avbpubkey', 'avb/r-gsi.avbpubkey',
         'avb/q-gsi.avbpubkey', 'apex', 'TRAILER!!!')
INODES = {name: 292445 + index for index, name in enumerate(('.', 'apex', 'avb',
          'avb/q-gsi.avbpubkey', 'avb/r-gsi.avbpubkey', 'avb/s-gsi.avbpubkey',
          'debug_ramdisk', 'dev', 'fstab.qcom', 'init', 'mnt', 'proc', 'sys'))}


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def read_newc(data):
    result = {}
    position = 0
    while position < len(data):
        header = data[position:position + 110]
        if len(header) != 110 or header[:6] != b'070701':
            raise ValueError('unexpected ramdisk archive format')
        fields = [int(header[6 + 8 * i:14 + 8 * i], 16) for i in range(13)]
        size, namelen = fields[6], fields[11]
        start = position + 110
        name_bytes = data[start:start + namelen]
        if not name_bytes.endswith(b'\0'):
            raise ValueError('invalid cpio name')
        name = name_bytes[:-1].decode('utf-8')
        start = (start + namelen + 3) & ~3
        payload = data[start:start + size]
        if len(payload) != size or name in result:
            raise ValueError('invalid/duplicate cpio entry')
        result[name] = (payload, fields[1])
        position = (start + size + 3) & ~3
        if name == 'TRAILER!!!':
            return result
    raise ValueError('cpio trailer missing')


def remake_ramdisk(source):
    entries = read_newc(gzip.decompress(source))
    if set(entries) != set(ORDER) - {'.'}:
        raise ValueError('unexpected original ramdisk contents')
    old = entries['fstab.qcom'][0]
    if old.count(ORIGINAL) != 1:
        raise ValueError('original ZUI12 system fstab line missing/ambiguous')
    entries['fstab.qcom'] = (old.replace(ORIGINAL, EROFS), entries['fstab.qcom'][1])
    result = bytearray()
    for name in ORDER:
        data, mode = entries.get(name, (b'', 0o40755 if name == '.' else 0))
        if name == 'TRAILER!!!':
            inode = mode = devminor = timestamp = 0
        else:
            inode, devminor = INODES[name], 95
            timestamp = 1790070602 if name in ('.', 'avb') else 1790072989 if name == 'fstab.qcom' else 0
        isdir = name == '.' or (mode & 0o170000) == 0o040000
        nlink = 9 if name == '.' else 2 if isdir else 1
        fields = (inode, mode, 0, 0, nlink, timestamp, len(data), 0,
                  devminor, 0, 0, len(name.encode()) + 1, 0)
        result.extend(b'070701' + b''.join(f'{n:08X}'.encode() for n in fields))
        result.extend(name.encode() + b'\0')
        result.extend(b'\0' * (-len(result) % 4))
        result.extend(data)
        result.extend(b'\0' * (-len(result) % 4))
    result.extend(b'\0' * (-len(result) % 512))
    return bytes(result)


def update_option(args, name, value):
    at = args.index(name)
    args[at + 1] = value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--zui12-boot', type=pathlib.Path, required=True)
    parser.add_argument('--image', type=pathlib.Path, required=True)
    parser.add_argument('--output', type=pathlib.Path, required=True)
    opts = parser.parse_args()
    for path, expected in ((opts.zui12_boot, STOCK_SHA), (opts.image, IMAGE_SHA)):
        if not path.is_file() or sha(path) != expected:
            parser.error(f'wrong input SHA256: {path}')
    if opts.output.exists():
        parser.error('refusing to replace existing output')
    if not opts.output.parent.is_dir():
        parser.error('output directory missing')
    with tempfile.TemporaryDirectory(prefix='tbj606f-reconstruct-') as work:
        folder = pathlib.Path(work)
        result = subprocess.run([sys.executable, str(ROOT / 'unpack_bootimg.py'),
                                 '--boot_img', str(opts.zui12_boot),
                                 '--out', str(folder), '--format=mkbootimg'],
                                check=True, capture_output=True, text=True)
        args = shlex.split(result.stdout)
        if args[args.index('--header_version') + 1] != '2':
            raise ValueError('expected ZUI12 boot header v2')
        if sha(folder / 'dtb') != DTB_SHA:
            raise ValueError('unexpected ZUI12 DTB')
        ramdisk = remake_ramdisk((folder / 'ramdisk').read_bytes())
        source_cpio = folder / 'modified.cpio'
        source_cpio.write_bytes(ramdisk)
        with (folder / 'ramdisk.erofs.gz').open('wb') as dst:
            subprocess.run(['gzip', '-n', '-9', '-c', str(source_cpio)],
                           check=True, stdout=dst)
        if sha(folder / 'ramdisk.erofs.gz') != RAMDISK_SHA:
            raise ValueError('derived EROFS ramdisk differs from validated ramdisk')
        with (folder / 'kernel.gz').open('wb') as dst:
            subprocess.run(['gzip', '-n', '-9', '-c', str(opts.image)],
                           check=True, stdout=dst)
        update_option(args, '--kernel', str(folder / 'kernel.gz'))
        update_option(args, '--ramdisk', str(folder / 'ramdisk.erofs.gz'))
        update_option(args, '--os_version', '10.0.0')
        update_option(args, '--os_patch_level', '2020-12')
        update_option(args, '--second_offset', '0x00000000')
        update_option(args, '--cmdline', args[args.index('--cmdline') + 1] + RAMOOPS)
        result = subprocess.run([sys.executable, str(ROOT / 'mkbootimg.py'), *args,
                                 '--output', str(opts.output)], check=True)
        if sha(opts.output) != BOOT_SHA:
            opts.output.unlink()
            raise ValueError('reconstructed boot differs from tested boot; discarded output')
    print('VALIDATED BOOT REPRODUCED', opts.output, BOOT_SHA)


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, subprocess.CalledProcessError) as e:
        print('Boot reconstruction failed:', e, file=sys.stderr)
        sys.exit(1)
