"""Shared12-cable motion allocation BEFORE supports or body fan-out detail.

All twelve factory cables stay separate; three cores are one provisional6mm
bundle, not36 unrelated flex loops. Geometry uses actual E6 housing stages.
Project R30/OD6/850usable are design requirements, NOT supplier claims.
"""
import json,math,time,itertools
from pathlib import Path
from plan_current_main_sources import ROOT,BASE,OUT,SHA
add=lambda a,b:[x+y for x,y in zip(a,b)]
sub=lambda a,b:[x-y for x,y in zip(a,b)]
mul=lambda a,s:[x*s for x in a]
dot=lambda a,b:sum(x*y for x,y in zip(a,b))
cross=lambda a,b:[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
norm=lambda a:math.sqrt(dot(a,a))

def curve_length(q):
    """Adaptive speed integration, NOT a short40-chord length estimate."""
    a=[3*(q[1][j]-q[0][j]) for j in range(3)]
    b=[6*(q[2][j]-2*q[1][j]+q[0][j]) for j in range(3)]
    c=[3*(q[3][j]-3*q[2][j]+3*q[1][j]-q[0][j]) for j in range(3)]
    def speed(t):return math.sqrt(sum((a[j]+b[j]*t+c[j]*t*t)**2 for j in range(3)))
    def integrate(lo,hi,fl,fm,fh,whole,eps,depth):
        mid=(lo+hi)/2;left=speed((lo+mid)/2);right=speed((mid+hi)/2)
        one=(mid-lo)*(fl+4*left+fm)/6;two=(hi-mid)*(fm+4*right+fh)/6
        if depth==0 or abs(one+two-whole)<15*eps:return one+two+(one+two-whole)/15
        return integrate(lo,mid,fl,left,fm,one,eps/2,depth-1)+integrate(mid,hi,fm,right,fh,two,eps/2,depth-1)
    fl,fm,fh=speed(0),speed(.5),speed(1)
    return integrate(0,1,fl,fm,fh,(fl+4*fm+fh)/6,1e-5,14)

def rotation(v,axis,angle):
    t=math.radians(angle);c,s=math.cos(t),math.sin(t)
    return add(add(mul(v,c),mul(cross(axis,v),s)),mul(axis,dot(axis,v)*(1-c)))

def transformed(p,v,axes,angles):
    # Placements compose Hip*Knee: apply child first, then parent.
    for ax,a in reversed(list(zip(axes,angles))):
        pivot=ax['pivot_mm'];p=add(pivot,rotation(sub(p,pivot),ax['axis'],a));v=rotation(v,ax['axis'],a)
    return p,v

def metrics(poles,samples=100):
    p0,p1,p2,p3=poles;length=0;minimum=float('inf');prev=p0;bounds=[list(p0),list(p0)]
    for i in range(samples+1):
        t=i/samples;s=1-t
        p=add(add(mul(p0,s**3),mul(p1,3*s*s*t)),add(mul(p2,3*s*t*t),mul(p3,t**3)))
        d=mul(add(add(mul(sub(p1,p0),s*s),mul(sub(p2,p1),2*s*t)),mul(sub(p3,p2),t*t)),3)
        dd=mul(add(mul(add(sub(p2,mul(p1,2)),p0),s),mul(add(sub(p3,mul(p2,2)),p1),t)),6)
        bend=norm(cross(d,dd))
        radius=norm(d)**3/bend if bend>1e-10 else float('inf')
        minimum=min(minimum,radius);length+=math.dist(prev,p);prev=p
        for j in range(3):bounds[0][j]=min(bounds[0][j],p[j]);bounds[1][j]=max(bounds[1][j],p[j])
    return curve_length(poles),minimum,bounds

def poles(start,axis,end,outward,h,b=None):
    return [start,add(start,mul(axis,h)),add(end,mul(outward,h if b is None else b)),end]

def exact_quarter(start,u,v,radius=30):
    from plan_current_mta_interfaces import curve
    assert abs(dot(u,v))<1e-6
    end=add(add(start,mul(u,radius)),mul(v,radius));k=math.sqrt(.5)
    middle=add(add(start,mul(u,radius*k)),mul(v,radius*(1-k)))
    return curve(start,end,middle,radius,math.pi/2)

def exact_turn_to(start,u,v,radius=30):
    """A real circular turn through the actual angle, not forced90deg."""
    from plan_current_mta_interfaces import curve
    c=max(-1,min(1,dot(u,v)));angle=math.acos(c);s=math.sin(angle)
    assert s>1e-8
    w=mul(sub(v,mul(u,c)),1/s)
    def at(t):return add(add(start,mul(u,radius*math.sin(t))),mul(w,radius*(1-math.cos(t))))
    return curve(start,at(angle),at(angle/2),radius,angle)

def best_span(start,axis,end,outward,target=None):
    """Bounded geometry allocation; a waypoint is NOT a new physical clamp."""
    best=None
    for h in range(30,271,20):
        bs=range(30,271,20)
        if target is not None:
            lo,hi=1.,500.
            if curve_length(poles(start,axis,end,outward,h,lo))>target:continue
            for _ in range(22):
                b=(lo+hi)/2
                if curve_length(poles(start,axis,end,outward,h,b))<target:lo=b
                else:hi=b
            bs=[(lo+hi)/2]
        for b in bs:
            q=poles(start,axis,end,outward,h,b);ll,rr,bb=metrics(q,80)
            if rr<31:continue
            rank=ll if target is None else -rr
            if best is None or rank<best[0]:best=(rank,ll,rr,bb,q)
    return best

def vertical_s(start,end,r=31):
    """Exact UP-to-UP S, with fixed radius and straight height slack."""
    from plan_current_mta_interfaces import line,curve
    up=[0,0,1];delta=sub(end,start);height=delta[2];delta[2]=0;distance=norm(delta)
    if distance<1e-8:return [line(start,end)] if height>0 else None
    if distance>2*r:return None
    direction=mul(delta,1/distance);phi=math.acos(1-distance/(2*r));sn,cs=math.sin(phi),math.cos(phi)
    extra=height-2*r*sn
    if extra<-1e-6:return None
    a0=add(start,mul(up,max(0,extra)/2));parts=[]
    if extra>1e-8:parts.append(line(start,a0))
    a1=add(add(a0,mul(up,r*sn)),mul(direction,r*(1-cs)))
    a2=add(add(a1,mul(up,r*sn)),mul(direction,r*(1-cs)))
    m1=add(add(a0,mul(up,r*math.sin(phi/2))),mul(direction,r*(1-math.cos(phi/2))))
    m2=add(add(a1,mul(up,r*(sn-math.sin(phi/2)))),mul(direction,r*(math.cos(phi/2)-cs)))
    parts.extend((curve(a0,a1,m1,r,phi),curve(a1,a2,m2,r,phi)))
    if extra>1e-8:parts.append(line(a2,end))
    assert math.dist(add(a2,mul(up,max(0,extra)/2)),end)<1e-6
    return parts

def low_return(start,dock,side,target=None):
    """One whole below-frame Knee return, no occupied roof corridor.

Two exact R30 quarters turn DOWN to UP and inboard60mm. Added dip
on both sides preserves cable length; the body grip remains inside200mm.
The minimum height is reported, not declared safe operating clearance.
"""
    from plan_current_mta_interfaces import line
    down=[0,0,-1];up=[0,0,1];inward=[0,-side,0]
    first=exact_quarter(start,down,inward);second=exact_quarter(first['end'],inward,up)
    transition=vertical_s(second['end'],dock)
    if transition is None:return None
    base=first['length_mm']+second['length_mm']+sum(q['length_mm'] for q in transition)
    dip=0 if target is None else (target-base)/2
    if dip<-1e-6:return None
    dip=max(0,dip);a=add(start,mul(down,dip));parts=[]
    if dip>1e-8:parts.append(line(start,a))
    first=exact_quarter(a,down,inward);second=exact_quarter(first['end'],inward,up)
    transition=vertical_s(second['end'],dock);assert transition is not None
    parts.extend((first,second));parts.extend(transition)
    return dict(spans_mm=[],transition_parts_mm=parts,return_parts_mm=[],
        flex_length_mm=sum(q['length_mm'] for q in parts),minimum_sampled_radius_mm=30,
        low_return_topology=True,loop_lowest_world_Z_mm=a[2]-30,
        body_arrival_axis_mm=up,intermediate_waypoint_is_not_a_support=True,
        sampled_bounds_mm=[[min(v[j] for q in parts for v in (q['start'],q['end'],q.get('mid',q['start']))) for j in range(3)],
                           [max(v[j] for q in parts for v in (q['start'],q['end'],q.get('mid',q['start']))) for j in range(3)]])

def knee_return(start,axis,dock,side,target=None,exact_up_S=False):
    # Changed topology after two one-cubic failures: an external UP transition
    # followed by a broad return DOWN to the body. Two C1 spans let the cable
    # turn outside the leg instead of folding at its short dock chord.
    mid=[dock[0],dock[1]+side*70,dock[2]+30];up=[0,0,1]
    transition=[]
    if exact_up_S:
        # A short S transition may be feasible as exact circles but NOT as
        # one cubic (FR2 best cubicR29.065, exact S R31 at the same datums).
        from plan_current_mta_interfaces import line,curve
        lateral=sub(mid,start);height=lateral[2];lateral[2]=0;distance=norm(lateral);r=31
        if distance<1e-8 or distance>2*r:return None
        direction=mul(lateral,1/distance);phi=math.acos(1-distance/(2*r))
        sn,cs=math.sin(phi),math.cos(phi);extra=height-2*r*sn
        if extra<-1e-6:return None
        a0=add(start,mul(up,max(0,extra)/2))
        if extra>1e-8:transition.append(line(start,a0))
        a1=add(add(a0,mul(up,r*sn)),mul(direction,r*(1-cs)))
        a2=add(add(a1,mul(up,r*sn)),mul(direction,r*(1-cs)))
        m1=add(add(a0,mul(up,r*math.sin(phi/2))),mul(direction,r*(1-math.cos(phi/2))))
        m2=add(add(a1,mul(up,r*(sn-math.sin(phi/2)))),mul(direction,r*(math.cos(phi/2)-cs)))
        transition.extend((curve(a0,a1,m1,r,phi),curve(a1,a2,m2,r,phi)))
        if extra>1e-8:transition.append(line(a2,mid))
        assert math.dist(add(a2,mul(up,max(0,extra)/2)),mid)<1e-6
        ll=sum(q['length_mm'] for q in transition)
        a=(ll,ll,r,[[min(start[j],mid[j]) for j in range(3)],[max(start[j],mid[j]) for j in range(3)]],None)
    else:a=best_span(start,axis,mid,mul(up,-1))
    if a is None:return None
    # A cubic is also a poor model for a180-degree return: use two EXACT
    # R35 quarters plus straight slack. Raising both sides by extra/2 keeps
    # exactly the same total cable length at every sampled joint pose.
    rr=abs(mid[1]-dock[1])/2;assert rr>=30
    base=9+math.pi*rr+mid[2]+9-dock[2]
    rise=9 if target is None else 9+(target-a[1]-base)/2
    if rise<9-1e-6:return None
    top=mid[2]+rise;inward=[0,-side,0];p=add(mid,mul(up,rise))
    from plan_current_mta_interfaces import line,curve
    parts=[line(mid,p)]
    for u,v in ((up,inward),(inward,[0,0,-1])):
        end=add(add(p,mul(u,rr)),mul(v,rr));k=math.sqrt(.5)
        middle=add(add(p,mul(u,rr*k)),mul(v,rr*(1-k)))
        parts.append(curve(p,end,middle,rr,math.pi/2));p=end
    parts.append(line(p,dock));ll=sum(q['length_mm'] for q in parts)
    return dict(spans_mm=[] if exact_up_S else [a[4]],transition_parts_mm=transition,return_parts_mm=parts,flex_length_mm=a[1]+ll,
        minimum_sampled_radius_mm=min(a[2],rr),
        sampled_bounds_mm=[[min(a[3][0][j],dock[j]) for j in range(3)],
                           [max(a[3][1][0],dock[0]),max(a[3][1][1],dock[1]),max(a[3][1][2],top+rr)]],
        intermediate_waypoint_is_not_a_support=True)

def plan():
    tick=time.monotonic();f=OUT/'harness-interfaces-plan.json';af=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json'
    old=json.loads(f.read_text());axes=json.loads(af.read_text())['axes'];result=[]
    previous_file=OUT/'moving-looms-plan.json'
    previous=json.loads(previous_file.read_text()) if previous_file.exists() else {}
    reuse={r['loom']:r for r in previous.get('looms',[]) if not r['rejected_poses'] and (previous.get('allocation_revision')==8 or not r['loom'].endswith('3'))} if previous.get('allocation_revision') in (7,8) else {}
    if any(previous.get('source_sha256',{}).get(q.relative_to(ROOT).as_posix())!=SHA(q) for q in (f,af)):reuse={}
    for row in old['looms']:
        leg=row['loom'][:2];i=int(row['loom'][-1])-1;s=1 if leg.endswith('L') else -1
        front=leg.startswith('F')
        dock=[(-145 if i==0 else -100 if i==1 else -120) if front else 185+i*20,
              s*((75 if front else 95) if i==0 else 95 if front and i==1 else 95+i*20),
              145 if i==0 else 30 if i==2 else 50 if front else 80]
        if row['loom'] in reuse and reuse[row['loom']]['body_dock_mm']==dock:
            result.append(reuse[row['loom']]);print('Reuse unchanged complete math family',row['loom'],flush=True);continue
        # Select the upper parallel socket at each Hip: same3nets, otherNC.
        # The4ports clear the original bolt-bearing circles with edge slots.
        choice={'FL1':1,'FR1':0,'RL1':0,'RR1':1}.get(row['loom'],row['project_connector_choice'])
        root=row['connector_reservation_world_mm'][choice]
        direction=row['cable_exit_world_axis']
        # Return toward body X on Hip/Ankle looms; knee cable returns DOWN
        # from an external raised loop, never a forced under-floor U fold.
        # The former universal inward-Y tangent imposed an impossible
        # short-radius fold before testing a single physical obstacle.
        outward=[0,0,1] if i==1 else ([-1,0,0] if front else [1,0,0])
        aa=[next(a for a in axes if a['code']==row['cad_code'] and a['stage']==st)
            for st in (('Hip',) if row['moving_saved_stage'].endswith('_Hip') else ('Hip','Knee'))]
        poses=[]
        for angles in itertools.product((-15,0,15),repeat=len(aa)):
            contact,v=transformed(root,direction,aa,angles)
            # The recorded point is a PCB contact inside the purchased shell,
            # NOT a free cable outlet. Allocate14mm to the unverified factory
            # mating assembly; no loose conductor is drawn through that shell.
            p=add(contact,mul(v,14));start=add(p,mul(v,0 if i==2 else 9))
            prefix=[];routing_start=start;routing_axis=v
            if i==0:
                # Complete the low lateral escape BEFORE rising: Foundation
                # occupies X-178..24/Y-98..100/Z65.99..137.23. An early UP
                # bend through that volume was rejected. Shared high return
                # stays outside the full Foundation/head bay, not a pocket.
                from plan_current_mta_interfaces import line
                side_axis=[0,s,0];prefix=[exact_quarter(start,v,side_axis)]
                lateral=prefix[-1]['end'];outer=[lateral[0],s*(115 if front else 135),lateral[2]]
                assert dot(sub(outer,lateral),side_axis)>9
                prefix.append(line(lateral,outer));prefix.append(exact_quarter(outer,side_axis,[0,0,1]))
                routing_start=prefix[-1]['end'];routing_axis=[0,0,1]
            if i==1 and front:
                # Follow the actual outward source angle directly DOWN on
                # R30. The previous forced fore/aft two-quarter transition
                # unnecessarily dropped too low and occupied another bay.
                prefix=[exact_turn_to(start,v,[0,0,-1])]
                routing_start=prefix[-1]['end'];routing_axis=[0,0,-1]
            if i==2:
                # Bound the initial inward excursion by R30, not a long
                # cubic handle crossing between opposed legs. The U return
                # goes fore/aft in the MOVING knee frame, not below the paws.
                # Opposed legs must NOT make their inward U in the same X
                # plane. Cheap coupled motion rejected five mutual contacts.
                # Left/right use opposite whole fore/aft return directions.
                _,x=transformed(root,[-s if front else s,0,0],aa,angles)
                prefix=[exact_quarter(start,v,x)]
                from plan_current_mta_interfaces import line
                # The9mm housing grip is on the fore/aft straight BETWEEN
                # quarters, not an inward land consuming the opposite leg gap.
                a=prefix[-1]['end'];prefix.append(line(a,add(a,mul(x,9))))
                prefix.append(exact_quarter(prefix[-1]['end'],x,mul(v,-1)))
                routing_start=prefix[-1]['end'];routing_axis=mul(v,-1)
            if i in (0,1,2):
                q=low_return(routing_start,dock,s) if i==1 and front else knee_return(routing_start,routing_axis,dock,s)
                poses.append(dict(angles=list(angles),contact_datum_mm=contact,start=p,axis=v,flex_start=start,
                    routing_start=routing_start,routing_axis=routing_axis,departure_parts_mm=prefix,
                    feasible_length_mm=q['flex_length_mm']+sum(v['length_mm'] for v in prefix) if q else 0,
                    status='NOMINAL_PROJECT_ONLY' if q else 'NO_R30_PROJECT_CURVE'))
                continue
            feasible=[]
            for h in range(30,291,20):
                for b in range(30,291,20):
                    q=poles(start,v,dock,outward,h,b);length,radius,bounds=metrics(q,50)
                    if radius>=31:feasible.append((length,h,b))
            if not feasible:poses.append(dict(angles=list(angles),status='NO_R30_PROJECT_CURVE'));continue
            length,h,b=min(feasible);poses.append(dict(angles=list(angles),start=p,axis=v,flex_start=start,
                feasible_length_mm=length,handle_mm=[h,b],status='NOMINAL_PROJECT_ONLY'))
        bad=[p for p in poses if p['status']=='NO_R30_PROJECT_CURVE']
        length=max((p.get('feasible_length_mm',0) for p in poses),default=0)+10
        for p in poses:
            if p['status']=='NO_R30_PROJECT_CURVE':continue
            if i in (0,1,2):
                prefix_length=sum(v['length_mm'] for v in p['departure_parts_mm'])
                q=low_return(p['routing_start'],dock,s,length-prefix_length) if i==1 and front else knee_return(p['routing_start'],p['routing_axis'],dock,s,length-prefix_length)
                if q is None:p['status']='REJECT_CONSTANT_LENGTH_RADIUS';bad.append(p)
                else:
                    q['flex_length_mm']+=prefix_length;p.update(q)
                continue
            best=None
            for h in range(15,316,15):
                lo,hi=1.,500.
                if curve_length(poles(p['flex_start'],p['axis'],dock,outward,h,lo))>length:continue
                for _ in range(22):
                    b=(lo+hi)/2;q=poles(p['flex_start'],p['axis'],dock,outward,h,b)
                    if curve_length(q)<length:lo=b
                    else:hi=b
                q=poles(p['flex_start'],p['axis'],dock,outward,h,(lo+hi)/2);ll,rr,bb=metrics(q,200)
                if best is None or rr>best[0]:best=(rr,ll,bb,q)
            if best is None:p['status']='REJECT_CONSTANT_LENGTH_RADIUS';bad.append(p);continue
            rr,ll,bb,q=best
            p.update(poles_mm=q,flex_length_mm=ll,minimum_sampled_radius_mm=rr,sampled_bounds_mm=bb)
            if rr<30:p['status']='REJECT_CONSTANT_LENGTH_RADIUS';bad.append(p)
        result.append(dict(loom=row['loom'],motion_stage=row['moving_saved_stage'],
            body_dock_mm=dock,cores=row['electrical'],project_bundle_OD_mm=6,project_dynamic_R_mm=30,
            project_factory_usable_minimum_mm=850,factory_nominal_mm=900,source_grip_land_mm=9,
            one_servo_plug_retained=True,second_socket_NC=True,manufacturer_flex_data_verified=False,
            project_connector_choice=choice,
            poses=poses,rejected_poses=len(bad),constant_flex_budget_mm=length,
            initial_land_mm=0 if i==2 else 9,project_factory_mating_reservation_mm=14,
            factory_mating_geometry_verified=False,
            body_fanout_budget_remaining_mm=850-14-(0 if i==2 else 9)-length-30,
            body_fanout_routes_and_native_grips='OPEN; no complete W5 from these curves'))
        print('Loom family',row['loom'],'rejected',len(bad),'fixedflex',round(length,3),flush=True)
    report=dict(status='PROJECT_FLEX_ALLOCATION_ONLY' if not any(r['rejected_poses'] for r in result) else 'REJECTED_PROJECT_FLEX_FAMILY',
        looms=result,selected=False,W5_complete=False,physical_pass=False,
        allocation_revision=8,count=12,body_core_count=36,nominal_factory_cables=12,nominal_six_packs=2,
        scope='One common cable model per3core factory loom; constant length sampled poses, not approved travel/continuous sweep/material clearance. Functional external loops, no body widening or cosmetic shell-fit claim.',
        changed_topology='Opposed Ankle cable U turns use opposite complete fore/aft directions in their moving frames after five mutual contacts in revision7 cheap motion. Other8families unchanged, including low front Knee returns.14mm factory mating reservation unverified, no cable through housing. Actual plugs/grips/native/access/floor qualification OPEN. Outboard free loops are not approval for wider printed body supports.',
        delivery_gates=['Actual34172 OD/Cu/usable length/cavity order/dynamic bend specification',
            '14mm factory mating reservation and real external outlet: measure delivered servo/plug. No housing cut or inferred void acceptance.',
            'Actual safe servo travel and unpowered supported movement, no tensile/solder/PCB load',
            'Independent housing and body grips, all36fan-out ends and actual changed-material checks'],
        source_sha256={p.relative_to(ROOT).as_posix():SHA(p) for p in (f,af,Path(__file__),ROOT/'tools/cad/plan_current_mta_interfaces.py')},
        planning_seconds=time.monotonic()-tick)
    (OUT/'moving-looms-plan.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=report['status'],seconds=report['planning_seconds'],looms=[dict(loom=r['loom'],bad=r['rejected_poses'],flex=r['constant_flex_budget_mm'],remaining=r['body_fanout_budget_remaining_mm']) for r in result])))
    return report

if __name__=='__main__':plan()
