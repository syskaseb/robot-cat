"""Editable two-part removable grip set, only after its common-space gate.

Historical board/route models remain immutable. Four changed screw placements
are recorded for later assembly integration, not extra installed screws.
"""
import json,time,tempfile,shutil
from pathlib import Path
import FreeCAD as A
import MeshPart
from plan_current_main_sources import ROOT,OUT,SHA
from open_deck_p0_supports import sketch,feature
from open_deck_p0_plate import rect,circle
import plan_u1_grouped_grips as P


def run():
    tick=time.monotonic();gf=OUT/'u1-grouped-grips-checks.json';pf=OUT/'u1-grouped-grips-plan.json'
    g=json.loads(gf.read_text());p=json.loads(pf.read_text())
    assert g['status']=='GROUPED_GRIP_SPACE_CLEAR_NATIVE_OPEN' and not g['contacts'] and not g['errors']
    for n,h in g['source_sha256'].items():assert SHA(ROOT/n)==h,n
    assert p=={k:v for k,v in P.allocation().items() if k!='bands'},'Plan must match gated source recipe'
    model=OUT/'U1GroupedGripsCurrent.FCStd';assert not model.exists(),'Receive existing result, do not duplicate'
    d=A.newDocument('U1GroupedGripsCurrent')
    par=d.addObject('App::VarSet','GripParameters');par.addProperty('App::PropertyLength','GPIOBridgeDepth');par.GPIOBridgeDepth=2.5
    expected={};volumes={};bodies=[]
    for owner in p['mount_axes_mm']:
        rows=[v for v in p['pads'] if v['owner']==owner]
        if owner=='GPIOGrip':
            priority=['NorthRail','Foot0','Foot1','Riser1','TopBridge','FrontSeatRoot','RearSeatRoot','GPIOFrontSeat','GPIORearSeat']
        else:
            priority=['WestSpine','FootBridge0','FootBridge1','Foot0','Foot1','JP3Bridge','JP3Seat','PWMRootReturn','PWMRoot','PWMSeat']
        assert set(priority)=={v['name'] for v in rows},owner
        rows.sort(key=lambda v:priority.index(v['name']))
        b=d.addObject('PartDesign::Body',owner);bodies.append(b)
        for v in rows:
            n=owner+v['name']
            if v.get('kind')=='disc':
                x,y,z=v['centre_mm'];sk=sketch(b,n+'Plan',z);circle(sk,x,y,2*v['radius_mm']);h=v['height_mm']
            else:
                x,y,z,X,Y,Z=v['bounds_mm'];sk=sketch(b,n+'Plan',z);rect(sk,x,y,X-x,Y-y);h=Z-z
            b.Tip=feature(b,'Pad',n,sk,'GripParameters.GPIOBridgeDepth' if v['name']=='TopBridge' else h)
        for v in (v for v in p['cuts'] if v['owner']==owner):
            x,y,z,X,Y,Z=v['bounds_mm'];n=owner+v['name'];sk=sketch(b,n+'Plan',Z);rect(sk,x,y,X-x,Y-y)
            b.Tip=feature(b,'Pocket',n,sk,Z-z)
        sk=sketch(b,owner+'ActualBoltAxes',100)
        for x,y in p['mount_axes_mm'][owner]:circle(sk,x,y,2.4)
        b.Tip=feature(b,'Pocket',owner+'BoltClearance',sk,80)
        d.recompute();validate(b)
        tools=[P.material(v) for v in rows];s=tools[0].multiFuse(tools[1:])
        tools=[P.box(v['bounds_mm']) for v in p['cuts'] if v['owner']==owner]
        if tools:s=s.cut(tools[0].multiFuse(tools[1:]))
        for x,y in p['mount_axes_mm'][owner]:s=s.cut(P.Part.makeCylinder(1.2,70,A.Vector(x,y,30)))
        expected[owner]=s
        assert b.Shape.cut(s).Volume<1e-5 and s.cut(b.Shape).Volume<1e-5,owner
        volumes[owner]=b.Shape.Volume
        print('Editable grouped grip',owner,round(time.monotonic()-tick,2),flush=True)
    par.GPIOBridgeDepth=2.7;d.recompute();validate(d.GPIOGrip)
    assert d.GPIOGrip.Shape.Volume>volumes['GPIOGrip']
    par.GPIOBridgeDepth=2.5;d.recompute()
    for b in bodies:validate(b);assert abs(b.Shape.Volume-volumes[b.Name])<1e-5
    # Native boxes/cuts for nominal purchased tie budgets remain editable.
    # Actual tie locking geometry/delivery hand tension are NOT supplier CAD.
    for n,s in P.allocation()['bands'].items():
        o=d.addObject('Part::Feature','PurchasedBudget_'+n);o.Shape=s
        o.addProperty('App::PropertyString','Evidence');o.Evidence='Installed project envelope, T18R111-00405 band2.5x1.0; head/loop shape provisional'
    d.saveAs(str(model));A.closeDocument(d.Name);exports=[]
    with tempfile.TemporaryDirectory(prefix='robot-cat-grouped-grips-') as td:
        fresh=Path(td)/model.name;shutil.copy2(model,fresh);d=A.openDocument(str(fresh));d.recompute()
        for owner in p['mount_axes_mm']:
            b=d.getObject(owner);validate(b);assert abs(b.Shape.Volume-volumes[owner])<1e-5
            s=b.Shape.copy()
            if owner=='GPIOGrip':s.rotate(A.Vector(0,0,0),A.Vector(1,0,0),90)
            bb=s.BoundBox;s.translate(A.Vector(-bb.XMin,-bb.YMin,-bb.ZMin))
            mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.05,AngularDeflection=.15,Relative=False)
            assert mesh.isSolid() and not mesh.hasNonManifolds() and mesh.countComponents()==1
            bb=mesh.BoundBox;size=[bb.XLength,bb.YLength,bb.ZLength];assert max(size)+10<256
            f=OUT/(owner+'_x1.stl');mesh.write(str(f))
            exports.append(dict(part=owner,path=f.relative_to(ROOT).as_posix(),sha256=SHA(f),quantity=1,size_mm=size,brim_each_mm=5,
                orientation='GPIO: north spine down; PCA: bearing feet down. Support bridges/slots as needed; phase2 slicer and PETG creep/fit gates, no print approval.'))
        A.closeDocument(d.Name)
    receipt=dict(status='TWO_GROUPED_GRIPS_NATIVE_PREPARED_OTHER_ENDS_SERVICE_OPEN',native=model.relative_to(ROOT).as_posix(),native_sha256=SHA(model),
        exports=exports,editable_parts=2,parameter_restore_mm=[2.5,2.7,2.5],relocated_reopen=True,
        changed_existing_hardware=g['changed_screws'],replaced_upper_washers=g['replaced_upper_washer_names'],
        purchased_ties=p['tie_supplier'],ties_quantity=4,
        assembly=['Source/USB disconnected; fit feet at four actual board axes while supportingPCB; retain captive nuts and screw lengths.',
            'Install three GPIO-front PWM JP3/fine groups and separate GPIO rear row ties on insulation only.',
            'Service: cut only dedicated wire ties, support PCB, remove two bracket bolts; remove GPIO bracket before plug withdrawal.',
            'BUS pair release, lower-board tool access and all U1-side restraint/service remain open; this is not wholeE1/W5.'],
        phase2=['Tie actual locking dimensions and hand tension; do not crush fine insulation.',
            'Right-rooted GPIO cantilever stiffness/creep and layer direction.',
            'PCA1mm common seat and thin slot edges require coupon/deburr/fit.',
            'Actual driver access/connector envelopes and thermal clearances.'],
        source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in (gf,pf,Path(__file__),ROOT/'tools/cad/plan_u1_grouped_grips.py',ROOT/'hardware/reference/hellermann-11100405-2026-10-12/dimensions.json')},
        worker_seconds=round(time.monotonic()-tick,3),selected=False,E1_complete=False,W5_complete=False,physical_pass=False)
    (OUT/'u1-grouped-grips-native.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt),flush=True)


def validate(body):
    assert body.Shape.isValid() and len(body.Shape.Solids)==1 and not body.Shape.check(True),body.Name
    for o in body.Group:
        assert not any(s in ('Invalid','Error') for s in o.State),(o.Name,list(o.State))
        if o.TypeId=='Sketcher::SketchObject':assert o.FullyConstrained and o.solve()==0,o.Name


if __name__=='__main__':run()
