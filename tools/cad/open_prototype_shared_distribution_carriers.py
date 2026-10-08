"""One native paired carrier for the frozen337b6c6 allocation.

Recess retained four bolt heads; do not move cases/routes again. This is a
changed mounting-interface candidate, not whole wiring or physical acceptance.
"""
from datetime import datetime, timezone
from pathlib import Path
import json, math, time
import FreeCAD as A
import Part
from open_deck_p0_supports import sketch, feature
from open_deck_p0_plate import rect, circle
from open_prototype_entry_chambers import MOUNTS, CONTEXT
from open_prototype_wiring_endpoints import ROOT, BASE, read, sha

OUT=BASE/'wiring-checkpoint'
MODEL=OUT/'SharedDistributionCarriers.FCStd'
PROOF=OUT/'shared-distribution-carrier-checks.json'


def planned_shapes(plan,mount,ctx):
    result={}
    for row in plan['distribution']+plan['mts']:
        ob=mount.getObject(row['native']) or ctx.getObject(row['native'])
        s=ob.Shape.copy();b=s.BoundBox
        s.translate(A.Vector(*row['centre_mm'])-A.Vector((b.XMin+b.XMax)/2,(b.YMin+b.YMax)/2,(b.ZMin+b.ZMax)/2))
        result[row['native']]=s
    def tube(segments,diameter):
        edges=[Part.makeLine(A.Vector(*q['start']),A.Vector(*q['end'])) if q['kind']=='line' else
            Part.Arc(A.Vector(*q['start']),A.Vector(*q['mid']),A.Vector(*q['end'])).toShape() for q in segments]
        first=edges[0]
        return Part.Wire(edges).makePipeShell([Part.Wire([Part.makeCircle(diameter/2,first.valueAt(first.FirstParameter),first.tangentAt(first.FirstParameter))])],True,False)
    for row in plan['holders']:
        name=row['holder'];axis=A.Vector(*row['axis']);s=mount.getObject(name+'_body_budget_CurrentReference').Shape.copy();b=s.BoundBox
        s.translate(-A.Vector((b.XMin+b.XMax)/2,(b.YMin+b.YMax)/2,(b.ZMin+b.ZMax)/2))
        rot=A.Rotation(A.Vector(1,0,0),axis);s.rotate(A.Vector(0,0,0),rot.Axis,rot.Angle*180/math.pi)
        s.translate(A.Vector(*row['input_mm'])+axis*25.5+A.Vector(0,0,1));result[name+'/case']=s
        inlet=next(q for q in plan['input_recipes'] if q['holder']==name)
        result[name+'/input']=tube(inlet['recipe']['segments'],4)
        p=A.Vector(*row['output_mm']);a=p+axis*3;c=a+A.Vector(0,0,-6);b=c+axis*6
        mid=c+(axis+A.Vector(0,0,1))*(6/math.sqrt(2));cut=b+A.Vector(0,0,-15)
        result[name+'/output']=tube([dict(kind='line',start=list(p),end=list(a)),dict(kind='arc',start=list(a),mid=list(mid),end=list(b)),dict(kind='line',start=list(b),end=list(cut))],4)
        result[name+'/sleeve']=Part.makeCylinder(3,26.5,cut+A.Vector(0,0,14),A.Vector(0,0,-1))
        result[name+'/new_grip']=Part.makeCylinder(1.05,21.5,cut,A.Vector(0,0,-1))
    for port in read(OUT/'shared-allocation-checks.json')['ports']:
        result['entry/'+port['role']]=Part.makeCylinder(2.1,9,A.Vector(*port['point_mm']),A.Vector(*port['departure']))
    for row in plan['mts']:
        b=result[row['native']].BoundBox
        for sign in (-1,1):result[row['native']+'/exit'+str(sign)]=Part.makeCylinder(2,9,A.Vector(b.XMin if sign<0 else b.XMax,row['centre_mm'][1],row['centre_mm'][2]),A.Vector(sign,0,0))
    return result


def build(doc,plan,mount):
    p=doc.addObject('App::VarSet','Parameters')
    p.addProperty('App::PropertyLength','WellDepth');p.WellDepth=3
    bodies=[]
    def pad(body,name,z,loops,height):
        sk=sketch(body,name+'Plan',z)
        for x,y,w,h in loops:rect(sk,x,y,w,h)
        body.Tip=feature(body,'Pad',name,sk,height)
    def reflected(y,h,sign):return y if sign>0 else -y-h
    for sign,side in [(1,'Left'),(-1,'Right')]:
        body=doc.addObject('PartDesign::Body',side+'DistributionCarrier');bodies.append(body)
        pad(body,side+'LowerBeam',58,[(-77,reflected(71,8,sign),178,8)],3)
        pad(body,side+'LowerPads',58,[(x-15,reflected(65.5,19,sign),30,19) for x in (-62,-25,12,49,86)],3)
        pad(body,side+'AnchorArms',58,[(x-5.5,reflected(75,19.75,sign),11,19.75) for x in (-13,71)],3)
        sk=sketch(body,side+'BearingBossPlan',56)
        for x in (-13,71):circle(sk,x,sign*84.75,11)
        body.Tip=feature(body,'Pad',side+'BearingBoss',sk,5)
        pad(body,side+'Posts',61,[(x-3,reflected(88.75,6,sign),6,6) for x in (-13,71)],48.01)
        pad(body,side+'UpperOuterBeam',109.01,[(-20,reflected(88.75,6,sign),98,6)],3)
        pad(body,side+'UpperArms',109.01,[(x-3,reflected(62.25,29.5,sign),6,29.5) for x in (-20,78)],3)
        pad(body,side+'UpperSpine',109.01,[(-65.5,reflected(58.25,8,sign),193.5,8)],3)
        pad(body,side+'RearBranch',109.01,[(109,reflected(20,42.25,sign),8,42.25)],3)
        rows=[r for r in plan['distribution'] if r['side']==('L' if sign>0 else 'R') and r['centre_mm'][2]==120]
        pad(body,side+'UpperPads',109.01,[(r['centre_mm'][0]-r['size_mm'][0]/2,r['centre_mm'][1]-r['size_mm'][1]/2,*r['size_mm'][:2]) for r in rows],3)
        small=[r for r in rows if r['size_mm'][2]==9]
        pad(body,side+'SmallCaseSteps',112.01,[(r['centre_mm'][0]-15,r['centre_mm'][1]-9.5,30,19) for r in small],1)
        sk=sketch(body,side+'BoltBorePlan',61)
        for x in (-13,71):circle(sk,x,sign*84.75,3.4)
        body.Tip=feature(body,'Pocket',side+'BoltBores',sk,5)
        sk=sketch(body,side+'BoltWellPlan',61)
        for x in (-13,71):circle(sk,x,sign*84.75,7.4)
        body.Tip=feature(body,'Pocket',side+'BoltWells',sk,'Parameters.WellDepth')
    spacer=doc.addObject('PartDesign::Body','DistributionSpacer');bodies.append(spacer)
    sk=sketch(spacer,'SpacerPlan',0);circle(sk,0,0,8);circle(sk,0,0,3.4)
    spacer.Tip=feature(spacer,'Pad','SpacerHeight',sk,8.28)
    links=[]
    for i,(x,y) in enumerate([(x,y) for x in (-13,71) for y in (-84.75,84.75)]):
        ob=doc.addObject('App::Link','DistributionColumn'+str(i+1));ob.setLink(spacer);ob.LinkPlacement.Base=A.Vector(x,y,47.72);links.append(ob)
    moved=[]
    for old in mount.SideMountHardware.Group:
        ob=doc.addObject('Part::Feature',old.Name);ob.Shape=old.Shape.copy()
        if old.Name.endswith(('Screw','TopWasher')):
            ob.setExpression('Placement.Base.z','-Parameters.WellDepth');moved.append(ob)
    doc.recompute()
    return bodies,links,moved


def validate(doc,bodies):
    doc.recompute();volumes={}
    for body in bodies:
        assert body.Shape.isValid() and len(body.Shape.Solids)==1 and not body.Shape.check(True),body.Name
        assert all('Invalid' not in o.State and 'Touched' not in o.State for o in body.Group),body.Name
        assert all(o.solve()==0 and o.FullyConstrained for o in body.Group if o.TypeId=='Sketcher::SketchObject'),body.Name
        volumes[body.Name]=body.Shape.Volume
    return volumes


def main():
    assert not MODEL.exists() and not PROOF.exists(),'Receive existing worker/result before rebuilding'
    tick=time.monotonic();plan=read(OUT/'shared-allocation-plan.json');previous=read(OUT/'shared-allocation-checks.json')
    assert not any(previous[k] for k in ('contacts','outside_torso','errors'))
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in (MOUNTS,CONTEXT,OUT/'shared-allocation-plan.json',OUT/'shared-allocation-checks.json',Path(__file__))}
    mount=A.openDocument(str(MOUNTS));ctx=A.openDocument(str(CONTEXT));doc=A.newDocument('SharedDistributionCarriers')
    proof=dict(status='PENDING',source_sha256=pins,reused_geometry_snapshot='337b6c6',contacts=[],errors=[],outside_torso=[],tested_pairs=0,selected=False,stage_completed=False,physical_pass=False,
        hardware_quantity_change={'M3x30':0,'M3_washer':0,'M3_nut':0},
        assembly=['Fit shorter four spacers and paired carriers; tighten four recessed bolts BEFORE adhesive WAGO installation',
            'Install lower WAGO then upper WAGO at retained2.49mm retention offset; adhesive is NOT wire strain relief',
            'Rail service requires local adhesive release of obscuring cases; not a claim of driver access through installed WAGO',
            'Routine ATO service must not require rail removal or74 WAGO disconnections'],
        open_gates=['Independent wire restraints/full outputs/MTA mounts/tails/S1/PWM/stock remain open','PETG print/bearing/creep and nominal bolt/adhesive fit need phase2','Supplier pad/cavity dimensions remain delivery gates'])
    try:
        bodies,links,moved=build(doc,plan,mount);baseline=validate(doc,bodies)
        original_head=doc.SideMount1Screw.Shape.BoundBox.ZMax
        doc.Parameters.WellDepth=2.5;trial=validate(doc,bodies)
        assert all(trial[n]>baseline[n] for n in ('LeftDistributionCarrier','RightDistributionCarrier'))
        assert abs(doc.SideMount1Screw.Shape.BoundBox.ZMax-original_head-.5)<1e-6
        doc.Parameters.WellDepth=3;restored=validate(doc,bodies)
        assert all(abs(restored[n]-v)<1e-6 for n,v in baseline.items())
        assert abs(doc.SideMount1Screw.Shape.BoundBox.ZMax-original_head)<1e-6
        proof['parameter_test']=dict(depth_mm=[3,2.5,3],matching_bolt_and_washer_moved=True,restored=True)
        doc.saveAs(str(MODEL))
        new={b.Name:b.Shape for b in bodies[:2]};new.update({o.Name:o.Shape for o in links});new.update({o.Name:o.Shape for o in moved})
        targets=planned_shapes(plan,mount,ctx)
        excluded={'SideDistributionRail','SideRailSpacer'}|{o.Name for o in mount.Objects if o.Name.startswith(('SideRail','SideColumn','SideMount'))}
        case_names={r['native'] for r in plan['distribution']}
        for o in mount.Objects:
            if o.Name in excluded or o.Name in case_names or o.Name=='BUS_CP2':continue
            if o.Name.endswith('_CurrentReference'):continue
            if 'Shape' in o.PropertiesList and not o.Shape.isNull() and (o.TypeId in ('PartDesign::Body','App::Link') or o.Name.endswith(('NominalPCB','_CP2')) or o.Name.startswith('BUSsupplier')):targets['retained/'+o.Name]=o.Shape
        for group in mount.Objects:
            if 'Group' in group.PropertiesList and 'Hardware' in group.Name:
                for o in group.Group:
                    if o.Name in excluded or 'Shape' not in o.PropertiesList or o.Shape.isNull():continue
                    targets['hardware/'+o.Name]=o.Shape
        for o in ctx.Objects:
            if 'Shape' in o.PropertiesList and not o.Shape.isNull() and o.Name.startswith(('P0_','Head_','TailBridge','S0_','S1_')) and o.Name!='P0_MG92BMount29':targets['context/'+o.Name]=o.Shape
        # Retained lower washer/nut cooperate with moved screws; no old side stack duplicate.
        targets.update({o.Name:o.Shape for o in doc.Objects if o.Name.startswith('SideMount') and o not in moved})
        def check(n,s,m,t):
            if not s.BoundBox.intersect(t.BoundBox):return
            proof['tested_pairs']+=1
            try:
                assert s.isValid() and t.isValid();hit=s.common(t);assert hit.isValid()
                # Nut/shaft thread engagement is intended; simplified solids omit threads.
                if n.startswith('SideMount') and m.startswith(n[:-5]) and m.endswith('Nut'):return
                if hit.Volume>1e-5:proof['contacts'].append(dict(a=n,b=m,volume_mm3=hit.Volume))
            except Exception as e:proof['errors'].append(dict(a=n,b=m,error=str(e)))
        for n,s in new.items():
            outside=s.cut(ctx.TorsoEnvelope.Shape);assert outside.isValid()
            if outside.Volume>1e-5:proof['outside_torso'].append(dict(part=n,volume_mm3=outside.Volume))
            for m,t in targets.items():check(n,s,m,t)
        for i,(n,s) in enumerate(new.items()):
            for m,t in list(new.items())[i+1:]:check(n,s,m,t)
        proof['native_geometry']=dict(valid_solids=3,strict_bop_errors=0,volumes_mm3=baseline,
            fully_constrained_sketches=sum(o.TypeId=='Sketcher::SketchObject' for o in doc.Objects),bearing_floor_mm=2,
            nominal_head_case_gap_mm=1.99,short_spacer_mm=8.28)
        proof['print_dimensions_mm']={b.Name:[b.Shape.BoundBox.XLength,b.Shape.BoundBox.YLength,b.Shape.BoundBox.ZLength] for b in bodies}
        assert all(max(q)<246 for q in proof['print_dimensions_mm'].values()),'10mm total margin to256 cube'
        body_names=[b.Name for b in bodies]
        A.closeDocument(doc.Name);doc=A.openDocument(str(MODEL));rebodies=[doc.getObject(n) for n in body_names]
        reopened=validate(doc,rebodies);assert all(abs(reopened[n]-v)<1e-6 for n,v in baseline.items())
        proof['reopen_geometry_restored']=True;proof['model_sha256']=sha(MODEL)
        proof['status']='NATIVE_CARRIERS_HAVE_OPEN_INTERFACES' if any(proof[k] for k in ('contacts','errors','outside_torso')) else 'NATIVE_CARRIER_STATIC_INTERFACES_CLEAR_WIRING_OPEN'
        if proof['status']=='NATIVE_CARRIER_STATIC_INTERFACES_CLEAR_WIRING_OPEN':
            import MeshPart, Mesh
            exports={}
            for b in rebodies:
                s=b.Shape.copy();s.translate(-A.Vector(s.BoundBox.XMin,s.BoundBox.YMin,s.BoundBox.ZMin))
                mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.15,AngularDeflection=.2,Relative=False)
                assert mesh.isSolid();path=OUT/(b.Name+'.stl');mesh.write(str(path));checkmesh=Mesh.Mesh(str(path));assert checkmesh.isSolid()
                exports[path.name]=sha(path)
            proof['exports']=exports
    finally:
        for d in (doc,mount,ctx):
            if d.Name in A.listDocuments():A.closeDocument(d.Name)
        proof.update(worker_seconds=time.monotonic()-tick,finished_utc=datetime.now(timezone.utc).isoformat())
        PROOF.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    assert all(sha(ROOT/n)==v for n,v in pins.items())
    print(json.dumps({k:proof[k] for k in ('status','contacts','errors','outside_torso','tested_pairs','worker_seconds')}),flush=True)


if __name__=='__main__':main()
