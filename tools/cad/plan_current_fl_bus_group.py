"""One coupled FL/BUS proposal, with explicit downstream invalidation.

The previous receiver relocation kept W003 through the new ankle riser.
Both BUS cores are now actually rerouted, not merely removed from a screen.
All36 leg fanouts must be regenerated for the fixed bundle boundaries. Stop
at a blocked complete endpoint before searching middles or starting native CAD.
Receipts reference retained families rather than duplicating their sampled data.
"""
import copy
import itertools
import heapq
import json
import math
import time
from collections import Counter
from pathlib import Path

from plan_current_leg_body_joins import ROOT, OUT, SHA, SharedMotionSpace, arch_family, exact_turn_to, sub, norm
from plan_current_bus_routes import ReservedSpace
from route_current_leg_fanouts import Space, search, sampling_parts, pose_row
from plan_current_joined_leg_looms import leave_port, reverse_parts, exact_quarter
from plan_current_mta_interfaces import line, add, mul
from screen_current_remaining_routes import route_rows
from plan_current_ground_tree import paired_east_tail
from open_prototype_path_preflight import samples
from plan_current_moving_looms import vertical_s
from screen_current_moving_looms import only_new_pairs
from current_material_reservations import FaceKeepouts,terminal_owners

UP=[0,0,1]
CHANGED=('W002','W003')
LONG_SOURCE=ROOT/'hardware/reference/servo-long-lead-2026-10-11/source.json'


def usable_blank(loom):
    # A different real bought component is not a relaxed900mm gate. Keep
    #the same50mm trim reserve. Candidate selection/native/E3 stay OPEN.
    # Allocate against the available real long lead; select the shorter
    #900mm lead only after ALL three complete core lengths are known.
    return 1169.2


class WitnessSpace(Space):
    """Keep the first rejecting witness in the existing gate, not a new audit."""
    def __init__(self,materials=None):
        super().__init__();self.materials=materials
    def clear(self,parts,ignore=(),margin=.7,root=None,material_terminal=None,qualified_material=False):
        self.hit=None
        if self.materials and not qualified_material:
            self.hit=self.materials.hit(parts,1+margin,
                terminal_owners(material_terminal) if material_terminal else (),3 if material_terminal else 0)
            if self.hit:return False
        expanded=sampling_parts(parts);prefix=[];walked=0
        for s in expanded:prefix.append(walked);walked+=s['length_mm']
        for i,p in samples(expanded,step=1):
            segment=expanded[i];within=math.dist(p,segment['start'])
            if segment['kind']=='arc':within=2*segment['radius_mm']*math.asin(min(1,within/(2*segment['radius_mm'])))
            along=prefix[i]+within
            key=tuple(math.floor(x/self.cell) for x in p)
            for d in itertools.product((-1,0,1),repeat=3):
                for q,r,name in self.grid.get(tuple(x+y for x,y in zip(key,d)),()):
                    if name in ignore:continue
                    # The allowed packed-core/jacket overlap is the first
                    #5mm of ACTUAL path travel, not the first segment. A
                    #short initial land must not create a false contact at
                    #the following arc. No other owner or remote span exempt.
                    if root and name==root[0] and along<=5+1e-8 and math.dist(q,root[1])<=5:continue
                    if math.dist(p,q)<r+1+margin:
                        self.hit=dict(other=name,point_mm=p,other_point_mm=q)
                        return False
        return True


def receiver(point, axis, direction, radius=10):
    """Nine mm insulation land followed by two explicit radius-correct turns."""
    q=[line(point,add(point,mul(axis,9)))]
    q.append(exact_quarter(q[-1]['end'],axis,direction,radius))
    q.append(line(q[-1]['end'],add(q[-1]['end'],mul(direction,4))))
    q.append(exact_quarter(q[-1]['end'],direction,UP,radius))
    return q


def coupled_approaches(relocation,bus,bridges,ground,registry):
    """Allocate ALL changed fixed ends before choosing a moving boundary."""
    prefixes={'W002':bus['receiving_prefixes']['W002'],
              'W003':bus['receiving_prefixes']['W003']}
    breakouts={w:bus['source_prefixes'][w] for w in ('W002','W003')}
    return prefixes,breakouts


def outboard_basis(loom,side):
    """Keep the actual low outlet/U; escape OUTWARD before rising at all.

    The rejected FL source turned vertically through its own side frame,
    then crossed the entire body/tail. Rear folds crossed the ground rails.
    One shared topology avoids both: leave the existing outlet tangent to
    Y140, turn UP outside the material, then an exact fixed-length roof arch.
    """
    changed=copy.deepcopy(loom)
    for pose in changed['poses']:
        start=pose['spans_mm'][0][0] if loom['loom']=='FL3' else pose['flex_start']
        axis=sub(pose['spans_mm'][0][1],start) if loom['loom']=='FL3' else pose['axis']
        axis=mul(axis,1/norm(axis))
        assert side*axis[1]>.5
        p=list(pose.get('departure_parts_mm',[])) if loom['loom']=='FL3' else []
        if loom['loom']=='FL3':
            length=(side*140-start[1])/axis[1];assert length>=0
            p.append(line(start,add(start,mul(axis,length))))
            # Cross fore/aft only AFTER leaving the side frame. The earlier
            #central crossing below the frame cut P0; the outboard bay is
            #a different topology. Rise aft of the head's yaw envelope.
            p.append(exact_turn_to(p[-1]['end'],axis,[1,0,0],31))
            a=p[-1]['end'];assert a[0]<-20
            p.append(line(a,[-20,a[1],a[2]]))
            p.append(exact_quarter(p[-1]['end'],[1,0,0],UP,31))
        else:
            # All affected Knee leads turn fore-aft BEFORE their rise,
            #separating the source region from adjacent Ankle cables.
            #FL2 must change WITH FL3; keeping its old low return forced
            #the Ankle cable into the purchased frame.
            p.append(exact_turn_to(start,axis,[1,0,0],31))
            p.append(exact_quarter(p[-1]['end'],[1,0,0],UP,31))
        a=p[-1]['end'];assert a[2]<180
        p.append(line(a,[a[0],a[1],180]))
        pose['departure_parts_mm']=p;a=p[-1]['end']
        pose['spans_mm']=[[a,add(a,[0,0,30]),add(a,[0,0,60]),add(a,[0,0,90])]]
    return changed


def descending_s(start,target):
    """Put excess height at the FREE end, not through the receiving PCB."""
    q=vertical_s([start[0],start[1],-start[2]],[target[0],target[1],-target[2]],10)
    if q is None:return None
    if len(q)>1 and q[-1]['kind']=='line' and q[-2]['kind']=='arc':
        tail=q.pop();extra=tail['length_mm']
        delta=[0,0,extra]
        # Shift both S arcs down along the start tangent; merge the added
        #height into the first land. True endpoints/tangents/R10 unchanged.
        first=q.pop(0) if q[0]['kind']=='line' else None
        origin=first['start'] if first else q[0]['start']
        for s in q:
            for key in ('start','mid','end'):
                if key in s:s[key]=add(s[key],delta)
        q.insert(0,line(origin,q[0]['start']))
    p=[]
    for segment in q:
        s=dict(segment)
        for key in ('start','mid','end'):
            if key in s:s[key]=[s[key][0],s[key][1],-s[key][2]]
        if s['length_mm']>1e-8:p.append(s)
    return p


def rising_s_family(loom,dock):
    """Constant cable length by flexing a rising S, not a tall roof return.

    The source tangent escapes laterally before turning UP. Each pose may
    change S radius, never below31mm. Intersect the true achievable length
    intervals, then solve that SAME cable length in every joint pose.
    """
    rows=[]
    for pose in loom['poses']:
        start=pose['spans_mm'][0][0];height=dock[2]-start[2]
        distance=math.dist(start[:2],dock[:2])
        if height<=0 or distance<1e-7:return None
        upper=(height*height+distance*distance)/(4*distance)
        # If distance>2R, the pair of quarter turns needs height>=2R.
        if height<distance:upper=height/2
        if upper<31:return None
        prefix=sum(s['length_mm'] for s in pose['departure_parts_mm'])
        def at(radius,start=start,prefix=prefix):
            p=vertical_s(start,dock,radius)
            return None if p is None else (prefix+sum(s['length_mm'] for s in p),p)
        small,big=at(31),at(upper*(1-1e-9))
        if small is None or big is None:return None
        rows.append((pose,upper,small[0],big[0],at))
    low=max(row[3] for row in rows);high=min(row[2] for row in rows)
    if low>high+1e-7:return None
    target=(low+high)/2;poses=[]
    for pose,upper,_,_,at in rows:
        lo,hi=31,upper
        for _ in range(40):
            mid=(lo+hi)/2
            if at(mid)[0]>target:lo=mid
            else:hi=mid
        radius=(lo+hi)/2;length,parts=at(radius)
        if abs(length-target)>1e-5:return None
        poses.append(dict(angles=pose['angles'],start=pose['start'],flex_start=pose['flex_start'],
            departure_parts_mm=pose['departure_parts_mm'],transition_parts_mm=parts,spans_mm=[],return_parts_mm=[],
            body_arrival_axis_mm=UP,flex_length_mm=length,sampled_minimum_R_mm=min(31,radius)))
    return dict(body_dock_mm=dock,fixed_bundle_guide_mm=target,poses=poses,
        topology='Lateral source escape then variable-radius rising S; fixed cable length, all R>=31')


def lateral_basis(loom,side):
    """All four affected leads leave the leg before any vertical return."""
    changed=copy.deepcopy(loom)
    for pose in changed['poses']:
        start=pose['spans_mm'][0][0] if loom['loom']=='FL3' else pose['flex_start']
        axis=sub(pose['spans_mm'][0][1],start) if loom['loom']=='FL3' else pose['axis']
        axis=mul(axis,1/norm(axis));assert side*axis[1]>.5
        parts=list(pose.get('departure_parts_mm',[])) if loom['loom']=='FL3' else []
        length=(side*180-start[1])/axis[1]
        if length<0:return None
        parts.append(line(start,add(start,mul(axis,length))))
        parts.append(exact_turn_to(parts[-1]['end'],axis,UP,31))
        a=parts[-1]['end'];pose['departure_parts_mm']=parts
        pose['spans_mm']=[[a,add(a,[0,0,30]),add(a,[0,0,60]),add(a,[0,0,90])]]
    return changed


def complete_breakout(loom,space):
    """Allocate the complete radial fan, not merely its virtual centre."""
    pose=next(p for p in loom['poses'] if not any(p['angles']))
    axis=pose['body_arrival_axis_mm'];join=loom['body_dock_mm'];hits=[]
    for rotation in (30,90,150,210,270,330):
        rows=[]
        for core,v in loom['cores'].items():
            a=math.radians(rotation+{'D':0,'G':120,'V':240}[core]);radial=[math.cos(a),math.sin(a),0]
            # This is a virtual jacket/core boundary, NOT a clamp. The
            # former imposed5mm straight land has no hardware owner and
            # ran all3 cores into the adjacent MTA feed before fanning.
            # Real receiving grips still require their separate9mm lands.
            p=[s for s in leave_port(add(join,mul(radial,1.2)),axis,radial,land=0) if s['length_mm']>1e-8]
            if not space.clear(p,margin=0,root=('Loom/'+loom['loom'],join)):
                hits.append(dict(rotation=rotation,wire=v['wire'],**space.hit));break
            rows.append((v['wire'],p))
        if len(rows)==3:return rows,hits
    return None,hits


def bundle_space(retained,looms,receiving=(),materials=None):
    space=WitnessSpace(materials)
    for row in retained:space.insert(row)
    for wid,p in receiving:space.insert(dict(wire=wid+'/receiver',OD_mm=2,segments=p))
    for loom in looms:
        for pose in loom['poses']:space.insert(pose_row(loom,pose))
    return space


def arch_middle(start,end,radius):
    d=[end[0]-start[0],end[1]-start[1],0];distance=math.hypot(*d[:2])
    if distance<2*radius:return None
    direction=mul(d,1/distance);peak=max(start[2],end[2])
    q=[line(start,[*start[:2],peak])]
    q.append(exact_quarter(q[-1]['end'],UP,direction,radius))
    q.append(line(q[-1]['end'],add(q[-1]['end'],mul(direction,distance-2*radius))))
    q.append(exact_quarter(q[-1]['end'],direction,[0,0,-1],radius))
    q.append(line(q[-1]['end'],end))
    return [s for s in q if s['length_mm']>1e-8]


def ground_middle(space,start,target,max_states=400):
    """One bounded R21 trunk corridor; never run a4.2mm trunk through R10."""
    axes=((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))
    ignore=('W025/receiver','W025/breakout');r=21;origin=tuple(start)
    first=(0,0,0,4);best={first:0};parents={};counter=itertools.count()
    queue=[(math.dist(start,target),0,next(counter),first)];expanded=0
    while queue and expanded<max_states:
        _,cost,_,state=heapq.heappop(queue)
        if cost!=best.get(state):continue
        expanded+=1;point=[origin[j]+r*state[j] for j in range(3)];u=axes[state[3]]
        if state[3]==4:
            end=arch_middle(point,target,r)
            if end and space.clear(end,ignore=ignore,margin=1.8):
                pieces=[];s=state
                while s!=first:
                    old,part=parents[s];pieces.append(part);s=old
                return list(reversed(pieces))+end,expanded
        for k,v in enumerate(axes):
            if k==state[3]:part=line(point,add(point,mul(u,r)))
            elif sum(x*y for x,y in zip(u,v))==0:part=exact_quarter(point,u,v,r)
            else:continue
            p=part['end']
            if not (-175<=p[0]<=180 and -100<=p[1]<=100 and 40<=p[2]<=290):continue
            if not space.clear([part],ignore=ignore,margin=1.8):continue
            newcost=cost+part['length_mm']
            if newcost+math.dist(p,target)>700:continue
            nxt=tuple(round((p[j]-origin[j])/r) for j in range(3))+(k,)
            if newcost>=best.get(nxt,float('inf')):continue
            best[nxt]=newcost;parents[nxt]=(state,part)
            heapq.heappush(queue,(newcost+math.dist(p,target),newcost,next(counter),nxt))
    return None,expanded


def direct_down_fan(loom,space,receiving):
    """A DOWN bundle can continue DOWN to its terminals, without a U-turn.

    The jacket split has no physical grip and no mandated UP return. Keep
    the true packed core centres at its boundary, then use exact R10 S-curves
    to the unchanged9mm receiving-grip approaches. All3 complete lengths and
    mutual separations are checked before accepting this bundle boundary.
    """
    join=loom['body_dock_mm'];failures=[]
    for rotation in (30,90,150,210,270,330):
        routes={};rows=[]
        for core,v in loom['cores'].items():
            wid=v['wire'];a=math.radians(rotation+{'D':0,'G':120,'V':240}[core])
            start=add(join,[1.2*math.cos(a),1.2*math.sin(a),0]);target=receiving[wid][-1]['end']
            arrival=next(p for p in loom['poses'] if not any(p['angles']))['body_arrival_axis_mm']
            p=descending_s(start,target) if arrival[2]<0 else arch_middle(start,target,10)
            if p is None:break
            blank=14+loom['initial_land_mm']+loom['fixed_bundle_guide_mm']+sum(s['length_mm'] for s in p+receiving[wid])+21
            if blank>usable_blank(loom['loom']):break
            if not space.clear(p,ignore=(wid+'/receiver',),margin=0,root=('Loom/'+loom['loom'],join)):
                failures.append(dict(rotation=rotation,wire=wid,**space.hit));break
            whole=p+reverse_parts(receiving[wid]);rows.append(dict(wire=wid,OD_mm=2,segments=whole))
            routes[wid]=dict(parts=whole,guide_mm=sum(s['length_mm'] for s in whole),minimum_factory_blank_project_mm=blank,
                loom=loom['loom'],project_R_mm=10,topology='Direct DOWN-to-DOWN R10 S; no virtual UP grip')
        if len(routes)!=3:continue
        if any(q['status']=='REJECT_PLANNING_PROXIMITY' for q in only_new_pairs([],rows)):continue
        return routes,failures
    return None,failures


def run():
    tick=time.monotonic(); pins={Path(__file__),LONG_SOURCE,Path(__file__).with_name('current_material_reservations.py')}
    long_source=json.loads(LONG_SOURCE.read_text())
    assert long_source['SKU']=='SPMA3007'
    assert long_source['derived']['nominal_length_mm']-long_source['project_assumptions_not_catalog_facts']['trim_reserve_mm']==usable_blank('FL3')
    def read(name):
        f=OUT/name; pins.add(f); q=json.loads(f.read_text())
        for n,h in q.get('source_sha256',{}).items():
            assert SHA(ROOT/n)==h,n
        return q
    previous=read('leg-body-joins-plan.json')
    stations=read('leg-stations-plan.json')
    termination=read('leg-terminations-plan.json')
    relocation=dict(rails={n:stations['stations'][n] for n in ('D_FL','FL_G')},leg_body_ends=termination['wires'])
    original=read('joined-leg-looms-plan.json')
    heads=read('head-wire-screen-reference.json')
    bus=read('BUS-routes-plan.json')
    registry=read('harness-interfaces-plan.json')
    ground=read('ground-tree-plan.json')
    bridges=read('data-bridges-plan.json')
    spatial=read('BUS-material-routing-space.json')
    materials=FaceKeepouts(spatial['boxes'])
    fixed,more=route_rows(tuple(OUT/(s+'-plan.json') for s in
        ('ground-tree','data-bridges','positive-source','s0-in-extension','BUS-routes')))
    pins.update(more)
    for wid in CHANGED: fixed.pop(wid,None)
    retained=list(fixed.values())+heads['rows']
    coupled_prefixes,coupled_breakouts=coupled_approaches(relocation,bus,bridges,ground,registry)
    # These were previously inserted only AFTER the FL candidate was chosen.
    # A locally clear candidate could therefore occupy the real BUS approach.
    # Both BUS ends and both trunk ends are now part of the initial allocation.
    planned_retained=retained+[dict(wire=wid+'/'+label,OD_mm=4.2 if wid=='W025' else 2,segments=p)
        for label,rows in (('receiver',coupled_prefixes),('breakout',coupled_breakouts)) for wid,p in rows.items()]
    chosen=[q for q in previous['looms'] if q['loom'] not in ('FL2','FL3','RL2','RR2')]
    raw=next(q for q in original['looms'] if q['loom']=='FL3')
    ends={q['wire']:q for q in relocation['leg_body_ends']}
    receiving={}
    for wid,end in ends.items():
        side=1 if end['body_point_mm'][1]>0 else -1
        core=next(k for loom in original['looms'] for k,v in loom['cores'].items() if v['wire']==wid)
        # Front ports are spaced along X. Turn across the row, not along
        #it: translating an EAST S-bend by4.75mm makes adjacent arcs cross.
        direction=[0,-1,0] if end['body_role'].split('.')[0] in ('D_FL','FL_G') else [0,side*(-1 if core=='V' else 1),0]
        receiving[wid]=receiver(end['body_point_mm'],end['body_departure_axis'],direction)
    # The old joins were averages of three terminal positions: there was
    # no room for the required radial fan. Allocate whole interior receiving
    # zones clear of the rear ground columns, before selecting a bundle.
    rear_changes={};rear_failures=[];rear_fans={}
    for name,side in (('FL2',1),('RL2',1),('RR2',-1)):
        raw_rear=next(q for q in original['looms'] if q['loom']==name)
        motion=SharedMotionSpace(planned_retained,chosen);found=None;counts=Counter();witnesses={}
        basis=lateral_basis(raw_rear,side)
        xs=(-100,-75) if name=='FL2' else (125,100)
        for dock in itertools.product(xs,(side*45,side*65),(150,170)):
            c=rising_s_family(basis,list(dock))
            if c is None:continue
            q=dict(loom=name,motion_stage=raw_rear['motion_stage'],initial_land_mm=raw_rear['initial_land_mm'],cores=raw_rear['cores'],**c)
            lower=14+q['initial_land_mm']+q['fixed_bundle_guide_mm']+max(math.dist(dock,ends[v['wire']]['body_point_mm']) for v in q['cores'].values())+21
            if lower>usable_blank(name):counts['capacity']+=1;continue
            hit=materials.hit(pose_row(q,next(p for p in q['poses'] if not any(p['angles'])))['segments'],3.5)
            if hit:counts[hit['other']]+=1;continue
            clear,hit=motion.clear(q)
            if not clear:
                counts[hit['other']]+=1;witnesses.setdefault(hit['other'],hit);continue
            fan,_=direct_down_fan(q,bundle_space(planned_retained,chosen+[q],receiving.items(),materials),receiving)
            if fan is None:counts['complete_fan']+=1;continue
            found=q;rear_fans.update(fan);break
        if found:chosen.append(found);rear_changes[name]=found
        else:rear_failures.append(dict(loom=name,cause='NO_WHOLE_REAR_RECEIVING_ZONE',rejections=dict(counts),witnesses=witnesses))
    space=SharedMotionSpace(planned_retained,chosen)
    targets=[ends[q['wire']]['body_point_mm'] for q in raw['cores'].values()]
    # A direct descending R10 S with lateral span>=20mm needs20mm
    #height above the complete receiver approach, not merely its mouth.
    minimum_down_join_z=max(receiving[q['wire']][-1]['end'][2] for q in raw['cores'].values())+20
    allocated_down_z=10*math.ceil(minimum_down_join_z/10)
    reject_counts=Counter(); candidate=None; trials=0;direct_fan=None;fan_failures=[];fl_witnesses={}
    for basis in (lateral_basis(raw,1),):
        prefix_hit=materials.hit(next(p for p in basis['poses'] if not any(p['angles']))['departure_parts_mm'],3.5)
        if prefix_hit:
            reject_counts[prefix_hit['other']]+=1;continue
        zones=[(180,(-130,60,170))]+list(itertools.product((180,210),itertools.product((-150,-120,-90),(40,60),(170,200))))
        for floor,dock in zones:
            trials+=1
            proposal=rising_s_family(basis,list(dock))
            if proposal is None:continue
            lower=14+basis['initial_land_mm']+proposal['fixed_bundle_guide_mm']+max(math.dist(dock,p) for p in targets)+21
            if lower>usable_blank('FL3'):reject_counts['factory_capacity_lower_bound']+=1;continue
            proposal=dict(loom='FL3',motion_stage=raw['motion_stage'],initial_land_mm=raw['initial_land_mm'],
                cores=raw['cores'],corridor='Original low U then outwardY140 before any rise',minimum_complete_blank_lower_bound_mm=lower,**proposal)
            hit=materials.hit(pose_row(proposal,next(p for p in proposal['poses'] if not any(p['angles'])))['segments'],3.5)
            if hit:reject_counts[hit['other']]+=1;continue
            clear,hit=space.clear(proposal)
            if clear:
                fan,hits=direct_down_fan(proposal,bundle_space(planned_retained,chosen+[proposal],receiving.items(),materials),receiving)
                if fan is not None:candidate=proposal;direct_fan=fan;break
                fan_failures.extend(hits[:1]);reject_counts['complete_down_fan']+=1;continue
            reject_counts[hit['other']]+=1;fl_witnesses.setdefault(hit['other'],hit)
        if candidate:break
    failures=list(rear_failures);routes={};prefixes={};breakouts={};total_states=0
    if candidate:
        chosen=chosen+[candidate]
        # Reserve complete sampled bundle families, not old nominal fanouts.
        channel=bundle_space(retained,chosen,materials=materials)
        routes.update(rear_fans);routes.update(direct_fan)
        for wid,r in routes.items():channel.insert(dict(wire=wid,OD_mm=2,segments=r['parts']))
        for wid,end in ends.items():
            p=receiving[wid]
            if wid not in routes and not channel.clear(p,margin=0,material_terminal=end['body_role'].split('.')[0]):failures.append(dict(wire=wid,cause='RECEIVER_APPROACH_BLOCKED',**channel.hit))
            prefixes[wid]=p
        # BUS source passages/grip roots stay exactly as qualified. The
        # downstream G route is invalidated even though G2 did not move.
        prefixes.update(coupled_prefixes)
        for wid in ('W002','W003'):
            breakouts[wid]=bus['source_prefixes'][wid]
            for label,p in [('source',breakouts[wid]),('receiver',prefixes[wid])]:
                # These exact source/receiver recipes and original cases
                #are already material-qualified. Still check new wires.
                #Face-box overfill of the real carrier passage is not a
                #reason to invalidate that unchanged exact BRep proof.
                if not channel.clear(p,margin=0,qualified_material=True):failures.append(dict(wire=wid,cause='BUS_'+label.upper()+'_APPROACH_BLOCKED',**channel.hit))
        for wid,p in prefixes.items():channel.insert(dict(wire=wid+'/receiver',OD_mm=4.2 if wid=='W025' else 2,segments=p))
        for wid in ('W002','W003'):
            channel.insert(dict(wire=wid+'/breakout',OD_mm=4.2 if wid=='W025' else 2,segments=breakouts[wid]))
        # Complete three-core breakouts follow each bundle's actual arrival
        # tangent; the old UP-only fanouts cannot be reused for DOWN arrivals.
        for loom in chosen:
            if loom['loom'] in ('FL2','FL3','RL2','RR2'):continue
            choice,hits=complete_breakout(loom,channel)
            if choice is None:failures.append(dict(loom=loom['loom'],cause='WHOLE_BREAKOUT_BLOCKED',witnesses=hits));continue
            for wid,p in choice:
                breakouts[wid]=p;channel.insert(dict(wire=wid+'/breakout',OD_mm=2,segments=p))
        # Never turn a blocked endpoint into thousands of futile A* states.
        if not failures:
            work=[]
            for loom in chosen:
                if loom['loom'] in ('FL2','FL3','RL2','RR2'):continue
                capacity=usable_blank(loom['loom'])-14-loom['initial_land_mm']-loom['fixed_bundle_guide_mm']-21
                for v in loom['cores'].values():
                    wid=v['wire'];fixedlen=sum(p['length_mm'] for p in prefixes[wid]+breakouts[wid])
                    work.append((capacity-fixedlen,wid,10))
            work.extend((850-14.05-21-sum(p['length_mm'] for p in prefixes[w]+breakouts[w]),w,10) for w in ('W002','W003'))
            for wid,reference in (('W007',bridges),('W025',ground)):
                whole=reference['routes'][wid]['parts']
                routes[wid]=dict(parts=whole,guide_mm=sum(v['length_mm'] for v in whole),project_R_mm=21 if wid=='W025' else 10,
                    retained_qualified_route=True)
            for budget,wid,radius in sorted(work):
                p,states=search(channel,breakouts[wid][-1]['end'],prefixes[wid][-1]['end'],budget,0,
                    (wid+'/receiver',wid+'/breakout'),max_states=600)
                total_states+=states
                if p is None:failures.append(dict(wire=wid,cause='BOUNDED_SHARED_MIDDLE_BLOCKED',states=states));break
                whole=breakouts[wid]+p+reverse_parts(prefixes[wid])
                routes[wid]=dict(parts=whole,guide_mm=sum(v['length_mm'] for v in whole),project_R_mm=radius)
                channel.insert(dict(wire=wid,OD_mm=2,segments=whole))
                print('Coupled route',wid,'states',states,flush=True)
    else:failures.append(dict(loom='FL3',cause='NO_WHOLE_FL_ZONE_WITH_COMPLETE_FAN_AND_CAPACITY'))
    factory_assignment={}
    if not failures:
        assert len(chosen)==12 and len(routes)==40
        for loom in chosen:
            length=max(14+loom['initial_land_mm']+loom['fixed_bundle_guide_mm']+routes[v['wire']]['guide_mm']+21
                for v in loom['cores'].values())
            assert length<=usable_blank(loom['loom'])+1e-7
            long=length>850
            factory_assignment[loom['loom']]=dict(component='SPMA3007' if long else 'SR-Cable-5264-3PIN-900mm-6PCS',
                nominal_mm=1219.2 if long else 900,trim_reserve_mm=50,maximum_three_core_requirement_mm=length,
                allowance_after_reserve_mm=(1169.2 if long else 850)-length,installed_quantity=1,selected=False)
    mutual=only_new_pairs([], [dict(wire=n,OD_mm=4.2 if n=='W025' else 2,segments=sampling_parts(r['parts'])) for n,r in routes.items()])
    failures.extend(dict(cause='COMPLETE_STATIC_CORES_INTERSECT',**q) for q in mutual if q['status']=='REJECT_PLANNING_PROXIMITY')
    result=dict(status='REJECTED_COUPLED_FL_BUS_PLAN' if failures else 'COUPLED_FL_BUS_PLANNING_ONLY',
        candidate_FL3=candidate,rear_receiving_changes=rear_changes,retained_families_reference='leg-body-joins-plan.json',rails=relocation['rails'],
        body_ends_reference='leg-terminations-plan.json',retained_original_rail_locations=True,
        minimum_direct_down_join_z_mm=minimum_down_join_z,
        factory_alternative=dict(SKU='SPMA3007',allocation_scope='All12 length ceilings; assign900mm only after all3 actual core guides fit850mm',nominal_mm=1219.2,trim_reserve_mm=50,
            installed_quantity=None,extra_inline_connections=0,selected=False,E3_complete=False),
        factory_assignment=factory_assignment,complete_static_core_near_pairs=mutual,
        invalidated_wire_ids=list(CHANGED),all36_leg_fanouts_invalidated=True,
        routes=routes,endpoint_failures=failures,trial_rejections=dict(reject_counts),direct_down_fan_rejections=fan_failures,trials=trials,
        search_states=total_states,source_prefixes=bus['source_prefixes'],FL_motion_witnesses=fl_witnesses,
        selected=False,W5_complete=False,physical_pass=False,native_changed=False,
        limitations=['Shared sampled path planning, not real-material or continuous-motion qualification',
            'All36 full fanouts, both BUS cores, bridge and R21 ground must be complete before native changes',
            'New rail supports, independent insulation grips, lever/tool access and whole stock remain OPEN'],
        worker_seconds=time.monotonic()-tick,
        source_sha256={p.relative_to(ROOT).as_posix():SHA(p) for p in pins})
    (OUT/'fl-bus-group-plan.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:result[k] for k in ('status','endpoint_failures','trial_rejections','trials','search_states','worker_seconds')}),flush=True)
    return result


if __name__=='__main__':run()
