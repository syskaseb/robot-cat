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
CHANGED=('W020','W004','W019','W031','W008','W030','W022','W069','W071')

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

def packed_front_prefixes(rows):
    """Concentric corners transport the measured triangular core packing.

    Translating the same W->N arc made radial spacing collapse at its exit.
    Common circle centres preserve the packing instead of trial offsets.
    """
    result={}
    for names in (('W004','W019','W020'),('W008','W030','W031')):
        common_x=min(rows[n]['free_start'][0] for n in names)-10
        common_y=max(rows[n]['free_start'][1] for n in names)+10
        common_z=max(rows[n]['free_start'][2] for n in names)+10
        for name in names:
            r=rows[name];p=copy.deepcopy(r['source_parts']);a=p[-1]['end']
            straight_to(p,[common_x,a[1],a[2]])
            if r['loom']=='FL1':
                radius=common_y-a[1];p.append(exact_quarter(p[-1]['end'],W,N,radius))
                p.append(exact_quarter(p[-1]['end'],N,U,common_z-a[2]))
            else:p.append(exact_quarter(p[-1]['end'],W,U,common_z-a[2]))
            result[name]=p
    return result

def spatial_half_return(parts,end,forward,minimum_radius=10):
    """Two real quarter-arcs and a straight bridge in the required 3D plane."""
    a=parts[-1]['end'];delta=np.asarray(end)-a;u=np.asarray(forward,float)
    axial=float(np.dot(delta,u));v=delta-axial*u;span=float(np.linalg.norm(v))
    assert span>=2*minimum_radius,('half_return_span',span)
    v=(v/span).tolist();reverse=(-u).tolist()
    if axial>0:straight_to(parts,(np.asarray(a)+axial*u).tolist())
    parts.append(exact_quarter(parts[-1]['end'],forward,v,minimum_radius))
    if span>2*minimum_radius+1e-7:
        straight_to(parts,(np.asarray(parts[-1]['end'])+(span-2*minimum_radius)*np.asarray(v)).tolist())
    parts.append(exact_quarter(parts[-1]['end'],v,reverse,minimum_radius))
    if axial<0:straight_to(parts,end)
    assert math.dist(parts[-1]['end'],end)<1e-6

def plan(rows):
    rows=copy.deepcopy(rows);result={};failures={};front=packed_front_prefixes(rows)
    for name in CHANGED:
        r=rows[name];p=copy.deepcopy(r.get('source_parts',[r['source_land']]))
        if name in ('W004','W019','W020','W008','W030','W031'):
            p=front[name]
            side=N if r['loom']=='FL1' else S
            if name in ('W020','W031'):rise(p,r['free_end'][2]-30)
            elif name in ('W004','W008'):
                voltage=rows['W020' if side==N else 'W031']
                rise(p,voltage['free_end'][2]-20);p.append(exact_quarter(p[-1]['end'],U,side,10))
            else:
                # Cross above, not through, the retained receiving U-return.
                rise(p,r['free_end'][2]+10);p.append(exact_quarter(p[-1]['end'],U,side,10))
                if name=='W019':
                    end=r['free_end'];a=p[-1]['end'];straight_to(p,[a[0],end[1]+20,a[2]])
                    p.append(exact_quarter(p[-1]['end'],N,E,10));a=p[-1]['end']
                    straight_to(p,[end[0]+20,a[1],a[2]])
                    p.append(exact_quarter(p[-1]['end'],E,D,10));a=p[-1]['end']
                    straight_to(p,[a[0],a[1],end[2]+10]);p.append(exact_quarter(p[-1]['end'],D,S,10))
                    a=p[-1]['end'];straight_to(p,[a[0],end[1]+10,a[2]])
                    p.append(exact_quarter(p[-1]['end'],S,W,10));straight_to(p,end)
                    q,error=math_gate(r,[*p,*r['receiving_parts']])
                    if q:result[name]=dict(q,architecture='FL1_packed_turns_and_cardinal_return_above_own_receiver')
                    else:failures[name]=error
                    continue
            label=r['loom']+'_joint_WEST_clear_sweep_then_ordered_UP_branches'
        elif name=='W069':
            p.append(exact_quarter(p[-1]['end'],W,U,10));p.append(exact_quarter(p[-1]['end'],U,N,10))
            spatial_half_return(p,r['free_end'],N)
            q,error=math_gate(r,[*p,*r['receiving_parts']])
            if q:result[name]=dict(q,architecture='RL1_spatial_R10_half_return_not_short_cubic')
            else:failures[name]=error
            continue
        elif name=='W071':
            # Rise BEFORE reaching W051's south-turn, not after crossing it.
            p.append(exact_quarter(p[-1]['end'],U,W,10))
            p.append(exact_quarter(p[-1]['end'],W,U,10));p.append(exact_quarter(p[-1]['end'],U,N,10))
            spatial_half_return(p,r['free_end'],N)
            q,error=math_gate(r,[*p,*r['receiving_parts']])
            if q:result[name]=dict(q,architecture='RL3_early_rise_and_spatial_R10_half_return')
            else:failures[name]=error
            continue
        else:
            end=r['free_end'];entry=[end[0]+10,end[1]+10,end[2]]
            r['receiving_parts']=[exact_quarter(entry,S,W,10),*r['receiving_parts']]
            r['receiving_grip_part_index']+=1;r['free_end']=entry;r['receiver_outward_axis']=N
            a=p[-1]['end'];straight_to(p,[a[0],a[1],a[2]+10]);p.append(exact_quarter(p[-1]['end'],U,S,10))
            label='FL2_north_GPIO_exit_without_replacing_E1_grip'
        candidate,error=finish(r,p,label)
        if candidate:result[name]=candidate
        else:failures[name]=error
    return rows,result,failures
