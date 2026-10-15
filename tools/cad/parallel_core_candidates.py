"""Reuse a sibling's corridor with the actual core-centre offset.

No module nudges, radius relaxation or acceptance from math alone. A short
shared parallel run branches into the unchanged receiving prefix. Whole
material/wire checks are still mandatory for every selected candidate.
"""
import copy,math
import numpy as np
from plan_current_moving_looms import metrics,exact_quarter
from plan_current_mta_interfaces import line
from plan_body_fanout_layout import part_points


def unit(v):
    n=math.sqrt(sum(x*x for x in v));assert n>1e-8
    return [x/n for x in v]


def tangent(part):
    if part['kind']=='line':return unit([b-a for a,b in zip(part['start'],part['end'])])
    if part['kind']=='bezier':return unit([b-a for a,b in zip(part['poles_mm'][-2],part['poles_mm'][-1])])
    a,b,c=(np.asarray(part[k],float) for k in ('start','mid','end'))
    v=b-a;w=c-a;n=np.cross(v,w)
    centre=a+(np.dot(v,v)*np.cross(w,n)+np.dot(w,w)*np.cross(n,v))/(2*np.dot(n,n))
    return unit(np.cross(n,c-centre))


def shifted(part,delta):
    q=copy.deepcopy(part)
    for k in ('start','mid','end'):
        if k in q:q[k]=[a+b for a,b in zip(q[k],delta)]
    if 'poles_mm' in q:q['poles_mm']=[[a+b for a,b in zip(p,delta)] for p in q['poles_mm']]
    return q


def proposals(row,sibling,sibling_route):
    assert row['loom']==sibling['loom'] and row['wire']!=sibling['wire']
    if row.get('source_free_axis',row['bodyward_bundle_tangent'])!=sibling.get('source_free_axis',sibling['bodyward_bundle_tangent']):return []
    delta=[a-b for a,b in zip(row['free_start'],sibling['free_start'])]
    source=row.get('source_parts',[row['source_land']])
    receiving=row.get('receiving_parts',[row['receiving_land']])
    if math.dist(source[-1]['end'],row['free_start'])>1e-6 or math.dist(receiving[0]['start'],row['free_end'])>1e-6:return []
    # Inherited routes may have no receiving_parts array. Find the actual
    # known free-end boundaries in the route, never guess a slice length.
    parts=sibling_route['parts']
    starts=[i for i,p in enumerate(parts) if math.dist(p['start'],sibling['free_start'])<1e-6]
    ends=[i+1 for i,p in enumerate(parts) if math.dist(p['end'],sibling['free_end'])<1e-6]
    if not starts or not ends or starts[0]>=ends[-1]:return []
    middle=parts[starts[0]:ends[-1]]
    candidates=[];seen=set()
    for count in range(1,min(len(middle),10)+1):
        prefix=[shifted(p,delta) for p in middle[:count]]
        p=prefix[-1]['end'];end=row['free_end'];u=tangent(prefix[-1]);v=row['receiver_outward_axis']
        for h,b in ((12,12),(18,38),(38,18),(38,38),(65,65)):
            poles=[p,[a+h*x for a,x in zip(p,u)],[a+b*x for a,x in zip(end,v)],end]
            length,radius,_=metrics(poles,40)
            if radius<10.5:continue
            length,radius,_=metrics(poles,400)
            if radius<10:continue
            branch=dict(kind='bezier',start=p,end=end,poles_mm=poles,length_mm=length)
            parts=[*source,*prefix,branch,*receiving]
            assert all(math.dist(a['end'],b['start'])<1e-6 for a,b in zip(parts,parts[1:]))
            guide=sum(p['length_mm'] for p in parts)
            spare=row['capacity_before_terminal_mm']-row['terminal_allowance_project_mm']-guide
            if spare<0:continue
            points=np.concatenate([part_points(p) for p in parts]);along=np.r_[0,np.cumsum(np.linalg.norm(np.diff(points,axis=0),axis=1))]
            remote=np.abs(along[:,None]-along[None,:])>4
            dist=np.sum((points[:,None,:]-points[None,:,:])**2,axis=2)
            if np.any(dist[remote]<2.1**2):continue
            key=(count,h,b)
            if key in seen:continue
            seen.add(key);candidates.append(dict(parts=parts,guide_mm=guide,spare_before_trim_mm=spare,
                minimum_sampled_R_mm=min(10,radius),source='shared_sibling_corridor',
                sibling_wire=sibling['wire'],actual_core_offset_mm=delta,shared_middle_parts=count))
    return sorted(candidates,key=lambda q:q['guide_mm'])


def west_north_return(row,first):
    """One R10 return corridor after the ONLY qualified RL3-G first bend.

    A 30mm lateral span permits a real return, unlike a tight cubic U-turn
    between the nearby source and receiver. This is a proposal, not clearance.
    """
    assert row['wire']=='W071' and tangent(first)[0]<-.999
    west=[-1,0,0];north=[0,1,0]
    a=first['end'];b=[a[0]-20,a[1],a[2]]
    straight=line(a,b);turn=exact_quarter(b,west,north,10)
    p=turn['end'];end=row['free_end'];v=row['receiver_outward_axis']
    poles=[p,[p[0],p[1]+18,p[2]],[e+18*x for e,x in zip(end,v)],end]
    length,radius,_=metrics(poles,400)
    if radius<10:return None
    branch=dict(kind='bezier',start=p,end=end,poles_mm=poles,length_mm=length)
    parts=[*row.get('source_parts',[row['source_land']]),first,straight,turn,branch,*row['receiving_parts']]
    guide=sum(p['length_mm'] for p in parts)
    spare=row['capacity_before_terminal_mm']-row['terminal_allowance_project_mm']-guide
    if spare<0:return None
    return dict(parts=parts,guide_mm=guide,spare_before_trim_mm=spare,
        minimum_sampled_R_mm=min(10,radius),source='one_shared_west_north_return_after_qualified_exit')
