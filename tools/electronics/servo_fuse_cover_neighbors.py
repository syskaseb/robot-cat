"""Exact selected cover brackets against changed bank; cached cover only.

No replacement/selection. Missing neighboring owners must not imply clearance.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/cad'),str(ROOT/'tools/electronics')]
from servo_fuse_inputs_r1 import save, sha

def main():
    import FreeCAD as A
    import Part
    from check_main_p0_placement import SavedShapes
    import servo_fuse_side_bank_r9 as layout
    started=datetime.now(timezone.utc)
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-cover-neighbors-r1'
    out.mkdir(parents=True,exist_ok=True)
    assert not (out/'checks.json').exists()
    reader=SavedShapes();native=ROOT/'hardware/cad/studies/upper-cover-mount-r1/CoverBracket.FCStd'
    bracket=reader.shape(native,'CoverBracket')
    owners,hashes,_=layout.current_owners()
    current_bracket_names=[n for n in owners if 'coverbracket' in n.lower()]
    neighbors={}
    for x in (-84,106):
        for side in (-1,1):
            s=bracket.copy()
            if side<0:s.rotate(A.Vector(),A.Vector(0,0,1),180)
            s.translate(A.Vector(x,side*88,109))
            n=f'CoverBracket_{x}_{side}';neighbors[n]=s
            s.exportBrep(str(out/(n+'.brep')))
    changed={}
    for folder,pattern in [('hardware/cad/studies/servo-fuse-bank-native-r3','*_WORLD.brep'),
                           ('hardware/electronics/full-cat/servo-fuse-bank-native-r3','*_DESIGN.brep'),
                           ('hardware/electronics/full-cat/servo-fuse-side-bank-r9','*_DESIGN.brep')]:
        for p in (ROOT/folder).glob(pattern):
            if p.stem.startswith(('Post_','Panel_')):continue
            changed[folder+'/'+p.stem]=Part.read(str(p));hashes[p.relative_to(ROOT).as_posix()]=sha(p)
    hits=[];errors=[];pairs=0
    for n,s in changed.items():
        for m,t in neighbors.items():
            if not s.BoundBox.intersect(t.BoundBox):continue
            pairs+=1
            try:
                c=s.common(t)
                if c.Volume>1e-5:hits.append(dict(part=n,owner=m,hit_mm3=c.Volume,bounds_mm=[getattr(c.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]))
            except Exception as e:errors.append(dict(part=n,owner=m,error=str(e)))
    ended=datetime.now(timezone.utc)
    save(out/'checks.json',dict(selected=False,physical_pass=False,existing_cache_bracket_names=current_bracket_names,
        added_actual_selected_brackets=list(neighbors),hits=hits,errors=errors,pairs=pairs,
        source_sha256={**hashes,**reader.hashes},script_sha256=sha(Path(__file__)),
        started_utc=started.isoformat(),finished_utc=ended.isoformat(),worker_wall_seconds=(ended-started).total_seconds()))
    print(json.dumps(dict(hits=hits,errors=errors,existing_cache_bracket_names=current_bracket_names)),flush=True)
if __name__=='__main__':main()
