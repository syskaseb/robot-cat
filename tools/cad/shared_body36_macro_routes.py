"""One joint macro architecture, not shortest sibling branch selection.

FL1 explicitly replaces all three old paths together. The other four paths
leave their previous failed corridor. Math proposes; actual material accepts.
"""
import copy, math
import numpy as np
from plan_current_moving_looms import exact_quarter, metrics
from plan_current_mta_interfaces import line
from parallel_core_candidates import tangent
from plan_body_fanout_layout import part_points

E,W,N,S,U,D=[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]
CHANGED=('W020','W004','W019','W022','W030','W069','W071')

def rise(parts,z):
    a=parts[-1]['end']; assert z>=a[2], (a,z)
    if z>a[2]+1e-7:parts.append(line(a,[a[0],a[1],z]))

def math_gate(row,parts):
    assert all(math.dist(a['end'],b['start'])<1e-6 for a,b in zip(parts,parts[1:]))
    guide=sum(p['length_mm'] for p in parts)
    spare=row['capacity_before_terminal_mm']-row['terminal_allowance_project_mm']-guide
    if spare<0:return None,dict(reason='length_budget',deficit_mm=-spare)
    pp=np.concatenate([part_points(p) for p in parts])
    along=np.r_[0,np.cumsum(np.linalg.norm(np.diff(pp,axis=0),axis=1))]
    remote=np.abs(along[:,None]-along[None,:])>4
    ds=np.sum((pp[:,None,:]-pp[None,:,:])**2,axis=2)
    if np.any(ds[remote]<2.1**2):return None,dict(reason='sampled_self_contact')
    return dict(parts=parts,guide_mm=guide,spare_before_trim_mm=spare,
                minimum_sampled_R_mm=min(p.get('radius_mm',p.get('sampled_radius_mm',float('inf'))) for p in parts)),None

def finish(row,prefix,label):
    p=prefix[-1]['end'];end=row['free_end'];u=tangent(prefix[-1]);v=row['receiver_outward_axis']
    d=math.dist(p,end);h=max(12,min(65,d/2))
    failures=[]
    # These are mathematical tangent handles, not repeated CAD offsets.
    for a,b in dict.fromkeys(((h,h),(38,38),(18,38),(38,18),(65,65))):
        poles=[p,[x+a*y for x,y in zip(p,u)],[x+b*y for x,y in zip(end,v)],end]
        length,radius,_=metrics(poles,400)
        if radius<10:failures.append(dict(reason='curvature',radius_mm=radius));continue
        branch=dict(kind='bezier',start=p,end=end,poles_mm=poles,length_mm=length,sampled_radius_mm=radius)
        q,error=math_gate(row,[*prefix,branch,*row.get('receiving_parts',[row['receiving_land']])])
        if q:return dict(q,architecture=label,branch_handles_mm=[a,b]),None
        failures.append(error)
    return None,dict(reason='no_math_branch_in_this_architecture',details=failures)

def straight_to(parts,point):
    if math.dist(parts[-1]['end'],point)>1e-7:parts.append(line(parts[-1]['end'],point))

def plan(rows):
    rows=copy.deepcopy(rows);result={};failures={}
    for name in CHANGED:
        r=rows[name];p=copy.deepcopy(r.get('source_parts',[r['source_land']]))
        if name in ('W004','W019','W020'):
            p.append(exact_quarter(p[-1]['end'],W,U,10))
            if name=='W020':rise(p,r['free_end'][2]-30)
            elif name=='W004':
                rise(p,rows['W020']['free_end'][2]-20);p.append(exact_quarter(p[-1]['end'],U,N,10))
            else:
                # A cardinal return reserves the full R10 turnaround. A short
                # cubic N->W here had R6.4 and is not another CAD candidate.
                end=r['free_end'];rise(p,end[2]-10);p.append(exact_quarter(p[-1]['end'],U,N,10))
                a=p[-1]['end'];straight_to(p,[a[0],end[1]-30,end[2]])
                p.append(exact_quarter(p[-1]['end'],N,E,10));a=p[-1]['end']
                straight_to(p,[end[0]+20,a[1],a[2]])
                p.append(exact_quarter(p[-1]['end'],E,N,10));p.append(exact_quarter(p[-1]['end'],N,W,10))
                straight_to(p,end)
                q,error=math_gate(r,[*p,*r['receiving_parts']])
                if q:result[name]=dict(q,architecture='FL1_joint_UP_then_full_R10_cardinal_return')
                else:failures[name]=error
                continue
            label='FL1_joint_UP_then_destination_ordered_branch'
        elif name=='W030':
            p.append(exact_quarter(p[-1]['end'],W,U,10));rise(p,107.5)
            label='FR1_above_retained_Frame_top95_plus_R10_and2p5'
        elif name=='W069':
            p.append(exact_quarter(p[-1]['end'],W,U,10));p.append(exact_quarter(p[-1]['end'],U,N,10))
            a=p[-1]['end'];straight_to(p,[a[0],r['free_end'][1]+20,a[2]])
            p.append(exact_quarter(p[-1]['end'],N,W,10));p.append(exact_quarter(p[-1]['end'],W,S,10))
            label='RL1_high_north_approach_not_east_branch_into_RL2'
        elif name=='W071':
            p.append(exact_quarter(p[-1]['end'],U,W,10));a=p[-1]['end'];p.append(line(a,[a[0]-20,a[1],a[2]]))
            p.append(exact_quarter(p[-1]['end'],W,U,10));p.append(exact_quarter(p[-1]['end'],U,N,10))
            label='RL3_return_above_W051_not_crossing_its_horizontal_turn'
        else:
            # Enter the unchanged grip/prefix from the SOUTH side of GPIOGrip,
            # not a cubic arriving horizontally through its long body.
            end=r['free_end'];entry=[end[0]+10,end[1]-10,end[2]]
            r['receiving_parts']=[exact_quarter(entry,N,W,10),*r['receiving_parts']]
            assert math.dist(r['receiving_parts'][0]['end'],end)<1e-6
            r['receiving_grip_part_index']+=1;r['free_end']=entry;r['receiver_outward_axis']=S
            a=p[-1]['end'];p.append(line(a,[a[0],a[1],a[2]+10]));p.append(exact_quarter(p[-1]['end'],U,S,10))
            label='FL2_south_side_receiver_entry_preserves_current9mm_grip'
        candidate,error=finish(r,p,label)
        if candidate:result[name]=candidate
        else:failures[name]=error
    return rows,result,failures
