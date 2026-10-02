"""Changed output ribs/slots/ties against actual bank, leads and neighbors."""
from pathlib import Path
from datetime import datetime,timezone
import sys,json
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics'),str(ROOT/'tools/cad')]
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-restraints-fit-r1'

def main():
    import FreeCAD as A
    import Part
    import servo_fuse_side_bank_r9 as layout
    begin=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True);assert not (OUT/'checks.json').exists()
    hashes={}
    def load(p):
        p=Path(p);hashes[p.relative_to(ROOT).as_posix()]=sha(p);return Part.read(str(p))
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    owners,h,_=layout.current_owners();hashes.update(h)
    owners.pop('R49Deck');owners['CandidateDeck']=load(ROOT/'hardware/electronics/full-cat/servo-fuse-bank-native-r5/Deck_candidate_UNSELECTED.brep')
    for folder,pattern in [('hardware/electronics/full-cat/servo-fuse-side-bank-r9','*_DESIGN.brep'),
                           ('hardware/electronics/full-cat/servo-fuse-bank-native-r5','*_DESIGN.brep'),
                           ('hardware/electronics/full-cat/servo-fuse-bank-outputs-r1','*_LOCAL_DESIGN.brep'),
                           ('hardware/electronics/full-cat/servo-fuse-cover-neighbors-r1','CoverBracket_*.brep')]:
        for p in (ROOT/folder).glob(pattern):
            if p.stem.startswith(('Panel_','Post_','Allen','NutTool')):continue
            owners[folder+'/'+p.stem]=load(p)
    parts={p.stem:load(p) for p in (ROOT/'hardware/cad/studies/servo-fuse-bank-restraints-r1').glob('*_WORLD.brep')}
    target={**parts}
    for p in (ROOT/'hardware/electronics/full-cat/servo-fuse-bank-restraints-r1').glob('*_TIE_DESIGN.brep'):target[p.stem]=load(p)
    meta_path=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-outputs-r1/checks.json';hashes[meta_path.relative_to(ROOT).as_posix()]=sha(meta_path)
    metadata=json.loads(meta_path.read_text(encoding='utf-8'))
    for row in metadata['lengths']:
        x,y,z=row['bank_exit_mm'];side=1 if y>0 else -1
        lo,hi=sorted((side*136,side*141))
        head=box([x+4.5,lo,z-7.4,x+10.5,hi,z-3.4])
        target[row['id']+'_TIE_HEAD_RESERVE']=head;head.exportBrep(str(OUT/(row['id']+'_TIE_HEAD_RESERVE.brep')))
    hits=[];errors=[];pairs=0
    def check(n,s,m,t):
        nonlocal pairs
        if not s.BoundBox.intersect(t.BoundBox):return
        pairs+=1
        try:
            c=s.common(t)
            if c.Volume>1e-5:hits.append(dict(part=n,owner=m,hit_mm3=c.Volume,bounds_mm=[getattr(c.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]))
        except Exception as e:errors.append(dict(part=n,owner=m,error=str(e)))
    for n,s in target.items():
        for m,t in owners.items():
            # Holder flange/latch conservatively reserved in its own aperture;
            # same explicit nominal seating condition as nativeR5, not waived wires.
            if n.endswith('_WORLD') and '/servo-fuse-side-bank-r9/F_' in m and not any(k in m for k in ('_ATO_','_IN_','_OUT_')):continue
            check(n,s,m,t)
        if not n.endswith('_WORLD'):
            for m,t in parts.items():check(n,s,m,t)
    slot_path=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-restraints-r1/checks.json';hashes[slot_path.relative_to(ROOT).as_posix()]=sha(slot_path)
    slot_checks=[]
    for spec in json.loads(slot_path.read_text(encoding='utf-8'))['slots']:
        b=spec['box_mm'];probe=box([b[0]+.1,b[1]+.1,b[2],b[3]-.1,b[4]-.1,b[5]])
        v=sum(probe.common(s).Volume for s in parts.values());assert v<1e-5
        slot_checks.append(dict(id=spec['id'],full_depth_clear=True,hit_mm3=v))
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='REJECTED' if hits or errors else 'OUTPUT_RESTRAINTS_CLEAR_COVER_INPUTS_LEGS_OPEN',
        selected=False,physical_pass=False,W5_complete=False,hits=hits,errors=errors,pairs=pairs,slot_checks=slot_checks,
        new_ties=12,tie_head_reservation_mm=[6,5,4],delivered_tie_head_verified=False,
        source_sha256=hashes,script_sha256=sha(Path(__file__)),started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds()))
    print(json.dumps(dict(hits=hits,errors=errors,pairs=pairs)),flush=True)
if __name__=='__main__':main()
