#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Verify a locally extracted TB-J606F flash ZIP against bundled checksums."""
import hashlib
from pathlib import Path, PurePosixPath
import sys


def main():
    root = Path(__file__).resolve().parent
    manifest = root / 'SHA256SUMS'
    if not manifest.is_file():
        raise ValueError('SHA256SUMS is missing')
    lines = manifest.read_text().splitlines()
    if not lines:
        raise ValueError('SHA256SUMS is empty')
    seen = set()
    for line in lines:
        expected, delimiter, name = line.partition('  ')
        if not delimiter or len(expected) != 64 or name in seen or not name or PurePosixPath(name).is_absolute() or any(part in ('.', '..') for part in PurePosixPath(name).parts):
            raise ValueError('malformed checksum entry: ' + line)
        seen.add(name)
        path = root / name
        if not path.is_file():
            raise ValueError('missing: ' + name)
        digest = hashlib.sha256()
        with path.open('rb') as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b''):
                digest.update(block)
        if digest.hexdigest() != expected:
            raise ValueError('SHA256 mismatch: ' + name)
        print('OK', name)
    print('Verified', len(seen), 'release files')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as err:
        print('Package verification failed:', err, file=sys.stderr)
        sys.exit(1)
