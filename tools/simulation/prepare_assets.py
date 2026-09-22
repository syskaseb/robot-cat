"""Restore checksummed generated numeric inputs and CAD meshes locally."""
import argparse,hashlib,zipfile
from cad_model import ROOT,REVISION


def restore(base,name):
    p=base/(name+'.zip');expected=p.with_suffix('.sha256').read_text().split()[0]
    assert hashlib.sha256(p.read_bytes()).hexdigest()==expected,p
    with zipfile.ZipFile(p) as archive:
        for member in archive.infolist():
            target=(base/member.filename).resolve()
            assert target.is_relative_to(base.resolve()),member.filename
            assert not member.is_dir() and target.suffix in ('.json','.stl'),member.filename
        archive.extractall(base)
    print('Restored',p.relative_to(ROOT))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--revision',choices=['v27','v28','v29','v30','v31','v32','v33','v34','v35'],default=REVISION)
    parser.add_argument('--metadata-only',action='store_true')
    parser.add_argument('--history',action='store_true',help='also restore v27 inputs for the incremental cover audit')
    args=parser.parse_args();base=ROOT/'hardware/simulation'/args.revision
    restore(base,'inputs')
    if not args.metadata_only:restore(base,'meshes')
    if args.history and args.revision!='v27':restore(ROOT/'hardware/simulation/v27','inputs')


if __name__=='__main__':main()
