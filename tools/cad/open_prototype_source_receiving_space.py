"""Read-only common space check for one coupled receiving/source family.

Whole changed modules and all four FHAC inputs are included together.
Invalidated S1/PI/WAGO routes are not presented as current clearance.
Point screens reject positive material witnesses only; no full tube claim.
"""
from datetime import datetime,timezone
from pathlib import Path
import json,time,math
import FreeCAD as A
import Part
import open_prototype_source_receiving_family as G
import open_prototype_source_group as B
import open_prototype_rr_receiving_branch as R
from open_prototype_entry_chambers import CONTEXT,MOUNTS
from open_prototype_path_preflight import samples

def run():
    assert not G.PROOF.exists(),'No unchanged heavy retry'
    tick=time.monotonic();p=G.build();compact=B.read(G.PLAN)
    assert R.geometry_digest(p)==compact['geometry_digest']
    files=[G.PLAN,CONTEXT,MOUNTS,G.OUT/'TailLocalCurrent.FCStd',Path(__file__)]
    pins=dict(compact['source_sha256'])
    pins.update({f.relative_to(G.ROOT).as_posix():B.sha(f) for f in files})
    assert all(B.sha(G.ROOT/n)==h for n,h in pins.items())
    result=dict(status='PENDING',contacts=[],outside=[],external_operator_outside=[],
        input_point_intrusions=[],input_outside=[],receiving_trunk_intrusions=[],
        errors=[],source_sha256=pins,selected=False,stage_completed=False,physical_pass=False,
        point_screen_not_full_tube=True,native_sources_saved=False,
        scope='All changed S1 parts/P_AUX/P_SYS/F_PI versus current other cases and retained valid material; four changed FHAC inputs and translated PI output/joint positive-point screen. Other conductors invalidated/open.',
        assembled_driver_proof_reused='s1-terminal-plane-budget.json: four Monitor obstructions unchanged; proposed bench prewire/install-before-Monitor sequence, NOT qualified removal or assembled tool clearance')
    docs=[]
    def box(c,size):return Part.makeBox(*size,A.Vector(*[v-d/2 for v,d in zip(c,size)]))
    try:
        docs=[A.openDocument(str(f)) for f in files[1:4]]
        ctx,mount,tail=docs;torso=ctx.TorsoEnvelope.Shape
        assert torso.isValid() and len(torso.Solids)==1
        scene=[];changed=[];records=B.read(G.OUT/'obstacle-map-current.json')['objects']
        for r in p['stations']+p['mta']+p['holders']:
            s=box(r['centre_mm'],r['size_mm']);assert s.isValid()
            (changed if r['role'] in p['changed_case_names'] else scene).append((r['role'],s))
        for r in records:
            n=r['name']
            if n.startswith('S1_'):
                if r['kind']=='service_budget':continue
                source=ctx.getObject(n);s=source.Shape.copy()
                spec=p['s1_module']
                s.rotate(A.Vector(*spec['pivot_mm']),A.Vector(1,0,0),spec['whole_rotation_deg'])
                s.translate(A.Vector(*spec['translation_mm']))
                if n.startswith('S1_ring_'):
                    ring=next(q for q in spec['rings'] if q['terminal']==int(n[-1]))
                    s.rotate(A.Vector(*ring['eye_mm']),A.Vector(0,0,1),ring['ring_rotation_z_deg'])
                assert s.isValid() and s.Solids,n
                changed.append((n,s));continue
            if r['kind'] in ('candidate_station','replaceable_support'):continue
            if r['basis'].startswith('Canonical whole-component/reference envelope') or n=='U1UnknownModuleReservation':
                v=r['bounds_mm'];s=box([(v[i]+v[i+3])/2 for i in range(3)],[v[i+3]-v[i] for i in range(3)])
            else:
                obj=tail.CurrentTailSupport if n=='CurrentTailSupport' else ctx.getObject(n) or mount.getObject(n)
                assert obj is not None and hasattr(obj,'Shape'),n
                s=obj.Shape
            assert s.isValid() and s.Solids,n
            scene.append((n,s))
        pairs=0
        for i,(n,s) in enumerate(changed):
            if n in p['changed_case_names'] or n in ('S1_body_CP2','S1_control_CP2'):
                out=s.cut(torso);assert out.isValid()
                if out.Volume>1e-6:
                    row=dict(name=n,volume_mm3=round(out.Volume,6))
                    (result['external_operator_outside'] if n=='S1_control_CP2' else result['outside']).append(row)
            for m,t in scene+changed[:i]:
                # Known intended mating within complete nominal S1 module.
                if n.startswith('S1_') and m.startswith('S1_') and not (n.startswith('S1_ring_') and m.startswith('S1_ring_')):continue
                if not s.BoundBox.intersect(t.BoundBox):continue
                common=s.common(t);assert common.isValid(),(n,m)
                pairs+=1
                if common.Volume>1e-6:result['contacts'].append(dict(a=n,b=m,volume_mm3=round(common.Volume,6)))
        result.update(tested_pairs=pairs,changed_parts=len(changed),retained_targets=len(scene))
        # One point screen for the entire changed input/prefix family.
        routes=[]
        for h in p['holders']:
            if h['role'] in ('F_PI','F_HY','F_HP','F_TY'):
                routes.append((h['role']+'/input',h['input_segments'],h['role'],h['input_target'].split('.')[0],2))
            if h['role']=='F_PI':
                routes += [('F_PI/output',h['output_segments'],'F_PI',None,2),
                    ('F_PI/sleeve',[B.line(h['sleeve_start_mm'],h['sleeve_end_mm'])],None,None,3),
                    ('F_PI/new_insulation',[B.line(h['output_segments'][-1]['end'],h['new_insulation_end_mm'])],None,None,1.05)]
        inventory=[(n,s,s.BoundBox) for n,s in scene+changed];witness={};outside={};count=queries=0
        for name,parts,source,receiver,radius in routes:
            for segment,q in samples(parts):
                count+=1;v=A.Vector(*q)
                if name not in outside and not torso.isInside(v,1e-7,True):outside[name]=dict(name=name,segment=segment,point_mm=q)
                for n,s,bbox in inventory:
                    if (name,n) in witness or not bbox.isInside(v):continue
                    if n==source and math.dist(q,parts[0]['start'])<=radius+1e-5:continue
                    if n==receiver and math.dist(q,parts[-1]['end'])<=radius+1e-5:continue
                    queries+=1
                    if s.isInside(v,1e-7,False):witness[name,n]=dict(a=name,b=n,segment=segment,point_mm=q)
        result.update(input_point_intrusions=list(witness.values()),input_outside=list(outside.values()),
                      sample_count=count,point_queries=queries)
        # Preserve HP receiving core while testing both moved cases together.
        core=next(r['core_segments'] for r in B.read(G.OUT/'source-fanouts-plan.json')['rows'] if r['wire']=='XB22')
        for segment,q in samples(core):
            v=A.Vector(*q)
            for n,s in changed:
                if n not in p['changed_case_names'] or not s.BoundBox.isInside(v):continue
                if s.isInside(v,1e-7,False):
                    result['receiving_trunk_intrusions'].append(dict(a='XB22/core',b=n,segment=segment,point_mm=q));break
            if result['receiving_trunk_intrusions']:break
        result['status']='REJECTED_COUPLED_SPACE_OR_INPUT_WITNESS' if any(result[k] for k in
            ('contacts','outside','input_point_intrusions','input_outside','receiving_trunk_intrusions')) else 'COUPLED_MODULE_SPACE_ONLY_FULL_ROUTES_AND_NATIVE_RETENTION_OPEN'
    except Exception as exc:
        result['errors'].append(str(exc));result['status']='ERROR_NOT_CLEARANCE';raise
    finally:
        for doc in docs:A.closeDocument(doc.Name)
        assert all(B.sha(G.ROOT/n)==h for n,h in pins.items()),'Source changed during calculation'
        result.update(worker_seconds=round(time.monotonic()-tick,3),finished_utc=datetime.now(timezone.utc).isoformat())
        G.PROOF.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({k:result[k] for k in ('status','contacts','outside','input_point_intrusions','input_outside','receiving_trunk_intrusions','errors','worker_seconds')}),flush=True)

if __name__=='__main__':run()
