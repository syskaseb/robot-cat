"""Bounded common free-channel routing, not successive manual wire nudges.

All receiver departures, all twelve moving envelopes and all retained wire
references enter one grid. Curved R10 moves avoid these references before
material CAD. This is only a sampled planning proposal, never material PASS.
"""
import heapq,itertools,json,math,time
from pathlib import Path
from plan_current_joined_leg_looms import (ROOT,OUT,SHA,UP,DOWN,R,add,mul,sub,
    norm,bridge,leave_port,reverse_parts,exact_quarter)
from plan_current_mta_interfaces import line
from screen_current_remaining_routes import route_rows
from screen_current_moving_looms import pose_row,only_new_pairs
from plan_current_moving_looms import poles,metrics,curve_length
from open_prototype_path_preflight import samples

AXES=((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))

def sampling_parts(parts):
    """Expand exact compact curve recipes ONLY while sampling, not on disk."""
    result=[]
    for q in parts:
        if q['kind']=='bezier':
            p=q['poles_mm']
            result.extend(pose_row(dict(loom='sample'),dict(start=p[0],flex_start=p[0],spans_mm=[p]))['segments'])
        else:result.append(q)
    return result

class Space:
    def __init__(self):self.grid={};self.cell=6
    def insert(self,row):
        for i,p in samples(sampling_parts(row['segments'])):
            key=tuple(math.floor(x/self.cell) for x in p)
            self.grid.setdefault(key,[]).append((p,row['OD_mm']/2,row['wire']))
    def clear(self,parts,ignore=(),margin=.7,root=None):
        walked=0
        for i,p in samples(sampling_parts(parts),step=1):
            key=tuple(math.floor(x/self.cell) for x in p)
            for d in itertools.product((-1,0,1),repeat=3):
                for q,r,name in self.grid.get(tuple(x+y for x,y in zip(key,d)),()):
                    if name in ignore:continue
                    if root and name==root[0] and i==0 and math.dist(p,parts[0]['start'])<=5 and math.dist(q,root[1])<=5:continue
                    bound=r+1+margin
                    if sum((x-y)**2 for x,y in zip(p,q))<bound*bound:return False
        return True

def search(space,start,target,budget,extra,ignore,max_states=2400):
    """Bounded search over exact R10 quarter turns and10mm straight lands.

    Last connection uses an exact UP/roof/DOWN arch with length compensation.
    Search is bounded once per complete conductor; no CAD variants are emitted.
    """
    def completion_cost(point,u):
        # Rank the actual required UP/arch/DOWN completion rather than
        # Euclidean distance, which wrongly attracts search below the roof.
        cost=0
        if u!=AXES[4]:
            if u==AXES[5]:return math.dist(point,target)+extra+4*R
            turn=exact_quarter(point,u,UP,R);point=turn['end'];cost=turn['length_mm']
        q=bridge(point,target,DOWN,extra_length=extra)
        return cost+sum(p['length_mm'] for p in q) if q else math.dist(point,target)+extra+4*R
    count=itertools.count();origin=tuple(start);first=(0,0,0,4)
    queue=[(completion_cost(start,AXES[4]),0,next(count),first)];best={first:0};parents={}
    expansions=0
    while queue and expansions<max_states:
        _,cost,_,state=heapq.heappop(queue)
        if cost!=best.get(state):continue
        expansions+=1
        point=[origin[j]+10*state[j] for j in range(3)];u=AXES[state[3]]
        if state[3]!=5 and math.dist(point,target)<budget-cost:
            end=bridge(point,target,DOWN,extra_length=extra) if state[3]==4 else None
            if end and cost+sum(q['length_mm'] for q in end)<=budget and space.clear(end,ignore):
                end[0]['planning_goal_count']=len(end)
                end[0]['planning_roof_extra_mm']=extra
                pieces=[];s=state
                while s!=first:
                    previous,part=parents[s];pieces.append(part);s=previous
                return list(reversed(pieces))+end,expansions
            # A horizontal free-channel departure need not turn UP again
            # merely to use the old roof bridge. Preserve both tangents with
            # one curvature-screened spatial curve; store its true poles and
            # length, while chords are only the cheap sampling representation.
            if state[3]<4:
                for h,b in ((30,30),(50,30),(30,50),(50,50),(80,30),(30,80),(80,50),(50,80)):
                    bez=poles(point,list(u),target,UP,h,b)
                    length,radius,_=metrics(bez,40)
                    if radius<10 or cost+length>budget:continue
                    end=[dict(kind='bezier',start=point,end=target,poles_mm=bez,length_mm=length,
                              project_sampled_min_R_mm=radius,planning_goal_count=1)]
                    if not space.clear(end,ignore):continue
                    pieces=[];s=state
                    while s!=first:
                        previous,part=parents[s];pieces.append(part);s=previous
                    return list(reversed(pieces))+end,expansions
        for k,v in enumerate(AXES):
            if k==state[3]:
                part=line(point,add(point,mul(u,10)))
            elif sum(x*y for x,y in zip(u,v))==0:
                part=exact_quarter(point,u,v,R)
            else:continue
            p=part['end']
            if not (-240<=p[0]<=300 and -250<=p[1]<=250 and -90<=p[2]<=290):continue
            new_cost=cost+part['length_mm'];heuristic=math.dist(p,target)
            if new_cost+heuristic>budget:continue
            nxt=tuple(round((p[j]-origin[j])/10) for j in range(3))+(k,)
            if new_cost>=best.get(nxt,float('inf')):continue
            if not space.clear([part],ignore):continue
            best[nxt]=new_cost;parents[nxt]=(state,part)
            heapq.heappush(queue,(new_cost+completion_cost(p,v),new_cost,next(count),nxt))
    return None,expansions

def run():
    tick=time.monotonic();f=OUT/'joined-leg-looms-plan.json';basis=json.loads(f.read_text())
    assert basis['status']=='JOINED_12_LOOMS_36_FANOUTS_LENGTH_ONLY'
    for n,h in basis['source_sha256'].items():assert SHA(ROOT/n)==h,n
    ef=OUT/'leg-terminations-plan.json';ends={q['wire']:q for q in json.loads(ef.read_text())['wires']}
    fixed,pins=route_rows(tuple(OUT/(t+'-plan.json') for t in ('ground-tree','data-bridges','positive-source','s0-in-extension')))
    hf=OUT/'head-wire-screen-reference.json';heads=json.loads(hf.read_text())
    for n,h in heads['source_sha256'].items():assert SHA(ROOT/n)==h,n
    old=list(fixed.values())+heads['rows'];bundles=[]
    for loom in basis['looms']:
        nominal=next(v for v in loom['poses'] if not any(v['angles']))
        bundles.append(pose_row(loom,nominal))
    space=Space()
    for row in old+bundles:space.insert(row)
    routes={};bad=[];prefixes={};total_states=0
    # Receiver V uses the INSIDE gallery; the outside gallery already carries
    # all12bank INPUT wires. Those distinct electrical roles must not overlap.
    for loom in basis['looms']:
        for name,fan in loom['fanouts'].items():
            q=ends[name];side=1 if q['body_point_mm'][1]>0 else -1
            direction=[0,side*(-1 if fan['core']=='V' else 1),0]
            parts=leave_port(q['body_point_mm'],q['body_departure_axis'],direction)
            prefixes[name]=parts
            if not space.clear(parts,margin=0):bad.append(dict(wire=name,cause='RECEIVER_DEPARTURE_OCCUPIED'))
    for name,parts in prefixes.items():space.insert(dict(wire=name+'/receiver',OD_mm=2,segments=parts))
    # Choose the direction of EACH WHOLE3core breakout against all other
    # references. Rotation is provisional conductor arrangement, not pinout.
    breakouts={}
    for loom in basis['looms']:
        join=loom['body_dock_mm'];choice=None
        for rotation in (30,90,150,210,270,330):
            rows=[];okay=True
            for name,fan in loom['fanouts'].items():
                angle=math.radians(rotation+{'D':0,'G':120,'V':240}[fan['core']]);radial=[math.cos(angle),math.sin(angle),0]
                start=add(join,mul(radial,1.2));parts=leave_port(start,UP,radial,land=5)
                if not space.clear(parts,margin=0,root=('Loom/'+loom['loom'],join)):okay=False;break
                rows.append(dict(wire=name+'/breakout',OD_mm=2,segments=parts))
            if okay and not any(q['status']=='REJECT_PLANNING_PROXIMITY' for q in only_new_pairs([],rows)):
                choice=rows;break
        if choice is None:bad.append(dict(loom=loom['loom'],cause='WHOLE3CORE_BREAKOUT_OCCUPIED'));continue
        for row in choice:
            name=row['wire'].split('/')[0];breakouts[name]=row['segments'];space.insert(row)
    # Do not search around a known blocked endpoint.
    if not bad:
        candidates=[]
        for loom in basis['looms']:
            nominal=next(v for v in loom['poses'] if not any(v['angles']))
            for name,fan in loom['fanouts'].items():
                # The nominal fanout ALREADY stores max-minus-nominal flex
                # slack. Subtract nominal here, not maximum a second time.
                capacity=850-14-loom['initial_land_mm']-nominal['flex_length_mm']-21
                a=breakouts[name][-1]['end'];b=prefixes[name][-1]['end']
                extra=loom['maximum_bundle_section_mm']-nominal['flex_length_mm']+10
                fixed_length=sum(q['length_mm'] for q in breakouts[name]+prefixes[name])
                candidates.append((capacity-fixed_length-math.dist(a,b),name,loom,capacity,fixed_length,extra))
        # Most constrained complete cables first, not their source-file order.
        for _,name,loom,capacity,fixed_length,extra in sorted(candidates,key=lambda q:q[:2]):
            start=breakouts[name][-1]['end'];target=prefixes[name][-1]['end']
            ignore=(name+'/receiver',name+'/breakout')
            parts,states=search(space,start,target,capacity-fixed_length,extra,ignore)
            total_states+=states
            if parts is None:
                bad.append(dict(wire=name,cause='NO_BOUNDED_FREE_CHANNEL',states=states));break
            whole=breakouts[name]+parts+reverse_parts(prefixes[name])
            length=sum(q['length_mm'] for q in whole)
            routes[name]=dict(parts=whole,radius_mm=1,guide_mm=length,loom=loom['loom'],
                search_states=states,remaining_mm=capacity-length,actual_cut_mm=None,
                guide_basis='Exact lines/arcs and adaptive Bezier length, NOT sum of sampling chords')
            space.insert(dict(wire=name,OD_mm=2,segments=whole))
            print('Common route',name,'states',states,'remaining',round(capacity-length,2),flush=True)
    result=dict(status='REJECTED_COMMON_FANOUT_CHANNEL_PLAN' if bad else 'COMMON_FANOUT_NOMINAL_CHANNELS_ONLY',
        routes=routes,rejected=bad,breakouts=breakouts,receiving_prefixes=prefixes,
        search_states=total_states,worker_seconds=time.monotonic()-tick,
        selected=False,W5_complete=False,physical_pass=False,motion_length_compensation_verified=False,
        scope='Bounded common free-channel proposal only. Real material, all sampled motions, independent grips/native/service/stock OPEN. No own conductor or bought part excluded.',
        source_sha256={q.relative_to(ROOT).as_posix():SHA(q) for q in pins|{f,ef,hf,Path(__file__),ROOT/'tools/cad/plan_current_joined_leg_looms.py',ROOT/'tools/cad/screen_current_moving_looms.py'}})
    (OUT/'leg-fanout-channels-plan.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:result[k] for k in ('status','rejected','search_states','worker_seconds')}),flush=True)
    return result

if __name__=='__main__':run()
