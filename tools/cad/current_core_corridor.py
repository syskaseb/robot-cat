"""Current-frame curvature planner, snapshot of the qualified grid algorithm.

Only source tangent dispatch differs from historical UP-only implementation.
No world datum falsification; callers must provide received real fan geometry.
"""
import heapq,itertools,math,time
import numpy as np
from plan_body_fanout_layout import AXES,reverse_part,part_points
from plan_current_moving_looms import add,mul,metrics,exact_quarter
from plan_current_mta_interfaces import line


def corridor(scene,row,backward=False):
    """One bounded tangent/curvature grid, then a checked final spatial span."""
    assert tuple(row.get('source_free_axis',row['bodyward_bundle_tangent'])) in AXES,'Expected actual cardinal source tangent'
    receiving=row.get('receiving_parts',[row['receiving_land']])
    source=row.get('source_parts',[row['source_land']])
    if backward:
        start=np.asarray(row['free_end']);end=np.asarray(row['free_start'])
        initial=[reverse_part(p) for p in reversed(receiving)]
        final_parts=[reverse_part(p) for p in reversed(source)]
        first_axis=AXES.index(tuple(row['receiver_outward_axis']))
        end_axis=row.get('source_free_axis',row['bodyward_bundle_tangent'])
    else:
        start=np.asarray(row['free_start']);end=np.asarray(row['free_end'])
        initial=source;final_parts=receiving
        first_axis=AXES.index(tuple(row.get('source_free_axis',row['bodyward_bundle_tangent'])));end_axis=row['receiver_outward_axis']
    fixed=sum(p['length_mm'] for p in source)+sum(p['length_mm'] for p in receiving)
    capacity=row['capacity_before_terminal_mm']-row['terminal_allowance_project_mm']-fixed
    first=(0,0,0,first_axis);queue=[(float(np.linalg.norm(end-start)),0,0,first)]
    best={first:0};parents={};serial=itertools.count(1);tick=time.monotonic();states=0
    while queue and states<1000 and time.monotonic()-tick<120:
        _,cost,_,state=heapq.heappop(queue)
        if cost!=best.get(state):continue
        states+=1;p=(start+10*np.asarray(state[:3])).tolist();u=AXES[state[3]]
        distance=math.dist(p,end)
        if cost>0 and distance+cost<capacity:
            handles=[max(12,min(65,distance/3)),18,38]
            for h,b in ((handles[0],handles[0]),(18,38),(38,18),(38,38)):
                poles=[p,add(p,mul(u,h)),add(end.tolist(),mul(end_axis,b)),end.tolist()]
                length,radius,_=metrics(poles,24)
                if radius<10.5 or length+cost>capacity:continue
                final=dict(kind='bezier',start=p,end=end.tolist(),poles_mm=poles,length_mm=length)
                pts=part_points(final)
                if not scene.clear(pts,row):continue
                length,radius,_=metrics(poles,400)
                if radius<10 or length+cost>capacity:continue
                final['length_mm']=length
                middle=[final];key=state
                while key!=first:
                    key,part=parents[key];middle.append(part)
                middle=list(reversed(middle[1:]))+[final]
                whole=[*initial,*middle,*final_parts]
                if backward:whole=[reverse_part(p) for p in reversed(whole)]
                points=np.concatenate([part_points(part) for part in whole])
                assert all(math.dist(a['end'],b['start'])<1e-6 for a,b in zip(whole,whole[1:]))
                along=np.r_[0,np.cumsum(np.linalg.norm(np.diff(points,axis=0),axis=1))]
                remote=np.abs(along[:,None]-along[None,:])>4
                distance=np.sum((points[:,None,:]-points[None,:,:])**2,axis=2)
                if np.any(distance[remote]<2.1**2):continue
                if not scene.clear(points,row):continue
                guide=sum(q['length_mm'] for q in whole)
                return dict(parts=whole,guide_mm=guide,spare_before_trim_mm=capacity+fixed-guide,
                            minimum_sampled_R_mm=min(10,radius),search_direction='receiver_to_source' if backward else 'source_to_receiver',
                            search_states=states,search_seconds=round(time.monotonic()-tick,3)),points
        for index,v in enumerate(AXES):
            if index==state[3]:part=line(p,add(p,mul(u,10)))
            elif sum(a*b for a,b in zip(u,v))==0:part=exact_quarter(p,u,v,10)
            else:continue
            nxt=tuple(round((part['end'][j]-start[j])/10) for j in range(3))+(index,)
            new_cost=cost+part['length_mm'];distance=math.dist(part['end'],end)
            if new_cost+distance>capacity or new_cost>=best.get(nxt,float('inf')):continue
            if not scene.clear(part_points(part),row):continue
            best[nxt]=new_cost;parents[nxt]=(state,part)
            heapq.heappush(queue,(new_cost+distance,new_cost,next(serial),nxt))
    return dict(error='BOUNDED_CURVATURE_CORRIDOR_EXHAUSTED_NOT_GEOMETRIC_IMPOSSIBILITY',
                search_states=states,search_seconds=round(time.monotonic()-tick,3)),None
