#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Statically validate P11-only A17 netbpfload 4.19.325 gate exception.

This proves only that the mandatory A17 5.4+5.10 check is narrowly scoped;
real BPF helper/program support and boot must be tested after building APEX.
"""
import argparse
from pathlib import Path
import sys


def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--connectivity-source',required=True,type=Path)
 args=parser.parse_args()
 p=args.connectivity_source/'bpf/loader/NetBpfLoad.cpp'
 data=p.read_text()
 checks={
  'P11 exact device': 'GetProperty("ro.product.vendor.device", "") == "J606F"',
  'P11 exact SoC BSP': 'GetProperty("ro.board.platform", "") == "bengal"',
  'P11 vendor sdk': 'GetIntProperty("ro.vendor.build.version.sdk", 0) == 30',
  'native 4.19 version': 'isKernelVersion(4, 19) && isAtLeastKernelVersion(4, 19, 325)',
  '5.4 gated check': 'isAtLeast25Q2 && !isAtLeastKernelVersion(5, 4) && !p11Legacy419',
  '5.10 gated check': 'isAtLeast25Q4 && !isAtLeastKernelVersion(5, 10) && !p11Legacy419',
  'legacy exception logging': 'P11 A17 bring-up: kernel 4.19.325 legacy BSP',
 }
 for label,fragment in checks.items():
  assert data.count(fragment)==1,(label,data.count(fragment))
 assert 'isAtLeast25Q2 && !isAtLeastKernelVersion(5, 4))' not in data
 assert 'isAtLeast25Q4 && !isAtLeastKernelVersion(5, 10))' not in data
 assert data.count('&& !p11Legacy419')==2
 print('PASS:',len(checks),'exact BPF gate/provenance checks')
 print('PASS: Android17 default 5.4/5.10 BPF version checks retained for other devices')
 print('NOT TESTED: kernel BPF program verifier, BTF, helper ABI, APEX runtime or actual device boot')

if __name__=='__main__':
 try:main()
 except (AssertionError,OSError) as e:
  print('FAIL:',e,file=sys.stderr);sys.exit(1)
