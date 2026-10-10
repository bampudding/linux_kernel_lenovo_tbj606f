#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Append clear later archival provenance to historical GitHub release notes.

Uses verified publication state; preserves old notes verbatim, idempotently.
No force upload, tag edit or replacement of old asset.
"""
import json,subprocess
from pathlib import Path

OWNER='bampudding/linux_kernel_lenovo_tbj606f'
STATE=Path('/root/archive-publish-legacy-20260925/publication-state.json')
entries=json.loads(STATE.read_text())['entries']
assert len(entries)==37 and all(x['status']=='verified_published' for x in entries.values())
for i,(tag,row) in enumerate(entries.items(),1):
    path='repos/'+OWNER+'/releases/tags/'+tag
    release=json.loads(subprocess.check_output(['gh','api',path],text=True))
    body=release['body'] or ''
    marker='### Supplemental historical kernel archive — 2026-09-25'
    addition=(f'{marker}\n\n'
      f'After the original release, a byte-verified archive, `{row["archive_name"]}`, '
      f'was recovered from the old HDD and added on 2026-09-25. It contains '
      f'`Image`, `Module.symvers`, normalized `kernel.config`, individual SHA256 '
      f'checksums and exact source-commit provenance (`{row["source_commit"]}`). '
      f'This is historical artifact preservation, **not** a new clean-rebuild or '
      f'successful-boot test. OEM-containing `boot.img` is intentionally excluded; '
      f'the archive by itself is not a flashable boot image.\n')
    if marker not in body:
        newbody=body.rstrip()+'\n\n'+addition if body.strip() else addition
        payload=json.dumps({'body':newbody},ensure_ascii=False).encode()
        subprocess.run(['gh','api','-X','PATCH','repos/'+OWNER+'/releases/'+str(release['id']),'--input','-'],input=payload,check=True,stdout=subprocess.DEVNULL)
    check=json.loads(subprocess.check_output(['gh','api',path],text=True))
    assert marker in check['body'] and check['body'].count(marker)==1
    assert body in check['body'] or marker in body
    print(f'[{i}/37] original release note preserved + archival addendum {tag}',flush=True)
