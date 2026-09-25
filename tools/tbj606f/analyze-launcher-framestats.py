#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Summarize frame stage timing from private `dumpsys gfxinfo PKG framestats`.

No external libs; raw traces must not be published (may contain device data).
Comparison app frame pacing differs; never equate a slow 30Hz intended
animation to missed deadlines in a 60Hz input-driven launcher.
"""
import argparse
from pathlib import Path

STAGES=(
 ('Input scheduling','Vsync','HandleInputStart'),
 ('Input handling','HandleInputStart','AnimationStart'),
 ('Animation','AnimationStart','PerformTraversalsStart'),
 ('Traversal','PerformTraversalsStart','DrawStart'),
 ('UI draw queue','DrawStart','SyncQueued'),
 ('RenderThread sync wait','SyncQueued','SyncStart'),
 ('RT preparation','SyncStart','IssueDrawCommandsStart'),
 ('Issue draw to swap','IssueDrawCommandsStart','SwapBuffers'),
 ('Swap to frame completed','SwapBuffers','FrameCompleted'),
 ('Frame total','IntendedVsync','FrameCompleted'),
)

def parse(path):
    text=path.read_text(errors='replace')
    rows=[]
    for section in text.split('---PROFILEDATA---')[1::2]:
        lines=section.strip().splitlines()
        if not lines or not lines[0].startswith('Flags,'):
            continue
        headers=[h for h in lines[0].split(',') if h]
        for line in lines[1:]:
            vals=[v for v in line.split(',') if v]
            if len(vals)!=len(headers):continue
            try:row=dict(zip(headers,map(int,vals)))
            except ValueError:continue
            if row.get('Flags')!=0 or row.get('FrameCompleted',0)<=row.get('IntendedVsync',0):continue
            rows.append(row)
    return rows

def pct(values,q):
    xs=sorted(values)
    return xs[min(len(xs)-1,int((len(xs)-1)*q))] if xs else None

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('files',nargs='+',type=Path)
    args=ap.parse_args()
    for path in args.files:
        rows=parse(path)
        print(f'{path}: sampled_recent_frames={len(rows)}')
        if len(rows)<40:print('INCONCLUSIVE: fewer than 40 valid frames; keep raw file and retry');continue
        print('stage                          p50     p90     p95 (ms)')
        for label,start,end in STAGES:
            times=[(r[end]-r[start])/1e6 for r in rows if start in r and end in r and r[end]>=r[start]]
            if not times:continue
            print(f'{label:29} {pct(times,.5):>5.1f} {pct(times,.9):>7.1f} {pct(times,.95):>7.1f}')
        missed=[r for r in rows if 'FrameDeadline' in r and r['FrameCompleted']>r['FrameDeadline']]
        print(f'FrameCompleted after FrameDeadline: {len(missed)}/{len(rows)}; gfxinfo Janky frames summary remains authoritative.')

if __name__=='__main__':main()
