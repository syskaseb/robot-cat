"""Changed seven profiles: exact round-tube reservations, no native rebuild.

Only common case/point evidence is reused. Include current W001 as a peer,
all four source wires, both MTA inputs, all unchanged factory/output profiles.
"""
from pathlib import Path
from datetime import datetime,timezone
import copy, json, math, time
import FreeCAD as A
import open_prototype_source_ato_level as G
import open_prototype_tail_clearance as H
import open_prototype_ground_current as Ground
from open_prototype_entry_chambers import CONTEXT,MOUNTS

B=G.B;OUT=G.OUT
DEST=OUT/'source-ato-level-radius.json'

def point_at(p,d):
    length,t0,_,r=B.segment_geometry(p)
    if r is None:return B.add(p['start'],B.mul(t0,d))
    a,m,b=p['start'],p['mid'],p['end'];u=B.sub(m,a);v=B.sub(b,a);n=B.cross(u,v)
    c=B.add(a,B.mul(B.add(B.mul(B.cross(v,n),B.dot(u,u)),B.mul(B.cross(n,u),B.dot(v,v))),1/(2*B.dot(n,n))))
    return B.add(c,B.add(B.mul(B.sub(a,c),math.cos(d/r)),B.mul(t0,r*math.sin(d/r))))

def trim_parts(parts,first=0,last=0):
    q=copy.deepcopy(parts)
    for front,amount in ((True,first),(False,last)):
        while amount>1e-10:
            i=0 if front else -1;p=q[i];length=B.segment_geometry(p)[0]
            if amount>=length-1e-10:
                q.pop(i);amount-=length;assert q,'Face cap removed the entire route';continue
            if p['kind']=='line':
                p['start' if front else 'end']=point_at(p,amount if front else length-amount)
            elif front:
                start=point_at(p,amount);mid=point_at(p,(amount+length)/2)
                p.update(start=start,mid=mid)
            else:
                end=point_at(p,length-amount);mid=point_at(p,(length-amount)/2)
                p.update(end=end,mid=mid)
            amount=0
    B.check_path(q);return q

def run():
    assert not DEST.exists(),'Do not repeat unchanged exact gate'
    tick=time.monotonic();p=G.build();prior=B.read(G.PROOF)
    assert not any(prior[k] for k in ('contacts','outside','input_point_intrusions','input_outside','receiving_trunk_intrusions','errors'))
    assert not B.read(G.PLAN)['known_mutual_conflicts']
    files=[G.PLAN,G.PROOF,CONTEXT,MOUNTS,OUT/'TailLocalCurrent.FCStd',Path(__file__),Path(H.__file__),
        Path(Ground.__file__),Ground.PLAN,Ground.PROOF]
    pins=dict(prior['source_sha256']);pins.update({f.relative_to(G.ROOT).as_posix():B.sha(f) for f in files})
    assert all(B.sha(G.ROOT/n)==h for n,h in pins.items())
    result=dict(status='PENDING',conflicts=[],outside=[],errors=[],tested_pairs=0,source_sha256=pins,
        selected=False,stage_completed=False,physical_pass=False,changed_profiles=p['changed_path_names'],
        scope='Exact centreline/material distances for seven changed full-radius reservations; reused valid case gate, current W001 peer. Native grips, fuse service, all remaining conductors, stock and delivered fit OPEN.',
        nominal_module_budgets_not_measured_collisions=True)
    docs=[]
    def progress(phase):print(json.dumps(dict(phase=phase,seconds=round(time.monotonic()-tick,2),pairs=result['tested_pairs'])),flush=True)
    def distance(n,s,m,t,r,basis):
        if not H.near(s,t,r):return
        progress(n+' / '+m);assert s.isValid() and t.isValid()
        d=s.distToShape(t)[0];result['tested_pairs']+=1;assert math.isfinite(d)
        if d<r-1e-6:result['conflicts'].append(dict(a=n,b=m,distance_mm=round(d,6),required_mm=r,basis=basis))
    try:
        progress('load pinned material')
        docs=[A.openDocument(str(f)) for f in (CONTEXT,MOUNTS,OUT/'TailLocalCurrent.FCStd')]
        ctx,mount,tail=docs;torso=ctx.TorsoEnvelope.Shape
        assert torso.isValid() and len(torso.Solids)==1
        scene=[(r['role'],H.box(r['centre_mm'],r['size_mm']),'nominal module reservation') for r in p['stations']+p['mta']+p['holders']]
        for r in B.read(OUT/'obstacle-map-current.json')['objects']:
            n=r['name']
            if n.startswith('S1_'):
                if r['kind']=='service_budget':continue
                s=ctx.getObject(n).Shape.copy();spec=p['s1_module']
                s.rotate(A.Vector(*spec['pivot_mm']),A.Vector(1,0,0),spec['whole_rotation_deg'])
                s.translate(A.Vector(*spec['translation_mm']))
                if n.startswith('S1_ring_'):
                    ring=next(t for t in spec['rings'] if t['terminal']==int(n[-1]))
                    s.rotate(A.Vector(*ring['eye_mm']),A.Vector(0,0,1),ring['ring_rotation_z_deg'])
                basis='valid retained transformed S1 nominal material'
            elif r['kind'] in ('candidate_station','replaceable_support'):continue
            elif r['basis'].startswith('Canonical whole-component/reference envelope') or n=='U1UnknownModuleReservation':
                v=r['bounds_mm'];s=H.box([(v[i]+v[i+3])/2 for i in range(3)],[v[i+3]-v[i] for i in range(3)])
                basis='whole-component reservation, not measured delivered shape'
            else:
                obj=tail.CurrentTailSupport if n=='CurrentTailSupport' else ctx.getObject(n) or mount.getObject(n)
                assert obj is not None and hasattr(obj,'Shape'),n
                s=obj.Shape;basis='valid retained saved material'
            assert s.isValid() and s.Solids,n
            scene.append((n,s,basis))
        rows=H.profiles(p)
        rows.update({r['wire']:(r['segments'],r['OD_mm']/2,'S1_ring_'+str(r['terminal']),r['target'].split('.')[0]) for r in p['s1_routes']})
        _,w=Ground.build();rows['W001']=(w['segments'],w['OD_mm']/2,None,'G1')
        curves={n:H.wire(row[0]) for n,row in rows.items()}
        joins=[{h['role']+'/'+s for s in ('output','sleeve','new_insulation')} | {r['wire'] for r in p['protected_receiving_rows'] if r['holder']==h['role']} for h in p['holders']]
        seen=set()
        for n in p['changed_path_names']:
            parts,r,source,receiver=rows[n];s=curves[n]
            progress(n+' / body boundary')
            d=s.distToShape(torso.Shells[0])[0];assert math.isfinite(d)
            if not torso.isInside(A.Vector(*parts[0]['start']),1e-7,True) or d<r-1e-6:
                result['outside'].append(dict(name=n,distance_mm=d,required_mm=r))
            for m,t,basis in scene:
                if not H.near(s,t,r):continue
                candidate=H.wire(trim_parts(parts,first=r+1e-5)) if m==source else H.wire(trim_parts(parts,last=r+1e-5)) if m==receiver else s
                distance(n,candidate,m,t,r,basis)
            for m,t in curves.items():
                pair=tuple(sorted((n,m)))
                if n==m or pair in seen or any(n in group and m in group for group in joins):continue
                seen.add(pair);distance(n,s,m,t,r+rows[m][1],'independent current conductor reservation')
        result['status']='REJECTED_FULL_RADIUS_RESERVATION' if result['conflicts'] or result['outside'] else 'SEVEN_PROFILE_RADIUS_CLEARANCE_ONLY_NATIVE_GRIPS_AND_FULL_WIRING_OPEN'
    except Exception as exc:
        result['errors'].append(str(exc));result['status']='ERROR_NOT_CLEARANCE';raise
    finally:
        for d in docs:A.closeDocument(d.Name)
        if not all(B.sha(G.ROOT/n)==h for n,h in pins.items()):result['errors'].append('Changed source pin');result['status']='INVALID_PINS'
        result.update(worker_seconds=round(time.monotonic()-tick,3),finished_utc=datetime.now(timezone.utc).isoformat())
        DEST.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({k:result[k] for k in ('status','conflicts','outside','errors','tested_pairs','worker_seconds')}),flush=True)

if __name__=='__main__':run()
