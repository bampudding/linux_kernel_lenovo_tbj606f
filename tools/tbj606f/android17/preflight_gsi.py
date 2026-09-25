#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Read-only P11 Android 17 GSI SELinux/vendor ABI preflight.

No root, mount, flash, img modification, or invented boot-success report.
Sparse ext4 is decoded to a temporary directory on the caller-selected HDD.
If vendor lacks an Android 17 system counterpart or policy compilation is
untested, explicitly report unresolved requirements.
"""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

PUBLIC_30_ATTR = re.compile(rb'\b[a-zA-Z_][a-zA-Z0-9_]*_30_0\b')


def run(argv):
    result = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            check=False)
    return result


def read_ext4(img, guest):
    """Read exactly a named small regular file from ext4 via debugfs."""
    for path in (guest, '/system' + guest):
        stat = run(['debugfs', '-R', 'stat ' + path, str(img)])
        if b'Inode:' not in stat.stdout or b'Type: regular' not in stat.stdout:
            continue
        content = run(['debugfs', '-R', 'cat ' + path, str(img)])
        if content.returncode == 0 and len(content.stdout) <= 16*1024*1024:
            return content.stdout, path
    return None, None


def prepare_ext4(img, dest):
    with img.open('rb') as fh:
        magic = fh.read(4)
        fh.seek(1080)
        ext = fh.read(2)
    if ext == b'\x53\xef':
        return img
    if magic == b'\x3a\xff\x26\xed':
        if not shutil.which('simg2img'):
            raise RuntimeError('Android sparse image requires simg2img')
        raw = dest/'system.raw.img'
        subprocess.run(['simg2img', str(img), str(raw)],check=True)
        return raw
    raise RuntimeError('Not a recognized raw ext4 or Android sparse image')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--system-img',required=True,type=Path,
                   help='Android17 ARM64 GSI system.img, never modified')
    p.add_argument('--vendor-dir',required=True,type=Path,
                   help='P11 extracted vendor/etc, not another tablet')
    p.add_argument('--scratch-dir',required=True,type=Path,
                   help='HDD path for possible sparse -> raw decode')
    p.add_argument('--require-sdk',type=int,default=37,
                   help='Required GSI SDK (37=Android17, 36=Android16 control)')
    p.add_argument('--json-out',type=Path)
    args=p.parse_args()
    vendor=args.vendor_dir/'selinux/plat_sepolicy_vers.txt'
    if not args.system_img.is_file() or not vendor.is_file():
        p.error('System image or P11 vendor SELinux version is missing')
    policy=vendor.read_text(errors='replace').strip()
    if not re.fullmatch(r'\d+\.0',policy):
        p.error('Vendor SELinux policy version malformed: '+repr(policy))
    manifest=args.vendor_dir/'vintf/manifest.xml'
    if not manifest.is_file() or not re.search(r'<manifest[^>]+target-level="5"',manifest.read_text()):
        p.error('Vendor directory is not the expected P11 ZUI14 FCM5 source')
    if not args.scratch_dir.is_dir():
        p.error('Preexisting scratch directory must be on HDD')
    result={'vendor_policy_abi':policy,'source_system_image':str(args.system_img),
            'checks':{},'errors':[], 'warnings':[]}
    with tempfile.TemporaryDirectory(prefix='p11-a17-readonly-',dir=args.scratch_dir) as d:
        raw=prepare_ext4(args.system_img,Path(d))
        files=[('platform',f'/etc/selinux/mapping/{policy}.cil'),
               ('plat_policy','/etc/selinux/plat_sepolicy.cil'),
               ('vndk_compat','/etc/llndk.libraries.30.txt')]
        for key,guest in files:
            content,source=read_ext4(raw,guest)
            result['checks'][key]={'present':content is not None,'path':source,
                                    'size':len(content) if content is not None else None}
            if key=='platform':
                if content is None:
                    result['errors'].append('GSI lacks real '+policy+'.cil platform mapping')
                else:
                    attrs=set(PUBLIC_30_ATTR.findall(content))
                    result['checks'][key]['versioned_symbols']=len(attrs)
                    if policy=='30.0' and len(attrs)<30:
                        result['errors'].append('30.0 mapping has too few ABI-30 symbol references; check incorrect renaming')
            elif key=='plat_policy' and content is None:
                result['errors'].append('GSI missing plat_sepolicy.cil')
        for key,guest in [('build_props','/build.prop'),('system_ext_30','/system_ext/etc/selinux/mapping/'+policy+'.cil'),('product_30','/product/etc/selinux/mapping/'+policy+'.cil')]:
            content,source=read_ext4(raw,guest)
            result['checks'][key]={'present':content is not None,'path':source}
            if key=='build_props' and content:
                for prop in ('ro.build.version.sdk','ro.build.version.release','ro.build.version.incremental'):
                    m=re.search(rb'(?m)^'+prop.encode()+rb'=(.+)$',content)
                    if m:result['checks'][key][prop]=m.group(1).decode(errors='replace').strip()
    # These files may be served by separate product/system_ext images; never
    # assert correctness based on their absence from only system.img.
    props=result['checks']['build_props']
    if props.get('ro.build.version.sdk')!=str(args.require_sdk):
        result['errors'].append(
            f'Expected SDK {args.require_sdk}, found '
            f'{props.get("ro.build.version.sdk", "missing")} in supplied system.img')
    result['checks']['build_props']['expected_sdk']=args.require_sdk
    if not result['checks']['system_ext_30']['present'] or not result['checks']['product_30']['present']:
        result['warnings'].append('Check separately mounted system_ext/product policies and their '+policy+'.cil mapping when present')
    if not result['checks']['vndk_compat']['present']:
        result['warnings'].append('LLNDK compatibility file not in examined system image; check system and VNDK APEX for vendor VNDK30')
    result['warnings'].append('Static file check only: NOT proof secilc policy merge, VINTF, BPF or physical boot succeeds')
    report=json.dumps(result,indent=2,ensure_ascii=False)
    print(report)
    if args.json_out:args.json_out.write_text(report+'\n')
    return 1 if result['errors'] else 0


if __name__=='__main__':
    try:sys.exit(main())
    except (OSError,RuntimeError,subprocess.CalledProcessError) as exc:
        print('PREFLIGHT ERROR:',exc,file=sys.stderr)
        sys.exit(2)
