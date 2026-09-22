"""Losslessly archive bulky generated assets without deleting local originals."""
from pathlib import Path
import hashlib
import zipfile
from cad_model import ROOT,OUT


def archive(target,paths,base):
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(paths):
            # Stable archive metadata: extracting/repacking identical numeric
            # inputs must not create a fresh multi-megabyte Git change.
            info=zipfile.ZipInfo(p.relative_to(base).as_posix(),date_time=(1980,1,1,0,0,0))
            info.external_attr=0o100644<<16
            z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
    digest=hashlib.sha256(target.read_bytes()).hexdigest()
    target.with_suffix('.sha256').write_text(digest+'  '+target.name+'\n',encoding='ascii')
    print(target.relative_to(ROOT),target.stat().st_size,digest)


def main():
    old=ROOT/'hardware/simulation/v25'
    paths=[p for p in old.rglob('*') if p.is_file() and p.suffix in ('.json','.sdf','.log')]
    if paths:archive(old/'superseded.zip',paths,old)
    for revision in ['v27','v28']:
        base=ROOT/'hardware/simulation'/revision
        paths=[base/n for n in ['geometry.json','model.json','stance-search.json'] if (base/n).exists()]
        if paths:archive(base/'inputs.zip',paths,base)
    archive(OUT/'meshes.zip',(OUT/'meshes').glob('*.stl'),OUT)
    paths=[p for p in (OUT/'trials').glob('*') if p.suffix in ('.json','.sdf','.log')]
    archive(OUT/'telemetry.zip',paths,OUT)


if __name__=='__main__':main()
