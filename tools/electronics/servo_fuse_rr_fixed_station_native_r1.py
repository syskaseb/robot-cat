"""Editable linked Deck integration of the accepted fixed RR station R2.

Keep both physical parents authoritative, not copied private bank/chassis.
Boxes/cylinders/sweeps rebuild the RR tray; linked native bank foot/post
drive its two clearance offsets. Probe the local mating parameter before
the expensive Deck union. Relocate all three documents and verify links.
This is a candidate, not a selected bank or qualified physical assembly.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys,shutil,tempfile
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rr-fixed-station-native-r1'
CAD=ROOT/'hardware/cad/studies/servo-fuse-rr-fixed-station-native-r1'

def main():
    import FreeCAD as A
    import Part,MeshPart
    start=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists(),'Preserve completed evidence'
    pins={}
    def pin(p):pins[p.relative_to(ROOT).as_posix()]=sha(p)
    def read(rel):p=ROOT/rel;pin(p);return json.loads(p.read_text(encoding='utf-8'))
    def load(rel):p=ROOT/rel;pin(p);return Part.read(str(p))
    proof=read('hardware/electronics/full-cat/servo-fuse-rr-fixed-station-r2/checks.json')
    assert not proof['hits'] and not proof['errors'] and proof['states']['solids']==1 and not proof['states']['BOP']
    pre=read('hardware/electronics/full-cat/servo-fuse-rear-output-stations-native-r3/preflight.json')
    final=read('hardware/electronics/full-cat/servo-fuse-rear-output-stations-parameter-r4/checks.json')
    deckrow=next(r for r in final['exports'] if r['tag']=='Deck')
    deckpath=ROOT/deckrow['file'];pin(deckpath)
    bankpath=ROOT/'hardware/cad/studies/servo-fuse-rear-output-reliefs-native-r1/BankRightRearOutputPassages.FCStd';pin(bankpath)
    target=load('hardware/electronics/full-cat/servo-fuse-rr-fixed-station-r2/RR_FIXED_FIXTURE.brep')
    dd=A.openDocument(str(deckpath));bd=A.openDocument(str(bankpath));d=A.newDocument('FixedRROutputDeck')
    dest=CAD/'DeckFixedRROutput.FCStd'
    # FreeCAD requires a saved owner before assigning external App::Links.
    d.saveAs(str(dest))
    try:
        p=d.addObject('App::VarSet','RRFixedParameters');p.addProperty('App::PropertyLength','Clearance');p.Clearance=.2
        def link(name,obj):
            q=d.addObject('App::Link',name);q.LinkedObject=obj;q.LinkTransform=False;return q
        parent=link('CurrentDeckParent',dd.getObject(deckrow['final']))
        bank=link('RemovableBankReference',bd.RearOutputPassagesFinished)
        foot=link('BankFoot57Reference',bd.RightFoot57);post=link('BankPost57Reference',bd.RightPost57)
        def box(name,b):
            q=d.addObject('Part::Box',name);q.Placement.Base=A.Vector(*b[:3])
            q.Length=b[3]-b[0];q.Width=b[4]-b[1];q.Height=b[5]-b[2];return q
        stock=[box('Fixed'+name,b) for name,b in pre['stocks'] if name.startswith('RR')]
        stock.append(box('FixedRRRoofBridge',[-75.5,-95,109.35,-67.5,-91,111.75]))
        tools=[]
        for name,z,od,pt,length in pre['grooves']:
            q=d.addObject('Part::Cylinder','Fixed'+name+'Groove');q.Height=length
            q.Placement=A.Placement(A.Vector(*pt),A.Rotation(A.Vector(0,0,1),A.Vector(1,0,0)))
            q.setExpression('Radius',f'{od/2} mm + RRFixedParameters.Clearance');tools.append(q)
        for name,b in pre['slots']+pre['strap_slots']:tools.append(box('Fixed'+name,b))
        routefolder='hardware/electronics/full-cat/servo-fuse-output-returns-complete-r8/'
        paths=[(ident+'_'+role,routefolder+ident+'_'+role+'_CENTERLINE.brep',od)
               for ident in ('W045','W053') for role,od in [('factory',5),('extension',4.2)]]
        paths += [(ident,'hardware/electronics/full-cat/servo-fuse-bank-connected-release-r4/release_0.0_'+ident+'_CENTERLINE.brep',3.1)
                  for ident in ('W038','W039')]
        for name,rel,od in paths:
            path=Part.Wire(load(rel).Edges);edge=path.Edges[0];normal=edge.tangentAt(edge.FirstParameter)
            route=d.addObject('Part::Feature','Fixed'+name+'PinnedRoute');route.Shape=path
            profile=d.addObject('Part::Circle','Fixed'+name+'Profile')
            profile.setExpression('Radius',f'{od/2} mm + RRFixedParameters.Clearance')
            profile.Placement=A.Placement(path.Vertexes[0].Point,A.Rotation(A.Vector(0,0,1),normal))
            sweep=d.addObject('Part::Sweep','Fixed'+name+'ClearanceSweep');sweep.Sections=[profile];sweep.Spine=(route,[]);sweep.Solid=True;sweep.Frenet=False;tools.append(sweep)
        for name,ref in [('Foot',foot),('Post',post)]:
            off=d.addObject('Part::Offset','Bank'+name+'Clearance');off.Source=ref
            off.setExpression('Value','RRFixedParameters.Clearance / 1 mm');tools.append(off)
        tools.append(bank)
        u=d.addObject('Part::MultiFuse','FixedRRStock');u.Shapes=stock;u.Refine=False
        t=d.addObject('Part::MultiFuse','FixedRRTools');t.Shapes=tools;t.Refine=False
        fixture=d.addObject('Part::Cut','FixedRRFixture');fixture.Base=u;fixture.Tool=t;fixture.Refine=False
        print('FIXED_RR_NATIVE_LOCAL_RECOMPUTE',flush=True);d.recompute()
        s=fixture.Shape.copy();assert s.isValid() and len(s.Solids)==1 and not s.check(True)
        delta=s.cut(target).Volume+target.cut(s).Volume
        assert delta<1e-5,('Preflight/native mismatch',delta)
        v=s.Volume;p.Clearance=.3;d.recompute();vp=fixture.Shape.Volume
        assert fixture.Shape.isValid() and len(fixture.Shape.Solids)==1 and abs(vp-v)>1e-5
        p.Clearance=.2;d.recompute();assert abs(fixture.Shape.Volume-v)<1e-5
        local=dict(parameter_mm=[.2,.3,.2],fixture_volumes_mm3=[v,vp,fixture.Shape.Volume],preflight_symmetric_difference_mm3=delta)
        fixture.Shape.exportBrep(str(OUT/'RR_FIXED_FIXTURE.brep'))
        f=d.addObject('Part::MultiFuse','FixedRROutputFinished');f.Shapes=[parent,fixture];f.Refine=False
        d.saveAs(str(dest));save(OUT/'local-preflight.json',dict(local,source_sha256=pins,physical_pass=False,selected=False))
        print('FIXED_RR_NATIVE_DECK_UNION',flush=True);d.recompute()
        ds=f.Shape.copy();print('FIXED_RR_NATIVE_DECK_BOP',flush=True)
        assert ds.isValid() and len(ds.Solids)==1 and not ds.check(True)
        dv=ds.Volume;d.saveAs(str(dest));ds.exportBrep(str(CAD/'Deck_WORLD.brep'))
        mesh=MeshPart.meshFromShape(Shape=ds,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
        assert mesh.isSolid() and mesh.countComponents()==1
        b=mesh.BoundBox;dims=[b.XLength,b.YLength,b.ZLength]
        assert dims[0]+10<256 and dims[1]+10<256 and dims[2]<256
        mesh.translate(-b.XMin,-b.YMin,-b.ZMin);mesh.write(str(CAD/'Deck_UNSELECTED.stl'))
        links=[dict(name=q.Name,file=q.LinkedObject.Document.FileName,target=q.LinkedObject.Name) for q in (parent,bank,foot,post)]
    finally:
        for doc in (d,dd,bd):A.closeDocument(doc.Name)
    # Preserve relative directory topology. Original source documents CLOSED.
    with tempfile.TemporaryDirectory(prefix='robot-cat-fixed-rr-relocate-') as td:
        temp=Path(td)
        for fp in (dest,deckpath,bankpath):
            targetpath=temp/fp.relative_to(ROOT);targetpath.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(fp,targetpath)
        r=A.openDocument(str(temp/dest.relative_to(ROOT)))
        try:
            r.recompute();assert abs(r.FixedRROutputFinished.Shape.Volume-dv)<1e-5
            assert r.FixedRRFixture.Shape.isValid() and len(r.FixedRRFixture.Shape.Solids)==1
            for name in ('CurrentDeckParent','RemovableBankReference','BankFoot57Reference','BankPost57Reference'):
                q=r.getObject(name);assert q.LinkedObject is not None
                assert Path(q.LinkedObject.Document.FileName).is_relative_to(temp),('Link escaped relocated tree',q.LinkedObject.Document.FileName)
            reopened=True
        finally:
            for name in list(A.listDocuments()):A.closeDocument(name)
    row=dict(tag='Deck',file=dest.relative_to(ROOT).as_posix(),final='FixedRROutputFinished',single_solid=True,strict_BOP_errors=0,
        closed_STL=True,relocated_reopen=reopened,dimensions_mm=dims,deck_volume_mm3=dv,local_mating_parameter=local,
        external_documents=[deckpath.relative_to(ROOT).as_posix(),bankpath.relative_to(ROOT).as_posix()],
        linked_targets=[dict(name=q['name'],target=q['target']) for q in links])
    save(OUT/'checks.json',dict(status='FIXED_RR_DECK_NATIVE_COMPLETE_SHARED_RELEASE_OPEN',selected=False,physical_pass=False,W5_complete=False,
        exports=[row],original_bank='hardware/cad/studies/servo-fuse-rear-output-reliefs-native-r1/BankRight_WORLD.brep',
        bank_mounts_preserved=4,wires_changed=False,purchased_parts_changed=False,installed_ties_changed=False,
        static_preflight='hardware/electronics/full-cat/servo-fuse-rr-fixed-station-r2/checks.json',
        common_module_lift_qualified=False,stock_delta=dict(additional_prints=0,fasteners=0,wires=0,straps=0,replacement='Deck'),
        source_sha256=pins,script_sha256=sha(Path(__file__)),started_utc=start.isoformat(),finished_utc=datetime.now(timezone.utc).isoformat(),
        worker_wall_seconds=(datetime.now(timezone.utc)-start).total_seconds()))
    print('FIXED_RR_NATIVE_COMPLETE',json.dumps(row),flush=True)
if __name__=='__main__':main()
