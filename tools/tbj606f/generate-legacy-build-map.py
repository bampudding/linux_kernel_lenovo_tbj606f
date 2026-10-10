#!/usr/bin/env python3
"""Record only verified Git ref associations for old build outputs; never guess a source commit."""
import hashlib,json,pathlib,subprocess,datetime
ROOT=pathlib.Path(__file__).resolve().parents[2]
HDD=pathlib.Path('/root/HDD/user0/P11/build-archive/20260923')
OUT=ROOT/'Documentation/tbj606f/archive/legacy-build-recipes-20260925.json'
REPO='https://github.com/bampudding/linux_kernel_lenovo_tbj606f'

def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
refs=git('for-each-ref','--format=%(refname:short)','refs/remotes/origin/p11/','refs/heads/p11/').splitlines()
refs={r.removeprefix('origin/') for r in refs}
rows=[]
for d in sorted(HDD.iterdir()):
 if not d.is_dir():continue
 config=d/'.config';image=d/'arch/arm64/boot/Image';vmlinux=d/'vmlinux'
 if not config.is_file():continue
 # Mapping is exact only when the folder suffix is an exact branch name.
 candidates=[r for r in refs if r=='p11/'+d.name]
 if not candidates and d.name.endswith('-test1'):
  candidates=[r for r in refs if r=='p11/'+d.name.removesuffix('-test1')]
 if not candidates and d.name.endswith('-diag2'):
  candidates=[r for r in refs if r=='p11/'+d.name.removesuffix('-diag2')]
 candidates=sorted(set(candidates))
 row={'hdd_build_folder':d.name,'saved_config_sha256':sha(config),
      'saved_image_sha256':sha(image) if image.is_file() else None,
      'saved_vmlinux_sha256':sha(vmlinux) if vmlinux.is_file() else None,
      'candidate_git_branches':candidates,
      'branch_attribution':'NAME_MATCH_ONLY_NOT_BUILD_VERIFIED' if candidates else 'UNKNOWN',
      'clean_rebuild_verified':False,
      'toolchain_identity':'UNKNOWN_FOR_THIS_HISTORICAL_BUILD',
      'recipe':'git checkout <candidate commit>; mkdir -p /separate/ssd/out; cp <archived-.config> /separate/ssd/out/.config; PATH=<clang-bin>:<cross-bin>:$PATH make O=/separate/ssd/out ARCH=arm64 CC=clang CROSS_COMPILE=aarch64-linux-android- CLANG_TRIPLE=aarch64-linux-gnu- olddefconfig Image dtbs; exact toolchain and source identity still require verification',
      'warning':'Name similarity alone does not prove this branch built these bytes; no claim of bit-for-bit reproduction.'}
 if candidates:row['candidate_commits']={b:git('rev-parse',b) for b in candidates}
 rows.append(row)
OUT.write_text(json.dumps({'schema_version':1,'scope':'historical build-archive/20260923; excludes current perf and build environment','source_repo':REPO,'rows':rows},indent=2)+'\n')
print('build stages',len(rows),'candidate named branch',sum(bool(r['candidate_git_branches']) for r in rows),'unknown',sum(not r['candidate_git_branches'] for r in rows))
