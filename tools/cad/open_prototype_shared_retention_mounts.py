"""One common U1 mount/fastener set with retained lever-free WAGO candidate.

Dimensioned native project assumptions remain assumptions. Test only changed
material/hardware and relevant current surroundings; preserve source documents.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, math, time, shutil, tempfile
from open_prototype_u1_side_support import ROOT, OUT, sha, deadline


def main():
    import FreeCAD as A, Part, Mesh, MeshPart
    from open_deck_p0_supports import sketch, feature
    from open_deck_p0_plate import rect, circle
    tick=time.monotonic();started=datetime.now(timezone.utc).isoformat();deadline()
    src=OUT/'RetentionMountsCandidate.FCStd';native=OUT/'RetentionMountsAssembly.FCStd';proof=OUT/'shared-retention-mount-checks.json'
    assert not native.exists() and not proof.exists(),'Receive existing result before another worker'
    old=json.loads((OUT/'wago-retention-checks.json').read_text(encoding='utf-8'))
    assert sha(src)==old['native_sha256'] and not old['nominal_reservation_contacts']
    plan=json.loads((OUT/'u1-shared-mount-plan.json').read_text(encoding='utf-8'))
    paths=[src,OUT/'wago-retention-checks.json',OUT/'u1-shared-mount-plan.json',OUT/'MountsCurrent.FCStd',
        OUT.parent/'OpenPrototypePlan.FCStd',ROOT/'hardware/electronics/full-cat/pwm-carrier-r3/population.json',
        ROOT/'hardware/reference/u1-adapter-2026-09-26/source.json',Path(__file__)]
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in paths}
    d=A.openDocument(str(src));context=None;baseline=None
    try:
        p=d.Parameters;upper=d.UpperCarrier
        for name,val in [('U1CentreX',94.59),('U1CentreY',33.),('U1BoardThickness',1.6),('U1TopInsulatorThickness',1.)]:
            p.addProperty('App::PropertyLength',name);setattr(p,name,val)
        p.U1SupportHeight=7.
        # Retained floor interface unchanged; extend the side platform beneath
        # BOTH spacer axes, not just beneath the nominal board outline.
        d.U1SideFoot.setExpression('Constraints[8]','Parameters.U1CentreX-18 mm')
        d.U1SidePlatform.setExpression('Constraints[8]','Parameters.U1CentreX-18 mm')
        d.U1SidePlatform.setDatum(9,A.Units.Quantity('26 mm'))
        d.U1SidePlatform.setDatum(11,A.Units.Quantity('21 mm'))
        for i,(sx,sy) in enumerate([(-1,-1),(1,1)]):
            pat=d.U1SideAttachmentPattern
            pat.setExpression(f'Constraints[{i*3}]',f'Parameters.U1CentreX {"+" if sx>0 else "-"} Parameters.U1HoleX')
            pat.setExpression(f'Constraints[{i*3+1}]',f'Parameters.U1CentreY {"+" if sy>0 else "-"} Parameters.U1HoleY')
            sp=d.getObject('U1Spacer'+str(i+1))
            sp.setExpression('LinkPlacement.Base.x',f'Parameters.U1CentreX {"+" if sx>0 else "-"} Parameters.U1HoleX')
            sp.setExpression('LinkPlacement.Base.y',f'Parameters.U1CentreY {"+" if sy>0 else "-"} Parameters.U1HoleY')
        d.removeObject('U1NominalOutlineOnly')
        board=d.addObject('PartDesign::Body','U1BoardAllowance')
        board.addProperty('App::PropertyString','Qualification');board.Qualification='Supplier outline; hole/thickness/pad pattern project assumptions, delivered fit OPEN'
        sk=sketch(board,'U1AllowanceOutline',0);rect(sk,-15.24,-8.89,30.48,17.78)
        board.Tip=feature(board,'Pad','U1AllowanceThickness',sk,'Parameters.U1BoardThickness')
        sk=sketch(board,'U1AllowanceHoles','Parameters.U1BoardThickness')
        for i,(sx,sy) in enumerate([(-1,-1),(1,1)]):
            circle(sk,sx*12.7,sy*3.81,2.4)
            sk.setExpression(f'Constraints[{i*3}]',f'{"" if sx>0 else "-"}Parameters.U1HoleX')
            sk.setExpression(f'Constraints[{i*3+1}]',f'{"" if sy>0 else "-"}Parameters.U1HoleY')
        board.Tip=feature(board,'Pocket','U1AllowanceBores',sk,'Parameters.U1BoardThickness')
        board.setExpression('Placement.Base.x','Parameters.U1CentreX');board.setExpression('Placement.Base.y','Parameters.U1CentreY')
        bottom='Parameters.UpperBase+Parameters.PlateThickness+Parameters.U1PlatformThickness+Parameters.U1SupportHeight'
        board.setExpression('Placement.Base.z',bottom)
        washer=d.addObject('PartDesign::Body','U1TopInsulator')
        sk=sketch(washer,'U1InsulatorPlan',0);circle(sk,0,0,4.5);circle(sk,0,0,2.4)
        washer.Tip=feature(washer,'Pad','U1InsulatorThickness',sk,'Parameters.U1TopInsulatorThickness')
        hardware=d.addObject('App::DocumentObjectGroup','U1NominalMountHardware')
        new={};tools={};washers=[]
        for i,(sx,sy) in enumerate([(-1,-1),(1,1)],1):
            expressions={'x':f'Parameters.U1CentreX {"+" if sx>0 else "-"} Parameters.U1HoleX',
                'y':f'Parameters.U1CentreY {"+" if sy>0 else "-"} Parameters.U1HoleY'}
            ob=d.addObject('App::Link','U1Insulator'+str(i));ob.setLink(washer)
            for axis,e in expressions.items():ob.setExpression('LinkPlacement.Base.'+axis,e)
            ob.setExpression('LinkPlacement.Base.z',bottom+'+Parameters.U1BoardThickness');washers.append(ob)
            cyl=lambda z,r,h:Part.makeCylinder(r,h,A.Vector(0,0,z))
            screw=cyl(-20,1,20).fuse(cyl(0,1.9,2))
            rad=4/math.sqrt(3);vs=[A.Vector(rad*math.cos(j*math.pi/3),rad*math.sin(j*math.pi/3),0) for j in range(6)]
            nut=Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(A.Vector(0,0,1.6)).cut(cyl(0,1.025,1.6))
            for suffix,shape,zexpr in [('Screw',screw,bottom+'+Parameters.U1BoardThickness+Parameters.U1TopInsulatorThickness'),
                ('Nut',nut,'Parameters.UpperBase-1.6 mm')]:
                ob=d.addObject('Part::Feature','U1Mount'+str(i)+suffix);ob.Shape=shape;hardware.addObject(ob)
                for axis,e in expressions.items():ob.setExpression('Placement.Base.'+axis,e)
                ob.setExpression('Placement.Base.z',zexpr);new[ob.Name]=ob
            # A filled socket probe would falsely hit the protruding shank.
            # Nominal AF4.3 mouth and2.4mm through clearance; not a tool SKU.
            mouthrad=4.3/math.sqrt(3)
            vs=[A.Vector(mouthrad*math.cos(j*math.pi/3),mouthrad*math.sin(j*math.pi/3),-.4) for j in range(6)]
            mouth=Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(A.Vector(0,0,2.))
            socket=cyl(-12,2.75,13.6).cut(cyl(-12,1.2,13.6)).cut(mouth)
            for suffix,shape,zexpr in [('Driver',cyl(0,1.25,40),bottom+'+Parameters.U1BoardThickness+Parameters.U1TopInsulatorThickness+2 mm'),
                ('NutSocket',socket,'Parameters.UpperBase-1.6 mm')]:
                ob=d.addObject('Part::Feature','U1Mount'+str(i)+suffix);ob.Shape=shape
                for axis,e in expressions.items():ob.setExpression('Placement.Base.'+axis,e)
                ob.setExpression('Placement.Base.z',zexpr);tools[ob.Name]=ob
        bodies=[upper,d.U1InsulatingSpacer,washer,board]
        def validate():
            deadline();d.recompute()
            for b in bodies:
                assert b.Shape.isValid() and len(b.Shape.Solids)==1 and not b.Shape.check(True),b.Name
                assert all('Invalid' not in o.State and 'Touched' not in o.State for o in b.Group),b.Name
                assert all(o.FullyConstrained and o.solve()==0 for o in b.Group if o.TypeId=='Sketcher::SketchObject'),b.Name
            for i in (1,2):
                sp=d.getObject('U1Spacer'+str(i));wa=d.getObject('U1Insulator'+str(i));bolt=d.getObject('U1Mount'+str(i)+'Screw')
                assert abs(sp.Shape.BoundBox.ZMax-board.Shape.BoundBox.ZMin)<1e-6
                assert abs(wa.Shape.BoundBox.ZMin-board.Shape.BoundBox.ZMax)<1e-6
                assert abs(bolt.Placement.Base.z-wa.Shape.BoundBox.ZMax)<1e-6
            return {b.Name:b.Shape.Volume for b in bodies}
        original=validate();p.U1HoleX=12.2;validate();p.U1HoleX=12.7;assert all(abs(validate()[n]-v)<1e-5 for n,v in original.items())
        p.U1SupportHeight=7.5;validate();p.U1SupportHeight=7.;assert all(abs(validate()[n]-v)<1e-5 for n,v in original.items())
        baseline=A.openDocument(str(OUT/'MountsCurrent.FCStd'));context=A.openDocument(str(OUT.parent/'OpenPrototypePlan.FCStd'))
        added=upper.Shape.cut(baseline.UpperCarrier.Shape);removed=baseline.UpperCarrier.Shape.cut(upper.Shape)
        assert added.isValid() and removed.isValid() and removed.Volume<1e-5,'Retained upper carrier material lost'
        targets={'UpperCarrierAdded':added,**{d.getObject('U1Spacer'+str(i)).Name:d.getObject('U1Spacer'+str(i)).Shape for i in (1,2)},
            **{o.Name:o.Shape for o in washers},**{n:o.Shape for n,o in new.items()}}
        actual={o.Name:o.Shape for o in context.Objects if 'Shape' in o.PropertiesList and not o.Shape.isNull()
            and (o.Name.startswith('P0_') or o.Name in ('LeftRiserWithMain','RightRiser','MainSupplierFamily'))}
        actual.update({o.Name:o.Shape for o in d.Objects if 'Shape' in o.PropertiesList and
            ((o.TypeId=='App::Link' and o.Name not in targets) or o.Name.startswith('BUSsupplier'))})
        actual['LowerCarrier']=d.LowerCarrier.Shape
        actual.update({o.Name:o.Shape for g in (d.NominalMountHardware,d.SideMountHardware) for o in g.Group})
        reservations={o.Name:o.Shape for o in d.Objects if 'Shape' in o.PropertiesList and
            (o.Name.endswith('NominalPCB') or o.Name.endswith('_CP2'))}
        reservations['U1BoardAllowance']=board.Shape
        reservations.update({o.Name:o.Shape for o in context.Objects if o.Name.startswith(('S0_','S1_','MTA_','F_PI_')) and 'Shape' in o.PropertiesList})
        pop=json.loads(paths[5].read_text(encoding='utf-8'))
        for c in pop['components']:
            x,y=c['center'];w,h=c['xy_max'];lo,hi=c['z_min'],c['z_max']
            reservations['PWMcase_'+c['ref']]=Part.makeBox(w,h,hi-lo,A.Vector(91.59+x-w/2,y-h/2,84.3202+lo))
        contacts=[];errors=[];reserved=[];pairs=0
        def compare(n,s,m,t,dest):
            nonlocal pairs
            if not s.BoundBox.intersect(t.BoundBox):return
            pairs+=1;deadline()
            try:
                assert s.isValid() and t.isValid(),(n,m)
                hit=s.common(t);assert hit.isValid()
                if hit.Volume>1e-5:dest.append(dict(a=n,b=m,volume_mm3=hit.Volume))
            except Exception as e:errors.append(dict(a=n,b=m,error=str(e)))
        for n,s in targets.items():
            for m,t in actual.items():compare(n,s,m,t,contacts)
            for m,t in reservations.items():compare(n,s,m,t,reserved)
            for m,t in targets.items():
                if m>n:compare(n,s,m,t,contacts)
        for m,t in {**actual,**reservations}.items():
            if m!='U1BoardAllowance':compare('U1BoardAllowance',board.Shape,m,t,reserved)
        for n,ob in tools.items():
            for m,t in {**actual,**targets}.items():
                if m!=n.replace('Driver','Screw').replace('NutSocket','Nut'):compare(n,ob.Shape,m,t,contacts)
            for m,t in reservations.items():compare(n,ob.Shape,m,t,reserved)
        # Each spacer foot bears on real platform material, excluding the bore.
        support=[]
        for i in (1,2):
            ob=d.getObject('U1Spacer'+str(i));x,y,z=ob.LinkPlacement.Base
            probe=Part.makeCylinder(2.25,.1,A.Vector(x,y,z-.1)).cut(Part.makeCylinder(1.2,.1,A.Vector(x,y,z-.1)))
            fraction=probe.common(upper.Shape).Volume/probe.Volume
            support.append(dict(spacer=ob.Name,bearing_fraction=fraction));assert fraction>1-1e-6
        # Wider photo-consistent pad pattern: not a delivered pad map and never
        # a route. Model its solder keepouts explicitly against new attachments.
        lead_screen=[];pad_hits=[]
        for t in pop['terminals']:
            if not t['ref'].startswith('U1_LAND.'):continue
            pin=int(t['ref'].split('.')[1]);px=-13.97+2.54*(pin-1) if pin<=12 else 13.97-2.54*(pin-13)
            py=-7.62 if pin<=12 else 7.62;x=94.59-px;y=33-py
            dx=x-91.59-t['x'];dy=y-t['y'];length=math.sqrt(dx*dx+dy*dy+4.5**2)
            lead_screen.append(dict(ref=t['ref'],assumed_adapter_xy_mm=[x,y],straight_bound_mm=length,
                plus3mm_planning_allowance_mm=length+3,actual_delivered_map=False))
            keepout=Part.makeCylinder(1.1,6,A.Vector(x,y,board.Shape.BoundBox.ZMin-3))
            for n,s in targets.items():compare('U1assumed_pad'+str(pin),keepout,n,s,pad_hits)
        assert max(r['plus3mm_planning_allowance_mm'] for r in lead_screen)<50
        assert not errors,errors
        exports=[]
        if not(contacts or reserved or pad_hits):
            for b,qty in [(upper,1),(d.U1InsulatingSpacer,2),(washer,2)]:
                s=b.Shape.copy();s.translate(A.Vector(-s.BoundBox.XMin,-s.BoundBox.YMin,-s.BoundBox.ZMin));path=OUT/(b.Name+'Retention.stl')
                MeshPart.meshFromShape(Shape=s,LinearDeflection=.04,AngularDeflection=.15,Relative=False).write(str(path))
                mesh=Mesh.Mesh(str(path));assert mesh.isSolid() and mesh.countComponents()==1
                bounds=[mesh.BoundBox.XLength+10,mesh.BoundBox.YLength+10,mesh.BoundBox.ZLength];assert max(bounds)<256
                exports.append(dict(part=b.Name,quantity=qty,path=path.relative_to(ROOT).as_posix(),sha256=sha(path),bounds_with_5mm_brim_mm=bounds))
        d.Label='Open prototype shared retention mounts; delivered adapter/adhesion OPEN';d.saveAs(str(native))
        A.closeDocument(context.Name);context=None;A.closeDocument(baseline.Name);baseline=None;A.closeDocument(d.Name)
        with tempfile.TemporaryDirectory(prefix='robot-cat-shared-retention-reopen-') as td:
            cp=Path(td)/native.name;shutil.copy2(native,cp);d=A.openDocument(str(cp));p=d.Parameters
            upper=d.UpperCarrier;washer=d.U1TopInsulator;board=d.U1BoardAllowance;bodies=[upper,d.U1InsulatingSpacer,washer,board]
            assert all(abs(validate()[n]-v)<1e-5 for n,v in original.items())
        result=dict(status='SHARED_RETENTION_MOUNTS_GEOMETRY_CLEAR_PROVISIONAL' if not(contacts or reserved or pad_hits) else 'SHARED_RETENTION_MOUNTS_REQUIRE_CHANGE',
            source_sha256=pins,native_sha256=sha(native),started_utc=started,finished_utc=datetime.now(timezone.utc).isoformat(),
            worker_wall_seconds=round(time.monotonic()-tick,3),changed_pairs=pairs,material_contacts=contacts,
            nominal_reservation_contacts=reserved,assumed_pad_keepout_contacts=pad_hits,errors=errors,
            spacer_bearing=support,lead_space_screen=lead_screen,local_lead_routes_qualified=False,
            parameter_cycles={'hole_x':[12.7,12.2,12.7],'support_height':[7,7.5,7]},relocated_reopen=True,exports=exports,
            retained_upper_removed_volume_mm3=removed.Volume,selected=False,stage_completed=False,physical_pass=False)
        assert all(sha(ROOT/k)==v for k,v in pins.items())
        proof.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({k:result[k] for k in ('status','worker_wall_seconds','changed_pairs','material_contacts','nominal_reservation_contacts','assumed_pad_keepout_contacts','errors')}),flush=True)
    finally:
        for ob in (context,baseline):
            if ob:A.closeDocument(ob.Name)
        if d.Name in A.listDocuments():A.closeDocument(d.Name)


if __name__=='__main__':main()
