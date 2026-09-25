#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Publish strictly redistributable historical kernel build artifacts to own tags.

EXCLUDES all boot/vendor/firmware, device logs, perf work and untagged data.
Never removes HDD files. Existing non-matching release assets cause an error.
"""
from __future__ import annotations
import argparse
import datetime
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile

REPO = Path(__file__).resolve().parents[2]
HDD = Path('/root/HDD/user0/P11')
AUDIT = REPO / 'Documentation/tbj606f/archive/release-reproducibility-audit.json'
GITHUB = 'bampudding/linux_kernel_lenovo_tbj606f'
STAGE = Path('/root/archive-publish-legacy-20260925')

def run(*argv):
    return subprocess.check_output(argv, text=True, cwd=REPO).strip()

def sha256_file(path):
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()

def member(name, content):
    info = tarfile.TarInfo(name)
    info.size = len(content)
    info.mtime = 0
    info.mode = 0o644
    info.uid = info.gid = 0
    info.uname = info.gname = ''
    return info

def create_package(release, artifact):
    tag = release['tag']
    assert release['hdd_exact_tag_complete_set']
    candidates = {Path(p).name: HDD/p for p in release['hdd_exact_tag_stage_files']}
    config_name = 'kernel.config' if 'kernel.config' in candidates else 'config'
    assert {'Image','Module.symvers',config_name}.issubset(candidates)
    canonical = {'Image': candidates['Image'], 'Module.symvers': candidates['Module.symvers'], 'kernel.config': candidates[config_name]}
    input_info = []
    for name,path in sorted(canonical.items()):
        assert path.is_file() and not path.is_symlink()
        assert path.resolve().is_relative_to((HDD/'releases'/tag).resolve())
        stat = path.stat()
        input_info.append({'file':name,'hdd_original_relative_path':str(path.relative_to(HDD)),'bytes':stat.st_size,'sha256':sha256_file(path),'mtime_ns':stat.st_mtime_ns,'inode':stat.st_ino})
    source_commit = run('git','rev-parse',tag+'^{commit}')
    assert source_commit == release['source_commit'], (tag,source_commit,release['source_commit'])
    provenance = {'schema_version':1,'kind':'historical-open-source-kernel-stage-artifacts','release_tag':tag,'git_source_commit':source_commit,'source_repo':'https://github.com/'+GITHUB,'original_hdd_items':input_info,'recovery_note':'This is the dated recovery of three existing kernel build artifacts for a source-only GitHub release. It does not assert clean rebuild of this historical version or tested installation.','exclusions':['OEM boot.img (ramdisk/DTB provenance)','vendor/firmware/dsp','current perf experiments','old debug logs']}
    payload = {'BUILD-PROVENANCE.json':(json.dumps(provenance,indent=2,ensure_ascii=False)+'\n').encode(),
               'README.txt':('TB-J606F historic kernel binary recovery: '+tag+'\nGitHub source tag: '+source_commit+'\nInputs: Image, Module.symvers, kernel.config.\nThis archive does not contain a flashable boot.img: supply legally obtained matching OEM boot/ramdisk and device-specific safe repacking procedure.\nOriginal build environment and bit-for-bit source rebuild have NOT been validated for every historic tag.\nSome historical tags represent failed or unbootable experiments. DO NOT flash solely because this archive exists.\n').encode()}
    for row in input_info:
        assert len(payload.get(row['file'],b''))==0
    sums = []
    for name,path in canonical.items():
        sums.append(sha256_file(path)+'  '+name)
    for name,content in sorted(payload.items()):
        sums.append(hashlib.sha256(content).hexdigest()+'  '+name)
    payload['SHA256SUMS'] = ('\n'.join(sorted(sums))+'\n').encode()
    artifact.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile(prefix='.tmp-legacy-',suffix='.tar.gz',dir=artifact.parent,delete=False) as tmp:
        temporary = Path(tmp.name)
    try:
        with temporary.open('wb') as file:
            with gzip.GzipFile(fileobj=file,mode='wb',filename='',mtime=0,compresslevel=6) as zipped:
                with tarfile.open(fileobj=zipped,mode='w|',format=tarfile.USTAR_FORMAT) as tar:
                    for name in sorted([*canonical,*payload]):
                        if name in canonical:
                            path=canonical[name]
                            info=member(name,b'')
                            info.size=path.stat().st_size
                            with path.open('rb') as src:tar.addfile(info,src)
                        else:
                            b=payload[name]
                            tar.addfile(member(name,b),io.BytesIO(b))
        with tarfile.open(temporary,'r:gz') as tar:
            assert set(tar.getnames())==set(canonical)|set(payload)
            for row in input_info:
                stream=tar.extractfile(row['file']);assert stream
                digest=hashlib.sha256()
                for b in iter(lambda:stream.read(1024*1024),b''):digest.update(b)
                assert digest.hexdigest()==row['sha256']
        # If the active experiment or earlier inventory changed, abort before upload.
        for row in input_info:
            path=HDD/row['hdd_original_relative_path'];stat=path.stat()
            assert (stat.st_mtime_ns,stat.st_size,stat.st_ino)==(row['mtime_ns'],row['bytes'],row['inode'])
        os.replace(temporary,artifact)
    finally:
        temporary.unlink(missing_ok=True)
    return provenance

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tag',help='one historical published stage tag; default all 37')
    parser.add_argument('--package-only',action='store_true')
    parser.add_argument('--staging',type=Path,default=STAGE)
    args=parser.parse_args()
    assert not args.staging.resolve().is_relative_to(HDD.resolve()), 'staging MUST be on SSD'
    assert args.staging.resolve()!=Path('/root/p11-kernel-lab/research/tbj606f-scroll-perf')
    releases=json.loads(AUDIT.read_text())['releases']
    chosen=[r for r in releases if r['hdd_exact_tag_complete_set'] and (args.tag is None or r['tag']==args.tag)]
    assert chosen and len(chosen)==(1 if args.tag else 37)
    destination=args.staging/'packages';statepath=args.staging/'publication-state.json'
    args.staging.mkdir(parents=True,exist_ok=True)
    state=json.loads(statepath.read_text()) if statepath.exists() else {'schema_version':1,'repo':GITHUB,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'entries':{}}
    for index,r in enumerate(chosen,1):
        tag=r['tag'];name='tbj606f-legacy-kernel-'+tag+'.tar.gz';artifact=destination/name
        try:
            provenance=create_package(r,artifact)
            digest=sha256_file(artifact)
            record={'tag':tag,'archive_name':name,'source_commit':provenance['git_source_commit'],'sha256':digest,'bytes':artifact.stat().st_size,'hdd_inputs':provenance['original_hdd_items'],'github_release':'https://github.com/'+GITHUB+'/releases/tag/'+tag,'status':'package_validated'}
            state['entries'][tag]=record
            statepath.write_text(json.dumps(state,indent=2)+'\n')
            if not args.package_only:
                info=json.loads(run('gh','api','repos/'+GITHUB+'/releases/tags/'+tag))
                remote=[a for a in info['assets'] if a['name']==name]
                if remote:
                    assert len(remote)==1 and remote[0]['digest']=='sha256:'+digest and remote[0]['size']==artifact.stat().st_size, 'Existing GitHub asset differs; no clobber: '+tag
                else:
                    subprocess.run(['gh','release','upload',tag,str(artifact),'-R',GITHUB],cwd=REPO,check=True)
                info=json.loads(run('gh','api','repos/'+GITHUB+'/releases/tags/'+tag))
                match=[a for a in info['assets'] if a['name']==name]
                assert len(match)==1 and match[0]['digest']=='sha256:'+digest and match[0]['size']==artifact.stat().st_size, 'Remote digest mismatch: '+tag
                record.update(status='verified_published',github_asset=match[0]['browser_download_url'],published_asset_id=match[0]['id'])
                statepath.write_text(json.dumps(state,indent=2)+'\n')
            print(f'[{index}/{len(chosen)}] {tag} {record["status"]} {record["bytes"]} bytes sha256={digest}',flush=True)
        except Exception as e:
            state['entries'].setdefault(tag,{})['error']=str(e)
            statepath.write_text(json.dumps(state,indent=2)+'\n')
            raise
    good=sum(e['status']=='verified_published' for e in state['entries'].values())
    print('PUBLISHED VERIFIED COUNT',good,'SOURCE STAGES',len(chosen),'STATE',statepath,flush=True)

if __name__=='__main__':main()
