#!/usr/bin/env python3
"""Create a deterministic, verified end-user ZIP (no OEM firmware or GSI)."""
import argparse
import hashlib
import pathlib
import stat
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
TOOLS = ROOT / 'tools/tbj606f'
EXPECTED = {
    'Image': 'af0b7b6b81c4f6ba3c5c2fbb044972a1bf502453ec19effa6d3664c094fdb2f8',
    'p11_audio_compat.ko': 'af7e14a238437b5fc7e29dc5fdf8453630d3981f0c4b7218f588ccf6aab08f40',
}
BINARIES = ('Image', 'Image.gz', 'p11_audio_compat.ko', 'kernel.config',
            'Module.symvers', 'System.map', 'TESTED-IMAGE-HASHES.txt')
SCRIPTS = ('install.sh', 'repack-boot.sh', 'make-hybrid-vendor.sh',
           'mkbootimg.py', 'unpack_bootimg.py', 'gki/generate_gki_certificate.py')


def sha(content):
    return hashlib.sha256(content).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kernel-assets', type=pathlib.Path, required=True,
                        help='verified public-v1/v3 kernel files directory')
    parser.add_argument('--output', type=pathlib.Path, required=True)
    args = parser.parse_args()
    payload = {}
    for name in BINARIES:
        path = args.kernel_assets / name
        if not path.is_file() or path.is_symlink():
            parser.error('missing regular kernel asset: ' + str(path))
        payload[name] = path.read_bytes()
    for name, expected in EXPECTED.items():
        if sha(payload[name]) != expected:
            parser.error(name + ' differs from the validated kernel release')
    for name in SCRIPTS:
        payload[name] = (TOOLS / name).read_bytes()
    payload['installation.md'] = (ROOT / 'Documentation/tbj606f/installation.md').read_bytes()
    payload['README-START-HERE.md'] = (TOOLS / 'FLASH-ZIP-README.md').read_bytes()
    payload['verify-package.py'] = (TOOLS / 'verify-package.py').read_bytes()
    payload['SHA256SUMS'] = ''.join(
        f'{sha(content)}  {name}\n' for name, content in sorted(payload.items())
    ).encode()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output, 'w', compression=zipfile.ZIP_DEFLATED,
                         compresslevel=9, allowZip64=True) as out:
        for name, content in sorted(payload.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 9, 24, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = ((stat.S_IFREG | (0o755 if name in SCRIPTS else 0o644)) << 16)
            out.writestr(info, content, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    with zipfile.ZipFile(args.output) as out:
        assert out.testzip() is None
        for name, content in payload.items():
            assert out.read(name) == content
    print(args.output, 'bytes', args.output.stat().st_size, 'sha256', sha(args.output.read_bytes()))


if __name__ == '__main__':
    main()
