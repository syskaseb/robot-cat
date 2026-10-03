"""Native integral raised saddles and eight T18I straps for joint-layout R3.

Feet at the solid Deck strips; straps pass BELOW locally raised roofs between
end feet, not through a new complex Deck Cut. Four accepted holder positions
and open-bottom cover are retained. Not a selected bank or full wire fit.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, sys, tempfile, shutil
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics'),str(ROOT/'tools/cad')]
from servo_fuse_inputs_r1 import sha,save
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-cradles-native-r1'
CAD=ROOT/'hardware/cad/studies/servo-fuse-rolled-cradles-native-r1'


def retained_owners(pin,load,Part):
    script=ROOT/'tools/electronics/servo_fuse_parent_complete_layout_r8.py'
    ns=dict(__file__=str(script),__name__='retained_definition_only')
    exec(compile(script.read_text(encoding='utf-8'),str(script),'exec'),ns)
    for rev in (5,6,7,8):pin(ROOT/f'tools/electronics/servo_fuse_parent_complete_layout_r{rev}.py')
    code=ns['code'];recipe=code[code.index('    # Reuse exact retained source recipe'):code.index('    basepath=')]
    ctx=dict(ROOT=ROOT,Part=Part,pin=pin,load=load,pins={},sha=sha,Path=Path)
    exec(compile('def receive():\n'+recipe+'\n    return owners,pins\n','retained_recipe','exec'),ctx)
    owners,pins=ctx['receive']()
    for rel,h in pins.items():
        assert sha(ROOT/rel)==h
        pin(ROOT/rel)
    owners['RetainedCover']=load(ROOT/'hardware/cad/studies/servo-fuse-main-reliefs-native-r1/Cover_WORLD.brep')
    return owners


def main():
    import FreeCAD as A
    import Part,MeshPart
    start=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists(),'Preserve completed results'
    pins={}
    def pin(p):pins[p.relative_to(ROOT).as_posix()]=sha(p)
    def load(p):pin(p);return Part.read(str(p))
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    def bounds(s):return [getattr(s.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]
    src=ROOT/'hardware/electronics/full-cat/servo-fuse-main-joint-layout-r3/checks.json';pin(src)
    joint=json.loads(src.read_text(encoding='utf-8'));assert not joint['hits'] and not joint['errors']
    stock=ROOT/'hardware/manufacturing/one-batch-prototype-r51/one-order-quantities.json';pin(stock)
    tie=next(r for r in json.loads(stock.read_text(encoding='utf-8'))['lines'] if r['id']=='tie:111-02370')
    assert tie['dimensions_mm']==dict(length=145,width=2.5,thickness=1.2,head_length=4.8,head_width=4.5,height_H=3.5)
    basepath=ROOT/'hardware/cad/studies/servo-fuse-parent-feed-grips-native-r2/DeckParentFeedGrips.FCStd';pin(basepath)
    base=load(ROOT/'hardware/cad/studies/servo-fuse-parent-feed-grips-native-r2/Deck_WORLD.brep')
    owners=retained_owners(pin,load,Part)
    changed={};feet=[];roofs=[];rows=[];straps=[];mount_failures=[]
    # Solid strip foot coordinates, not body-centre-only supports over windows.
    fy=dict(FL=(53,58),FR=(-60,-55.5),RL=(55.5,59.5),RR=(-94.5,-90.5))
    for row in joint['holders']:
        leg=row['leg'];b=row['bounds_mm'];cx,cy,cz=row['centre_mm'];ya,yb=fy[leg]
        ry0=min(b[1],ya);ry1=max(b[4],yb)
        roof=[b[0],ry0,b[2]-3,b[3],ry1,b[2]];roofs.append((leg,roof))
        body=load(ROOT/f'hardware/electronics/full-cat/servo-fuse-main-joint-layout-r3/{leg}_MTA_BODY.brep')
        changed[leg+'_MTA_BODY']=body
        for j,x in enumerate((b[0],b[3]-4)):
            foot=[x,ya,108.8,x+4,yb,b[2]-3]
            fs=box(foot);feet.append((leg+'Foot'+str(j),foot));changed[leg+'_Foot_'+str(j)]=fs
            expected=4*(yb-ya)*.2;actual=fs.common(base).Volume
            if abs(actual-expected)>1e-4:mount_failures.append(dict(leg=leg,foot=j,expected_mm3=expected,actual_mm3=actual))
        changed[leg+'_Roof']=box(roof)
        for j,x in enumerate((cx-9,cx+9)):
            z0=b[2]-4.2;z1=b[5]+1.2
            # Nominal tight bands touch outer surfaces, not holder internals.
            bands=[(x-1.25,ry0-1.2,z0,x+1.25,ry0,z1),
                (x-1.25,ry1,z0,x+1.25,ry1+1.2,z1),
                (x-1.25,ry0,z0,x+1.25,ry1,b[2]-3),
                (x-1.25,ry0,b[5],x+1.25,ry1,z1)]
            for k,q in enumerate(bands):changed[f'{leg}_Tie_{j}_Band_{k}']=box(q)
            head=[x-2.25,ry1-4.8,z1,x+2.25,ry1,z1+3.5]
            changed[f'{leg}_Tie_{j}_Head']=box(head)
            centreline=2*((ry1-ry0)+1.2+(z1-z0)-1.2)
            assert centreline+15<=145
            straps.append(dict(leg=leg,index=j,x_mm=x,sku='111-02370',centreline_mm=centreline,
                insertion_reserve_assumed_mm=15,available_length_mm=145,lower_band_z_mm=[z0,b[2]-3],head_bounds_mm=head))
        rows.append(dict(leg=leg,roof_bounds_mm=roof,body_bounds_mm=b,feet_y_mm=[ya,yb],
            intended_contact='Holder lower face on raised roof, two full feet on solid Deck strip; two body straps inserted under roof between feet.',
            PETG='Deck base down, roof bridge nominal22..27.5mm across; tune supports/bridging in phase2, no print-toolpath or creep qualification.'))
    save(OUT/'intent.json',dict(holders=rows,straps=straps,mount_failures=mount_failures,selected=False,physical_pass=False))
    print('CRADLES_AND_EIGHT_STRAPS_DEFINED',len(mount_failures),flush=True)
    d=A.openDocument(str(basepath));dest=CAD/'DeckRolledCradles.FCStd'
    try:
        p=d.addObject('App::VarSet','RolledCradleParameters');p.addProperty('App::PropertyLength','RoofThickness');p.RoofThickness=3
        objs=[]
        for name,b in feet+[(leg+'Roof',b) for leg,b in roofs]:
            o=d.addObject('Part::Box',name);o.Length=b[3]-b[0];o.Width=b[4]-b[1];o.Height=b[5]-b[2];o.Placement.Base=A.Vector(*b[:3])
            leg=name[:2];bottom=next(r['bounds_mm'][2] for r in joint['holders'] if r['leg']==leg)
            if name.endswith('Roof'):
                o.setExpression('Height','RolledCradleParameters.RoofThickness')
                o.setExpression('Placement.Base.z',f'{bottom} mm - RolledCradleParameters.RoofThickness')
            else:o.setExpression('Height',f'{bottom-108.8} mm - RolledCradleParameters.RoofThickness')
            objs.append(o)
        f=d.addObject('Part::MultiFuse','RolledCradlesFinished');f.Shapes=[d.ParentFeedGripFinished]+objs;f.Refine=False
        print('NATIVE_CRADLES_RECOMPUTE',flush=True);d.recompute();shape=f.Shape.copy()
        strict=shape.check(True);assert shape.isValid() and len(shape.Solids)==1 and not strict,str(strict)
        volume=shape.Volume;p.RoofThickness=3.2;d.recompute();probe=f.Shape.Volume;assert abs(probe-volume)>1
        for leg,b in roofs:assert abs(d.getObject(leg+'Roof').Shape.BoundBox.ZMax-b[5])<1e-6
        p.RoofThickness=3;d.recompute();assert abs(f.Shape.Volume-volume)<1e-5
        shape=f.Shape.copy();d.saveAs(str(dest));shape.exportBrep(str(CAD/'Deck_WORLD.brep'))
        mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
        assert mesh.isSolid() and mesh.countComponents()==1;bb=mesh.BoundBox;dims=[bb.XLength,bb.YLength,bb.ZLength]
        assert max(dims[0]+10,dims[1]+10)<256 and dims[2]<256
        mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin);mesh.write(str(CAD/'DeckRolledCradles_UNSELECTED.stl'))
    finally:A.closeDocument(d.Name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-rolled-cradles-') as td:
        q=Path(td)/dest.name;shutil.copy2(dest,q);re=A.openDocument(str(q))
        try:re.recompute();assert abs(re.RolledCradlesFinished.Shape.Volume-volume)<1e-5
        finally:A.closeDocument(re.Name)
    print('NATIVE_CRADLES_SAVED',flush=True)
    owners['CandidateDeck']=shape
    hits=[];errors=[];pairs=0
    def check(n,s,m,t):
        nonlocal pairs
        if not s.BoundBox.intersect(t.BoundBox):return
        pairs+=1
        try:
            h=s.common(t)
            if h.Volume>1e-5:
                hits.append(dict(part=n,owner=m,volume_mm3=h.Volume,bounds_mm=bounds(h)))
                h.exportBrep(str(OUT/f'HIT_{len(hits)}.brep'))
        except Exception as e:errors.append(dict(part=n,owner=m,error=str(e)))
    # Feet/roofs are integral Deck geometry. Check them against every retained
    # owner, but their union with their own Deck is intended, not a collision.
    for n,s in changed.items():
        s.exportBrep(str(OUT/(n+'_DESIGN.brep')))
        for m,t in owners.items():
            if m=='CandidateDeck' and ('_Foot_' in n or n.endswith('_Roof')):continue
            check(n,s,m,t)
        print('CRADLE_SHARED_FIT',n,len(hits),len(errors),flush=True)
    items=list(changed.items())
    for i,(n,s) in enumerate(items):
        for m,t in items[i+1:]:
            if n[:2]==m[:2] and (('_Foot_' in n and m.endswith('_Roof')) or ('_Foot_' in m and n.endswith('_Roof'))):continue
            check(n,s,m,t)
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='NATIVE_CRADLES_STRAPS_CONTACTS' if hits or errors or mount_failures else 'NATIVE_CRADLES_STRAPS_STATIC_CLEAR_FEEDS_SERVICE_OPEN',
        selected=False,physical_pass=False,W5_complete=False,holders=rows,straps=straps,mount_failures=mount_failures,
        native=dict(file=dest.relative_to(ROOT).as_posix(),final='RolledCradlesFinished',single_solid=True,strict_BOP_errors=0,closed_STL=True,relocated_reopen=True,
            parameter_mm=[3,3.2,3],volumes_mm3=[volume,probe,volume],dimensions_mm=dims,mating_body_floor_preserved=True),
        hits=hits,errors=errors,pairs=pairs,source_sha256=pins,script_sha256=sha(Path(__file__)),
        open=['Full eight feeds/joints/insulation grips and shared module removal still required.','Prototype MTA envelopes/factory100mm lead assumption and strap/bridge/load trials remain phase2.'],
        started_utc=start.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-start).total_seconds()))
    print(json.dumps(dict(hits=len(hits),errors=len(errors),mount_failures=len(mount_failures),pairs=pairs)),flush=True)


if __name__=='__main__':main()
