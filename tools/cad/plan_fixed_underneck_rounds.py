"""One rounded3D factory return with a shared fixed receiver allocation.

Exact-radius turns and tangent straights replace the over-restrictive single
cubic U. Virtual tangent points are NOT clamps. ReceiverY is obtained from
the intersection of all31length/width intervals, before material/native CAD.
"""
import json, math, time
from pathlib import Path
from plan_current_main_sources import ROOT, BASE, SHA
from plan_current_moving_looms import add,sub,mul,dot,norm,rotation,exact_turn_to
from plan_current_mta_interfaces import line

OUT=BASE/'head-wiring-checkpoint'
R=31.5
START=[-176.,47.21874542459709,153.5]
PIVOT=[-152.,-5.25,25.]
END_XZ=[-194.,80.]
RESERVE=math.hypot(3.5,1.8)/2


def route(yaw,slack,receiver_y=0):
    anchor=add(PIVOT,rotation(sub(START,PIVOT),[0,0,1],yaw))
    u=rotation([0,1,0],[0,0,1],yaw);w=[0,-1,0]
    p=add(anchor,mul(u,9));end=[END_XZ[0],receiver_y+9,END_XZ[1]]
    a=R+slack;b=R+p[1]-end[1]+slack
    q1=add(p,mul(u,a));q2=sub(end,mul(w,b));v=sub(q2,q1);length=norm(v);v=mul(v,1/length)
    t1=math.acos(max(-1,min(1,dot(u,v))));t2=math.acos(max(-1,min(1,dot(v,w))))
    d1=R*math.tan(t1/2);d2=R*math.tan(t2/2)
    margins=[a-d1,b-d2,length-d1-d2]
    if min(margins)<-1e-8:return None,margins
    f=sub(q1,mul(u,d1));c=exact_turn_to(f,u,v,R)
    last=sub(q2,mul(v,d2));d=exact_turn_to(last,v,w,R)
    assert math.dist(add(d['end'],mul(w,b-d2)),end)<1e-7
    pieces=[line(anchor,p),line(p,f),c,line(c['end'],last),d,line(d['end'],end),line(end,[END_XZ[0],receiver_y,END_XZ[1]])]
    # Includes both9mm lands; prefix is separate and rigid yaw-owned.
    length=18+a+b+length-2*(d1+d2)+R*(t1+t2)
    return dict(yaw=yaw,slack_mm=slack,parts=pieces,length_after_prefix_mm=length,
        minimum_radius_mm=R,tangent_margins_mm=margins,
        conservative_upperY_mm=max(q1[1],q2[1],p[1],end[1])+RESERVE),margins


def run():
    tick=time.monotonic();source=OUT/'neck-factory-plan.json';prefix=json.loads(source.read_text())['factory']['qualified_exit_length_mm']
    target=250-prefix;intervals=[];failures=[]
    print('Shared exact-radius factory return; derive receiver from31poses',flush=True)
    for yaw in range(-15,16):
        anchor=add(PIVOT,rotation(sub(START,PIVOT),[0,0,1],yaw));u=rotation([0,1,0],[0,0,1],yaw)
        p=add(anchor,mul(u,9));max_slack=100-RESERVE-p[1]-R
        lo,hi=0.,max_slack
        if hi<0 or route(yaw,hi)[0] is None:
            failures.append(dict(yaw=yaw,cause='No nonoverlapping rounded polygon within200mm width',
                maximum_slack_mm=hi,margins_mm=route(yaw,max(0,hi))[1]));break
        if route(yaw,lo)[0] is None:
            for _ in range(40):
                mid=(lo+hi)/2
                if route(yaw,mid)[0] is None:lo=mid
                else:hi=mid
            minimum=hi+1e-6
        else:minimum=0.
        low=route(yaw,minimum)[0];high=route(yaw,max_slack)[0]
        intervals.append(dict(yaw=yaw,minimum_slack_mm=minimum,maximum_slack_mm=max_slack,
            receiver_Y_interval_mm=[low['length_after_prefix_mm']-target,high['length_after_prefix_mm']-target]))
    shared=[max((q['receiver_Y_interval_mm'][0] for q in intervals),default=0),
            min((q['receiver_Y_interval_mm'][1] for q in intervals),default=-1)]
    poses=[];chosen=None
    if len(intervals)==31 and shared[0]<=shared[1]:
        chosen=sum(shared)/2
        for row in intervals:
            lo,hi=row['minimum_slack_mm'],row['maximum_slack_mm']
            for _ in range(40):
                mid=(lo+hi)/2;q=route(row['yaw'],mid,chosen)[0]
                if q is None or q['length_after_prefix_mm']<target:lo=mid
                else:hi=mid
            q=route(row['yaw'],(lo+hi)/2,chosen)[0]
            assert q and abs(q['length_after_prefix_mm']+prefix-250)<1e-6
            poses.append(q)
    report=dict(status='ROUNDED_FACTORY_SHARED_SPACE_MATH_CLEAR_MATERIAL_OPEN' if len(poses)==31 else 'REJECTED_ROUNDED_FACTORY_SHARED_SPACE',
        selected=False,native_changed=False,W2_complete=False,W3_complete=False,physical_pass=False,
        full_factory_mm=250,prefix_mm=prefix,fixed_receiver_XZ_mm=END_XZ,
        derived_shared_receiver_Y_interval_mm=shared,fixed_receiver_Y_mm=chosen,
        allocations=intervals,failures=failures,poses=poses,
        factory_profile_and_dynamic_radius_provisional=True,project_radius_mm=R,
        retained=['Actual S exit','Uncut factory250','Both9mm straight lands','Full200mm width'],
        removes_if_qualified=['MovingJR arm toY134','Second3coreyawflex'],
        decision='Exactfillets rather than singlecubic. Position derived jointly from all31poses, not one scalar collision fix.',
        remaining=['Actualfixedroot bearing faces, all3fixedroutes/independentgrips and JR together',
                   'Head/body/currentwire material and self-distance gates','Native/assembly/stock/selection'],
        source_sha256={p.relative_to(ROOT).as_posix():SHA(p) for p in (source,Path(__file__),Path(__file__).with_name('plan_current_moving_looms.py'))},
        worker_seconds=round(time.monotonic()-tick,3))
    (OUT/'fixed-underneck-rounds-plan.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('status','derived_shared_receiver_Y_interval_mm','fixed_receiver_Y_mm','failures','worker_seconds')}),flush=True)


if __name__=='__main__':run()
