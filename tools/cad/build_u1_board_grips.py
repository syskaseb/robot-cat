"""Extend both existing removable anchors, only after a clear shared gate.

No new feet, PCB holes or fastener stack; original retainer bar remains the
same separately qualified part. Do not run for a rejected allocation.
"""
import json,time,tempfile,shutil
import FreeCAD as A
import MeshPart
from pathlib import Path
from plan_current_main_sources import ROOT,OUT,SHA
from open_deck_p0_supports import sketch,feature
from open_deck_p0_plate import rect,circle
import plan_u1_board_grips as P
from build_u1_grouped_grips import validate


def run():
    tick=time.monotonic();gf=OUT/'u1-board-grips-checks.json';pf=OUT/'u1-board-grips-plan.json'
    g=json.loads(gf.read_text());p=json.loads(pf.read_text())
    assert g['status']=='BOARD_GRIPS_SHARED_CLEAR_NATIVE_OPEN' and not g['contacts'] and not g['errors']
    for n,h in g['source_sha256'].items():assert SHA(ROOT/n)==h,n
    assert p=={k:v for k,v in P.allocation().items() if k!='bands'}
    original=OUT/'U1SocketRetainer.FCStd';model=OUT/'U1BoardGripsCurrent.FCStd'
    assert not model.exists(),'Receive existing result first'
    d=A.openDocument(str(original));d.Label='U1BoardGripsCurrent'
    p0=d.addObject('App::VarSet','BoardGripParameters')
    height=87.32-84.3202
    p0.addProperty('App::PropertyLength','WestColumnHeight');p0.WestColumnHeight=height
    baselines={};old={n:d.getObject(n).Shape.copy() for n in ('AnchorLeft','AnchorRight')}
    for name in old:
        b=d.getObject(name);rows=[r for r in p['pads'] if r['owner']==name]
        priority=['WestRoot','WestColumn','WestTopRail','RearBeam','RearLeftSeat','OEBeam','OESeat',
            'FrontBeam','FrontSeat','FineRoot','FineColumn','FineSeat','SouthRoot','SouthBridge','XL02SeatLink','XL02Seat'] if name=='AnchorLeft' else [
            'RightColumn','RightTopRail','RightRearBeam','RearRightSeat']
        assert set(priority)=={r['name'] for r in rows}
        rows.sort(key=lambda r:priority.index(r['name']))
        for r in rows:
            x,y,z,X,Y,Z=r['bounds_mm'];n='Grip'+r['name']
            sk=sketch(b,n+'Plan',z);rect(sk,x,y,X-x,Y-y)
            b.Tip=feature(b,'Pad',n,sk,'BoardGripParameters.WestColumnHeight' if r['name']=='WestColumn' else Z-z)
            b.Tip.Refine=True
        for r in p['cuts']:
            if r['owner']!=name:continue
            n='Grip'+r['name']
            if r.get('kind')=='cylinder':
                x,y,z=r['centre_mm'];h=r['height_mm'];sk=sketch(b,n+'Plan',z+h)
                circle(sk,x,y,2*r['radius_mm'])
            else:
                x,y,z,X,Y,Z=r['bounds_mm'];h=Z-z;sk=sketch(b,n+'Plan',Z);rect(sk,x,y,X-x,Y-y)
            b.Tip=feature(b,'Pocket',n,sk,h)
            b.Tip.Refine=True
        d.recompute();validate(b)
        material=old[name].multiFuse([P.G.box(r['bounds_mm']) for r in rows])
        for r in p['cuts']:
            if r['owner']==name:material=material.cut(P.cut_shape(r))
        assert old[name].cut(material).Volume<1e-5,'Original bearing/eye must remain intact'
        difference=[b.Shape.cut(material).Volume,material.cut(b.Shape).Volume]
        assert max(difference)<1e-5,(name,difference,
            str(b.Shape.cut(material).BoundBox),str(material.cut(b.Shape).BoundBox),
            [(o.Name,o.Shape.Volume,list(o.State)) for o in b.Group if 'Shape' in o.PropertiesList and o.TypeId!='Sketcher::SketchObject'])
        baselines[name]=b.Shape.Volume
    p0.WestColumnHeight=height+.2;d.recompute();validate(d.AnchorLeft)
    assert d.AnchorLeft.Shape.Volume>baselines['AnchorLeft']
    p0.WestColumnHeight=height;d.recompute()
    for name,v in baselines.items():validate(d.getObject(name));assert abs(d.getObject(name).Shape.Volume-v)<1e-5
    for n,s in P.allocation()['bands'].items():
        ob=d.addObject('Part::Feature','WireRestraint_'+n);ob.Shape=s
        ob.addProperty('App::PropertyString','Evidence');ob.Evidence='Installed project budget, not supplier knot/closing or pull-load proof'
    d.saveAs(str(model));A.closeDocument(d.Name);exports=[]
    with tempfile.TemporaryDirectory(prefix='robot-cat-board-grips-') as td:
        fresh=Path(td)/model.name;shutil.copy2(model,fresh);d=A.openDocument(str(fresh));d.recompute()
        for name,v in baselines.items():
            b=d.getObject(name);validate(b);assert abs(b.Shape.Volume-v)<1e-5
            s=b.Shape.copy();bb=s.BoundBox;s.translate(A.Vector(-bb.XMin,-bb.YMin,-bb.ZMin))
            mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.04,AngularDeflection=.15,Relative=False)
            assert mesh.isSolid() and not mesh.hasNonManifolds() and mesh.countComponents()==1
            bb=mesh.BoundBox;size=[bb.XLength,bb.YLength,bb.ZLength];assert max(size)+10<256
            f=OUT/(name+'_wire_grips_x1.stl');mesh.write(str(f))
            exports.append(dict(part=name,quantity=1,path=f.relative_to(ROOT).as_posix(),sha256=SHA(f),size_mm=size,brim_each_mm=5,
                orientation='Original foot down, support cantilevers/eyes as needed in phase2; no slicer/print approval.'))
        A.closeDocument(d.Name)
    receipt=dict(status='U1_BOARD_GRIPS_NATIVE_PREPARED_SERVICE_AND_POWER_GRIPS_OPEN',native=model.relative_to(ROOT).as_posix(),native_sha256=SHA(model),
        exports=exports,editable_replacement_parts=2,retained_bar_not_duplicate_export=True,
        parameter_restore_mm=[height,height+.2,height],relocated_reopen=True,
        existing_stack_unchanged=True,new_screws=0,new_T18R=p['ties_quantity'],lacing_blanks_mm=p['lacing_blanks_mm'],
        service=['Sources absent; dedicated cable ties/laces are independent of the2module retainer ties.',
            'Release and support affected wires before loosening PCB1 anchor bolts; do not pull solder joints.',
            'Cut only2module ties and lift bar for adapter service; release retained BUS pair first as separately planned.',
            'Complete latest-scene withdrawal/tool/parking check still OPEN.'],
        phase2=['Actual knot dimensions and snug hand tension, do not flatten insulation.',
            'Small cantilevers/slot edges need PETG coupon/creep/dry fit.',
            'Cut-length lacing availability or equivalent measured product must be resolved before stock selection.'],
        source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in [gf,pf,original,Path(__file__),Path(P.__file__)]},
        selected=False,E1_complete=False,W5_complete=False,physical_pass=False,worker_seconds=round(time.monotonic()-tick,3))
    (OUT/'u1-board-grips-native.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt),flush=True)


if __name__=='__main__':run()
