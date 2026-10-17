"""Correct the CAUSE of end-wall crossings in a new derived native document.

Moving only the inner end planes3mm changed the taper, not just end openness.
Keep inner/outer station X aligned; subtracting coincident capped volumes still
opens the neck/tail. Receive the added material against current full motion.
"""
import json,time
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import OUT,STAGES
from check_feline_leg_body import placement
from check_feline_shared_space import tube_prefix
from datetime import datetime as DT,timezone as TZ


def main():
    tick=time.monotonic();reader=SavedShapes();source=OUT/'FelineTorsoPanels.FCStd';target=OUT/'FelineTorsoPanelsEndCorrected.FCStd'
    assert not target.exists(),'Receive existing derived native before another build'
    oldmeta=json.loads((OUT/'shared-skin-exact.json').read_text());assert oldmeta['native_sha256']==sha(source)
    access=json.loads((OUT/'skin-access-native.json').read_text());names=[r['object'] for r in access['parts']]
    report=dict(status='END_WALL_CORRECTION_BUILD_RUNNING',selected=False,physical_pass=False,
        source_native_sha256=sha(source),native_built=False,contacts=[],clearance_failures=[],errors=[],pairs=0,
        leg_poses=[],head_poses=[],full_wiring_complete=False, mounts_cowls_service_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (source,OUT/'shared-skin-exact.json',OUT/'skin-base-wall-thickness.json',Path(__file__))})
    receipt=OUT/'skin-end-correction.json';deadline=DT.fromisoformat('2026-10-17T07:30:00+00:00')
    def save():
        report['worker_seconds']=round(time.monotonic()-tick,3);receipt.write_text(json.dumps(report,indent=2)+'\n')
    def gate():
        if DT.now(TZ.utc)>=deadline:
            report.update(status='END_WALL_CORRECTION_DEADLINE_PARTIAL');save();raise TimeoutError('Window ended; partial preserved')
    old={n:reader.shape(source,n) for n in names};doc=A.openDocument(str(source));live=doc.Name
    try:
        doc.saveAs(str(target));p=doc.Parameters;p.set('A6','InnerEndOverrun');p.set('B6','0 mm');p.setAlias('B6','InnerEndOverrun')
        doc.InnerNativeSection0.setExpression('Placement.Base.x','-141.5 mm - Parameters.InnerEndOverrun')
        doc.InnerNativeSection7.setExpression('Placement.Base.x','183.5 mm + Parameters.InnerEndOverrun')
        doc.recompute();gate();volumes={}
        for n in names:
            s=doc.getObject(n).Shape;assert s.isValid() and len(s.Solids)==1 and not s.check(True),n
            volumes[n]=s.Volume
        p.set('B6','.1 mm');doc.recompute();gate()
        assert all(doc.getObject(n).Shape.isValid() for n in names)
        assert any(abs(doc.getObject(n).Shape.Volume-volumes[n])>.001 for n in names)
        p.set('B6','0 mm');doc.recompute();gate()
        assert all(abs(doc.getObject(n).Shape.Volume-volumes[n])<1e-4 for n in names)
        doc.save();A.closeDocument(live);live=None
        d=A.openDocument(str(target));live=d.Name
        assert abs(d.InnerNativeSection0.Placement.Base.x+141.5)<1e-7 and abs(d.InnerNativeSection7.Placement.Base.x-183.5)<1e-7
        assert all(d.getObject(n).Shape.isValid() and abs(d.getObject(n).Shape.Volume-volumes[n])<1e-4 for n in names)
        A.closeDocument(live);live=None
        report.update(native_built=True,native=target.relative_to(ROOT).as_posix(),native_sha256=sha(target),fresh_reopen=True,
            end_overrun_parameter_test_mm=[0,.1,0],native_seconds=round(time.monotonic()-tick,3))
        fresh=SavedShapes();panels={n:fresh.shape(target,n) for n in names};delta={n:s.cut(old[n]) for n,s in panels.items()}
        assert all(s.isNull() or s.isValid() for s in delta.values())
        report['added_mm3']={n:s.Volume for n,s in delta.items()}
        # Exact side-wall distance, no cap-face zero-distance shortcut.
        sides=[]
        for n in ('OuterNative','InnerNative'):
            shape=fresh.shape(target,n);faces=[f for f in shape.Faces if f.optimalBoundingBox().XLength>1e-6]
            sides.append(Part.makeShell(faces))
        gap,witness,_=sides[0].distToShape(sides[1]);report['base_lateral_minimum_mm']=gap
        report['base_wall_witnesses_mm']=[[[v.x,v.y,v.z] for v in pair] for pair in witness[:8]]
        save();print('Corrected base wall',gap,'added',report['added_mm3'],flush=True)
        if gap<.001:
            report['status']='END_WALL_CAUSE_CORRECTION_STILL_CROSSES_NO_REPEAT';save();return
        scenariofile=OUT/'motion-receivers-checks.json';scenario=json.loads(scenariofile.read_text());current=ROOT/scenario['native']
        assert scenario['native_built'] and sha(current)==scenario['native_sha256']
        planfile=ROOT/scenario['module_plan'];plan=json.loads(planfile.read_text());motionfile=OUT/'motion-layout.json';motion=json.loads(motionfile.read_text())
        head=set(next(g['objects'] for g in plan['groups'] if g['role']=='HeadMechanism'))
        leg={n for g in motion['membership'].values() for ns in g.values() for n in ns}
        scene={n:reader.shape(current,n) for g in plan['groups'] for n in g['objects']}
        for n in reader.doc(current):
            if n not in scene and n.startswith(('Print_P0_','Print_CP2_TailRiser','Battery','Ref_Material_P0_','Ref_Material_tail_','BellyFoot','FrameHardwareNew')):scene[n]=reader.shape(current,n)
        prefixes=json.loads((OUT/'prefix-allocation.json').read_text());specs={r['id']:r for r in prefixes['specifications']};wires={}
        for key,k in prefixes['allocation'].items():
            r=specs[key]
            if r['role'] in plan['motion_receiving_changes']:continue
            bend=next(c['bend'] for c in prefixes['domains'][key] if c['option']==k)
            wires[key]=tube_prefix(r['point'],r['direction'],r['radius'],bend,12.4)
        for row in scenario['factory_routes']:
            edges=[]
            for e in row['parts']:
                a,b=A.Vector(*e['start']),A.Vector(*e['end']);edges.append(Part.makeLine(a,b) if e['kind']=='line' else Part.Arc(a,A.Vector(*e['mid']),b).toShape())
            w=Part.Wire(edges);e=w.Edges[0];p=e.valueAt(e.FirstParameter);t=e.tangentAt(e.FirstParameter)
            wires['Factory:'+row['wire']]=w.makePipeShell([Part.Wire([Part.makeCircle(row['radius_mm'],p,t)])],True,False)
        bounds={n:s.optimalBoundingBox() for n,s in delta.items()}
        def check(pn,s,n,other,scope,pose=None,clearance=0):
            gate();a,b=bounds[pn],other.BoundBox
            distance2=sum(max(0,x-y,z-w)**2 for x,y,z,w in [(a.XMin,b.XMax,b.XMin,a.XMax),(a.YMin,b.YMax,b.YMin,a.YMax),(a.ZMin,b.ZMax,b.ZMin,a.ZMax)])
            if distance2>clearance*clearance:return
            report['pairs']+=1
            try:
                c=s.common(other);assert c.isNull() or c.isValid()
                if c.Volume>1e-5:report['contacts'].append(dict(panel=pn,object=n,scope=scope,pose=pose,volume_mm3=c.Volume))
                elif clearance:
                    d=s.distToShape(other)[0]
                    if d<clearance-1e-5:report['clearance_failures'].append(dict(panel=pn,object=n,scope=scope,gap_mm=d,required_mm=clearance))
            except Exception as exc:report['errors'].append(dict(panel=pn,object=n,error=str(exc)))
        for pn,s in delta.items():
            for n,other in scene.items():
                if n not in leg and n not in head:check(pn,s,n,other,'added_fixed')
            for n,other in wires.items():check(pn,s,n,other,'added_known_wire',clearance=1.25)
        save();print('Added wall static',report['pairs'],'hits',len(report['contacts']),'gaps',len(report['clearance_failures']),flush=True)
        if any(report[k] for k in ('contacts','clearance_failures','errors')):
            report['status']='END_CORRECTION_ADDED_FIXED_MATERIAL_REJECTED';save();return
        axes=json.loads((ROOT/'hardware/simulation/p0/e6-leg-compatibility.json').read_text())['axes']
        for i,pose in enumerate(motion['poses'][:36]):
            start=report['pairs']
            for code,g in motion['membership'].items():
                aa=[next(a for a in axes if a['code']==code and a['stage']==stage) for stage in STAGES];tf=placement(aa,pose['legs'][code]['angles_delta_degrees'])
                for stage,ns in g.items():
                    for n in ns:
                        other=scene[n].copy();other.Placement=tf[stage]*other.Placement
                        for pn,s in delta.items():check(pn,s,n,other,'added_leg',i)
            report['leg_poses'].append(dict(index=i,pairs=report['pairs']-start));save()
            print('Added wall leg',i,'hits',len(report['contacts']),flush=True)
            if any(report[k] for k in ('contacts','errors')):
                report['status']='END_CORRECTION_ADDED_LEG_MATERIAL_REJECTED';save();return
        for pitch in (-10,0,5):
            for yaw in (-15,0,15):
                for n in head:
                    other=scene[n].copy()
                    if pitch:other.rotate(A.Vector(*plan['head_pitch_axis_mm']),A.Vector(0,1,0),pitch)
                    if yaw:other.rotate(A.Vector(*plan['head_yaw_axis_mm']),A.Vector(0,0,1),yaw)
                    for pn,s in delta.items():check(pn,s,n,other,'added_head',[pitch,yaw])
                report['head_poses'].append([pitch,yaw]);save()
        report.update(status='END_ALIGNED_WALL_DELTA36LEGS9HEADS_CLEAR_FULL_WIRING_MOUNTS_OPEN' if not any(report[k] for k in ('contacts','clearance_failures','errors')) else 'END_CORRECTION_HEAD_REVIEW_REQUIRED',
            previous_material_motion_proof_reused=True,whole_current_wiring_acceptance=False,known_wire_pieces_checked=len(wires),
            stale_changed_approaches_omitted=8,minimum_webs_print_strength_open=True)
        report['source_sha256'].update({p.relative_to(ROOT).as_posix():sha(p) for p in (current,scenariofile,planfile,motionfile,OUT/'prefix-allocation.json')})
        report['source_sha256'].update(reader.hashes);save()
        print(json.dumps({k:report[k] for k in ('status','base_lateral_minimum_mm','pairs','worker_seconds')}),flush=True)
    except TimeoutError:print('Deadline saved; no further exact operations',flush=True)
    except Exception as exc:
        report.update(status='END_WALL_CORRECTION_INCOMPLETE',error=str(exc));save();raise
    finally:
        if live and live in A.listDocuments():A.closeDocument(live)


if __name__=='__main__':main()
