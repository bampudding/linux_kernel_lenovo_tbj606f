#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Check a P11-only Android 17 SELinux 30.0 compatibility source overlay.

Checks AOSP module graph and provenance; CANNOT replace full AOSP
sepolicy compilation and the combined P11 vendor policy binary test.
"""
import argparse
import hashlib
from pathlib import Path
import re
import sys

NAMES=(
 '30.0.board.compat.map','30.0.board.compat.cil','30.0.board.ignore.map',
 'plat_30.0.cil','system_ext_30.0.cil','product_30.0.cil',
 '30.0.ignore.cil','system_ext_30.0.ignore.cil',
 'product_30.0.ignore.cil','30.0.compat.cil',
 'system_ext_30.0.compat.cil',
)
EXPECTED={
 '30.0.cil':'37483953b960c5b4cfe7e432a50c18c5afdce6ab6c5d1490c76ed251930e43db',
 '30.0.compat.cil':'2b40198379e1bb65ca2af156b25562381273144d94c5ae223b5ed9905d7437cc',
 '30.0.ignore.cil':'29ebff2887697e9663c64aaa48df0b3450b0d0c67c260c8d0baaf67e2f076615',
}

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--a17-sepolicy',required=True,type=Path)
 p.add_argument('--p11-vendor-etc',required=True,type=Path)
 a=p.parse_args();tree=a.a17_sepolicy;vendor=a.p11_vendor_etc
 version=(vendor/'selinux/plat_sepolicy_vers.txt').read_text().strip()
 assert version=='30.0', f'Wrong vendor ABI: {version}'
 manifest=(vendor/'vintf/manifest.xml').read_text()
 assert re.search(r'<manifest[^>]+target-level="5"',manifest),'P11 manifest target 5 changed'
 bp=(tree/'compat/Android.bp').read_text();root=(tree/'Android.bp').read_text()
 found=re.findall(r'(?m)^\s*name: "([^"]+)"',bp)
 assert len(found)==len(set(found)),'duplicate Soong module names in compat'
 assert all(found.count(n)==1 for n in NAMES),set(NAMES)-set(found)
 for k in ['plat_','system_ext_','product_']:
  name=k+'30.0.cil';next_=k+'31.0.cil'
  block=re.search(r'(?s)se_cil_compat_map \{\s*name: "'+re.escape(name)+r'".*?^\}',bp,re.M)
  assert block and 'top_half: "'+next_+'"' in block.group(0),name
 for name in ['30.0.board.compat.map','30.0.board.compat.cil','30.0.board.ignore.map']:
  assert 'name: "'+name+'"' in bp,name
 for name in ['plat_30.0.cil','system_ext_30.0.cil','product_30.0.cil',
              '30.0.compat.cil','system_ext_30.0.compat.cil']:
  assert '"'+name+'",' in root,name
 for name,digest in EXPECTED.items():
  f=tree/'private/compat/30.0'/name
  assert hashlib.sha256(f.read_bytes()).hexdigest()==digest,f'{name} differs from AOSP Android16 ABI bridge'
 assert (tree/'prebuilts/api/30.0/Android.bp').is_file(),'30.0 public API snapshot missing'
 b=(tree/'private/compat/30.0/30.0.cil').read_bytes()
 n=len(set(re.findall(rb'[A-Za-z_][A-Za-z0-9_]*_30_0',b)))
 assert n>1000,n
 print('PASS: P11 vendor policy ABI=30.0, VINTF FCM=5')
 print('PASS: 11 restored Soong modules; 30->31->newer policy chain preserved')
 print('PASS: original AOSP Android16 30.0 compatibility data SHA256 matches 3/3')
 print('PASS: AOSP 30.0 public policy snapshot and 5 packaging references present')
 print('PASS: 30.0 source versioned symbols:',n)
 print('NOT TESTED: complete Android17 secilc/system_ext/product/vendor combined policy or device boot')

if __name__=='__main__':
 try:main()
 except (AssertionError, OSError) as e:
  print('FAIL:',e,file=sys.stderr);sys.exit(1)
