"""One removable PETG side channel protects the accepted west FR return.

Separate small print keeps Cover/Bank within256mm with10mm brim allowance.
Two M3x8 DIN912/SKL000383 nuts from existing catalogue, new installed roles
not free/spare stock. Bank attachment has full bearing on actual panel.
Bench attach before laying wire; guard travels with bank during removal.
No physical stiffness, fit or full-bank service qualification.
"""
from pathlib import Path
from datetime import datetime,timezone
import sys,json,math,tempfile,shutil
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'tools/electronics'),str(ROOT/'tools/cad')]
from servo_fuse_inputs_r1 import sha,save
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-fr-return-guard-native-r1'
CAD=ROOT/'hardware/cad/studies/servo-fuse-fr-return-guard-native-r1'

def main():
    import FreeCAD as A
    import Part,MeshPart
    from servo_fuse_rolled_cradles_native_r1 import retained_owners
    start=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True);assert not (OUT/'checks.json').exists()
    pins={};V=A.Vector
    def pin(p):pins[p.relative_to(ROOT).as_posix()]=sha(p)
    def load(p):pin(p);return Part.read(str(p))
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],V(*b[:3]))
    def nbox(d,n,b):
        o=d.addObject('Part::Box',n);o.Length=b[3]-b[0];o.Width=b[4]-b[1];o.Height=b[5]-b[2];o.Placement.Base=V(*b[:3]);return o
    q=ROOT/'hardware/electronics/full-cat/servo-fuse-front-station-shared-fit-r1/checks.json';pin(q);prior=json.loads(q.read_text(encoding='utf-8'));assert not prior['hits'] and not prior['errors']
    q=ROOT/'hardware/manufacturing/one-batch-prototype-r51/one-order-quantities.json';pin(q);catalog=json.loads(q.read_text(encoding='utf-8'))
    screw=next(r for r in catalog['lines'] if r.get('supplier_sku')=='0912A2-M030X008VISK')
    nut=next(r for r in catalog['lines'] if r.get('supplier_sku')=='SKL000383')
    assert screw['dimensions_mm']==dict(d=3,L=8,b=8,head_d=5.5,head_h=3,key=2.5,pitch=.5)
    assert nut['dimensions_mm']['AF']==5.5 and nut['dimensions_mm']['H']==2.4
    owners=retained_owners(pin,load,Part);owners.pop('Bank/RightClipAccessFinished_WORLD');owners.pop('RetainedCover')
    owners['CandidateDeck']=load(ROOT/'hardware/cad/studies/servo-fuse-rolled-cradles-native-r7/Deck_WORLD.brep')
    owners['Cover']=load(ROOT/'hardware/cad/studies/servo-fuse-fr-joint-station-native-r1/Cover_WORLD.brep')
    for folder,pat in [('servo-fuse-front-source-ports-r2','*_DESIGN.brep'),('servo-fuse-main-joint-layout-r3','*_MTA_BODY.brep'),('servo-fuse-rolled-cradles-native-r7','*Tie*_DESIGN.brep'),('servo-fuse-fr-joint-station-native-r1','*Tie*_DESIGN.brep')]:
        for p in (ROOT/'hardware/electronics/full-cat'/folder).glob(pat):owners[folder+'/'+p.stem]=load(p)
    bankpath=ROOT/'hardware/cad/studies/servo-fuse-fr-joint-station-native-r1/BankRightFRJointStation.FCStd';pin(bankpath)
    bankbase=load(ROOT/'hardware/cad/studies/servo-fuse-fr-joint-station-native-r1/BankRight_WORLD.brep')
    guarddoc=A.newDocument('FRReturnGuard');bankdoc=A.openDocument(str(bankpath));exports=[]
    try:
        p=guarddoc.addObject('App::VarSet','GuardParameters');p.addProperty('App::PropertyLength','HoleDiameter');p.HoleDiameter=3.4
        bparam=bankdoc.addObject('App::VarSet','FRGuardParameters');bparam.addProperty('App::PropertyLength','HoleDiameter');bparam.HoleDiameter=3.4
        specs=[('OuterWall',[-116.5,-97,132.5,-114.5,85,167]),('RearWall',[-116.5,-97,132.5,-95,-95,167]),
               ('FrontWall',[-116.5,83,132.5,-95,85,167]),('Floor',[-116.5,-97,132.5,-95,85,134.5]),
               ('Roof',[-116.5,-97,165,-95,85,167]),('AttachmentTab',[-97,-97,146.5,-85,-91,149.5])]
        stocks=[nbox(guarddoc,n,b) for n,b in specs]
        gu=guarddoc.addObject('Part::MultiFuse','GuardStock');gu.Shapes=stocks;gu.Refine=False
        gtools=[];btools=[];hardware={};mounts=[]
        foot=box([-96,-97,146.4,-86,-91,146.5]);assert abs(bankbase.common(foot).Volume/.1-60)<1e-5
        for i,x in enumerate((-94,-88)):
            for d,par,tools in [(guarddoc,'GuardParameters',gtools),(bankdoc,'FRGuardParameters',btools)]:
                o=d.addObject('Part::Cylinder','GuardScrewTool'+str(i));o.Height=10;o.Placement.Base=V(x,-94,140)
                o.setExpression('Radius',par+'.HoleDiameter / 2');tools.append(o)
            shank=Part.makeCylinder(1.5,8,V(x,-94,141.5));head=Part.makeCylinder(2.75,3,V(x,-94,149.5))
            hardware[f'Screw{i}']=shank.fuse(head)
            rad=5.5/math.sqrt(3);vs=[V(x+rad*math.cos(math.pi/6+k*math.pi/3),-94+rad*math.sin(math.pi/6+k*math.pi/3),142.3) for k in range(6)]
            solid=Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(V(0,0,2.4)).cut(Part.makeCylinder(1.5,2.6,V(x,-94,142.2)))
            hardware[f'Nut{i}']=solid
            # Real ring bearing of the nominal5.5mm screw head on tab/panel.
            ring=Part.makeCylinder(2.75,.1,V(x,-94,146.4)).cut(Part.makeCylinder(1.7,.2,V(x,-94,146.35)))
            assert abs(bankbase.common(ring).Volume-ring.Volume)<1e-5
            mounts.append(dict(x_mm=x,y_mm=-94,bank_surface_z_mm=146.5,tab_thickness_mm=3,bank_panel_mm=1.8,
                               screw_length_mm=8,nut_height_mm=2.4,nominal_thread_beyond_nut_mm=.8,full_ring_bearing=True))
        gh=guarddoc.addObject('Part::MultiFuse','GuardTools');gh.Shapes=gtools
        gf=guarddoc.addObject('Part::Cut','FRReturnGuardFinished');gf.Base=gu;gf.Tool=gh;gf.Refine=False
        bh=bankdoc.addObject('Part::MultiFuse','FRGuardHoleTools');bh.Shapes=btools
        bf=bankdoc.addObject('Part::Cut','FRGuardBankFinished');bf.Base=bankdoc.getObject('FRJointStationFinished');bf.Tool=bh;bf.Refine=False
        print('FR_GUARD_NATIVE_RECOMPUTE',flush=True);guarddoc.recompute();bankdoc.recompute()
        guard=gf.Shape.copy();bank=bf.Shape.copy()
        for s in (guard,bank):assert s.isValid() and len(s.Solids)==1 and not s.check(True)
        changed=dict(hardware,Guard=guard);owners['NativeBank']=bank
        pairs=0;hits=[];errors=[]
        for n,s in changed.items():
            for m,t in owners.items():
                if not s.BoundBox.intersect(t.BoundBox):continue
                pairs+=1
                try:
                    h=s.common(t)
                    if h.Volume>1e-5:hits.append(dict(part=n,owner=m,volume_mm3=h.Volume))
                except Exception as ex:errors.append(dict(part=n,owner=m,error=str(ex)))
        # Guard/head/nut contacts are bearing faces, not penetrating solids.
        for n,s in hardware.items():
            h=s.common(guard)
            if h.Volume>1e-5:hits.append(dict(part=n,owner='Guard',volume_mm3=h.Volume))
        source=owners['servo-fuse-front-source-ports-r2/W042_extension_DESIGN']
        external=source.common(box([-250,-200,0,-98,200,250]))
        cavity=box([-114.5,-95,134.5,-94.5,83,165])
        uncovered=external.cut(cavity).Volume
        assert external.Volume>0
        save(OUT/'fit.json',dict(pairs=pairs,hits=hits,errors=errors,external_source_mm3=external.Volume,
                               external_source_outside_guard_cavity_mm3=uncovered,selected=False,physical_pass=False))
        if hits or errors or uncovered>1e-5:
            guard.exportBrep(str(OUT/'Guard_REJECTED.brep'));bank.exportBrep(str(OUT/'Bank_REJECTED.brep'))
        assert not hits and not errors and uncovered<1e-5,(hits,uncovered)
        for d,par,f,s,tag,name in [(guarddoc,p,gf,guard,'Guard','FRReturnGuard.FCStd'),(bankdoc,bparam,bf,bank,'BankRight','BankRightFRGuard.FCStd')]:
            v=s.Volume;par.HoleDiameter=3.6;d.recompute();probe=f.Shape.Volume;assert probe<v
            par.HoleDiameter=3.4;d.recompute();assert abs(f.Shape.Volume-v)<1e-5
            for o in d.Objects:
                if hasattr(o,'Visibility'):o.Visibility=False
            f.Visibility=True;dest=CAD/name;d.saveAs(str(dest));s.exportBrep(str(CAD/(tag+'_WORLD.brep')))
            mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
            assert mesh.isSolid() and mesh.countComponents()==1
            # Roof/down for Bank; guard's long outer wall flat on the bed.
            if tag=='BankRight':mesh.rotate(math.pi,0,0)
            else:mesh.rotate(0,math.pi/2,0)
            bb=mesh.BoundBox;dims=[bb.XLength,bb.YLength,bb.ZLength];assert bb.XLength+10<256 and bb.YLength+10<256 and bb.ZLength<256
            mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin);mesh.write(str(CAD/(tag+'_UNSELECTED.stl')))
            with tempfile.TemporaryDirectory(prefix='robot-cat-fr-guard-') as td:
                moved=Path(td)/dest.name;shutil.copy2(dest,moved);re=A.openDocument(str(moved))
                try:re.recompute();assert abs(re.getObject(f.Name).Shape.Volume-v)<1e-5
                finally:A.closeDocument(re.Name)
            exports.append(dict(tag=tag,file=dest.relative_to(ROOT).as_posix(),final=f.Name,single_solid=True,strict_BOP_errors=0,
                                closed_STL=True,relocated_reopen=True,dimensions_mm=dims,parameter_volumes_mm3=[v,probe,v]))
        for n,s in hardware.items():s.exportBrep(str(OUT/(n+'_DESIGN.brep')))
    finally:A.closeDocument(guarddoc.Name);A.closeDocument(bankdoc.Name)
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='FR_EXTERNAL_RETURN_GUARD_STATIC_NATIVE_COMPLETE_SERVICE_OPEN',selected=False,physical_pass=False,W5_complete=False,
        exports=exports,mounts=mounts,pairs=pairs,hits=hits,errors=errors,external_source_outside_guard_cavity_mm3=uncovered,
        stock_delta=dict(new_prints=1,installed_M3x8=2,screw_SKU='0912A2-M030X008VISK',installed_M3nuts=2,nut_SKU='SKL000383',new_fastener_SKUs=0),
        recipe=['Removed unpowered bank: mount side channel with2M3x8 and2nuts before routing FR, underside nuts accessible before other parts.',
                'Lay the west source return through the open inboard face, prepare the opposing lap, close its two insulation ties.',
                'Guard stays attached to bank through whole-bank removal; removing guard alone first requires disconnecting source and releasing FR insulation ties.'],
        open=['Guard cantilever/PETG deflection/pull retention and tie/tool access with delivered parts require phase2 trials, not physical PASS.',
              'Full-bank source disconnection/lever access/removal, other feeds and final stock/E3/selection remain OPEN.'],
        source_sha256=pins,script_sha256=sha(Path(__file__)),started_utc=start.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-start).total_seconds()))
    print(json.dumps(dict(exports=len(exports),pairs=pairs,hits=len(hits),additional_prints=1)),flush=True)
if __name__=='__main__':main()
