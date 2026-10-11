"""Verify or replay exact archived BRep dependencies without overwriting files."""
import argparse,hashlib,json,zipfile
from pathlib import Path,PurePosixPath
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/aux-wiring-checkpoint'

def replay(verify_only=False):
    meta=json.loads((OUT/'retained-inputs.json').read_text())
    archive=OUT/'retained-inputs.zip'
    assert hashlib.sha256(archive.read_bytes()).hexdigest()==meta['zip_sha256']
    pending=[]
    with zipfile.ZipFile(archive) as z:
        assert set(z.namelist())=={r['path'] for r in meta['files']}
        for row in meta['files']:
            rel=PurePosixPath(row['path'])
            assert not rel.is_absolute() and '..' not in rel.parts and rel.suffix=='.brep'
            dest=(ROOT/str(rel)).resolve();assert dest.is_relative_to(ROOT.resolve())
            data=z.read(str(rel));assert hashlib.sha256(data).hexdigest()==row['sha256']
            if dest.exists():assert hashlib.sha256(dest.read_bytes()).hexdigest()==row['sha256'],str(dest)
            else:pending.append((dest,data))
    if not verify_only:
        for dest,data in pending:
            dest.parent.mkdir(parents=True,exist_ok=True)
            with dest.open('xb') as f:f.write(data)
    return dict(verified=len(meta['files']),missing=len(pending),restored=0 if verify_only else len(pending))
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--verify-only',action='store_true')
    print(json.dumps(replay(ap.parse_args().verify_only)))
