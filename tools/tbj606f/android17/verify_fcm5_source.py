#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""P11-only Android17 FCM5 source packaging preflight (not runtime VINTF)."""
import argparse
from pathlib import Path
import re
import sys
import hashlib


def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--a17-hardware-interfaces',type=Path,required=True)
 p.add_argument('--a16-hardware-interfaces',type=Path,required=True)
 p.add_argument('--p11-vendor-etc',type=Path,required=True)
 args=p.parse_args()
 a=args.a17_hardware_interfaces/'compatibility_matrices'
 b=args.a16_hardware_interfaces/'compatibility_matrices'
 v=(args.p11_vendor_etc/'vintf/manifest.xml').read_text()
 assert re.search(r'<manifest[^>]+target-level="5"',v),'Not the P11 FCM5 hybrid vendor'
 cur=a/'compatibility_matrix.5.xml';original=b/'compatibility_matrix.5.xml'
 assert cur.read_bytes()==original.read_bytes(),'Modified instead of genuine A16 FCM5 snapshot'
 assert b'level="5"' in cur.read_bytes()
 s=(a/'Android.bp').read_text()
 m=re.search(r'SYSTEM_MATRIX_DEPS_A17\s*=\s*\[(.*?)\]',s,re.S)
 assert m and '"framework_compatibility_matrix.5.xml"' in m.group(1),'FCM5 missing from A17 packaging'
 assert s.count('name: "framework_compatibility_matrix.5.xml"')==1,'FCM5 duplicate/absent'
 print('PASS: P11 hybrid vendor FCM5, Android17 FCM5 packaging restored')
 print('PASS: byte-identical A16 FCM5 matrix',hashlib.sha256(cur.read_bytes()).hexdigest())
 print('NOT TESTED: Android17 Soong VINTF assembly or device VINTF compatibility')

if __name__=='__main__':
 try:main()
 except (AssertionError,OSError) as e:print('FAIL:',e,file=sys.stderr);sys.exit(1)
