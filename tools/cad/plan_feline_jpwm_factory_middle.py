"""Four whole-JPWM middle feasibility witnesses, before roots or native CAD.

These are geometric minimum-path witnesses, NOT storage of all225mm leads.
No amount of clear source-grip geometry qualifies a blocked factory middle.
"""
import math,time
import numpy as np
from scipy.optimize import brentq
import feline_tangent_routes as ft
from feline_atomic_save import save_json
from plan_feline_layout import OUT
from plan_feline_n01_shared import pipe
from receive_feline_underplate_return_gallery import bend,forward
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from receive_feline_aux_vertical_unit import material_spacing


def parallel_csc(a,b,axis,R=12.4):
    """Exact same-heading circular-straight-circular path in its own plane."""
    a=np.asarray(a,float);b=np.asarray(b,float);d=np.asarray(axis,float)
    delta=b-a;L=float(delta@d);off=delta-L*d;H=np.linalg.norm(off)
    assert L>0 and H>1e-7
    u=off/H
    f=lambda t:(H-2*R)*math.cos(t)-L*math.sin(t)+2*R
    # f(0) and f(pi) can BOTH be positive although a valid shorter
    # forward CSC exists between them. Bracket the first root by the
    # analytic minimum, not pi (e.g. L40.53/H38.4/R12.4).
    minimum_angle=math.pi-math.atan2(L,H-2*R)
    if f(minimum_angle)>1e-8:
        raise ValueError('No forward parallel CSC at the prescribed radius')
    angle=brentq(f,0.,minimum_angle)
    straight=(H-2*R*(1-math.cos(angle)))/math.sin(angle)
    assert straight>=0
    rows=[];q,t=bend(rows,a,d,u,R,angle)
    q=forward(rows,q,t,straight)
    # Opposite curvature returns to the original heading, not a sharp joint.
    n=(d-t*float(d@t));n/=np.linalg.norm(n)
    q,t=bend(rows,q,t,n,R,angle)
    assert np.linalg.norm(q-b)<1e-6 and np.linalg.norm(t-d)<1e-6
    return rows


def curves(packet,ends):
    from receive_feline_current_face_escape import require_receivers
    require_receivers(ends)
    result={}
    for eid,e in packet['updates'].items():
        other=next(r for r in ends if r['portion_id']==e['portion_id'] and r['id']!=eid)
        a=e['routing_exit_mm'];b=other['routing_exit_mm'];d=e['routing_exit_axis'];arrival=-np.asarray(other['routing_exit_axis'])
        if np.linalg.norm(np.asarray(d)-arrival)<1e-6:rows=parallel_csc(a,b,d)
        else:
            two=ft.biarc(a,d,b,arrival,.5)
            assert ft.min_radius(two)>=12.4
            rows=[]
            for s in two:
                r=dict(kind=s['kind'],start=s['start'],end=s['end'],length_mm=s['length'])
                if s['kind']=='arc':
                    r.update(mid=list(ft.samples(s,s['length']/2))[1],radius_mm=s['radius'])
                rows.append(r)
        result[e['wire']]=dict(parts=rows,length_mm=sum(r['length_mm'] for r in rows),
            source_end_id=eid,receiver_end_id=other['id'],selected_source_prefix_mm=e['source_prefix_length_mm'],
            minimum_R_mm=min(r.get('radius_mm',math.inf) for r in rows),
            uncut225_storage_NOT_qualified=True)
    return result


def planar_csc(a,d0,b,d1,R=12.4):
    """Shortest of four XY circle/straight/circle families; NO clearance.

    Unlike a forward biarc this permits the prescribed receiver to lie
    behind its arrival tangent. Only four analytic circle-side pairs, not
    an endpoint/pose lattice. Long turns are kept, never replaced by chords.
    """
    a=np.asarray(a,float);b=np.asarray(b,float)
    d0=np.asarray(d0,float);d1=np.asarray(d1,float)
    assert abs(a[2]-b[2])<1e-7 and abs(d0[2])+abs(d1[2])<1e-7
    assert abs(np.linalg.norm(d0)-1)+abs(np.linalg.norm(d1)-1)<1e-7
    left=lambda d:np.array([-d[1],d[0],0.])
    sweep=lambda v:0. if min(v%(2*math.pi),(-v)%(2*math.pi))<1e-9 else v%(2*math.pi)
    candidates=[]
    for s0 in (-1,1):
        for s1 in (-1,1):
            c0=a+s0*R*left(d0);c1=b+s1*R*left(d1)
            v=c1-c0;D=np.linalg.norm(v)
            if D<1e-8 or abs((s0-s1)*R)>D+1e-8:continue
            phi=math.atan2(v[1],v[0]);alpha=math.asin(np.clip((s0-s1)*R/D,-1,1))
            for theta in (phi+alpha,phi+math.pi-alpha):
                d=np.array([math.cos(theta),math.sin(theta),0.]);n=left(d)
                p=c0-s0*R*n;q=c1-s1*R*n;length=float((q-p)@d)
                if length<-1e-7:continue
                t0=math.atan2(d0[1],d0[0]);t1=math.atan2(d1[1],d1[0])
                angles=(sweep(s0*(theta-t0)),sweep(s1*(t1-theta)))
                rows=[];start=a;heading=d0
                if angles[0]:start,heading=bend(rows,start,heading,s0*left(heading),R,angles[0])
                assert np.linalg.norm(start-p)<1e-6
                start=forward(rows,start,d,max(0.,length));heading=d
                if angles[1]:start,heading=bend(rows,start,heading,s1*left(heading),R,angles[1])
                assert np.linalg.norm(start-b)<1e-6 and np.linalg.norm(heading-d1)<1e-6
                candidates.append(rows)
    if not candidates:raise ValueError('No prescribed-radius planar CSC')
    return min(candidates,key=lambda rows:sum(r['length_mm'] for r in rows))


def direct_outboard_math(packet,ends):
    """One constructed two-level topology; fit cuts only on free pigtails.

    Upper pair: a red semicircle has diameter2R, not a forced tiny biarc.
    Lower pair: vertical descent beyond the plate, then parallel XZ/XY
    returns. The two module wires occupy separate constant-Z final planes.
    No fitting brackets before these four complete factory budgets fit.
    """
    from receive_feline_current_face_escape import require_receivers
    require_receivers(ends,changed_source_ids=('XP02.source/extra/start',))
    from feline_source_saddles import segment
    from check_main_p0_placement import ROOT
    R=12.4;routes={};u1=__import__('json').loads((OUT/'n01-U1-frontband-common-plan.json').read_text())['specs']
    targets={e['wire']:e for e in ends if e['wire'].startswith(('XP02.','XP03.')) and e.get('group')!='JPWM'}
    for e in packet['updates'].values():
        w=e['wire'];p=np.asarray(e['routing_exit_mm']);d=np.asarray(e['routing_exit_axis']);rows=[]
        target=targets[w];b=np.array([116.,75.,79.25]) if w=='XP02.source' else np.asarray(target['routing_exit_mm'])
        if w.endswith('.module'):
            assert np.allclose(d,[0,0,-1])
            q=forward(rows,p,d,p[2]-(b[2]+R))
            q,t=bend(rows,q,d,[-1,0,0],R)
            rows+=parallel_csc(q,b,t,R)
            spec=u1[e['wire']+'/extra/end']
            jacket=sum(segment(r).Length for r in spec['parts']);bare=sum(segment(r).Length for r in spec['bare_parts'])
            counter=jacket+bare;allowance=16. # unchanged selected E2 allowance
        elif w=='XP02.source':
            assert np.allclose(d,[0,0,1]) and abs(p[0]-b[0]-2*R)<1e-6 and abs(p[1]-b[1])<1e-6
            q=forward(rows,p,d,b[2]-p[2]);q,t=bend(rows,q,d,[-1,0,0],R)
            q,t=bend(rows,q,t,[0,0,-1],R)
            assert np.linalg.norm(q-b)<1e-6 and np.allclose(t,[0,0,-1])
            counter=10.25;allowance=40. # unchanged selected fuse/termination allowance
        else:
            # Clear the unchanged fuse's top69 by1.25 plus jacket.925;
            # no arbitrary millimetre trial after a collision.
            first=69.+1.25+.925-p[2]-R
            q=forward(rows,p,d,first);q,t=bend(rows,q,d,[-1,0,0],R)
            choices=[]
            for ratio in (.5,1.,2.):
                try:
                    a=ft.biarc(q,t,b,-np.asarray(target['routing_exit_axis']),ratio)
                    if ft.min_radius(a)>=R:choices.append(a)
                except ValueError:pass
            assert choices,'Need changed upper corridor, not unsupported radius'
            for s in min(choices,key=ft.length):
                row=dict(kind=s['kind'],start=s['start'],end=s['end'],length_mm=s['length'])
                if s['kind']=='arc':row.update(mid=list(ft.samples(s,s['length']/2))[1],radius_mm=s['radius'])
                rows.append(row)
            counter=12.25;allowance=11.
        middle=sum(segment(r).Length for r in rows);need=9.+middle+counter+allowance
        routes[w]=dict(parts=rows,middle_mm=middle,connector_prefix_mm=9.,counterpart_prefix_mm=counter,
            additional_selected_termination_allowance_mm=allowance,minimum_catalogue_mm=220.,
            nominal_fit_need_mm=need,minimum_catalogue_margin_mm=220.-need,
            free_end_fit_cut_only=True,factory_contact_preserved=True,selected_SKU_unchanged=True)
    result=dict(status='JPWM_DIRECT_OUTBOARD_ALL_FOUR_FACTORY_BUDGETS_'+('RECEIVED' if all(r['minimum_catalogue_margin_mm']>=0 for r in routes.values()) else 'HOLD'),
        routes=routes,real_solids_motion_roots_assembly_and_source_FPWM_grip_OPEN=True,N01_complete=False,physical_pass=False)
    save_json(OUT/'n01-JPWM-direct-outboard-four-factory-plan.json',result)
    print(result['status'],[(w,round(r['nominal_fit_need_mm'],3),round(r['minimum_catalogue_margin_mm'],3)) for w,r in routes.items()],flush=True)
    return result


def screen(packet,ends,world,fixed,metadata,posed,posedmeta):
    tick=time.monotonic();routes=curves(packet,ends);shapes={w:pipe(r['parts'],.925) for w,r in routes.items()}
    q=SolidQueries();checks={};targets={**fixed,**posed};metas={**metadata,**posedmeta}
    mates={'XP02.source':{'JPWMSource:XP02.source','Station:F_PWM_whole:F_PWM:out_after_turn_grip'},
        'XP03.source':{'JPWMSource:XP03.source','Station:G_TAIL:wire:G_TAIL.3'},
        'XP02.module':{'JPWMSource:XP02.module','U1Five:XP02.module:jacket'},
        'XP03.module':{'JPWMSource:XP03.module','U1Five:XP03.module:jacket'}}
    # Only the two continuous own prefixes are excluded. Grips/other wires,
    # tools and roots stay in the common-space test at their existing margin.
    for w,s in shapes.items():
        for n,t in targets.items():
            if n in mates[w]:continue
            required=material_spacing(w,dict(kind='wire'),n,metas.get(n,{}))
            if bbox_lower_bound(s.BoundBox,t.BoundBox)>=required+1e-6:continue
            a=s;b=t
            if n==world.bus['name']:
                a=s.copy();a.Placement=world.bus['inverse']*a.Placement;b=world.bus['original']
            gap=q.distance(a,b);checks[w+'|'+n]=dict(ok=gap>=required-1e-6,gap_mm=gap,minimum_mm=required)
        print('JPWM_MIDDLE_RECEIVED',w,'queries',len(checks),flush=True)
    for i,w in enumerate(shapes):
        for v in list(shapes)[i+1:]:
            gap=q.distance(shapes[w],shapes[v]);checks[w+'|'+v]=dict(ok=gap>=.2-1e-6,gap_mm=gap,minimum_mm=.2)
    failures=[k for k,v in checks.items() if not v['ok']]
    result=dict(status='JPWM_FOUR_MINIMUM_MIDDLES_STATIC_'+('HOLD' if failures else 'RECEIVED'),
        routes=routes,checks=checks,failures=failures,worker_seconds=round(time.monotonic()-tick,3),
        uncut225_storage_roots_motion_assembly_OPEN=True,N01_complete=False,physical_pass=False)
    save_json(OUT/'n01-JPWM-four-minimum-middles-static.json',result)
    print(result['status'],result['worker_seconds'],'holds',failures,flush=True)
    return result,shapes
