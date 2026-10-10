#!/usr/bin/env python3
"""Read-only verification of the seven previously unmatched archived build stages."""
import hashlib,json,pathlib,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[2]
REPO='bampudding/linux_kernel_lenovo_tbj606f'
TAG='tbj606f-legacy-gpl-build-outputs-20260925'
old=json.loads((ROOT/'Documentation/tbj606f/archive/legacy-build-recipes-20260925.json').read_text())['rows']
seven={r['hdd_build_folder']:r for r in old if not r['candidate_git_branches']}
assert len(seven)==7
new=json.loads((ROOT/'Documentation/tbj606f/archive/seven-unmatched-build-resolution-20260925.json').read_text())['entries']
assert {r['build_folder'] for r in new}==set(seven)
remote=json.loads(subprocess.check_output(['gh','api','repos/'+REPO+'/releases/tags/'+TAG],text=True))
assets={a['name']:a for a in remote['assets']}
for r in new:
 n=r['build_folder'];a=assets[r['asset']]
 assert a['digest']=='sha256:'+r['asset_sha256'] and a['size']==r['asset_bytes']
 assert r['image_sha256']==seven[n]['saved_image_sha256']
 if r['source_branch']:
  ref='refs/heads/'+r['source_branch']
  got=subprocess.check_output(['git','ls-remote','origin',ref],cwd=ROOT,text=True).split()[0]
  assert got==r['source_commit'],(n,got)
 print('PASS',n,r['decision'],r['asset_bytes'],flush=True)
assert sum(r['decision']=='source_branch_plus_release' for r in new)==6
assert sum(r['decision']=='release_only' for r in new)==1
print('PASS 6 source context branches (1 newly created), 1 release-only, all 7 remotely verified')
