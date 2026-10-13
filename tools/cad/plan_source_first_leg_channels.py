"""Derive8 replacement leg sections from sockets, not inherited flex anchors.

Hip1 takes its rigid turn outside the complete motor BEFORE going outboard.
Ankle3 turns back outward on the source-owned member BEFORE Knee flex.
Left/right inner U exits use opposite X half-spaces, not colliding centreplanes.
The4 clear role2 sections are retained; all new complete paths need material.
"""
import copy,itertools,json,math,time,sys
from pathlib import Path
from plan_current_main_sources import ROOT,OUT,SHA
from plan_current_moving_looms import add,sub,mul,dot,cross,rotation
from plan_current_mta_interfaces import line
from circular_joint_flex import csc,fixed_length_straight_slack
from rigid_tangent_channel import turn
from plan_continuous_joint_family import parts_for_loom,self_screen,flex
from open_prototype_path_preflight import samples
from plan_current_rigid_factory_joins import moved_parts
from route_current_leg_fanouts import sampling_parts
from screen_current_moving_looms import only_new_pairs


def reverse(parts):
    out=copy.deepcopy(list(reversed(parts)))
    for p in out:p['start'],p['end']=p['end'],p['start']
    return out


def solve(row):
    def ends(a):
        pv=row['pivot_mm'];v=row['joint_axis']
        moving=add(pv,rotation(sub(row['moving_anchor_rest_world_mm'],pv),v,a))
        tangent=rotation(row['moving_tangent_rest_world'],v,a)
        return add(row['fixed_anchor_world_mm'],mul(row['fixed_tangent_world'],9)),row['fixed_tangent_world'],sub(moving,mul(tangent,9)),tangent,moving
    options=[]
    for signs in ((1,1),(-1,-1),(1,-1),(-1,1)):
        trials=[csc(*ends(a)[:4],row['joint_axis'],31.5,signs) for a in range(-15,16)]
        if any(q is None for q in trials):continue
        maximum=row.get('maximum_total_turn_deg')
        def short(q):return maximum is None or sum(p['length_mm']/31.5 for p in q['parts'] if p['kind']=='arc')<=math.radians(maximum)+1e-6
        if not all(short(q) for q in trials):continue
        length=math.ceil((max(q['length_mm'] for q in trials)+5)/5)*5
        poses=[fixed_length_straight_slack(*ends(a)[:4],row['joint_axis'],signs,length) for a in range(-15,16)]
        if all(q is not None and short(q) for q in poses):options.append((length,signs,poses))
    if not options:return False
    length,signs,poses=min(options,key=lambda x:x[0]);row['poses']=[]
    for a,q in zip(range(-15,16),poses):
        start,u,end,v,moving=ends(a)
        row['poses'].append(dict(angle=a,parts=[line(row['fixed_anchor_world_mm'],start),*q['parts'],line(end,moving)],radius_mm=31.5))
    row.update(flex_length_mm=length,flex_guide_mm=length,guide_mm=length+18,circular_topology=signs)
    return True


def outward_receiver_y(row,x,side,z,minimum):
    """Solve the full31-pose short-U tangent inequalities BEFORE geometry.

    Circle centres must remain on the declared short turning branch, with
    8mm centre/tangent margin. It is a bounded linear spatial allocation,
    not a grid of curves or an arbitrary extra cable-length sweep.
    """
    n=row['joint_axis'];down=[0,0,-1];out=[0,side,0]
    sign=1 if dot(cross(n,down),out)>0 else -1
    fixed=[x,side*35.5,-8];start=add(fixed,mul(down,9));c1=add(start,mul(cross(n,down),sign*31.5))
    extra=0
    for angle in range(-15,16):
        v=rotation([0,0,1],n,angle)
        def at(y):
            point=[x,side*y,z];moving=add(row['pivot_mm'],rotation(sub(point,row['pivot_mm']),n,angle))
            end=sub(moving,mul(v,9));c2=add(end,mul(cross(n,v),sign*31.5));d=sub(c2,c1)
            dx=dot(d,down);dy=dot(d,out);vx=dot(v,down);vy=dot(v,out)
            return dy,dx*vy-dy*vx
        a=at(minimum);b=at(minimum+1)
        for old,new in zip(a,b):
            slope=new-old;assert slope>0
            extra=max(extra,(8-old)/slope)
    return math.ceil(minimum+max(0,extra))


def run():
    tick=time.monotonic();fp=OUT/'leg-source-current-plan.json';oldfp=OUT/'continuous-joint-family-plan.json'
    af=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json'
    family=json.loads(fp.read_text());original=json.loads(oldfp.read_text());axes=json.loads(af.read_text())['axes']
    routes={r['loom']:r for r in family['routes']};errors=[];changes=[];near=[]
    underbody='--underbody-roots' in sys.argv
    near_member='--near-member-receivers' in sys.argv
    frame_edge='--frame-edge-receivers' in sys.argv or near_member
    surface='--surface-receivers' in sys.argv or frame_edge
    underside='--underside-receivers' in sys.argv or surface
    shared_underbody='--shared-underbody' in sys.argv or underside
    underbody=underbody or shared_underbody
    central='--central-roots' in sys.argv or underbody
    allocated='--allocated' in sys.argv or central;spaces=[]
    for row in family['hips']:
        if not row['loom'].endswith('1'):continue
        route=routes[row['loom']];src=route['source'];n=src['cable_exit_world_axis']
        side=1 if row['physical_leg'].endswith('Left') else -1
        out=[0,side,0];port=src['connector_reservation_world_mm'][src['project_connector_choice']]
        outer=add(port,mul(n,14));land=add(port,mul(n,23))
        arc,_=turn(land,n,out,math.pi/2,31.5);p=arc[-1]['end']
        span=dot(sub(row['moving_anchor_rest_world_mm'],p),out);assert span>0
        moving=add(p,mul(out,span));prefix=[line(outer,land),*arc,line(p,moving)]
        row['moving_anchor_rest_world_mm']=moving;row['moving_tangent_rest_world']=mul(out,-1)
        zmax=max(add(row['pivot_mm'],rotation(sub(moving,row['pivot_mm']),row['joint_axis'],a))[2] for a in range(-15,16))
        row['fixed_anchor_world_mm']=[moving[0],moving[1],zmax+2*31.5+18+5]
        row['fixed_tangent_world']=out
        if not solve(row):errors.append(dict(loom=row['loom'],cause='SOURCE_FIRST_HIP_NO_COMMON_RADIUS_LENGTH'))
        route['source_parts']=reverse(prefix);changes.append(row['loom']+'/Hip')
    for i,row in enumerate(family['knees']):
        if not row['loom'].endswith('3'):continue
        name=row['loom'];route=routes[name];src=route['source'];axis=src['cable_exit_world_axis']
        side=1 if row['physical_leg'].endswith('Left') else -1
        # Opposite source-turn half-spaces prevent opposed left/right leads
        # from sharing one underbody centre return. This is a whole U topology.
        turn_to=[side,0,0];port=src['connector_reservation_world_mm'][src['project_connector_choice']]
        outer=add(port,mul(axis,14));land=add(port,mul(axis,23))
        arc,out=turn(land,axis,turn_to,math.pi,31.5);p=arc[-1]['end']
        old=copy.deepcopy(next(r for r in original['knees'] if r['loom']==name))
        link=copy.deepcopy(next(r for r in original['interstage'] if r['loom']==name))
        if allocated:
            # Allocate the complete2/3 swept planes in their TRUE common
            # normal, not worldY: axis tilt and raised role2 Z consume gap.
            other=next(r for r in family['knees'] if r['loom']==name[:-1]+'2')
            normal=old['joint_axis'];outward=mul(normal,1 if dot(normal,[0,side,0])>0 else -1)
            required=max(dot(old['fixed_anchor_world_mm'],outward),dot(other['fixed_anchor_world_mm'],outward)+8)
            if central:
                # The old witness is Hip2 FLEX versus Knee3, not two parallel
                # Knee planes. Include the entire Hip2 curve in Knee's parent
                # frame at every sampled Hip angle before allocating plane3.
                h2=next(r for r in family['hips'] if r['loom']==name[:-1]+'2')
                ax=next(a for a in axes if a['code']==row['cad_code'] and a['stage']=='Hip')
                occupied=[]
                for angle in (-15,0,15):
                    ps=next(p for p in h2['poses'] if p['angle']==angle)['parts'] if 'parts' in h2['poses'][0] else None
                    if ps is None:
                        from plan_current_joint_local_looms import expanded_pose
                        ps=expanded_pose(h2,angle)['parts']
                    for _,point in samples(sampling_parts(ps),step=1):
                        parent=add(ax['pivot_mm'],rotation(sub(point,ax['pivot_mm']),ax['axis'],-angle))
                        occupied.append(dot(parent,outward))
                required=max(required,max(occupied)+8)
            delta=(required-dot(old['fixed_anchor_world_mm'],outward))/dot([0,side,0],outward)
            if frame_edge:
                # Translate the ENTIRE role3 Hip/interstage/Knee corridor
                # with its receiving root, not a local arc. Actual frames
                # extend to|Y|100; keep wire centre at104 or farther.
                original_root=old['fixed_anchor_world_mm'][1]+side*delta-side*90
                delta+=max(0,104-side*original_root)
            shift=[0,side*delta,0];hip=next(r for r in family['hips'] if r['loom']==name)
            for key in ('fixed_anchor_world_mm','moving_anchor_rest_world_mm'):hip[key]=add(hip[key],shift)
            if central:
                # The inherited90mm AXIAL bridge makes a single cubic's
                # radius fail after true swept-plane separation. Put that
                # span in the Hip joint-normal plane, with the fixed root
                # toward the body. Preserve the interstage +Z departure.
                span90=abs(hip['fixed_anchor_world_mm'][0]-hip['moving_anchor_rest_world_mm'][0])
                hip['fixed_anchor_world_mm']=[hip['moving_anchor_rest_world_mm'][0],hip['moving_anchor_rest_world_mm'][1]-side*span90,hip['moving_anchor_rest_world_mm'][2]]
                if underside:
                    # The downward return crossed the actual Knee motor and
                    # LegLink, not the source socket. Receive OUTWARD from
                    # beyond the complete station frame before flexing.
                    hip['fixed_anchor_world_mm'][1]=side*108
                    hip['fixed_tangent_world']=[0,side,0]
                if surface:
                    # Complete affected target height, not a2mm witness
                    # nudge. Receive above motors, currentrear station and
                    # full W048/W056 (Zmax73.37), including9land+3radius+5.
                    witness=json.loads((OUT/'leg-source-obstacle-witness.json').read_text())
                    high=max(q['target_bounds_mm'][5] for q in witness['results'] if q['loom'].endswith('3'))
                    hip['fixed_anchor_world_mm'][1]=hip['moving_anchor_rest_world_mm'][1]-side*span90
                    hip['fixed_anchor_world_mm'][2]=math.ceil(high+9+3+5)
                    hip['fixed_tangent_world']=[0,0,-1]
                    hip['maximum_total_turn_deg']=195
                if not solve(hip):errors.append(dict(loom=name,cause='JOINT_NORMAL_HIP3_RADIUS'))
            else:
                hip['poses']=[];solved=None
                for length in (hip['flex_guide_mm'],180,200):
                    candidate=[flex(hip,a,length) for a in range(-15,16)]
                    if all(p is not None for p in candidate):solved=candidate;break
                if solved:
                    hip.update(flex_guide_mm=length,flex_length_mm=length,guide_mm=length+18)
                    hip['poses']=[dict(angle=a,parts=p) for a,p in zip(range(-15,16),solved)]
                else:errors.append(dict(loom=name,cause='ALLOCATED_HIP3_RADIUS'))
            old['fixed_anchor_world_mm']=add(old['fixed_anchor_world_mm'],shift)
            for part in link['parts']:
                for key in ('start','mid','end'):
                    if key in part:part[key]=add(part[key],shift)
            spaces.append(dict(leg=old['physical_leg'],normal_plane_gap_mm=8,whole_Hip3_plane_shift_world_mm=shift))
        normal=old['joint_axis'];tangent=mul(old['moving_tangent_rest_world'],-1)
        span=dot(sub(old['fixed_anchor_world_mm'],p),normal)/dot(out,normal)-31.5
        assert span>0,(name,span)
        q=add(p,mul(out,span));last,heading=turn(q,out,tangent,math.pi/2,31.5)
        moving=last[-1]['end']
        assert abs(dot(sub(moving,old['fixed_anchor_world_mm']),normal))<1e-5
        old.update(moving_anchor_rest_world_mm=moving,moving_tangent_rest_world=mul(heading,-1))
        if not solve(old):errors.append(dict(loom=name,cause='OUTWARD_SOURCE_RETURN_NO_COMMON_KNEE_FLEX'))
        family['knees'][i]=old
        family['interstage'][next(i for i,r in enumerate(family['interstage']) if r['loom']==name)]=link
        route['source_parts']=reverse([line(outer,land),*arc,line(p,q),*last]);changes.append(name+'/Knee')
    if allocated and not errors:
        for row in family['hips']:
            if not row['loom'].endswith('1'):continue
            leg=row['physical_leg'];points=[]
            for k in family['knees']:
                if k['physical_leg']!=leg:continue
                r=routes[k['loom']]
                for hip,knee in itertools.product((-15,0,15),repeat=2):
                    ps=parts_for_loom(family,k['loom'],hip,knee,axes)+moved_parts(r['source_parts'],r['source'],hip,knee,axes)
                    points.extend(p for _,p in samples(sampling_parts(ps),step=1))
            front=leg.startswith('Front')
            x=((max(p[0] for p in points)+8) if front else (min(p[0] for p in points)-8)) if central else ((min(p[0] for p in points)-8) if front else (max(p[0] for p in points)+8))
            route=routes[row['loom']];src=route['source'];axis=src['cable_exit_world_axis'];side=1 if leg.endswith('Left') else -1;out=[0,side,0]
            port=src['connector_reservation_world_mm'][src['project_connector_choice']];outer=add(port,mul(axis,14));land=add(port,mul(axis,23))
            if central:
                a,u=turn(land,axis,out,math.pi/2,31.5)
                station_plan=json.loads((OUT/'data-ground-mounts-plan.json').read_text())
                outer_station=max(max(abs(r['bounds_mm'][1]),abs(r['bounds_mm'][4])) for r in station_plan['pads'])
                # Reserve complete station frame, cable radius, a second
                # wire radius and2mm assembly margin before the cross-run.
                cross_y=outer_station+3+3+2
                if underbody:
                    # Two underbody planes8mm apart, BOTH west of the whole
                    # front-power case and its R31.5 return. No front/rear
                    # Hip1 exchange through the narrow Hip2 central gap.
                    power=next(r for r in station_plan['stations'] if r['name']=='FL_P')
                    rear=power['case_bounds_world_mm'][0]-31.5-5
                    x=rear-8 if front else rear
                    if shared_underbody:
                        # Joint allocation, not successive witness nudges:
                        # both left Hip1 complete sweeps need X>25.078;
                        # the entire FL/FR powercase occupies X25..55.
                        # Put BOTH receiving planes east of the cases,
                        # with8mm space for cable/independent root margin.
                        allocation=json.loads((OUT/'underbody-channel-allocation.json').read_text())
                        lower=max(r['free_x_intervals_mm'][-1][0] for r in allocation['results'])
                        high_case=max(r['case_bounds_world_mm'][3] for r in station_plan['stations'] if r['name'] in ('FL_P','FR_P'))
                        east=math.ceil(max(lower,high_case+8))
                        x=east if front else east+8
                        assert all(any(lo<=x<=hi for lo,hi in r['free_x_intervals_mm']) for r in allocation['results'])
                    moving_y=85.;cross_y=moving_y+31.5
                first_end=a[-1]['end'];corner0=[first_end[0],side*(cross_y-31.5),first_end[2]]
                if near_member:
                    # Front: one outward/down source elbow, no200mm
                    # rotating cross-body return or remote moving clamp.
                    # Rear: short return on the source side of Hip3, next
                    # to the existing rail end. Both roots follow members.
                    h3=next(r for r in family['hips'] if r['loom']==row['loom'][:-1]+'3')
                    x=first_end[0] if front else math.ceil(h3['fixed_anchor_world_mm'][0]+8+2)
                if surface:
                    cross_y=outward_receiver_y(row,x,side,first_end[2]-31.5,cross_y)
                    corner0=[first_end[0],side*(cross_y-31.5),first_end[2]]
                assert dot(sub(corner0,first_end),out)>=0
                b,u=turn(corner0,u,mul(axis,-1),math.pi/2,31.5)
                p=b[-1]['end'];corner=[x+axis[0]*31.5,p[1],p[2]]
                assert (near_member and front) or dot(sub(corner,p),mul(axis,-1))>=0
                end_heading=[0,0,-1] if underside else mul(out,-1) if underbody else out
                c,u=turn(corner,mul(axis,-1),end_heading,math.pi/2,31.5);moving=c[-1]['end']
                route['source_parts']=reverse([line(outer,land),*a,line(first_end,corner0),*b,line(p,corner),*c])
                if near_member and front:
                    c,u=turn(corner0,out,[0,0,-1],math.pi/2,31.5);moving=c[-1]['end']
                    route['source_parts']=reverse([line(outer,land),*a,line(first_end,corner0),*c])
                row['fixed_anchor_world_mm'][1]=moving[1]
                zmax=max(add(row['pivot_mm'],rotation(sub(moving,row['pivot_mm']),row['joint_axis'],a))[2] for a in range(-15,16))
                row['fixed_anchor_world_mm'][2]=zmax+2*31.5+18+5
                if underbody:
                    zmin=min(add(row['pivot_mm'],rotation(sub(moving,row['pivot_mm']),row['joint_axis'],a))[2] for a in range(-15,16))
                    row['fixed_anchor_world_mm'][2]=zmin-(2*31.5+18+5)
                    row['fixed_tangent_world']=mul(out,-1)
                    row['moving_tangent_rest_world']=out
                if underside:
                    # Whole receiving topology: vertical moving entry stays
                    # beyond the station frames; fixed entry is immediately
                    # below the retained side rail, not an85mm hanging post.
                    row['fixed_anchor_world_mm']=[x,side*(cross_y-2*31.5-18),-8]
                    row['fixed_tangent_world']=[0,0,-1]
                    row['moving_tangent_rest_world']=[0,0,1]
                if surface:
                    row['fixed_anchor_world_mm']=[x,side*35.5,-8]
                    row['maximum_total_turn_deg']=195
            else:
                extra=(x-land[0])/axis[0]-31.5;assert extra>=0,(leg,extra)
                corner=add(land,mul(axis,extra));arc,_=turn(corner,axis,out,math.pi/2,31.5);p=arc[-1]['end']
                moving=[x,row['moving_anchor_rest_world_mm'][1],p[2]];assert dot(sub(moving,p),out)>0
                route['source_parts']=reverse([line(outer,land),line(land,corner),*arc,line(p,moving)])
            row['moving_anchor_rest_world_mm']=moving;row['fixed_anchor_world_mm'][0]=x
            if not solve(row):errors.append(dict(loom=row['loom'],cause='ALLOCATED_HIP1_RADIUS'))
            spaces.append(dict(leg=leg,Hip1_plane_x_mm=x,entire_Knee_sample_x_mm=[min(p[0] for p in points),max(p[0] for p in points)],sampling_margin_mm=2,required_jacket_sum_plus_margin_mm=8))
    cases=0
    if not errors:
        for leg in ('FrontLeft','FrontRight','RearLeft','RearRight'):
            own=[r for r in family['hips'] if r['physical_leg']==leg]
            for hip,knee in itertools.product((-15,0,15),repeat=2):
                rows=[];cases+=1
                for r in own:
                    route=routes[r['loom']]
                    parts=parts_for_loom(family,r['loom'],hip,knee,axes)+moved_parts(route['source_parts'],route['source'],hip,knee,axes)
                    bad=self_screen(parts)
                    if bad:errors.append(dict(loom=r['loom'],hip=hip,knee=knee,self_contact=bad))
                    rows.append(dict(wire=r['loom'],OD_mm=6,segments=sampling_parts(parts)))
                hits=only_new_pairs([],rows);near.extend(dict(leg=leg,hip=hip,knee=knee,**q) for q in hits)
                if any(q['status']=='REJECT_PLANNING_PROXIMITY' for q in hits):errors.append(dict(leg=leg,hip=hip,knee=knee,mutual=hits))
            print('Source-first shared',leg,'errors',len(errors),flush=True)
        # Include all other legs, not just each own3 family, at nominal pose.
        all_rows=[]
        for n,r in routes.items():
            parts=parts_for_loom(family,n,0,0,axes)+r['source_parts'];guide=sum(p['length_mm'] for p in parts)
            r.update(guide_to_body_grip_mm=guide,nominal_factory_remaining_after50mm_trim_mm=850-guide)
            all_rows.append(dict(wire=n,OD_mm=6,segments=sampling_parts(parts)))
        cross=only_new_pairs([],all_rows)
        if any(q['status']=='REJECT_PLANNING_PROXIMITY' for q in cross):errors.append(dict(cause='WHOLE12_NOMINAL',mutual=cross))
    family.update(status='REJECTED_SOURCE_FIRST_LEG_PLAN' if errors else 'LEG_SOURCE_FIRST_MATH_CLEAR_MATERIAL_OPEN',routes=list(routes.values()),errors=errors,whole_space_allocations=spaces,
        changed_sections=changes,shared_cases=cases,near_pairs=near,selected=False,native_changed=False,W5_complete=False,physical_pass=False,
        decision='Move source plane outside complete motor first; route inner Ankle3 exit back to outboard Knee plane before flex. No old anchor/S retained when it crosses centre/body. Opposite left/right inner turn halfspaces.',
        source_sha256={p.relative_to(ROOT).as_posix():SHA(p) for p in (fp,oldfp,af,Path(__file__),Path(__file__).with_name('circular_joint_flex.py'))},worker_seconds=round(time.monotonic()-tick,3))
    filename='leg-source-near-member-plan.json' if near_member else 'leg-source-frame-edge-plan.json' if frame_edge else 'leg-source-surface-plan.json' if surface else 'leg-source-underside-plan.json' if underside else 'leg-source-shared-underbody-plan.json' if shared_underbody else 'leg-source-underbody-plan.json' if underbody else 'leg-source-central-plan.json' if central else 'leg-source-allocated-plan.json' if allocated else 'leg-source-first-plan.json'
    (OUT/filename).write_text(json.dumps(family,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:family[k] for k in ('status','worker_seconds')}),'errors',len(errors),flush=True)


if __name__=='__main__':run()
