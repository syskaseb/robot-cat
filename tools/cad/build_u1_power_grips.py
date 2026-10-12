"""Native shared MAIN/USB/G_TAIL grips; no historical assembly overwritten."""
import json,time,tempfile,shutil
from pathlib import Path
import FreeCAD as A
import MeshPart
from open_deck_p0_supports import sketch
from open_deck_p0_plate import rect,circle
from build_u1_grouped_grips import validate
import plan_u1_power_grips as P
ROOT,OUT,BASE,SHA=P.ROOT,P.OUT,P.BASE,P.SHA


def run():
    tick=time.monotonic();gf=OUT/'u1-power-grips-checks.json';pf=OUT/'u1-power-grips-plan.json'
    g=json.loads(gf.read_text());p=json.loads(pf.read_text())
    assert g['status']=='POWER_GRIPS_SHARED_CLEAR_NATIVE_OPEN' and not g['contacts'] and not g['errors']
    for n,h in g['source_sha256'].items():assert SHA(ROOT/n)==h,n
    assert p==json.loads(json.dumps({k:v for k,v in P.allocation().items() if k!='bands'}))
    model=OUT/'U1PowerGripsCurrent.FCStd';assert not model.exists(),'Receive existing native first'
    d=A.newDocument('U1PowerGripsCurrent');original={}
    for name,f in [('LowerCarrier001',OUT/'U1InterfaceCarriersCurrent.FCStd'),
                   ('E2Fixture',BASE/'aux-wiring-checkpoint/AUXPowerCurrent.FCStd')]:
        src=A.openDocument(str(f));b=d.copyObject(src.getObject(name),True);original[name]=b.Shape.copy()
        A.closeDocument(src.Name)
    main=d.addObject('PartDesign::Body','MAINGrip')
    par=d.addObject('App::VarSet','PowerGripParameters')
    par.addProperty('App::PropertyLength','MainRailThickness');par.MainRailThickness=2
    expected={};volumes={}
    for name in ('MAINGrip','LowerCarrier001','E2Fixture'):
        b=d.getObject(name);inv=b.Placement.inverse()
        rows=[v for v in p['pads'] if v['owner']==name]
        if name=='MAINGrip':
            priority=['Foot0','FootRoot0','Post0','Rail','FootRoot1','Foot1','Post1','TopReturn','InsulationSeat']
            rows.sort(key=lambda v:priority.index(v['name']))
        for v in rows:
            n='Power'+v['name'];old=b.Tip
            if v.get('kind')=='disc':
                a=inv.multVec(A.Vector(*v['centre_mm']));sk=sketch(b,n+'Plan',a.z)
                circle(sk,a.x,a.y,2*v['radius_mm']);h=v['height_mm']
            else:
                a=inv.multVec(A.Vector(*v['bounds_mm'][:3]));z=inv.multVec(A.Vector(*v['bounds_mm'][3:]))
                sk=sketch(b,n+'Plan',a.z);rect(sk,a.x,a.y,z.x-a.x,z.y-a.y);h=z.z-a.z
            ob=b.newObject('PartDesign::Pad',n);ob.Profile=sk
            if old:ob.BaseFeature=old
            ob.Refine=True
            if v['name']=='Rail':ob.setExpression('Length','PowerGripParameters.MainRailThickness')
            else:ob.Length=h
            b.Tip=ob;sk.Visibility=False;d.recompute()
        if name=='MAINGrip':
            old=b.Tip;sk=sketch(b,'PowerActualMAINAxes',65)
            for x,y in P.AXES:circle(sk,x,y,2.4)
            ob=b.newObject('PartDesign::Pocket','PowerMAINBoltBores');ob.Profile=sk;ob.BaseFeature=old
            ob.Length=20;ob.Refine=True;b.Tip=ob;d.recompute()
        validate(b);s=P.material(rows[0]).multiFuse([P.material(v) for v in rows[1:]])
        if name=='MAINGrip':
            for x,y in P.AXES:s=s.cut(P.Part.makeCylinder(1.2,15,A.Vector(x,y,45)))
        else:
            s=original[name].fuse(s)
            assert original[name].cut(s).Volume<1e-5,'Retained material removed'
        s=s.removeSplitter();difference=[b.Shape.cut(s).Volume,s.cut(b.Shape).Volume]
        assert max(difference)<1e-5,(name,difference)
        expected[name]=s;volumes[name]=b.Shape.Volume
        print('Power grip native',name,round(time.monotonic()-tick,2),flush=True)
    par.MainRailThickness=2.2;d.recompute();validate(main)
    assert main.Shape.Volume>volumes['MAINGrip']
    par.MainRailThickness=2;d.recompute()
    for name,v in volumes.items():validate(d.getObject(name));assert abs(d.getObject(name).Shape.Volume-v)<1e-5
    for n,s in P.allocation()['bands'].items():
        o=d.addObject('Part::Feature','Installed_'+n);o.Shape=s
        o.addProperty('App::PropertyString','Evidence')
        o.Evidence=('802534B max1.6764x0.381; knot envelope provisional' if n.startswith('GTail')
                    else 'T18R band2.5x1; head/closing envelope provisional')+'; phase2 fit gate'
    for n,s in P.main_hardware().items():
        o=d.addObject('Part::Feature',n);o.Shape=s
        o.addProperty('App::PropertyString','Evidence');o.Evidence='Existing source stack; two upper washers replaced by1mmfeet, M2x12+.7Z, not extra hardware'
    d.saveAs(str(model));A.closeDocument(d.Name);exports=[]
    with tempfile.TemporaryDirectory(prefix='robot-cat-power-grips-') as td:
        copy=Path(td)/model.name;shutil.copy2(model,copy);d=A.openDocument(str(copy));d.recompute()
        for name,v in volumes.items():
            b=d.getObject(name);validate(b);assert abs(b.Shape.Volume-v)<1e-5
            s=b.Shape.copy();bb=s.BoundBox;s.translate(A.Vector(-bb.XMin,-bb.YMin,-bb.ZMin))
            mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.04,AngularDeflection=.15,Relative=False)
            assert mesh.isSolid() and not mesh.hasNonManifolds() and mesh.countComponents()==1
            bb=mesh.BoundBox;size=[bb.XLength,bb.YLength,bb.ZLength];assert max(size)+10<256
            f=OUT/(name+'_power_grips_x1.stl');mesh.write(str(f))
            exports.append(dict(part=name,quantity=1,path=f.relative_to(ROOT).as_posix(),sha256=SHA(f),size_mm=size,brim_each_mm=5,
                orientation='Foot/floor down; cantilever supports/coupon in phase2, no slicer approval'))
        A.closeDocument(d.Name)
    r=dict(status='U1_POWER_GRIPS_NATIVE_PREPARED_SERVICE_SELECTION_OPEN',native=model.relative_to(ROOT).as_posix(),native_sha256=SHA(model),
        exports=exports,editable_parts=3,parameter_restore_mm=[2,2.2,2],relocated_reopen=True,
        new_T18R=p['new_T18R'],lacing_blanks_mm=p['lacing_blanks_mm'],new_metal_fasteners=0,MAIN_upper_washers_removed=2,MAIN_screw_raise_mm=.7,
        MAIN_nut_protrusion_mm=.5252,MAIN_common_land_mm=3,
        replaced_parts=['LowerCarrier001 U1InterfaceCarriersCurrent print','E2Fixture AUXPowerCurrent print'],
        service=['No sources/USB connected; support wires, cut dedicated band before board or USB withdrawal.',
                 'MAIN grip uses both existingM2 mount axes; release all4cores before loosening either board screw.',
                 'Short3mm common insulated land requires gentle tension and actual unplugged pull/strain check in phase2.',
                 'Complete shared lever/tool/module access stillOPEN; do not select this local receipt as whole wiring.'],
        source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in [gf,pf,Path(__file__),Path(P.__file__)]},
        selected=False,E1_complete=False,W5_complete=False,physical_pass=False,worker_seconds=round(time.monotonic()-tick,3))
    (OUT/'u1-power-grips-native.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)


if __name__=='__main__':run()
