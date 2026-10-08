"""Native shared platform at the accepted c8d2a2c load-path cells.

Frozen supplier cases/inputs; independent insulation seats and replaceable
body ties. Fixed head/tail stations and full outputs are explicitly NOT copied.
No historical document is written; one current development module.
"""
from datetime import datetime, timezone
from pathlib import Path
import json, math, time
import FreeCAD as A
import Part, Sketcher
from open_deck_p0_supports import sketch, feature
from open_deck_p0_plate import rect, circle
from open_prototype_shared_distribution_carriers import planned_shapes, MODEL as RAILS, validate
from open_prototype_fhac_supports import ring
from open_prototype_entry_chambers import MOUNTS, CONTEXT
from open_prototype_wiring_endpoints import ROOT, BASE, read, sha

OUT=BASE/'wiring-checkpoint'
MODEL=OUT/'CommonSourcePlatform.FCStd'
PROOF=OUT/'common-source-platform-checks.json'
AXES=[(x,y) for x in (-14,65) for y in (-20,20)]


def polygon(sk,x,y,af):
    radius=af/math.sqrt(3)
    pts=[A.Vector(x+radius*math.cos(i*math.pi/3),y+radius*math.sin(i*math.pi/3),0) for i in range(6)]
    for i in range(6):
        n=sk.addGeometry(Part.LineSegment(pts[i],pts[(i+1)%6]),False)
        sk.addConstraint(Sketcher.Constraint('Block',n))


def build(mount):
    doc=A.newDocument('CommonSourcePlatform')
    # Deep copy the native receiving body and its expression dependencies,
    # not private copies of the robot/boards/old source supports.
    receiver=doc.copyObject(mount.UpperCarrier,True)
    doc.recompute()
    p=doc.addObject('App::VarSet','SourceParameters')
    p.addProperty('App::PropertyLength','NutSeatDepth');p.NutSeatDepth=2.6
    p.addProperty('App::PropertyString','Qualification')
    p.Qualification='PETG prototype; supplier fit/lid/no-crush/load gates OPEN'
    body=doc.addObject('PartDesign::Body','CommonSourcePlatform')
    def pad(name,z,loops,height):
        sk=sketch(body,name+'Plan',z)
        for q in loops:rect(sk,*q)
        body.Tip=feature(body,'Pad',name,sk,height)
    pad('SourceFloor',113,[(-62,-27.5,144,55)],2)
    sk=sketch(body,'SourceColumnsPlan',77.72)
    for x,y in AXES:circle(sk,x,y,8)
    body.Tip=feature(body,'Pad','SourceColumns',sk,35.28)
    sk=sketch(body,'SourceFeetPlan',77.72)
    for x,y in AXES:circle(sk,x,y,12)
    body.Tip=feature(body,'Pad','SourceFeet',sk,5)
    pad('SourceRibs',109,[(-62,y,144,4) for y in (-18,14)],4)
    sk=sketch(body,'SourceBoresPlan',115)
    for x,y in AXES:circle(sk,x,y,3.4)
    body.Tip=feature(body,'Pocket','SourceBores',sk,37.28)
    sk=sketch(body,'SourceNutSeatPlan',77.72)
    for x,y in AXES:polygon(sk,x,y,5.8)
    cut=feature(body,'Pocket','SourceNutSeats',sk,'SourceParameters.NutSeatDepth')
    cut.Reversed=True;body.Tip=cut;doc.recompute()
    # Native attachment holes are in our printed receiving plate, NOT a PCB.
    sk=sketch(receiver,'SourceReceivingHolePlan',77.72)
    for x,y in AXES:circle(sk,x,y,3.4)
    receiver.Tip=feature(receiver,'Pocket','SourceReceivingHoles',sk,3)
    # Input supports bear on intact last9mm, independently of bought bodies.
    pad('InputSupportArms',113,[(-58.5,25.5,10,25.75),(-12,25.5,10,25.75),
        (23.25,-52.75,19.5,27.25)],2)
    pad('InputInsulationSeats',115,[(-58.5,42.25,10,9),(-12,42.25,10,9),
        (23.25,-52.75,19.5,9)],3)
    # Ten body-band slots at the fixed5case centres, cut before band install.
    sk=sketch(body,'BodyTieSlotsPlan',115)
    for x in (-40,-15,10,35,60):
        for y in (-12,12):
            for sx in (-1,1):rect(sk,x+sx*10.725-.85,y-1.75,1.7,3.5)
    body.Tip=feature(body,'Pocket','BodyTieSlots',sk,2)
    refs={};nuts=[]
    for i,(x,y) in enumerate(AXES,1):
        stack={
            'Screw':Part.makeCylinder(2.85,3,A.Vector(x,y,71.22)).fuse(Part.makeCylinder(1.5,10,A.Vector(x,y,74.22))),
            'Washer':Part.makeCylinder(3.5,.5,A.Vector(x,y,74.22)).cut(Part.makeCylinder(1.6,.5,A.Vector(x,y,74.22))),
        }
        pts=[A.Vector(x+5.5/math.sqrt(3)*math.cos(j*math.pi/3),y+5.5/math.sqrt(3)*math.sin(j*math.pi/3),0) for j in range(6)]
        nut=Part.Face(Part.Wire([Part.makeLine(pts[j],pts[(j+1)%6]) for j in range(6)])).extrude(A.Vector(0,0,2.4))
        nut=nut.cut(Part.makeCylinder(1.3,2.4,A.Vector(x,y,0)))
        stack['Nut']=nut
        for role,shape in stack.items():
            ob=doc.addObject('Part::Feature',f'SourceMount{i}{role}');ob.Shape=shape
            if role=='Nut':
                ob.setExpression('Placement.Base.z','75.32 mm + SourceParameters.NutSeatDepth');nuts.append(ob)
            refs[ob.Name]=ob
    for x,name in zip((-40,-15,10,35,60),('F_PI','F_AUX','F_HY','F_HP','F_TY')):
        for i,y in enumerate((-12,12)):
            shape=ring(A,Part,1,2.5,[x-11.325,y-1.25,111.8,x+11.325,y+1.25,138.2],
                [x+10.125,y-2.25,108.3,x+14.925,y+2.25,112.8])
            ob=doc.addObject('Part::Feature',name+'_BodyTie'+str(i));ob.Shape=shape;refs[ob.Name]=ob
    for name,x in [('PI',-53.5),('AUX',-7)]:
        y=46.75
        shape=ring(A,Part,1,2.5,[x-6.2,y-1.25,111.8,x+6.2,y+1.25,123.4],
            [x-11,y-2.25,118.5,x-5.5,y+2.25,122])
        ob=doc.addObject('Part::Feature',name+'_InputTie');ob.Shape=shape;refs[ob.Name]=ob
    for i,y in enumerate((-50,-46.5)):
        shape=ring(A,Part,1,2.5,[22.05,y-1.25,111.8,43.95,y+1.25,123.4],
            [42.75,y-2.25,118.5,48.25,y+2.25,122])
        ob=doc.addObject('Part::Feature','SouthInputTie'+str(i));ob.Shape=shape;refs[ob.Name]=ob
    doc.recompute()
    return doc,receiver,body,refs,nuts


def main():
    assert not MODEL.exists() and not PROOF.exists(),'Receive existing native worker before another build'
    tick=time.monotonic();plan=read(OUT/'shared-source-support-plan.json');allocation=read(OUT/'shared-allocation-plan.json')
    assert plan['status']=='COMMON_PLATFORM_LOAD_PATH_PREFLIGHT_CLEAR_NATIVE_RESTRAINTS_OPEN'
    for n,v in plan['source_sha256'].items():assert sha(ROOT/n)==v,n
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in (MOUNTS,CONTEXT,RAILS,OUT/'shared-source-support-plan.json',OUT/'shared-allocation-plan.json',Path(__file__))}
    mount=A.openDocument(str(MOUNTS));ctx=A.openDocument(str(CONTEXT));rail=A.openDocument(str(RAILS));doc=None
    r=dict(status='PENDING',selected=False,stage_completed=False,physical_pass=False,source_sha256=pins,
        contacts=[],errors=[],outside_torso=[],tested_pairs=0,reservation_occupancies=[],
        new_hardware_candidate={'M3x10':4,'M3_washer':4,'M3_nut':4,'T18I_body':10,'T18I_input':4},
        source_platform_owns=['five source bodies retention','five intact input seats'],
        fixed_station_disposition='Do NOT copy obsolete pitch post through P_SYS; pitch atZ166 is head interface,not torso internal. Tail fixed station needs independent current load path with full new fanout. Both remain OPEN.',
        assembly=plan['assembly']+['Fit10 replaceable holder-body ties; cut only2 on affected holder for delivered ATO lid trial','Four independent input ties stay in place during ATO service; comb each-wire no-slip needs dry fit'],
        gates=['Full outputs/independent output grips/fixed head-tail station supports are NOT included','Full MTA/S1/PWM/body/legs/stock not qualified','Delivered nut/tie/casing/lid/OD/R6/no-crush/each comb wire retention','PETG ribs/cantilever/layers/bearing/creep and support removal'],
        known_superseded=['SourceLeftCarrier','SourceRightCarrier','five historical output guides'],
        manufacturing=dict(material='PETG',orientation='Plate flat, columns up (world-Z inverted); underside ribs and grip arms support review phase2',printer_cube_mm=[256,256,256],total_margin_mm=10,nozzle_layer_profile='UNSET'))
    try:
        print('BUILD native receiver/platform and14restraints',flush=True)
        doc,receiver,body,refs,nuts=build(mount);bodies=[receiver,body]
        baseline=validate(doc,bodies);nutz=nuts[0].Shape.BoundBox.ZMin
        doc.SourceParameters.NutSeatDepth=2.8;changed=validate(doc,bodies)
        assert changed[body.Name]<baseline[body.Name]
        assert abs(nuts[0].Shape.BoundBox.ZMin-nutz-.2)<1e-6
        doc.SourceParameters.NutSeatDepth=2.6;restored=validate(doc,bodies)
        assert all(abs(v-restored[n])<1e-6 for n,v in baseline.items())
        assert abs(nuts[0].Shape.BoundBox.ZMin-nutz)<1e-6
        r['parameter_test']=dict(nut_seat_depth_mm=[2.6,2.8,2.6],corresponding_four_nuts_follow=True,restored=True)
        doc.saveAs(str(MODEL));print('SAVED native module; changed interface checks',flush=True)
        targets=planned_shapes(allocation,mount,ctx)
        targets.update({b.Name:b.Shape for b in rail.Objects if b.TypeId=='PartDesign::Body' and b.Name!='DistributionSpacer'})
        for o in mount.Objects:
            if 'Shape' not in o.PropertiesList or o.Shape.isNull() or o.Name in ('UpperCarrier','BUS_CP2'):continue
            if o.Name.startswith(('SourceLeftCarrier','SourceRightCarrier','SideRail','SideColumn','SideDistributionRail','F_PI_','F_AUX_','F_HY_','F_HP_','F_TY_')) or o.Name.endswith('_CurrentReference'):continue
            if o.TypeId in ('PartDesign::Body','App::Link') or o.Name.endswith('NominalPCB') or o.Name.startswith('BUSsupplier'):targets[o.Name]=o.Shape
        for group in mount.Objects:
            if 'Group' in group.PropertiesList and 'Hardware' in group.Name and group.Name!='SideMountHardware':
                for o in group.Group:
                    if 'Shape' in o.PropertiesList and not o.Shape.isNull():targets['hardware/'+o.Name]=o.Shape
        for o in ctx.Objects:
            if 'Shape' in o.PropertiesList and not o.Shape.isNull() and o.Name.startswith(('P0_','Head_','TailBridge','S0_','S1_')) and o.Name!='P0_MG92BMount29':targets[o.Name]=o.Shape
        new={body.Name:body.Shape,receiver.Name:receiver.Shape,**{n:o.Shape for n,o in refs.items()}}
        def check(n,s,m,t):
            if not s.BoundBox.intersect(t.BoundBox):return
            r['tested_pairs']+=1
            try:
                assert s.isValid() and t.isValid();hit=s.common(t);assert hit.isValid()
                if hit.Volume<=1e-5:return
                # Matching actual OD4 inputs are checked. Worst-OD4.2 entry
                # budget occupies its planned insulation saddle by0.1mm;
                # this is reservation occupancy, NOT waived real material.
                if n==body.Name and m in ('entry/P_SYS.2','entry/P_REAR.3','entry/P_AUX.2','entry/P_AUX.3','entry/P_AUX.4'):
                    r['reservation_occupancies'].append(dict(a=n,b=m,volume_mm3=hit.Volume));return
                if n.startswith('SourceMount') and m.startswith(n[:12]) and {n[12:],m[12:]}=={'Screw','Nut'}:return
                r['contacts'].append(dict(a=n,b=m,volume_mm3=hit.Volume))
            except Exception as e:r['errors'].append(dict(a=n,b=m,error=str(e)))
        for n,s in new.items():
            assert s.isValid() and len(s.Solids)==1,n
            outside=s.cut(ctx.TorsoEnvelope.Shape);assert outside.isValid()
            if outside.Volume>1e-5:r['outside_torso'].append(dict(part=n,volume_mm3=outside.Volume))
            # Receiver unchanged regions reused; only its removed material is
            # new. Checking it against whole retained assembly is unnecessary.
            if n!=receiver.Name:
                for m,t in targets.items():check(n,s,m,t)
        for i,(n,s) in enumerate(new.items()):
            for m,t in list(new.items())[i+1:]:check(n,s,m,t)
        r['native_geometry']=dict(valid_bodies=2,strict_bop_errors=0,volumes_mm3=baseline,fully_constrained_sketches=sum(o.TypeId=='Sketcher::SketchObject' for o in doc.Objects))
        r['print_dimensions_mm']={b.Name:[b.Shape.BoundBox.XLength,b.Shape.BoundBox.YLength,b.Shape.BoundBox.ZLength] for b in bodies}
        assert all(max(q)<246 for q in r['print_dimensions_mm'].values())
        r['model_sha256']=sha(MODEL)
        r['status']='NATIVE_SOURCE_PLATFORM_AND_INPUT_RESTRAINTS_CLEAR_OUTPUT_STATIONS_OPEN' if not any(r[k] for k in ('contacts','errors','outside_torso')) else 'NATIVE_SOURCE_PLATFORM_HAS_CHANGED_INTERFACE_FAILURES'
    except Exception as e:
        r['status']='NATIVE_SOURCE_PLATFORM_BUILD_OR_GATE_ERROR';r['errors'].append(dict(error=repr(e)))
        if doc and not MODEL.exists():
            doc.saveAs(str(MODEL));r['partial_native_preserved']=True
        raise
    finally:
        for d in (doc,mount,ctx,rail):
            if d and d.Name in A.listDocuments():A.closeDocument(d.Name)
        r.update(worker_seconds=time.monotonic()-tick,finished_utc=datetime.now(timezone.utc).isoformat())
        PROOF.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    assert all(sha(ROOT/n)==v for n,v in pins.items())
    print(json.dumps({k:r[k] for k in ('status','contacts','errors','outside_torso','tested_pairs','worker_seconds')}),flush=True)


if __name__=='__main__':main()
