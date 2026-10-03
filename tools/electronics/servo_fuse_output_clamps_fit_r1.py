"""Changed upper keepers and the twelve REAL replacement loops, installed.

Use every current owner. Only each keeper's own bank union is intentional;
no exemption for wires, terminals, the other side or purchased parts. Loop
positions include the exact T18I planning head and both cinch slots.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-output-clamps-fit-r1'

def main():
    import FreeCAD as A
    import Part
    start=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists()
    loader=ROOT/'tools/electronics/servo_fuse_rr_clip_approach_r1.py'
    code=loader.read_text(encoding='utf-8');code=code[:code.index('    # These boxes are exactly')]
    code=code.replace('servo-fuse-rr-clip-approach-r1','servo-fuse-output-clamps-fit-r1')+'    return owners,pins,final\n'
    ns=dict(__file__=str(loader),__name__='owners_only');exec(compile(code,str(loader),'exec'),ns)
    owners,pins,_=ns['main']();pins[loader.relative_to(ROOT).as_posix()]=sha(loader)
    def load(rel):p=ROOT/rel;pins[rel]=sha(p);return Part.read(str(p))
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    folder='hardware/electronics/full-cat/servo-fuse-output-rib-exits-native-r3'
    proofpath=ROOT/folder/'checks.json';pins[proofpath.relative_to(ROOT).as_posix()]=sha(proofpath)
    proof=json.loads(proofpath.read_text(encoding='utf-8'))
    assert len(proof['exports'])==2 and len(proof['openings'])==12
    keys=dict(BankRight='Bank/RightClipAccessFinished_WORLD',BankLeft='Bank/LeftClipAccessFinished_WORLD')
    for tag,key in keys.items():owners[key]=load('hardware/cad/studies/servo-fuse-output-rib-exits-native-r3/'+tag+'_WORLD.brep')
    owners['CandidateDeck']=load('hardware/cad/studies/servo-fuse-rr-mount-pair-native-r1/Deck_WORLD.brep')
    removed=[]
    for key in list(owners):
        if '/servo-fuse-bank-restraints-' in key and '_INPUT_' not in key and key.endswith('_TIE_DESIGN'):
            removed.append(key);del owners[key]
        elif '/servo-fuse-bank-restraints-fit-' in key and '_INPUT_' not in key and key.endswith('_TIE_HEAD_RESERVE'):
            removed.append(key);del owners[key]
    hits=[];errors=[];pairs=0;targets={};bearing=[]
    def check(name,s,key,t):
        nonlocal pairs
        if not s.BoundBox.intersect(t.BoundBox):return
        pairs+=1
        try:
            c=s.common(t)
            if c.Volume>1e-5:
                hits.append(dict(part=name,owner=key,mm3=c.Volume,bounds_mm=[getattr(c.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]))
                c.exportBrep(str(OUT/f'HIT_{len(hits)}.brep'))
        except Exception as exc:errors.append(dict(part=name,owner=key,error=str(exc)))
    for spec in proof['openings']:
        ident=spec['id'];rb=spec['bearing_roof_bounds_mm'];cx=(rb[0]+rb[3])/2
        sy0,sy1=(137,140) if rb[1]>0 else (-140,-137)
        roof=load(folder+'/'+ident+'_ROOF_STOCK.brep')
        # Same exact native slots; remove them from small new stock, not a bbox waiver.
        slots=[box([cx+dx-1,sy0,rb[2]-.1,cx+dx+1,sy1,rb[5]+.1]) for dx in (-3.5,3.5)]
        roof=roof.cut(slots[0].fuse(slots[1]));targets[ident+'_UpperKeeper']=roof
        tie=load(folder+'/'+ident+'_UPWARD_TIE_DESIGN.brep');targets[ident+'_T18I']=tie
        for key,t in owners.items():
            if key!=keys[spec['owner']]:check(ident+'_UpperKeeper',roof,key,t)
            check(ident+'_T18I',tie,key,t)
        check(ident+'_T18I',tie,ident+'_UpperKeeper',roof)
        b=spec['hole_bounds_mm'];cz=(b[2]+b[5])/2
        assert abs(rb[2]-(cz+1.2))<1e-6
        bearing.append(dict(id=ident,upper_surface_tangent_to_planning_insulation=True,
            same_T18I_cinches_upwards=True,wire_OD_assumed_mm=2.4,physical_grip_qualified=False))
        print('UPPER_CLAMP_INSTALLED',ident,len(hits),len(errors),flush=True)
        if hits or errors:break
    names=list(targets)
    if not hits and not errors:
        for i,n in enumerate(names):
            for other in names[i+1:]:
                if n.split('_')[0]==other.split('_')[0]:continue
                check(n,targets[n],other,targets[other])
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='REJECTED' if hits or errors else 'TWELVE_UPPER_CLAMPS_AND_REPLACEMENT_LOOPS_STATIC_CLEAR',
        selected=False,physical_pass=False,W5_complete=False,pairs=pairs,hits=hits,errors=errors,
        checked_clamps=len(bearing),replaced_output_ties=12,removed_old_tie_geometry=removed,bearing=bearing,
        source_sha256=pins,script_sha256=sha(Path(__file__)),started_utc=start.isoformat(),finished_utc=end.isoformat(),
        worker_wall_seconds=(end-start).total_seconds()))
    print('UPPER_CLAMPS_FIT_COMPLETE',len(bearing),len(hits),len(errors),flush=True)

if __name__=='__main__':main()
