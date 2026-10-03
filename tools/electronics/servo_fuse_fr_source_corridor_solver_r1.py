"""Bounded whole-route fit for FR source X-offset, all current owners.

R11 factory/lap is retained. One scalar (-4..6mm) is solved against actual
fixed wires, holders, Deck and body ties, not only the last colliding item.
Cover is explicitly NOT accepted: its new passages/protection are next.
No supplier length, physical bend/clearance, native grip or stock PASS.
"""
from pathlib import Path
from datetime import datetime,timezone
import sys,json,math
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics'),str(ROOT/'tools/cad')]
from servo_fuse_inputs_r1 import sha,save
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-fr-source-corridor-solver-r1'

def main():
    import FreeCAD as A
    import Part
    from servo_fuse_rolled_cradles_native_r1 import retained_owners
    start=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists()
    pins={}
    def pin(p):pins[p.relative_to(ROOT).as_posix()]=sha(p)
    def load(p):pin(p);return Part.read(str(p))
    script=ROOT/'tools/electronics/servo_fuse_parent_complete_layout_r5.py';pin(script)
    text=script.read_text(encoding='utf-8');defs=text[text.index('    class Route:'):text.index('    X=V')]
    ctx=dict(V=A.Vector,math=math,Part=Part)
    exec(compile('def define():\n'+defs+'\n    return Route\n','route_builder','exec'),ctx)
    Route=ctx['define']();V=A.Vector;X=V(1,0,0);Z=V(0,0,1);N=V(0,1,0);S=-N
    folder=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-source-loop-r11'
    q=folder/'checks.json';pin(q);prior=json.loads(q.read_text(encoding='utf-8'))
    assert not prior['errors'] and not prior['factory_failures']
    owners=retained_owners(pin,load,Part)
    owners['CandidateDeck']=load(ROOT/'hardware/cad/studies/servo-fuse-rolled-cradles-native-r7/Deck_WORLD.brep')
    owners['Bank/RightClipAccessFinished_WORLD']=load(ROOT/'hardware/cad/studies/servo-fuse-feed-reliefs-native-r6/BankRight_WORLD.brep')
    owners.pop('RetainedCover')
    for p in (ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-cradles-native-r7').glob('*Tie*_DESIGN.brep'):
        owners['BodyStrap/'+p.stem]=load(p)
    for p in (ROOT/'hardware/electronics/full-cat/servo-fuse-main-joint-layout-r3').glob('*_MTA_BODY.brep'):
        owners[p.stem]=load(p)
    for p in folder.glob('*_DESIGN.brep'):
        if p.stem.startswith('W042') and p.stem!='W042_factory_DESIGN':continue
        owners['Feed/'+p.stem]=load(p)
    joint=next(r for r in prior['joints'] if r['id']=='W042')
    joint_y=joint['centre_mm'][1];joint_z=joint['centre_mm'][2]
    results=[];accepted=None
    # Prefer smallest displacement from the unoffset WAGO axis.
    for dx in (0,1,-1,2,-2,3,-3,4,-4,5,6):
        e=Route([-24,11,113.5]);e.shift(N,V(dx,0,24),25.2)
        e.arc(N,-X,25.2);assert e.p.y+2.1<89
        e.line([-85.5,e.p.y,137.5]);e.arc(-X,S,25.2)
        e.shift(S,Z*(joint_z-137.5),25.2)
        e.line([-110.7,joint_y+25.2,joint_z]);e.arc(S,X,25.2)
        e.line([-68.5,joint_y,joint_z]);assert e.edges[-1].Length>=16
        path,tube=e.shape(4.2,N);hits=[];errors=[];pairs=0
        for n,s in owners.items():
            if not tube.BoundBox.intersect(s.BoundBox):continue
            pairs+=1
            try:
                h=tube.common(s)
                if h.Volume>1e-5:hits.append(dict(owner=n,volume_mm3=h.Volume))
            except Exception as ex:errors.append(dict(owner=n,error=str(ex)))
        result=dict(source_dx_mm=dx,path_mm=path.Length,pairs=pairs,hits=hits,errors=errors)
        results.append(result);print('WHOLE_FR_SOURCE_OFFSET',dx,len(hits),len(errors),flush=True)
        if not hits and not errors:
            accepted=result;path.exportBrep(str(OUT/'W042_extension_CENTERLINE.brep'))
            tube.exportBrep(str(OUT/'W042_extension_DESIGN.brep'));break
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='SOURCE_FIXED_OWNERS_CLEAR_CASING_GRIPS_OPEN' if accepted else 'NO_CLEAR_SOURCE_OFFSET',
        selected=False,physical_pass=False,W5_complete=False,accepted=accepted,results=results,
        retained_factory_report=q.relative_to(ROOT).as_posix(),
        open=['Native cover passages/exterior protection and two-sided insulation grips, service and stock.'],
        source_sha256=pins,script_sha256=sha(Path(__file__)),started_utc=start.isoformat(),
        finished_utc=end.isoformat(),worker_wall_seconds=(end-start).total_seconds()))
    print(json.dumps(dict(accepted=accepted,attempts=len(results))),flush=True)

if __name__=='__main__':main()
