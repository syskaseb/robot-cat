"""Eight complete nominal MTA-to-real-joint factory lead paths.

Do not force a quarter bend where collinear exits allow a straight lead.
R12.4 and100mm usable wire are project assumptions, not catalogue guarantees.
"""
import json,math
import numpy as np
from plan_feline_layout import BASE,OUT
from plan_feline_endpoints import transfer_port


def scurve(a,b,axis,R=12.4,land=9):
    a=np.array(a);b=np.array(b);v=np.array(axis);v=v/np.linalg.norm(v)
    delta=b-a;L=float(delta@v);offset=delta-L*v;H=float(np.linalg.norm(offset))
    assert L>0,('Joint lies behind factory exit',L)
    if H<.001:
        assert L>=2*land
        return [dict(kind='line',start=a.tolist(),end=b.tolist(),length_mm=float(np.linalg.norm(delta)))],L/2
    u=offset/H;angle=math.acos(1-min(H/(2*R),1));span=2*R*math.sin(angle);l=(L-span)/2
    assert l>=land-1e-5,('No complete end lands',l,land)
    q=a+l*v;r=q+R*math.sin(angle)*v+R*(1-math.cos(angle))*u
    cross=max(0,H-2*R);r2=r+cross*u
    t=r2+R*math.sin(angle)*v+R*(1-math.cos(angle))*u
    mid1=q+R*math.sin(angle/2)*v+R*(1-math.cos(angle/2))*u
    mid2=r2+R*(math.sin(angle)-math.sin(angle/2))*v+R*(math.cos(angle/2)-math.cos(angle))*u
    return [dict(kind='line',start=a.tolist(),end=q.tolist(),length_mm=l),
        dict(kind='arc',start=q.tolist(),mid=mid1.tolist(),end=r.tolist(),radius_mm=R,length_mm=R*angle),
        *([dict(kind='line',start=r.tolist(),end=r2.tolist(),length_mm=cross)] if cross else []),
        dict(kind='arc',start=r2.tolist(),mid=mid2.tolist(),end=t.tolist(),radius_mm=R,length_mm=R*angle),
        dict(kind='line',start=t.tolist(),end=b.tolist(),length_mm=l)],l


def routes(plan):
    source=json.loads((BASE/'body-harness-checkpoint/remaining25-interface-allocation.json').read_text())
    ends={r['id']:r for r in source['ends']};groups={g['role']:g for g in plan['groups']};result=[]
    for wire in ('W026','W037','W041','W042','W044','W045','W052','W053'):
        first,last=ends[wire+'/factory/start'],ends[wire+'/factory/end']
        land=first['land'];d=(np.array(land['centre_world_mm'])-first['point_world_mm'])/4.5
        arole,a,axis=transfer_port(plan,first['role'],first['point_world_mm'],d)
        brole,b,_=transfer_port(plan,last['role'],last['point_world_mm'])
        assert np.dot(axis,groups[brole]['factory_exit_axis'])<-.999
        parts,straight=scurve(a,b,axis)
        length=sum(p['length_mm'] for p in parts);assert length<=100
        result.append(dict(wire=wire,start_role=first['role'],end_role=last['role'],
            source_group=arole,joint_group=brole,parts=parts,radius_mm=2.1,
            guide_mm=length,minimum_end_straight_mm=straight,
            factory100mm_provisional_margin_mm=100-length,
            full_factory_guide=True,custom_extension_route_complete=False,
            factory_usable100_is_project_assumption=True))
    return result


if __name__=='__main__':
    plan=json.loads((OUT/'module-layout.json').read_text());rows=routes(plan)
    print(json.dumps([dict(wire=r['wire'],guide_mm=r['guide_mm'],land=r['minimum_end_straight_mm']) for r in rows]))
