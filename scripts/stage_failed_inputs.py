#!/usr/bin/env python3
"""Copy explicitly listed unresolved FASTAs to safe paths without altering originals.
No Kleborate execution, downloading or biological exclusion. Requires original run files.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,re,shutil,sys
from pathlib import Path

def stage(project: Path, paths_file: Path, destination: Path):
    if not project.is_dir():raise ValueError('Original project directory not found')
    if destination.exists():raise FileExistsError('Choose a new destination; originals will not be overwritten')
    if not re.fullmatch(r'[A-Za-z0-9_./-]+',str(destination.expanduser().absolute())):
        raise ValueError('Destination must have no spaces, parentheses or shell metacharacters')
    paths=[x for x in paths_file.read_text(encoding='utf-8').splitlines() if x.strip()]
    if not paths:raise ValueError('Recovery list is empty')
    destination.mkdir(parents=True); ready=[]; records=[]; seen={}
    for raw in paths:
        source=Path(raw);source=source if source.is_absolute() else project/source
        record={'original_path':raw,'status':'','safe_path':'','sha256_uncompressed':''}
        if not source.is_file():record['status']='MISSING_SOURCE';records.append(record);continue
        name=re.sub(r'\.(fna|fa|fasta)(\.gz)?$','',source.name,flags=re.I)
        if not re.fullmatch(r'[A-Za-z0-9_.-]+',name):
            record['status']='UNSAFE_BASENAME_REVIEW';records.append(record);continue
        target=destination/(name+'.fna')
        opener=gzip.open if source.suffix.lower()=='.gz' else open
        try:
            digest=hashlib.sha256()
            with opener(source,'rb') as f, target.open('xb') as out:
                first=True
                for block in iter(lambda:f.read(1024*1024),b''):
                    if first and not block.lstrip().startswith(b'>'):raise ValueError('Not a FASTA header')
                    first=False;digest.update(block);out.write(block)
                if first:raise ValueError('Empty FASTA')
            record.update(status='STAGED',safe_path=str(target.absolute()),sha256_uncompressed=digest.hexdigest())
            ready.append(str(target.absolute()))
        except (OSError,ValueError,EOFError) as exc:
            record['status']='FAILED: '+str(exc)
        records.append(record)
    with (destination/'staging_manifest.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
    (destination/'ready_fasta_paths.txt').write_text(''.join(p+'\n' for p in ready),encoding='utf-8')
    print('Requested:',len(paths),'Staged:',len(ready),'Unresolved:',len(paths)-len(ready))
    print('Review:',destination/'staging_manifest.csv')
    return 0 if len(paths)==len(ready) else 2

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project',type=Path,required=True)
    p.add_argument('--paths-file',type=Path,required=True)
    p.add_argument('--destination',type=Path,required=True)
    a=p.parse_args()
    try:sys.exit(stage(a.project,a.paths_file,a.destination))
    except (OSError,ValueError) as e:sys.exit('STOP: '+str(e))
