"""Matched replaceable two-WAGO data shelf, receiving plate and tie lands.

One current editable candidate. Full changed data conductors and source-family
selection remain explicit dependencies; this is not a full wiring milestone.
"""
from datetime import datetime, timezone
from pathlib import Path
import copy, json, math, time
import FreeCAD as A
import Part
import MeshPart
import Mesh
from open_prototype_source_retention import OUT, ROOT, sha
from open_prototype_side_source_routes import load_scene
from open_prototype_tail_clearance import near, box, wire, profiles
from open_prototype_source_group import read, add, mul, line
from open_deck_p0_supports import sketch, feature
from open_deck_p0_plate import rect, circle
from open_prototype_shared_distribution_carriers import validate

MODEL=OUT/'DataShelfCurrent.FCStd'
DEST=OUT/'data-shelf-package.json'


def bind_data(p):
    """Reallocate the two complete cases/ten entries, not a W042 micro-notch."""
    for role,x in (('D_RL',-80),('D_RR',-40)):
        row=next(r for r in p['stations'] if r['role']==role)
        # Left case reuses its already-qualified narrow roof footprint; only
        # the right case must turn away from W042's north-side vertical bend.
        left=role=='D_RL'
        row.update(centre_mm=[x,-20,128],size_mm=[19,30,9] if left else [30,19,9],rotation='90' if left else '0')
        for i in range(1,6):
            point=[x+9.5,-20+(i-3)*4.75,128] if left else [x+(i-3)*4.75,-29.5,128]
            p['ports'][f'{role}.{i}'].update(point_mm=point,departure=[1,0,0] if left else [0,-1,0])
    for e in p['body_ends']:
        if e['current_role'].startswith(('D_RL.','D_RR.')):e['datum']=copy.deepcopy(p['ports'][e['current_role']])
    return p


def build(native):
    doc=A.newDocument('DataShelfCurrent')
    carrier=doc.copyObject(native.UpperCarrier,True);doc.recompute()
    # The original lightened plate has only50mm2 below the proposed foot.
    # Add a continuous native load path back to its existing -14/-20 root;
    # do not move the same unsupported foot by a few millimetres.
    sk=sketch(carrier,'DataReceivingEarPlan',74.72)
    rect(sk,-70,-22,62,8)
    carrier.Tip=feature(carrier,'Pad','DataReceivingEar',sk,3)
    bearing_owner=carrier.Shape.copy()
    par=doc.addObject('App::VarSet','DataParameters')
    par.addProperty('App::PropertyLength','ShelfThickness');par.ShelfThickness=3
    par.addProperty('App::PropertyString','Qualification')
    par.Qualification='Nominal prototype; adhesive retains cases only, T18I grips insulation. Delivered cavity/fit/pull gates OPEN.'
    body=doc.addObject('PartDesign::Body','DataShelf')
    def pad(name,z,loops,h):
        sk=sketch(body,name+'Plan',z)
        for q in loops:rect(sk,*q)
        body.Tip=feature(body,'Pad',name,sk,h)
    pad('DataFeet',77.72,[(-70,-22,30,8)],3)
    pad('DataPost',80.72,[(-58,-22,6,8)],42.78)
    pad('DataShelfFloor','123.5 mm - DataParameters.ShelfThickness',
        [(-89.5,-35,19,30),(-70.5,-24,15.5,8),(-55,-29.5,30,19)],'DataParameters.ShelfThickness')
    pad('DataGripArms','123.5 mm - DataParameters.ShelfThickness',
        [(-70.5,-35,9,30),(-55,-38.5,30,9)],'DataParameters.ShelfThickness')
    pad('DataInsulationLands',123.5,[(-70,-32,8,24),(-52,-38,24,8)],2.4)
    # Transverse open tunnels put straps underneath the lands, above G2. They
    # do not cross either WAGO lever or bear on an unknown supplier underside.
    sk=sketch(body,'DataTieTunnelsPlan',123.1)
    rect(sk,-67.6,-36,3.2,32);rect(sk,-56,-36.1,32,3.2)
    body.Tip=feature(body,'Pocket','DataTieTunnels',sk,1.6)
    sk=sketch(body,'DataFootBoresPlan',80.72)
    for x in (-65,-45):circle(sk,x,-18,3.4)
    body.Tip=feature(body,'Pocket','DataFootBores',sk,3)
    sk=sketch(carrier,'DataReceivingBoresPlan',77.72)
    for x in (-65,-45):circle(sk,x,-18,3.4)
    carrier.Tip=feature(carrier,'Pocket','DataReceivingBores',sk,3)
    doc.recompute()
    return doc,carrier,body,bearing_owner


def run():
    assert not MODEL.exists() and not DEST.exists(),'Receive current result before another build'
    tick=time.monotonic();allocation=read(OUT/'source-group-allocation.json');p=bind_data(copy.deepcopy(allocation['family']))
    docs=[];doc=None
    report=dict(status='PENDING',selected=False,stage_completed=False,physical_pass=False,
        local_data_mount_complete=False,contacts=[],errors=[],tested_pairs=0,
        full_data_conductors_and_source_family_still_open=True,
        assembly=['On unstacked upper plate fit DataShelf with two M3x10 and washers/nuts; driver is used before G2 installation',
                  'Install/retain D_RL and D_RR on the marked flat floors; supplier pad/cavity fit after delivery',
                  'Lay insulated wires on8mm lands within9mm straight approaches, pass one T18I through each transverse tunnel',
                  'Snug ties on insulation only; no tie across levers; do not energize before phase2 wiring and pull checks',
                  'Deep shelf removal may require releasing adjacent G2 adhesive without disconnecting its conductors; not routine ATO service'],
        hardware_contribution={'M3x10':2,'M3_washer':2,'M3_nut':2,'T18I':2},
        delivery_gates=['WAGO cavity and adhesive pad datum','nominal4.2mmOD maximum insulation land; actual data wire may be smaller',
                        'PETG deformation/fastener bearing','T18I routing, head fit, insulation pull/no-crush'],
        rejected_old_mounts=['obsolete D_RL and D_RR upper-tier mounts; no active selection yet'])
    def progress(s):print(json.dumps(dict(phase=s,seconds=round(time.monotonic()-tick,2))),flush=True)
    def material(n,s,m,t):
        if not near(s,t,0):return
        assert s.isValid() and t.isValid(),(n,m)
        v=s.common(t).Volume;report['tested_pairs']+=1
        if v>1e-6:report['contacts'].append(dict(a=n,b=m,volume_mm3=v))
    try:
        progress('load shared scene and native receiving owner')
        docs,fixed,rings,torso,paths=load_scene(p)
        inputs=paths+[OUT/'source-group-allocation.json',OUT/'obstacle-map-current.json',Path(__file__),
                      Path(__file__).with_name('open_prototype_side_source_routes.py')]
        report['source_sha256']={f.relative_to(ROOT).as_posix():sha(f) for f in inputs}
        # Prove two new roots lie on material before drilling the receiving plate.
        before=docs[0].UpperCarrier.Shape
        feet=Part.makeBox(30,8,.2,A.Vector(-70,-22,77.52))
        area=feet.common(before).Volume/.2
        report['original_root_bearing_area_mm2']=area
        doc,carrier,body,bearing_owner=build(docs[0])
        area=feet.common(bearing_owner).Volume/.2
        assert area>239,('Incomplete matched receiving ear',area)
        report['root_bearing_area_mm2']=area
        for x in (-65,-45):
            test=Part.makeCylinder(2.7,3,A.Vector(x,-18,74.72))
            assert test.common(bearing_owner).Volume>test.Volume*.999,'Root lacks full fastener bearing'
        base=validate(doc,[carrier,body])
        doc.DataParameters.ShelfThickness=3.2;changed=validate(doc,[carrier,body])
        assert changed['DataShelf']>base['DataShelf'] and abs(changed['UpperCarrier']-base['UpperCarrier'])<1e-6
        doc.DataParameters.ShelfThickness=3;restored=validate(doc,[carrier,body])
        assert all(abs(base[n]-restored[n])<1e-6 for n in base)
        report['parameter_test']=dict(thickness_mm=[3,3.2,3],restored=True)
        progress('native parts/parameter restore checked')
        added_ear=carrier.Shape.cut(before)
        for n,s,basis in fixed:
            if n=='UpperCarrier':continue
            material('DataShelf',body.Shape,n,s)
            if not added_ear.isNull() and added_ear.Volume>1e-6:material('DataReceivingEar',added_ear,n,s)
        for t,s in rings.items():material('DataShelf',body.Shape,'S1_ring_'+str(t),s)
        # Both reoriented complete cases, all ten entries and their project
        # top-access budgets must fit, not just the shelf underneath them.
        changed_cases=[]
        for role in ('D_RL','D_RR'):
            row=next(r for r in p['stations'] if r['role']==role)
            case=box(row['centre_mm'],row['size_mm']);changed_cases.append((role,case))
            access=box([row['centre_mm'][0],-20,140.5],row['size_mm'][:2]+[16])
            for n,s,_ in fixed:
                if n==role:continue
                material(role,case,n,s);material(role+'/top_budget',access,n,s)
            if case.cut(torso).Volume>1e-6 or access.cut(torso).Volume>1e-6:
                report['contacts'].append(dict(a=role,b='torso boundary'))
        material('DataShelf',body.Shape,'UpperCarrier',carrier.Shape)
        outside=body.Shape.cut(torso).Volume
        if outside>1e-6:report['contacts'].append(dict(a='DataShelf',b='torso boundary',volume_mm3=outside))
        for n,(parts,r,_,_) in profiles(p).items():
            c=wire(parts)
            if near(c,body.Shape,r):
                d=c.distToShape(body.Shape)[0];report['tested_pairs']+=1
                if d<r-1e-6:report['contacts'].append(dict(a=n,b='DataShelf',distance_mm=d,required_mm=r))
            if not added_ear.isNull() and near(c,added_ear,r):
                d=c.distToShape(added_ear)[0];report['tested_pairs']+=1
                if d<r-1e-6:report['contacts'].append(dict(a=n,b='DataReceivingEar',distance_mm=d,required_mm=r))
        # Every port keeps its complete9mm straight approach, including NC.
        entries=[]
        for role in ('D_RL','D_RR'):
            for i in range(1,6):
                v=p['ports'][f'{role}.{i}'];start=v['point_mm'];end=add(start,mul(v['departure'],9))
                c=wire([line(start,end)]);d=c.distToShape(body.Shape)[0]
                assert d>=2.1-1e-6,(role,i,d)
                entry=Part.makeCylinder(2.1,9,A.Vector(*start),A.Vector(*v['departure']))
                for n,s,_ in fixed:
                    if n!=role:material(f'{role}.{i}/entry',entry,n,s)
                if entry.cut(torso).Volume>1e-6:report['contacts'].append(dict(a=f'{role}.{i}/entry',b='torso boundary'))
                entries.append(dict(port=f'{role}.{i}',point_mm=start,departure=v['departure'],straight_mm=9,support_mm=8))
        hardware=[]
        for i,x in enumerate((-65,-45)):
            screw=Part.makeCylinder(1.5,10,A.Vector(x,-18,70.72)).fuse(Part.makeCylinder(2.85,3,A.Vector(x,-18,80.72)))
            washer=Part.makeCylinder(3.5,.5,A.Vector(x,-18,74.22)).cut(Part.makeCylinder(1.6,.5,A.Vector(x,-18,74.22)))
            nut=Part.makePolygon([A.Vector(x+2.75/math.cos(math.pi/6)*math.cos(a*math.pi/3),-18+2.75/math.cos(math.pi/6)*math.sin(a*math.pi/3),71.82) for a in range(7)])
            nut=Part.Face(Part.Wire(nut.Edges)).extrude(A.Vector(0,0,2.4)).cut(Part.makeCylinder(1.6,2.4,A.Vector(x,-18,71.82)))
            for suffix,s in (('Screw',screw),('Washer',washer),('Nut',nut)):
                ob=doc.addObject('Part::Feature',f'DataMount{i+1}{suffix}');ob.Shape=s;hardware.append(ob)
                material(ob.Name,s,'DataShelf',body.Shape);material(ob.Name,s,'UpperCarrier',carrier.Shape)
                for n,t,_ in fixed:
                    if n!='UpperCarrier':material(ob.Name,s,n,t)
        for i,x in enumerate((-80,-40)):
            # Conservative installed strap/head envelope; not a supplier solid
            # or a claim of a measured tightened loop around unknown insulation.
            if i==0:
                outer=Part.makeBox(2.5,33.2,9.45,A.Vector(-67.25,-36.6,121.75))
                inner=Part.makeBox(3,31,7.25,A.Vector(-67.5,-35.5,122.85))
                head=Part.makeBox(5,5,5,A.Vector(-68.5,-41,128))
            else:
                outer=Part.makeBox(33.2,2.5,9.45,A.Vector(x-16.6,-35.75,121.75))
                inner=Part.makeBox(31,3,7.25,A.Vector(x-15.5,-36,122.85))
                head=Part.makeBox(5,5,5,A.Vector(x-20,-37,128))
            strap=outer.cut(inner)
            for suffix,s in (('StrapBudget',strap),('HeadBudget',head)):
                ob=doc.addObject('Part::Feature',f'DataTie{i+1}{suffix}');ob.Shape=s
                material(ob.Name,s,'DataShelf',body.Shape)
                for n,t,_ in fixed:material(ob.Name,s,n,t)
                for n,(parts,r,_,_) in profiles(p).items():
                    c=wire(parts)
                    if near(c,s,r) and c.distToShape(s)[0]<r-1e-6:report['contacts'].append(dict(a=n,b=ob.Name))
        report['changed_stations']=[r for r in p['stations'] if r['role'] in ('D_RL','D_RR')]
        report['changed_ports']={n:v for n,v in p['ports'].items() if n.startswith(('D_RL.','D_RR.'))}
        report['invalidated_wires']=['W011','W012','W013','W014','W015','W016','W017','W018']
        report['tie_budget']=dict(loop_perimeter_max_mm=85.3,nominal_stock_length_mm=100,
                                slot_width_mm=3.2,slot_height_mm=1.6,strap_width_mm=2.5,strap_thickness_mm=1.1,
                                not_manufacturer_measured_shape=True)
        report['entry_lands']=entries;report['native_volumes_mm3']=base
        report['sketches']=len([o for o in doc.Objects if o.TypeId=='Sketcher::SketchObject'])
        report['print_bounds_mm']={b.Name:[b.Shape.BoundBox.XLength,b.Shape.BoundBox.YLength,b.Shape.BoundBox.ZLength] for b in (carrier,body)}
        assert all(max(v)<=246 for v in report['print_bounds_mm'].values()),'Print margin'
        if report['contacts']:
            report['status']='REJECTED_DATA_MOUNT_CHANGED_INTERFACES'
            return
        # References are named as reservations, not native fabrication bodies.
        for role in ('D_RL','D_RR'):
            row=next(r for r in p['stations'] if r['role']==role)
            ob=doc.addObject('Part::Feature',role+'_NominalCase');ob.Shape=box(row['centre_mm'],row['size_mm'])
        doc.recompute();doc.saveAs(str(MODEL));report['model_sha256']=sha(MODEL)
        exports={}
        for b in (carrier,body):
            f=OUT/('DataShelf_'+b.Name+'.stl')
            mesh=MeshPart.meshFromShape(Shape=b.Shape,LinearDeflection=.08,AngularDeflection=.25,Relative=False)
            assert mesh.isSolid() and not mesh.hasNonManifolds(),b.Name
            mesh.write(str(f));reloaded=Mesh.Mesh(str(f))
            assert reloaded.isSolid() and not reloaded.hasNonManifolds(),f.name
            exports[f.name]=dict(sha256=sha(f),closed=True,manifold=True)
        report['exports']=exports
        A.closeDocument(doc.Name);doc=None
        reopen=A.openDocument(str(MODEL));validate(reopen,[reopen.UpperCarrier,reopen.DataShelf])
        assert all(abs(reopen.getObject(n).Shape.Volume-v)<1e-6 for n,v in base.items())
        A.closeDocument(reopen.Name)
        report.update(status='NATIVE_DATA_MOUNT_AND_TEN_STRAIGHT_APPROACHES_PREPARED',
                      local_data_mount_complete=True,reopen_verified=True)
    except Exception as exc:
        report['errors'].append(str(exc));report['status']='ERROR_NOT_ACCEPTANCE';raise
    finally:
        if doc:A.closeDocument(doc.Name)
        for d in docs:A.closeDocument(d.Name)
        if 'source_sha256' in report:assert all(sha(ROOT/n)==h for n,h in report['source_sha256'].items()),'Changed input'
        report.update(worker_seconds=round(time.monotonic()-tick,3),finished_utc=datetime.now(timezone.utc).isoformat())
        DEST.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({k:report.get(k) for k in ('status','contacts','errors','print_bounds_mm','worker_seconds')}),flush=True)


if __name__=='__main__':run()
