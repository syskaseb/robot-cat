"""Changed source group against valid retained material, not bbox verdicts.

Factory/case dimensions with unknown delivery datums are planning volumes.
Old supports are excluded explicitly as INVALIDATED, not declared clear.
"""
from datetime import datetime, timezone
from pathlib import Path
import json, math, time
import FreeCAD as A
import Part
import open_prototype_source_group as G
from open_prototype_entry_chambers import CONTEXT, MOUNTS
from open_prototype_wiring_endpoints import ROOT, read, sha

def run():
    tick=time.monotonic();assert not G.PROOF.exists(),'Receive existing worker, no unchanged gate'
    plan=read(G.PLAN);rebuilt=G.build()
    for k in ('stations','ports','permutation','body_ends','mta','tails','s1_routes','holders'):
        assert plan[k]==rebuilt[k],k
    tail_path=G.OUT/'TailLocalCurrent.FCStd'
    files=[G.PLAN,CONTEXT,MOUNTS,tail_path,G.OUT/'obstacle-map-current.json',Path(__file__),Path(G.__file__)]
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in files}
    result=dict(status='PENDING',selected=False,stage_completed=False,physical_pass=False,
        errors=[],outside=[],budget_overlaps=[],retained_contacts=[],route_overlaps=[],
        tested_pairs=0,source_sha256=pins,intentional_overlaps=[],
        scope='20stations/4MTA/5FHAC/fourS1/8factorytails/5input+5outputprefix/5coveredjoints/newinsulation/2changed actual rings; full retained inventory and wholemodule reservations. Not full wiring/service/native acceptance.')
    docs=[];scene=[];paths=[];retained=[];modules=[]
    def box(c,size):return Part.makeBox(*size,A.Vector(*[v-d/2 for v,d in zip(c,size)]))
    def tube(parts,od):
        edges=[Part.makeLine(A.Vector(*p['start']),A.Vector(*p['end'])) if p['kind']=='line'
            else Part.Arc(A.Vector(*p['start']),A.Vector(*p['mid']),A.Vector(*p['end'])).toShape() for p in parts]
        first=edges[0];path=Part.Wire(edges)
        circle=Part.Wire([Part.makeCircle(od/2,first.Vertexes[0].Point,first.tangentAt(first.FirstParameter))])
        s=path.makePipeShell([circle],True,False)
        assert s.isValid() and len(s.Solids)==1,'Invalid pipe cannot certify clearance'
        return s
    def compare(n,s,m,t,bucket):
        assert s.isValid() and t.isValid(),(n,m)
        if not s.BoundBox.intersect(t.BoundBox):return
        hit=s.common(t);assert hit.isValid(),(n,m)
        result['tested_pairs']+=1
        if hit.Volume>1e-6:result[bucket].append(dict(a=n,b=m,volume_mm3=round(hit.Volume,6)))
    try:
        docs=[A.openDocument(str(p)) for p in (CONTEXT,MOUNTS,tail_path)]
        ctx,mount,tail=docs;torso=ctx.TorsoEnvelope.Shape
        assert torso.isValid() and len(torso.Solids)==1
        for r in plan['stations']+plan['mta']+plan['holders']:
            scene.append((r['role'],box(r['centre_mm'],r['size_mm'])))
        changed_rings={}
        for r in plan['s1_routes']:
            if r['terminal'] not in (5,6):continue
            n='S1_ring_'+str(r['terminal']);s=ctx.getObject(n).Shape.copy()
            rotation=A.Rotation(A.Vector(1,0,0),A.Vector(*r['barrel_direction']))
            s.rotate(A.Vector(*r['eye_mm']),rotation.Axis,rotation.Angle*180/math.pi)
            assert s.isValid() and len(s.Solids)==1
            changed_rings[n]=s;scene.append((n,s))
        result['changed_actual_rings']=list(changed_rings)
        excluded=[]
        for r in read(G.OUT/'obstacle-map-current.json')['objects']:
            n=r['name']
            if r['kind'] in ('candidate_station','replaceable_support') or n in changed_rings:
                excluded.append(dict(name=n,reason='Changed candidate or INVALIDATED support; replacement qualification OPEN'))
                continue
            if r['basis'].startswith('Canonical whole-component/reference envelope') or n=='U1UnknownModuleReservation':
                b=r['bounds_mm'];modules.append((n,box([(b[i]+b[i+3])/2 for i in range(3)],
                    [b[i+3]-b[i] for i in range(3)])))
                continue
            obj=tail.CurrentTailSupport if n=='CurrentTailSupport' else ctx.getObject(n) or mount.getObject(n)
            assert obj is not None and hasattr(obj,'Shape'),'Unresolved retained reference: '+n
            s=obj.Shape;assert s.isValid() and s.Solids,'Invalid retained shape: '+n
            retained.append((n,s))
        assert sum(n.startswith('F_') and '_CP2_' in n for n,_ in retained)>=48
        assert {'S1_body_CP2','S1_control_CP2','S1_driver_5','S1_driver_6','F_PWM_CP2','CurrentTailSupport'}.issubset({n for n,_ in retained})
        result.update(retained_solid_count=len(retained),whole_module_budgets=[n for n,_ in modules],excluded_changed_interfaces=excluded)
        for r in plan['tails']+plan['s1_routes']:paths.append((r['wire'],tube(r['segments'],r['OD_mm'])))
        for h in plan['holders']:
            paths.append((h['role']+'/input',tube(h['input_segments'],4)))
            paths.append((h['role']+'/output',tube(h['output_segments'],4)))
            paths.append((h['role']+'/sleeve',tube([G.line(h['sleeve_start_mm'],h['sleeve_end_mm'])],h['sleeve_OD_mm'])))
            paths.append((h['role']+'/new_insulation',tube([G.line(h['output_segments'][-1]['end'],h['new_insulation_end_mm'])],2.1)))
        assert len(paths)==32
        for n,s in scene+paths:
            outside=s.cut(torso);assert outside.isValid()
            if outside.Volume>1e-6:result['outside'].append(dict(name=n,volume_mm3=round(outside.Volume,6)))
            for m,t in retained:
                if n.startswith('S1_ring_') and m in ('S1_screw_'+n[-1],'S1_seat_budget_'+n[-1]):
                    result['intentional_overlaps'].append(dict(a=n,b=m,reason='Declared same terminal bearing/screw mating; not a general waiver'))
                    continue
                compare(n,s,m,t,'retained_contacts')
        for i,(n,s) in enumerate(scene):
            for m,t in scene[:i]+modules:compare(n,s,m,t,'budget_overlaps')
        for i,(n,s) in enumerate(paths):
            # No blanket own-source/receiver exclusion: returning routes must
            # not reenter their case. Only the covered same-wire joint mates.
            for m,t in scene+modules:compare(n,s,m,t,'route_overlaps')
            for m,t in paths[:i]:
                same_holder=n.split('/')[0]==m.split('/')[0] and '/' in n and '/' in m
                intentional=(same_holder and (n.endswith('/sleeve') or m.endswith('/sleeve')) and
                    n.endswith(('/output','/new_insulation','/sleeve')) and m.endswith(('/output','/new_insulation','/sleeve')))
                if intentional:
                    result['intentional_overlaps'].append(dict(a=n,b=m,reason='Covered solder joint and its own factory/new insulation'))
                    continue
                compare(n,s,m,t,'route_overlaps')
        result['status']='REQUIRES_COUPLED_SOURCE_CAUSE_CHANGE' if any(result[k] for k in
            ('outside','budget_overlaps','retained_contacts','route_overlaps')) else 'SOURCE_GROUP_GATE_ONLY_DOWNSTREAM_AND_NATIVE_OPEN'
    except Exception as exc:
        result['errors'].append(str(exc));raise
    finally:
        for doc in docs:A.closeDocument(doc.Name)
        result.update(worker_seconds=round(time.monotonic()-tick,3),finished_utc=datetime.now(timezone.utc).isoformat())
        G.PROOF.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    assert all(sha(ROOT/p)==h for p,h in pins.items()),'Source changed during gate'
    print(json.dumps({k:result[k] for k in ('status','tested_pairs','retained_solid_count','outside','budget_overlaps','retained_contacts','route_overlaps','errors','worker_seconds')}),flush=True)

if __name__=='__main__':run()
