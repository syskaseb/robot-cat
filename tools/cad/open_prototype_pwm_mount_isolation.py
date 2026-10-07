"""Own replaceable insulating shoulder washers; changed PWM mounting only.

Nominal PETG geometry is not a dielectric/creep or delivered-fit qualification.
No commercial washer SKU, supplier pad position or U1 support is invented.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, time, tempfile, shutil

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/mounting-checkpoint'

def sha(p):
    import hashlib
    return hashlib.sha256(p.read_bytes()).hexdigest()

def guard():
    assert datetime.now(timezone.utc)<datetime.fromisoformat('2026-10-07T23:10:24+00:00')

def main():
    import FreeCAD as A, Part, Mesh, MeshPart
    from open_deck_p0_supports import sketch, feature
    from open_deck_p0_plate import circle
    guard(); tick=time.monotonic(); started=datetime.now(timezone.utc).isoformat()
    source=OUT/'DistributionMounts.FCStd'; native=OUT/'InsulatedMounts.FCStd'
    proof=OUT/'pwm-mount-isolation-checks.json'
    assert not native.exists() and not proof.exists(), 'Receive existing worker; no duplicate'
    inherited=json.loads((OUT/'distribution-mount-checks.json').read_text(encoding='utf-8'))
    assert inherited['status']=='SHARED_DISTRIBUTION_MOUNTS_LOCAL_CLEAR'
    assert sha(source)==inherited['native_sha256']
    population_path=ROOT/'hardware/electronics/full-cat/pwm-carrier-r3/population.json'
    paths=[source,OUT/'distribution-mount-checks.json',OUT/'board-hardware-checks.json',
           population_path,ROOT/'hardware/cad/studies/full-cat-board-carrier/r6/isolation.json',Path(__file__)]
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in paths}
    hardware=json.loads(paths[2].read_text(encoding='utf-8'))
    pop=json.loads(population_path.read_text(encoding='utf-8'))
    d=A.openDocument(str(source))
    try:
        p=d.Parameters
        for name,value in [('PwmInsulatorThickness',1.),('PwmInsulatorNeck',1.6002)]:
            p.addProperty('App::PropertyLength',name);setattr(p,name,value)
        body=d.addObject('PartDesign::Body','PwmInsulatingShoulderWasher')
        body.addProperty('App::PropertyString','Material');body.Material='PETG; provisional fit, creep and insulation coupon OPEN'
        sk=sketch(body,'PwmInsulatorNeckPlan','-Parameters.PwmInsulatorNeck')
        circle(sk,0,0,3.);circle(sk,0,0,2.4)
        body.Tip=feature(body,'Pad','PwmInsulatorNeckPad',sk,'Parameters.PwmInsulatorNeck')
        sk=sketch(body,'PwmInsulatorHeadPlan',0)
        circle(sk,0,0,5.);circle(sk,0,0,2.4)
        body.Tip=feature(body,'Pad','PwmInsulatorHeadPad',sk,'Parameters.PwmInsulatorThickness')
        stacks=[]; changed={}; links=[]
        for i,row in enumerate([r for r in hardware['fasteners'] if r['role']=='PWM1608'],1):
            name=row['id'];x,y=row['axis_xy_mm'];washer=d.getObject(name+'TopWasher')
            assert washer is not None
            d.removeObject(washer.Name)
            ob=d.addObject('App::Link',name+'TopInsulator');ob.setLink(body)
            ob.LinkPlacement.Base=A.Vector(x,y,84.3202);links.append(ob)
            screw=d.getObject(name+'Screw')
            screw.setExpression('Placement.Base.z','Parameters.PwmInsulatorThickness - 0.3 mm')
            underhead=row['underhead_z_mm']+.7;tip=underhead-row['length_mm']
            nz=row['nut_z_mm'];engagement=min(underhead,nz[1])-max(tip,nz[0])
            assert engagement>=1.6-1e-6 and nz[0]-tip>0
            stacks.append(dict(id=name,axis_xy_mm=[x,y],length_mm=14,underhead_z_mm=underhead,
                tip_z_mm=tip,nut_z_mm=nz,nominal_nut_engagement_mm=engagement,
                protrusion_mm=nz[0]-tip,metal_head_above_copper_plane_mm=1.,
                shoulder_od_mm=3.,pcb_hole_mm=3.2,bore_mm=2.4,insulator_od_mm=5.))
        def valid():
            guard();d.recompute();s=body.Shape
            assert s.isValid() and len(s.Solids)==1 and not s.check(True)
            assert all('Invalid' not in o.State and 'Touched' not in o.State for o in body.Group)
            assert all(o.FullyConstrained and o.solve()==0 for o in body.Group if o.TypeId=='Sketcher::SketchObject')
            for row in stacks:
                screw=d.getObject(row['id']+'Screw')
                assert abs(screw.Placement.Base.z-(p.PwmInsulatorThickness.Value-.3))<1e-6
            return s.Volume
        volume=valid();p.PwmInsulatorThickness=1.2;assert valid()>volume
        p.PwmInsulatorThickness=1.;assert abs(valid()-volume)<1e-6
        targets={o.Name:o.Shape for o in d.Objects if o.TypeId=='App::Link'}
        targets.update({n:d.getObject(n).Shape for n in ['LowerCarrier','UpperCarrier','Pi4NominalPCB',
            'PWM9685NominalPCB','AUX4092NominalPCB','PWM1608NominalPCB']})
        targets.update({o.Name:o.Shape for o in d.NominalMountHardware.Group})
        # Supplier maximum component cases remain named reservations, not actual
        # solid contact evidence. Coordinates are component-side Eagle XY.
        parts={}
        for row in pop['components']:
            x,y=row['center'];w,h=row['xy_max'];lo,hi=row['z_min'],row['z_max']
            parts[row['ref']]=Part.makeBox(w,h,hi-lo,A.Vector(91.59+x-w/2,y-h/2,84.3202+lo))
        contacts=[];reservations=[];errors=[];tested=0
        def compare(name,s,others,dest):
            nonlocal tested
            for n,t in others.items():
                if n==name or not s.BoundBox.intersect(t.BoundBox):continue
                tested+=1;guard()
                try:
                    assert s.isValid() and t.isValid();hit=s.common(t);assert hit.isValid()
                    if hit.Volume>1e-5:dest.append(dict(a=name,b=n,volume_mm3=hit.Volume))
                except Exception as e:errors.append(dict(a=name,b=n,error=str(e)))
        for row,ob in zip(stacks,links):
            root=row['id'];screw=d.getObject(root+'Screw')
            changed.update({ob.Name:ob.Shape,screw.Name:screw.Shape})
            compare(ob.Name,ob.Shape,targets,contacts)
            compare(screw.Name,screw.Shape,targets,contacts)
            compare(ob.Name,ob.Shape,parts,reservations)
            compare(screw.Name,screw.Shape,parts,reservations)
            x,y=row['axis_xy_mm']
            compare(root+'DriverAllowance',Part.makeCylinder(1.5,18,A.Vector(x,y,row['underhead_z_mm']+2)),parts,reservations)
        # Changed carrier-to-population evidence: never covered by inherited
        # plain PCB checks. Underside solder and U1 are explicitly still open.
        compare('UpperCarrier',d.UpperCarrier.Shape,parts,reservations)
        assert not(contacts or reservations or errors), (contacts,reservations,errors)
        for ob in body.Group:
            if ob.ViewObject:ob.Visibility=False
        if body.ViewObject:body.Visibility=False
        d.saveAs(str(native))
        s=body.Shape.copy();b=s.BoundBox;s.translate(A.Vector(-b.XMin,-b.YMin,-b.ZMin))
        export=OUT/'PwmInsulatingShoulderWasher.stl'
        MeshPart.meshFromShape(Shape=s,LinearDeflection=.04,AngularDeflection=.15,Relative=False).write(str(export))
        mesh=Mesh.Mesh(str(export));assert mesh.isSolid() and mesh.countComponents()==1
        size=[mesh.BoundBox.XLength+10,mesh.BoundBox.YLength+10,mesh.BoundBox.ZLength]
        assert max(size)<256
        A.closeDocument(d.Name)
        with tempfile.TemporaryDirectory(prefix='robot-cat-insulator-reopen-') as td:
            relocated=Path(td)/native.name;shutil.copy2(native,relocated);d=A.openDocument(str(relocated))
            p=d.Parameters;body=d.PwmInsulatingShoulderWasher
            assert abs(valid()-volume)<1e-6
        result=dict(status='PWM_MOUNT_ISOLATION_NOMINAL_CLEAR',selected=False,stage_completed=False,physical_pass=False,
            started_utc=started,finished_utc=datetime.now(timezone.utc).isoformat(),worker_wall_seconds=round(time.monotonic()-tick,3),
            source_sha256=pins,native_sha256=sha(native),changed_pairs=tested,material_contacts=contacts,
            component_case_reservation_contacts=reservations,errors=errors,population_cases=len(parts),
            parameter_roundtrip_mm=[1,1.2,1],relocated_reopen=True,stacks=stacks,
            replaced_metal_top_washers=2,own_replaceable_petg_insulators=2,
            exports=[dict(part=body.Name,quantity=2,path=export.relative_to(ROOT).as_posix(),sha256=sha(export),bounds_with_5mm_brim_mm=size)],
            assembly='Replace ONLY two upper PWM1608 steel washers; shoulder enters PCB hole, flange above copper. Verify coupon/fit/no crush/creep with isolated source before physical assembly.',
            limitations=['Own nominal design, no vendor SKU or insulation certification; 0.3mm radial neck wall requires physical print/fit assessment',
                'Actual solder-side height/insulated wire paths and temperature remain phase2 conditions; no energizing authority',
                'U1 adapter575070 still has no qualified support: exact thickness/pad locations absent. Do not guess copper-free clip sites'],
            adapter_stack=pop['adapter_stack'])
        assert all(sha(ROOT/k)==v for k,v in pins.items())
        proof.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({k:result[k] for k in ['status','worker_wall_seconds','changed_pairs','population_cases','material_contacts','component_case_reservation_contacts']}),flush=True)
    finally:
        if d.Name in A.listDocuments():A.closeDocument(d.Name)

if __name__=='__main__':main()
