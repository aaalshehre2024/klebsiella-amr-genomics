#!/usr/bin/env python3
"""Freeze upload provenance; fold only byte-identical reuploads, then audit result tables.
Python standard library only. No network access, deletion, or biological exclusions.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,sys
from pathlib import Path
from audit_submission import audit

def canonicalize(input_dir: Path, specs: list[dict]):
    seen={}; canonical=[]; registry=[]
    for s in specs:
        source=input_dir/s['filename']
        digest=hashlib.sha256(source.read_bytes()).hexdigest()
        if digest != s['sha256']:
            raise ValueError('Input checksum differs: '+s['filename'])
        duplicate=seen.get(digest)
        if not duplicate:
            seen[digest]=s['package_id'];canonical.append(s)
        registry.append(dict(upload_id=s['package_id'],tranche=s.get('upload_tranche',''),filename=s['filename'],
            sha256=digest,bytes=source.stat().st_size,canonical_package_id=duplicate or s['package_id'],
            classification='BYTE_IDENTICAL_REUPLOAD' if duplicate else 'CHECKSUM_DISTINCT_PACKAGE'))
    return canonical,registry

def run(input_dir: Path, manifest: Path, out: Path):
    if out.exists():raise FileExistsError('Refusing to overwrite '+str(out))
    specs=json.loads(manifest.read_text(encoding='utf-8'))
    canonical,registry=canonicalize(input_dir,specs)
    out.mkdir(parents=True)
    selected=out/'canonical_package_selection.json'
    selected.write_text(json.dumps(canonical,indent=2),encoding='utf-8')
    with (out/'upload_registry.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(registry[0]));w.writeheader();w.writerows(registry)
    result=audit(input_dir,selected,out/'tables')
    result.update(upload_events=len(specs),new_upload_events=sum(s.get('upload_tranche')=='batch02' for s in specs),
        byte_identical_reuploads=len(specs)-len(canonical),unique_archive_payloads=len(canonical))
    (out/'combined_summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print('Combined audit:',out)
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir',type=Path,required=True)
    parser.add_argument('--manifest',type=Path,required=True)
    parser.add_argument('--output-dir',type=Path,required=True)
    a=parser.parse_args()
    try:run(a.input_dir,a.manifest,a.output_dir)
    except (OSError,ValueError) as e:sys.exit('STOP: '+str(e))
