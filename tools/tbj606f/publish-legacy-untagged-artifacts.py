#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Package/verify non-OEM source/code + kernel artifacts from old untagged HDD groups.

One archive per original group, plus full classification manifest. NEVER scans
scroll-performance-20260924, never packages stock boot/vendor/ramdisk/runtime,
never claims source->Image reproducibility without an exact source commit.
Never deletes originals. After public release exists, --upload is resumable.
"""
from __future__ import annotations
import argparse,datetime,gzip,hashlib,io,json,os,re,subprocess,tarfile,tempfile
from pathlib import Path

HDD=Path('/root/HDD/user0/P11')
REPO=Path(__file__).resolve().parents[2]
RELEASES=HDD/'releases'
EXPERIMENTS=HDD/'experiments'
STAGING=Path('/root/archive-publish-legacy-20260925/untagged')
TAG='tbj606f-legacy-gpl-stages-20260925'
GITHUB='bampudding/linux_kernel_lenovo_tbj606f'
SKIP_GROUPS={('releases','github'),('releases','p11-a16-zui14-hybrid-stable-20260924'),('experiments','scroll-performance-20260924')}
CHOSEN_LITERAL={'Image','Image-initvisible','Module.symvers','config','kernel.config','p11_audio_compat.c','p11_audio_compat.Makefile'}

def sha_bytes(stream):
 h=hashlib.sha256()
 for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
 return h.hexdigest()
def file_digest(path):
 with path.open('rb') as f:return sha_bytes(f)
def tarinfo(name,size):
 info=tarfile.TarInfo(name);info.size=size;info.mtime=0;info.mode=0o644;info.uid=info.gid=0;info.uname=info.gname='';return info

def wanted(path,root):
 rel=path.relative_to(root)
 if path.is_symlink() or not path.is_file():return False
 if any(t in rel.parts for t in ('work','.git','__pycache__','runtime','ramdisk','unpack','repack','success-20260923-161757')):return False
 if len(rel.parts)==1 and path.name in CHOSEN_LITERAL:return True
 if path.stat().st_size>20_000_000:return False
 if path.suffix=='.patch' and 'scroll' not in str(rel).lower():return True
 if path.suffix=='.sh' and 'scroll' not in str(rel).lower():return True
 if re.fullmatch(r'build_p11diag.*\.py',path.name):return True
 return False

def do_package(root,where,kind):
 files=[]
 for path in sorted(root.rglob('*')):
  if wanted(path,root):
   rel=path.relative_to(root)
   assert not path.is_symlink() and path.resolve().is_relative_to(root.resolve())
   stat=path.stat()
   files.append({'path':str(rel),'original_hdd_path':str(path.relative_to(HDD)),
                 'sha256':file_digest(path),'bytes':stat.st_size,'mtime_ns':stat.st_mtime_ns,'inode':stat.st_ino})
 if not files:return None
 provenance={'schema_version':1,'kind':'unmapped-legacy-kernel-or-source-artifacts','group':kind+'/'+root.name,
             'source_commit':'UNKNOWN_UNVERIFIED_FOR_THIS_GROUP','source_tag':'NONE_VERIFIED',
             'warning':'Standalone historical recovery only. Raw Image is NOT verified reproducible from an inferred branch, source commit or binary archive. Some debugging images never booted. Do not flash solely from this archive.',
             'exclusions':['OEM boot.img/ramdisk/dtb','vendor/product/DSP','runtime and user logs','latest active performance source and measurements'],
             'files':files}
 blobs={'BUILD-PROVENANCE.json':(json.dumps(provenance,indent=2)+'\n').encode(),
        'README.txt':('TB-J606F old standalone archive group: '+kind+'/'+root.name+'\nThese are individual public-code/kernel-only historical data, not a tested/flashable release. Exact source commit unknown for this loose HDD directory. Original files remain on HDD until separately authorized deletion. OEM boot/vendor/recovery are excluded.\n').encode()}
 sums=[x['sha256']+'  '+x['path'] for x in files]
 sums.extend(hashlib.sha256(value).hexdigest()+'  '+name for name,value in blobs.items())
 blobs['SHA256SUMS']=('\n'.join(sorted(sums))+'\n').encode()
 where.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.NamedTemporaryFile(prefix='.tmp-legacy-',suffix='.tar.gz',dir=where.parent,delete=False) as tf:tmp=Path(tf.name)
 try:
  with tmp.open('wb') as output:
   with gzip.GzipFile(fileobj=output,mode='wb',filename='',mtime=0,compresslevel=6) as zipped:
    with tarfile.open(fileobj=zipped,mode='w|',format=tarfile.PAX_FORMAT) as tar:
     for x in files:
      path=HDD/x['original_hdd_path']
      with path.open('rb') as src:tar.addfile(tarinfo(x['path'],x['bytes']),src)
     for name,bytes_ in sorted(blobs.items()):tar.addfile(tarinfo(name,len(bytes_)),io.BytesIO(bytes_))
  with tarfile.open(tmp,'r:gz') as archive:
   assert len(archive.getnames())==len(files)+len(blobs)
   for x in files:
    stream=archive.extractfile(x['path']);assert stream and sha_bytes(stream)==x['sha256']
  for x in files:
   st=(HDD/x['original_hdd_path']).stat()
   assert (st.st_mtime_ns,st.st_size,st.st_ino)==(x['mtime_ns'],x['bytes'],x['inode'])
  os.replace(tmp,where)
 finally:tmp.unlink(missing_ok=True)
 return {'group':kind+'/'+root.name,'archive':where.name,'size':where.stat().st_size,'sha256':file_digest(where),'files':files,'status':'packaged_verified'}

def main():
 args=argparse.ArgumentParser(description=__doc__)
 args.add_argument('--upload',action='store_true')
 arg=args.parse_args()
 assert not STAGING.resolve().is_relative_to(HDD.resolve())
 audit=json.loads((REPO/'Documentation/tbj606f/archive/release-reproducibility-audit.json').read_text())
 tag_names={r['tag'] for r in audit['releases']}
 groups=[]
 for kind,base in [('releases',RELEASES),('experiments',EXPERIMENTS)]:
  for root in sorted(base.iterdir()):
   if not root.is_dir() or (kind,root.name) in SKIP_GROUPS:continue
   if kind=='releases' and root.name in tag_names:continue
   groups.append((kind,root))
 assert len([r for k,r in groups if k=='releases'])==43
 STAGING.mkdir(parents=True,exist_ok=True)
 statepath=STAGING/'publication-state.json'
 state=json.loads(statepath.read_text()) if statepath.exists() else {'schema_version':1,'tag':TAG,'github_release':'https://github.com/'+GITHUB+'/releases/tag/'+TAG,'creation_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'entries':{}}
 remote={}
 if arg.upload:
  release=json.loads(subprocess.check_output(['gh','api','repos/'+GITHUB+'/releases/tags/'+TAG],text=True,cwd=REPO))
  remote={a['name']:a for a in release['assets']}
 for ix,(kind,root) in enumerate(groups,1):
  name=f'tbj606f-old-{kind}-{root.name}.tar.gz'
  path=STAGING/'packages'/name
  record=do_package(root,path,kind)
  if record is None:
   state['entries'][kind+'/'+root.name]={'group':kind+'/'+root.name,'archive':None,'status':'no_redistributable_files_found','warning':'Only images/logs/OEM or unselected files; original HDD contents must remain.'}
   continue
  if arg.upload:
   match=remote.get(name)
   if match:
    assert match['digest']=='sha256:'+record['sha256'] and match['size']==record['size'], 'Existing remote asset differs: '+name
   else:
    subprocess.run(['gh','release','upload',TAG,str(path),'-R',GITHUB],check=True,cwd=REPO)
    match=json.loads(subprocess.check_output(['gh','api','repos/'+GITHUB+'/releases/tags/'+TAG],text=True,cwd=REPO))
    match=next(a for a in match['assets'] if a['name']==name)
    remote[name]=match
   assert match['digest']=='sha256:'+record['sha256'] and match['size']==record['size']
   record.update(status='verified_published',github_url=match['browser_download_url'])
  state['entries'][record['group']]=record
  statepath.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n')
  print(f'[{ix}/{len(groups)}] {record["group"]}: {record["status"]} {record["size"]}',flush=True)
 state['group_count']=len(groups)
 state['pub_count']=sum(x['status']=='verified_published' for x in state['entries'].values())
 state['no_public_artifact_count']=sum(x['status']=='no_redistributable_files_found' for x in state['entries'].values())
 statepath.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n')
 print('SUMMARY',state['group_count'],'verified_published',state['pub_count'],'no_public_artifact',state['no_public_artifact_count'],flush=True)

if __name__=='__main__':main()
