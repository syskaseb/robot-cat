"""Read-only, scoped exact-radius gate for the allocated TY corridor.

Reuse the pinned case/point gate. Test only the five changed profiles against
retained valid material, explicit module reservations and existing conductors.
Same-conductor covered joints are intentional, not independent wire clashes.
No native rebuild, source-route selection or moving-tail acceptance.
"""
from datetime import datetime, timezone
from pathlib import Path
import copy, json, math, time
import FreeCAD as A
import Part
import open_prototype_rl_tail_group as G
import open_prototype_source_group as B
import open_prototype_rr_receiving_branch as R
from open_prototype_entry_chambers import CONTEXT, MOUNTS

DEST=G.OUT/'tail-corridor-radius-clearance.json'

def wire(parts):
    edges=[Part.makeLine(A.Vector(*p['start']),A.Vector(*p['end'])) if p['kind']=='line'
           else Part.Arc(A.Vector(*p['start']),A.Vector(*p['mid']),A.Vector(*p['end'])).toShape()
           for p in parts]
    s=Part.Wire(edges)
    assert s.isValid(), 'Invalid centreline is not clearance'
    return s

def trim(parts, first=0, last=0):
    q=copy.deepcopy(parts)
    for i,d,key,sign in [(0,first,'start',1),(-1,last,'end',-1)]:
        if not d: continue
        assert q[i]['kind']=='line' and B.segment_geometry(q[i])[0]>d
        q[i][key]=B.add(q[i][key],B.mul(B.segment_geometry(q[i])[1],sign*d))
    return wire(q)

def box(c,size):
    return Part.makeBox(*size,A.Vector(*[v-d/2 for v,d in zip(c,size)]))

def near(s,t,r):
    a,b=s.BoundBox,t.BoundBox
    gap2=sum(max(0,x-v,u-y)**2 for x,y,u,v in
             [(a.XMin,a.XMax,b.XMin,b.XMax),(a.YMin,a.YMax,b.YMin,b.YMax),(a.ZMin,a.ZMax,b.ZMin,b.ZMax)])
    return gap2<=(r+1e-6)**2

def profiles(p):
    rows={r['wire']:(r['segments'],r['OD_mm']/2,
          'MTA_'+r['leg'] if r['leg'] in ('FL','FR','RL','RR') else None,
          r.get('target','').split('.')[0] or None) for r in p['tails']}
    for h in p['holders']:
        n=h['role']
        rows[n+'/input']=(h['input_segments'],2,n,h['input_target'].split('.')[0])
        rows[n+'/output']=(h['output_segments'],2,n,None)
        rows[n+'/sleeve']=([B.line(h['sleeve_start_mm'],h['sleeve_end_mm'])],3,None,None)
        rows[n+'/new_insulation']=([B.line(h['output_segments'][-1]['end'],h['new_insulation_end_mm'])],1.05,None,None)
    return rows

def run():
    assert not DEST.exists(), 'No unchanged repeat'
    tick=time.monotonic();p=G.build();plan=B.read(G.PLAN);prior=B.read(G.PROOF)
    assert R.geometry_digest(p)==plan['geometry_digest']
    assert not any(prior[k] for k in ('contacts','outside','input_point_intrusions','input_outside','receiving_trunk_intrusions','errors'))
    pins=dict(prior['source_sha256'])
    assert all(B.sha(G.ROOT/n)==h for n,h in pins.items()), 'Pinned case/point proof changed'
    pins.update({f.relative_to(G.ROOT).as_posix():B.sha(f) for f in (G.PROOF,Path(__file__))})
    result=dict(status='PENDING',conflicts=[],outside=[],errors=[],tested_pairs=0,
        selected=False,stage_completed=False,physical_pass=False,source_sha256=pins,
        changed_case_proof_reused=G.PROOF.name,changed_profiles=p['changed_path_names'],
        reservations_are_not_measured_supplier_collisions=True,
        complete_source_wiring_native_grips_stock_and_moving_continuation_open=True)
    docs=[]
    def progress(phase):
        result['last_phase']=phase
        print(json.dumps(dict(phase=phase,seconds=round(time.monotonic()-tick,2),pairs=result['tested_pairs'])),flush=True)
    def distance(n,s,m,t,r,basis):
        if not near(s,t,r):return
        progress(n+' / '+m)
        assert s.isValid() and t.isValid(), (n,m)
        d=s.distToShape(t)[0];result['tested_pairs']+=1
        assert math.isfinite(d), (n,m)
        if d<r-1e-6:
            result['conflicts'].append(dict(a=n,b=m,distance_mm=round(d,6),required_mm=r,basis=basis))
    try:
        progress('load retained documents')
        docs=[A.openDocument(str(f)) for f in (CONTEXT,MOUNTS,G.OUT/'TailLocalCurrent.FCStd')]
        ctx,mount,tail=docs;torso=ctx.TorsoEnvelope.Shape
        assert torso.isValid() and len(torso.Solids)==1
        scene=[]
        for r in p['stations']+p['mta']+p['holders']:
            scene.append((r['role'],box(r['centre_mm'],r['size_mm']),'nominal module reservation'))
        for r in B.read(G.OUT/'obstacle-map-current.json')['objects']:
            n=r['name']
            if n.startswith('S1_'):
                if r['kind']=='service_budget':continue
                s=ctx.getObject(n).Shape.copy();spec=p['s1_module']
                s.rotate(A.Vector(*spec['pivot_mm']),A.Vector(1,0,0),spec['whole_rotation_deg'])
                s.translate(A.Vector(*spec['translation_mm']))
                if n.startswith('S1_ring_'):
                    ring=next(q for q in spec['rings'] if q['terminal']==int(n[-1]))
                    s.rotate(A.Vector(*ring['eye_mm']),A.Vector(0,0,1),ring['ring_rotation_z_deg'])
                basis='retained transformed S1 material'
            elif r['kind'] in ('candidate_station','replaceable_support'):continue
            elif r['basis'].startswith('Canonical whole-component/reference envelope') or n=='U1UnknownModuleReservation':
                v=r['bounds_mm'];s=box([(v[i]+v[i+3])/2 for i in range(3)],[v[i+3]-v[i] for i in range(3)])
                basis='whole-component reservation, not measured material'
            else:
                obj=tail.CurrentTailSupport if n=='CurrentTailSupport' else ctx.getObject(n) or mount.getObject(n)
                assert obj is not None and hasattr(obj,'Shape'),n
                s=obj.Shape;basis='retained saved material'
            assert s.isValid() and s.Solids,n
            scene.append((n,s,basis))
        rows=profiles(p);curves={n:wire(r[0]) for n,r in rows.items()}
        joins=[{h['role']+'/'+side for side in ('output','sleeve','new_insulation')} |
               {r['wire'] for r in p['protected_receiving_rows'] if r['holder']==h['role']}
               for h in p['holders']]
        pairs=set()
        for n in p['changed_path_names']:
            parts,r,source,receiver=rows[n];s=curves[n]
            progress(n+' boundary')
            d=s.distToShape(torso.Shells[0])[0]
            if not torso.isInside(A.Vector(*parts[0]['start']),1e-7,True) or d<r-1e-6:
                result['outside'].append(dict(name=n,distance_mm=d,required_mm=r))
            for m,t,basis in scene:
                if not near(s,t,r):continue
                candidate=trim(parts,first=r+1e-5) if m==source else trim(parts,last=r+1e-5) if m==receiver else s
                distance(n,candidate,m,t,r,basis)
            for m,t in curves.items():
                pair=tuple(sorted((n,m)))
                if n==m or pair in pairs or any(n in group and m in group for group in joins):continue
                pairs.add(pair)
                distance(n,s,m,t,r+rows[m][1],'independent current conductor reservation')
        result['status']='REJECTED_FULL_RADIUS_RESERVATION' if result['conflicts'] or result['outside'] else 'SCOPED_TY_RADIUS_CLEARANCE_ONLY_NATIVE_AND_MOVING_CONTINUATION_OPEN'
    except Exception as exc:
        result['errors'].append(str(exc));result['status']='ERROR_NOT_CLEARANCE';raise
    finally:
        for doc in docs:A.closeDocument(doc.Name)
        if not all(B.sha(G.ROOT/n)==h for n,h in pins.items()):
            result['errors'].append('Source changed during check');result['status']='INVALID_PINS'
        result.update(worker_seconds=round(time.monotonic()-tick,3),finished_utc=datetime.now(timezone.utc).isoformat())
        DEST.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({k:result[k] for k in ('status','conflicts','outside','errors','tested_pairs','worker_seconds')}),flush=True)

if __name__=='__main__':run()
