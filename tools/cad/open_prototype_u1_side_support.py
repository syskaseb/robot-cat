"""One provisional U1 side platform on the existing rigid upper carrier.

Supplier outline is known; hole coordinates/thickness are adjustable project
assumptions, NOT a validated mounting pattern. Keep the current set unchanged.
Only new material is checked; no repeated baseline audits or live GUI mutation.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, time, hashlib, tempfile, shutil

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/mounting-checkpoint'
STATE=ROOT.parent/'robot-cat/.codex/hooks/robot-cat-work-window.json'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def deadline():
    w=json.loads(STATE.read_text(encoding='utf-8-sig'))
    assert w['enabled'] and w['window_id']=='open-prototype-retention-20261008'
    assert datetime.now(timezone.utc)<datetime.fromisoformat(w['deadline_utc'].replace('Z','+00:00'))
    u=w['last_account_usage'];age=(datetime.now(timezone.utc)-datetime.fromisoformat(u['checked_utc'].replace('Z','+00:00'))).total_seconds()
    assert -30<=age<=600 and u['ordinary_usage_allowed'] and u['weekly_remaining_percent']>0

def main():
    import FreeCAD as A, Part, Mesh, MeshPart
    from open_deck_p0_supports import sketch, feature
    from open_deck_p0_plate import rect, circle
    started=datetime.now(timezone.utc).isoformat();tick=time.monotonic();deadline()
    src=OUT/'MountsCurrent.FCStd';native=OUT/'U1SideSupportCandidate.FCStd';proof=OUT/'u1-side-support-checks.json'
    assert not native.exists() and not proof.exists(),'Receive existing result before any new attempt'
    plan=json.loads((OUT/'retention-plan.json').read_text(encoding='utf-8'))
    assert sha(src)==plan['baseline_sha256']
    inputs=[src,OUT/'retention-plan.json',ROOT/'hardware/electronics/full-cat/pwm-carrier-r3/population.json',Path(__file__)]
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in inputs}
    d=A.openDocument(str(src))
    try:
        upper=d.UpperCarrier;before=upper.Shape.copy();p=d.Parameters
        for n,v in [('U1PlatformThickness',2.5),('U1HoleX',12.7),('U1HoleY',3.81),('U1SupportHeight',4.)]:
            p.addProperty('App::PropertyLength',n);setattr(p,n,v)
        # Join the untouched floor from Y24..27; no added material within PCB footprint in Z>=82.72.
        sk=sketch(upper,'U1SideFoot', 'Parameters.UpperBase');rect(sk,73.59,24,36,29)
        upper.Tip=feature(upper,'Pad','U1SideExtension',sk,'Parameters.PlateThickness')
        sk=sketch(upper,'U1SidePlatform','Parameters.UpperBase+Parameters.PlateThickness')
        rect(sk,73.59,31,36,22)
        upper.Tip=feature(upper,'Pad','U1SidePlatformThickness',sk,'Parameters.U1PlatformThickness')
        sk=sketch(upper,'U1SideAttachmentPattern','Parameters.UpperBase+Parameters.PlateThickness+Parameters.U1PlatformThickness')
        for i,(sx,sy) in enumerate([(-1,-1),(1,1)]):
            circle(sk,91.59+sx*12.7,42+sy*3.81,2.4)
            sk.setExpression(f'Constraints[{i*3}]',f'91.59 mm {"+" if sx>0 else "-"} Parameters.U1HoleX')
            sk.setExpression(f'Constraints[{i*3+1}]',f'42 mm {"+" if sy>0 else "-"} Parameters.U1HoleY')
        upper.Tip=feature(upper,'Pocket','U1AttachmentClearance',sk,'Parameters.PlateThickness+Parameters.U1PlatformThickness')
        spacer=d.addObject('PartDesign::Body','U1InsulatingSpacer')
        sk=sketch(spacer,'U1SpacerPlan',0);circle(sk,0,0,4.5);circle(sk,0,0,2.4)
        spacer.Tip=feature(spacer,'Pad','U1SpacerHeight',sk,'Parameters.U1SupportHeight')
        new_links=[]
        for i,(sx,sy) in enumerate([(-1,-1),(1,1)]):
            ob=d.addObject('App::Link','U1Spacer'+str(i+1));ob.setLink(spacer)
            ob.setExpression('LinkPlacement.Base.x',f'91.59 mm {"+" if sx>0 else "-"} Parameters.U1HoleX')
            ob.setExpression('LinkPlacement.Base.y',f'42 mm {"+" if sy>0 else "-"} Parameters.U1HoleY')
            ob.setExpression('LinkPlacement.Base.z','Parameters.UpperBase+Parameters.PlateThickness+Parameters.U1PlatformThickness')
            new_links.append(ob)
        def valid():
            deadline();d.recompute()
            for b in [upper,spacer]:
                assert b.Shape.isValid() and len(b.Shape.Solids)==1 and not b.Shape.check(True),b.Name
                assert all('Invalid' not in o.State and 'Touched' not in o.State for o in b.Group),b.Name
                assert all(o.FullyConstrained and o.solve()==0 for o in b.Group if o.TypeId=='Sketcher::SketchObject')
            return {b.Name:b.Shape.Volume for b in [upper,spacer]}
        base=valid();p.U1HoleX=12.2;valid();p.U1HoleX=12.7;assert all(abs(v-valid()[n])<1e-6 for n,v in base.items())
        p.U1SupportHeight=4.5;trial=valid();assert trial['U1InsulatingSpacer']>base['U1InsulatingSpacer']
        p.U1SupportHeight=4.;assert all(abs(v-valid()[n])<1e-6 for n,v in base.items())
        added=upper.Shape.cut(before);assert added.isValid()
        removed=before.cut(upper.Shape);assert removed.isValid()
        assert removed.Volume<26,'Only two candidate attachment bores remove original/new material'
        targets={'UpperCarrierAdded':added,**{o.Name:o.Shape for o in new_links}}
        obstacles={o.Name:o.Shape for o in d.Objects if 'Shape' in o.PropertiesList and not o.Shape.isNull()
            and (o.TypeId=='App::Link' and o not in new_links or o.Name.startswith('BUSsupplier') or o.Name.endswith('NominalPCB'))}
        contacts=[];errors=[];reservations=[];pairs=0
        def compare(n,s,m,t,dest):
            nonlocal pairs
            if not s.BoundBox.intersect(t.BoundBox):return
            pairs+=1;deadline()
            try:
                assert s.isValid() and t.isValid();hit=s.common(t);assert hit.isValid()
                if hit.Volume>1e-5:dest.append({'a':n,'b':m,'volume_mm3':hit.Volume})
            except Exception as e:errors.append({'a':n,'b':m,'error':str(e)})
        for n,s in targets.items():
            for m,t in obstacles.items():compare(n,s,m,t,reservations if m.endswith('NominalPCB') else contacts)
        pop=json.loads(inputs[2].read_text(encoding='utf-8'))
        for c in pop['components']:
            x,y=c['center'];w,h=c['xy_max'];lo,hi=c['z_min'],c['z_max']
            t=Part.makeBox(w,h,hi-lo,A.Vector(91.59+x-w/2,y-h/2,84.3202+lo))
            for n,s in targets.items():compare(n,s,'PWMcase_'+c['ref'],t,reservations)
        dist=json.loads((OUT/'distribution-mount-plan.json').read_text(encoding='utf-8'))
        for r in dist['distribution']:
            x,y=r['centre_xy_mm'];w,h,t=r['size_mm'];s=Part.makeBox(w,h,t,A.Vector(x-w/2,y-h/2,r['base_z_mm']))
            for n,q in targets.items():compare(n,q,r['role']+'_casing_budget',s,reservations)
        assert not contacts and not errors and not reservations,(contacts,errors,reservations)
        # The board is an allowance, not a fabricated supplied PCB geometry.
        board=Part.makeBox(30.48,17.78,1.6,A.Vector(76.35,33.11,84.22))
        ob=d.addObject('Part::Feature','U1NominalOutlineOnly');ob.Shape=board
        ob.addProperty('App::PropertyString','Qualification');ob.Qualification='Project thickness/hole assumptions; delivered fit OPEN'
        for n,s in targets.items():compare(n,s,'U1NominalOutlineOnly',board,reservations)
        assert not reservations
        exports=[]
        for b,qty in [(upper,1),(spacer,2)]:
            path=OUT/(b.Name+'U1Candidate.stl');s=b.Shape.copy();s.translate(A.Vector(-s.BoundBox.XMin,-s.BoundBox.YMin,-s.BoundBox.ZMin))
            MeshPart.meshFromShape(Shape=s,LinearDeflection=.04,AngularDeflection=.15,Relative=False).write(str(path))
            m=Mesh.Mesh(str(path));assert m.isSolid() and m.countComponents()==1
            bounds=[m.BoundBox.XLength+10,m.BoundBox.YLength+10,m.BoundBox.ZLength];assert max(bounds)<256
            exports.append({'part':b.Name,'quantity':qty,'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'bounds_with_5mm_brim_mm':bounds})
        d.saveAs(str(native));A.closeDocument(d.Name)
        with tempfile.TemporaryDirectory(prefix='robot-cat-u1-side-reopen-') as td:
            cp=Path(td)/native.name;shutil.copy2(native,cp);d=A.openDocument(str(cp));upper=d.UpperCarrier;spacer=d.U1InsulatingSpacer;p=d.Parameters
            assert all(abs(v-valid()[n])<1e-6 for n,v in base.items())
        result=dict(status='U1_SIDE_PLATFORM_CANDIDATE_GEOMETRY_CLEAR_DELIVERED_ATTACHMENT_OPEN',source_sha256=pins,native_sha256=sha(native),
            started_utc=started,finished_utc=datetime.now(timezone.utc).isoformat(),worker_wall_seconds=round(time.monotonic()-tick,3),
            changed_pairs=pairs,material_contacts=contacts,reservation_contacts=reservations,errors=errors,
            added_volume_mm3=added.Volume,removed_volume_mm3=removed.Volume,parameter_cycles={'hole_x':[12.7,12.2,12.7],'support_height':[4,4.5,4]},relocated_reopen=True,
            exports=exports,selected=False,stage_completed=False,physical_pass=False,
            known_bounds=['Two attachment holes and thickness are project assumptions, not supplier pattern',
                'Existing MountsCurrent/current-set untouched; candidate not a second print selection',
                'Actual bolt/washer/solder support and local50mm wires still require qualification; no whole-stage credit'])
        assert all(sha(ROOT/k)==v for k,v in pins.items())
        proof.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({k:result[k] for k in ['status','worker_wall_seconds','changed_pairs','material_contacts','reservation_contacts']}),flush=True)
    finally:
        if d.Name in A.listDocuments():A.closeDocument(d.Name)

if __name__=='__main__':main()
