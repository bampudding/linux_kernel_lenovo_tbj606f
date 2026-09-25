#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Private, reversible one-byte experiment: disable unsafe SF Always latch.

Supply the exact archived stable TB-J606F hybrid vendor ext4 and a NEW
output filename. Never checks out, redistributes, flashes or overwrites it.
The output is a diagnostic candidate; not a general vendor update.
"""
import argparse
import hashlib
import mmap
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ORIGINAL_SHA256 = 'b0cca3012109d045122dccdbd22f2505327ec7550576daa37d4bde643a39d3dd'
SIZE = 796917760
OLD = b'debug.sf.latch_unsignaled=1'
NEW = b'debug.sf.latch_unsignaled=0'
assert len(OLD)==len(NEW)


def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(4*1024*1024),b''):
            h.update(block)
    return h.hexdigest()


def prop(path):
    with tempfile.TemporaryDirectory(prefix='p11-sf-property-check-') as temp:
        local=Path(temp)/'build.prop'
        subprocess.run(['debugfs','-R',f'dump /build.prop {local}',str(path)],check=True,
                       stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        return local.read_bytes()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('original',type=Path)
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    original=args.original.resolve()
    output=args.output.absolute()
    if original==output or output.exists():
        parser.error('output must be a separate, nonexistent file')
    if not original.is_file() or original.stat().st_size!=SIZE:
        parser.error('wrong/missing original vendor size')
    actual=digest(original)
    if actual!=ORIGINAL_SHA256:
        parser.error(f'wrong original vendor SHA256: {actual}')
    before=prop(original)
    if before.count(OLD)!=1 or NEW in before:
        parser.error('original /build.prop does not have exactly one expected latch property')
    output.parent.mkdir(parents=True,exist_ok=True)
    try:
        # The raw ext4 image uses normal uncompressed file data, so a same-size
        # in-place DATA byte substitution avoids changing inode/SELinux,
        # shared-block metadata, permissions, timestamps and filesystem layout.
        shutil.copyfile(original,output)
        with output.open('r+b') as stream:
            with mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_WRITE) as mapping:
                position=mapping.find(OLD)
                if position<0 or mapping.find(OLD,position+len(OLD))!=-1 or mapping.find(NEW)!=-1:
                    raise RuntimeError('not exactly one vendor property occurrence in image')
                mapping[position:position+len(OLD)]=NEW
                mapping.flush()
        after=prop(output)
        if after!=before.replace(OLD,NEW,1):
            raise RuntimeError('vendor property changed beyond one-byte replacement')
        with original.open('rb') as f1,output.open('rb') as f2:
            delta=0
            for a,b in zip(iter(lambda:f1.read(4*1024*1024),b''),
                           iter(lambda:f2.read(4*1024*1024),b'')):
                if a!=b:
                    delta+=sum(x!=y for x,y in zip(a,b))
        if delta!=1 or output.stat().st_size!=SIZE:
            raise RuntimeError(f'expected one byte changed; got {delta}')
        print('baseline:',ORIGINAL_SHA256)
        print('candidate:',digest(output))
        print('verified: exactly ONE image data byte changed, /build.prop only')
        print('property:',OLD.decode(),'->',NEW.decode())
        print('NOTICE: candidate vendor still requires user/device A/B validation; do not release/flash automatically')
    except BaseException:
        output.unlink(missing_ok=True)
        raise

if __name__=='__main__':main()
