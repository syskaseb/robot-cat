"""Changed cover interfaces only; no full-E6 reload or physical qualification."""
from pathlib import Path
from datetime import datetime,timezone
import json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-cover-fit-r1'

def main():
    import FreeCAD as A
    import Part
    begin=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists()
    hashes={}
    def load(rel):
        p=ROOT/rel;hashes[rel]=sha(p);return Part.read(str(p))
    cover=load('hardware/cad/studies/servo-fuse-cover-native-r1/Cover_WORLD.brep')
    original=load('hardware/cad/studies/head-yaw-end-restraints-r1/CoverYawEndSeat.brep')
    removed=original.cut(cover);assert cover.cut(original).Volume<1e-5
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    preserved=[]
    for x in (-84,106):
        for side in (-1,1):
            lo,hi=sorted((side*88,side*102))
            v=removed.common(box([x-6,lo,109,x+6,hi,121])).Volume
            assert v<1e-5,(x,side,v)
            preserved.append(dict(kind='CoverMount',xy=[x,side*91],removed_mm3=v))
    for x in (-19,-4):
        zone=box([x-.2,132.9,134,x+2.2,139.1,140])
        v=removed.common(zone).Volume;assert v<1e-5
        preserved.append(dict(kind='ExistingHeadTieSlotAndRim',x=x,removed_mm3=v))
    obstacles={}
    for folder,pattern in [('hardware/cad/studies/servo-fuse-bank-native-r5','*_WORLD.brep'),
                           ('hardware/electronics/full-cat/servo-fuse-side-bank-r9','*_DESIGN.brep'),
                           ('hardware/electronics/full-cat/servo-fuse-bank-native-r5','*_DESIGN.brep'),
                           ('hardware/electronics/full-cat/servo-fuse-cover-neighbors-r1','CoverBracket_*.brep')]:
        for p in (ROOT/folder).glob(pattern):
            if p.stem.startswith(('Panel_','Post_','Allen','NutTool')):continue
            obstacles[folder+'/'+p.stem]=load(p.relative_to(ROOT).as_posix())
    rows=[];hits=[];errors=[]
    for lift in (0,5,15,30,50):
        s=cover.copy();s.translate(A.Vector(0,0,lift))
        for n,t in obstacles.items():
            if not s.BoundBox.intersect(t.BoundBox):continue
            try:
                v=s.common(t).Volume;row=dict(lift_mm=lift,owner=n,hit_mm3=v);rows.append(row)
                if v>1e-5:hits.append(row)
            except Exception as e:errors.append(dict(lift_mm=lift,owner=n,error=str(e)))
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='REJECTED' if hits or errors else 'CHANGED_COVER_CLEAR_SAMPLED',
        selected=False,physical_pass=False,W5_complete=False,hits=hits,errors=errors,pairs=len(rows),rows=rows,
        sampled_lifts_mm=[0,5,15,30,50],continuous_withdrawal_qualified=False,
        assembly_condition='Unplug head JR and release two existing head ties before removing cover. Bank bolts installed with cover removed; do not claim wrench access through closed cover.',
        preserved_interfaces=preserved,source_sha256=hashes,script_sha256=sha(Path(__file__)),
        started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds()))
    print(json.dumps(dict(hits=hits,errors=errors,pairs=len(rows))),flush=True)
if __name__=='__main__':main()
