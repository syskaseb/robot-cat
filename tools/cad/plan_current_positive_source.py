"""Complete canonical positive-source guides, with explicit S0 delivery gate.

No manufacturer terminal bay is invented from the nominal S0 cylinder.
The pre-fuse source remains the intact short factory lead, no added joint.
"""
import json,math,time
from pathlib import Path
from plan_current_main_sources import ROOT,BASE,OUT,U,D,E,W,N,S,entry,straight,finish,offset,add,mul,curve,SHA
from plan_current_main_pi_wiring import turn
from open_prototype_source_group import check_path
from screen_current_remaining_routes import route_rows
from open_prototype_path_preflight import screen
R=25.2

def plan():
    rows,pins=route_rows((OUT/'ground-tree-plan.json',OUT/'data-bridges-plan.json'))
    # These points come from whole_cat_interior's canonical source model,
    # not the wrongly attributed RetentionMountsAssembly register frame.
    plus=[-73,-58.8,50];f0in=[-48,-58.8,50]
    f0out=[3,-58.8,50];post1=[57,-58.8,31];post2=[63.75,-58.8,31]
    source={'W075':entry(plus,E,25)}
    q=entry(f0out,E,44);turn(q,E,D,10);straight(q,post1);source['W076_FACTORY']=q
    incoming=[-.5,math.sqrt(3)/2,0];outgoing=[math.sqrt(3)/2,.5,0]
    intip=add([-89,16,80],mul(incoming,-26.9));outtip=add([-65,16,80],mul(outgoing,26.9))
    # Keep the entire protected extension on the original y-58.8 aisle
    # until after its rise. Old y-40 transfer entered both Pi free cores
    # and the qualified XS33 path. No changes to those retained wires.
    q=entry(post2,U);turn(q,U,W,R);offset(q,W,U,14.8)
    end=q[-1]['end'];a=math.pi/3
    land=(intip[1]-end[1]-R*(1-math.cos(a)))/math.sin(a);assert land>=9
    corner=add(add(intip,mul(incoming,-land)),[R*math.sin(a),-R*(1-math.cos(a)),0])
    assert corner[0]<end[0] and abs(corner[1]-end[1])<1e-6
    straight(q,corner)
    def at(t):return add(corner,[-R*math.sin(t),R*(1-math.cos(t)),0])
    q.append(curve(corner,at(a),at(a/2),R,a));straight(q,intip);source['W076_EXTENSION']=q
    # Whole lower departure replaces the rejected upper fuse/MTA aisle.
    # Preserve30degree OUT barrel clocking, descend in its own tangent
    # plane below XS33 and the ATO band, then cross east atY97.5 before
    # rising outside BOTH the front output and the S1 source columns.
    # Allocate the entire crossing slab between frame top38.52 (+2.1
    # jacket) and lowest Pi core65.1948 (-3.15 pair exclusion): Z55.
    # The old65.2 slab ran through the Pi pair;29.6 ran through the frame.
    # Two full-radius S-arcs descend25, without entering either occupied slab.
    q=entry(outtip,outgoing,0);offset(q,outgoing,D,25);q.pop(0)
    a=math.pi/6;start=q[-1]['end']
    def at(t):return add(start,[R*(math.sin(a)-math.sin(a-t)),R*(math.cos(a-t)-math.cos(a)),0])
    q.append(curve(start,at(a),at(a/2),R,a))
    straight(q,[140-R,q[-1]['end'][1],q[-1]['end'][2]]);turn(q,E,U,R)
    offset(q,U,N,97.5-q[-1]['end'][1])
    tail=entry([45,58.8,161.4],N,3);turn(tail,N,U,R)
    start=q[-1]['end'];end=tail[-1]['end'];top=230
    assert top-R>=max(start[2],end[2]);straight(q,[start[0],start[1],top-R]);turn(q,U,W,R)
    # Stay on the shared NORTH aisle until west of the complete W062
    # ground column. Only then shift toward P_SYS.1; no diagonal shortcut
    # cutting back across its jacket envelope.
    delta=start[1]-end[1];run=math.sqrt(4*R*delta-delta*delta)
    straight(q,[end[0]+R+run,start[1],top]);offset(q,W,S,delta)
    turn(q,W,D,R)
    straight(q,end);source['W066']=finish(q,tail)
    roles={'W075':['BAT.plus','F0.in'],'W076_FACTORY':['F0.out','POST_F0.1'],
      'W076_EXTENSION':['POST_F0.2','S0.IN.barrel_tip'],'W066':['S0.OUT.barrel_tip','P_SYS.1']}
    routes={}
    for n,q in source.items():
        factory=n in ('W075','W076_FACTORY');check_path(q,min_radius=10 if factory else R)
        length=sum(v['length_mm'] for v in q);extra={'W075':5,'W076_FACTORY':11,'W076_EXTENSION':26,'W066':29}[n]
        limit={'W075':50,'W076_FACTORY':84.5}.get(n)
        if limit is not None:assert length+extra<=limit
        routes[n]=dict(parts=q,radius_mm=2.25 if factory else 2.1,guide_mm=length,
          endpoints=roles[n],termination_allowance_mm=extra,nominal_blank_mm=length+extra,
          actual_cut_mm=None,retained_limit_mm=limit,static_R_mm=10 if factory else R,
          material='Original intact F0 supplied12AWG, provisionalOD4.5/R10' if factory else 'HELU23802 red4mm2, supplierR25.2/nominalOD4.2')
    for n in routes:rows.pop(n,None)
    new=[dict(wire=n,OD_mm=2*r['radius_mm'],segments=r['parts']) for n,r in routes.items()]
    g=screen(dict(tails=list(rows.values()),s1_routes=new,holders=[]))
    bad=[r for r in g['near_pairs'] if r['b'] in routes and r['status']=='REJECT_PLANNING_PROXIMITY']
    pins.update((Path(__file__),ROOT/'tools/cad/whole_cat_interior.py',BASE/'OpenPrototypePlan.FCStd'))
    return dict(status='REJECTED_POSITIVE_SOURCE_SHARED_PLAN' if bad else 'POSITIVE_SOURCE_PLAN_S0_TERMINAL_BAY_GATE_OPEN',
      routes=routes,rejected=bad,screen_seconds=g['worker_seconds'],selected=False,W5_complete=False,physical_pass=False,
      source_frame='OpenPrototypePlan.FCStd canonical world source; old register source attribution corrected',
      S0_gate='Nominal cylinder overlaps IN stud/barrel seating: unknown actual terminal bay/insulation. Not physical metal contact proof and not a clearance waiver. M4/source acceptance remains open until actual dimensions or explicitly accepted delivery-fit adjustable interface.',
      before_F0='W075 is intact25mm guide +5mm solder allowance. No added prefuse splice.',
      after_F0='W076_FACTORY -> existing WAGO221-412 -> HELU23802 extension; both joints independently restrained; native still OPEN',
      P_SYS='Retained current NORTH face45/38.5/32/25.5/19; W066port1, W067port2, W068port3 unchanged. No invented U1 pinout.',
      source_sha256={q.relative_to(ROOT).as_posix():SHA(q) for q in pins})

if __name__=='__main__':
    tick=time.monotonic();p=plan();p['planning_seconds']=time.monotonic()-tick
    (OUT/'positive-source-plan.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=p['status'],lengths={n:round(r['nominal_blank_mm'],3) for n,r in p['routes'].items()},rejected=p['rejected'],seconds=p['planning_seconds'])))
