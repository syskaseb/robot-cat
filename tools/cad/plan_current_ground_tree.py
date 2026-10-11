"""Five complete fixed ground trunks, one simultaneous shared-lane proposal.

Use the selected4mm2 TKD minimum fixed R21; motion looms are separate.
No old end is accepted by proximity, and no cable cut/native is selected.
"""
import json,math,time
from pathlib import Path
from plan_current_main_sources import ROOT,OUT,U,D,E,W,N,S,entry,straight,finish,curve,add,mul,SHA,reverse
from plan_current_main_pi_wiring import turn
from open_prototype_source_group import check_path
R=21
GY,GZ=-54,169
G1_PORT={'W060':1,'W001':2,'W036':3,'W025':5,'W061':4}
def gx(wid):return -53+6.5*(G1_PORT[wid]-1)

def bend(q,u,v):turn(q,u,v,R)
def transfer(q,u,v,d,r=R):
    if d>=2*r:
        turn(q,u,v,r);straight(q,add(q[-1]['end'],mul(v,d-2*r)));turn(q,v,u,r);return
    a=q[-1]['end'];angle=math.acos(1-d/(2*r));sn,cs=math.sin(angle),math.cos(angle)
    b=add(add(a,mul(u,r*sn)),mul(v,r*(1-cs)));c=add(add(b,mul(u,r*sn)),mul(v,r*(1-cs)))
    mid1=add(add(a,mul(u,r*math.sin(angle/2))),mul(v,r*(1-math.cos(angle/2))))
    mid2=add(add(b,mul(u,r*(sn-math.sin(angle/2)))),mul(v,r*(math.cos(angle/2)-cs)))
    q.extend((curve(a,b,mid1,r,angle),curve(b,c,mid2,r,angle)))

def north_tail(x,top,out):
    # Common vertical fan, NOT the rejected shared north-facing stair at
    # Z161/Y14 across XA03/XA05. Five columns stay on their mouth pitch.
    q=entry([x,GY,GZ],U)
    straight(q,[x,GY,top-R]);bend(q,U,out);return q

def paired_east_tail(wid,top,out):
    # Both eastward mouths go UNDER the retained XB11 atZ185 as one
    # concentric pair. Their second bends restore two vertical columns
    # with6.5mm spacing;9mm grips lie on these columns, not at the mouth.
    q=entry([gx(wid),GY,GZ],U,3)
    turn(q,U,E,21 if wid=='W025' else 27.5)
    turn(q,E,U,27.5 if wid=='W025' else 21)
    straight(q,[q[-1]['end'][0],GY,top-R]);bend(q,U,out);return q

def front_arch():
    # The former FR receiving row sat beneath opposing MTA joints. Move
    # the WHOLE unselected rail/factory-loom boundary toY-88: its vertical
    # exit now clears both the jointY-84.55 and output-wireY-96 corridors.
    q=entry([-10.5,-88,79.5],U);straight(q,[-10.5,-88,180])
    tail=entry([gx('W036'),GY,GZ],U,3);bend(tail,U,S);bend(tail,S,U)
    a=q[-1]['end'];b=tail[-1]['end'];delta=[b[0]-a[0],b[1]-a[1],0]
    span=math.sqrt(sum(x*x for x in delta));v=[x/span for x in delta]
    transfer(q,U,mul(v,-1),2*R-span)
    a=q[-1]['end'];span=2*R
    straight(q,[a[0],a[1],232])
    bend(q,U,v)
    straight(q,add(q[-1]['end'],mul(v,span-2*R)));bend(q,v,D)
    straight(q,b);return finish(q,tail)

def allocate_front_arch(routes):
    from screen_current_remaining_routes import route_rows
    from open_prototype_path_preflight import screen
    old,_=route_rows()
    for n in routes:old.pop(n,None)
    peers=[dict(wire=n,OD_mm=4.2 if n!='W001' and n!='W060' else 3.1 if n=='W001' else 2.1,segments=q)
      for n,q in routes.items() if n!='W036']
    rejected=[]
    # Bounded whole-approach capacity allocation in9mm grip-length units;
    # one final plan, no archived scalar variants or repeated CAD workers.
    for e in ('WholeFR_G_Y-88_southG1_fan',):
        q=front_arch()
        r=screen(dict(tails=list(old.values())+peers,s1_routes=[dict(wire='W036',OD_mm=4.2,segments=q)],holders=[]))
        bad=[v for v in r['near_pairs'] if v['b']=='W036' and v['status']=='REJECT_PLANNING_PROXIMITY']
        if not bad:
            routes['W036']=q
            return dict(topology=e,G1_arrival='southern double quarter; columnY-96',candidates_screened=len(rejected)+1,rejected=rejected,
              basis='Known whole retained centrelines only; actual material/motion acceptance remains pending')
        rejected.append(dict(topology=e,owners=sorted({v['a'] for v in bad})))
    raise ValueError(('No shared FR approach corridor; change whole receiving gallery',rejected))

def plan():
    f=OUT/'harness-interfaces-plan.json';registry=json.loads(f.read_text());rows={r['id']:r for r in registry['body_conductors']}
    routes={};g1=dict(casing_mm=[-58.5,GY-5.5,GZ-22,-21.5,GY+5.5,GZ],centre_mm=[-40,GY,GZ-11],
      rotation_x_degrees=90,translation_from_retention_mm=[36,GY+84.75,GZ-111.99],entry_axis=U,
      ports={str(i):[-53+6.5*(i-1),GY,GZ] for i in range(1,6)},native_mount='OPEN')
    # The OLD G1 mouth row is crossed by retained XB12/XB13/XS13 and its
    # rising columns by XB32. Allocate all five occupied mouths together in
    # an open mid-body station. No retained W1/W3/W4 wire moves; ONLY W060
    # from the partial MAIN/Pi receipt is superseded, never whole W1 credit.
    q=entry([-139.5,84,112.5],U);bend(q,U,E);bend(q,E,U)
    transfer(q,U,S,24)
    straight(q,[-97.5,60,242]);bend(q,U,E)
    tail=paired_east_tail('W025',263,N)
    straight(q,[tail[-1]['end'][0]-R,60,263]);bend(q,E,S)
    straight(q,tail[-1]['end']);routes['W025']=finish(q,tail)
    # Rise above the complete ATO144.8 envelope BEFORE turning north.
    # The previous low quarter crossed F_R2_ATO; its housing is not cut.
    # The full low E departure bypasses W042_Joint before rising; its
    # original direct column passed through that retained opposed splice.
    # Then one vertical-plane arch, not an east/north loop through S1.
    routes['W036']=front_arch()
    q=paired_east_tail('W061',257,N)
    straight(q,[q[-1]['end'][0],-24,257]);bend(q,N,E)
    # A deliberate diagonal G2 rise keeps its tall column away from BOTH
    # adjacent ground output transfers, not repeated independent offsets.
    tail=entry([101.5,34.5,155],E);angle=math.radians(20);v=[0,-math.sin(angle),math.cos(angle)]
    bend(tail,E,v);start=tail[-1]['end'];normal=[0,math.cos(angle),math.sin(angle)]
    def at(t):return add(add(start,mul(v,R*math.sin(t))),mul(normal,R*(1-math.cos(t))))
    tail.append(curve(start,at(angle),at(angle/2),R,angle))
    column_y=tail[-1]['end'][1]
    straight(tail,[131.5,column_y,236]);bend(tail,U,W)
    transfer(q,E,N,column_y-q[-1]['end'][1])
    straight(q,tail[-1]['end']);routes['W061']=finish(q,tail)
    for wid,y,land,top,end_y in [('W062',39.25,40,263,90),('W063',44,46,233,-90)]:
        q=entry([101.5,y,155],E,land);bend(q,E,U)
        x=q[-1]['end'][0]
        if wid=='W062':
            transfer(q,U,N,end_y-y);straight(q,[x,end_y,top-R]);bend(q,U,W)
        else:straight(q,[x,y,top-R]);bend(q,U,S)
        # Whole rear D/G receiving gallery moves above and OUTSIDE the
        # preserved populated decks. A vertical feed to the old below-deck
        # central mouths crossed both PCBs and the structural carrier.
        # Fan from the rear mouth first; its full R21 return stays outside.
        tail=entry([109.75,end_y,79.5],U);straight(tail,[109.75,end_y,top-R]);bend(tail,U,E)
        # The complete loop uses an eastward offset before returning west.
        # Route via a shared high Y lane, not through the old S1 arch.
        if wid=='W063':straight(q,[x,end_y+R,top]);bend(q,S,W)
        straight(q,tail[-1]['end']);routes[wid]=finish(q,tail)
    # Reuse the already-clear lower MAIN/GND approach. Only the new G1
    # departure and high bridge replace its former prefix.
    oldmain=json.loads((OUT/'main-pi-plan.json').read_text());old=oldmain['routes']['W060']['parts']
    q=entry([gx('W060'),GY,GZ],U);turn(q,U,W,11.1);turn(q,W,D,11.1)
    x=q[-1]['end'][0];straight(q,[x,GY,76.2948]);turn(q,D,N,11.1)
    straight(q,[x,-24,65.1948]);turn(q,N,E,11.1)
    # Preserve the original MAIN pad approach; cross the S0 south tangent
    # outside its full circle, not by extending the old turn farther west.
    transfer(q,E,N,12.9-9.911,11.1)
    straight(q,old[6]['end']);q+=old[7:];routes['W060']=q
    # Source return is a whole current route; historical140mm is not a cap.
    # Native XT60 cups face EAST, as in the canonical source recipe.
    # Do not fabricate a westward exit from the housing bounding box.
    # Leave the source bay SOUTH before rising. Its former north transfer
    # traversed the live UpperCarrier, F_R1 terminal and W4 cradle/fasteners.
    # Entire source exit now stays outside those modules, no cradle cutouts.
    q=entry([-73,-58.8,57],E,3);turn(q,E,S,12.4)
    straight(q,[-57.6,-78.1,57]);turn(q,S,U,12.4)
    # Move the whole column east BELOW the MTA band, then restore its
    # G1 column above that band. The southern gap alone cannot hold a
    # column between the MTA body and its separate output cable.
    straight(q,[-57.6,-90.5,80]);transfer(q,U,E,27.6,12.4)
    straight(q,[-30,-90.5,180]);transfer(q,U,W,16.5,12.4)
    straight(q,[gx('W001'),-90.5,207.6]);turn(q,U,N,12.4)
    tail=entry([gx('W001'),GY,GZ],U);straight(tail,[gx('W001'),GY,207.6]);turn(tail,U,S,12.4)
    # Southern arch enters G1 from its own column, separate from MAIN's
    # westward bridge; both routes have complete straight insulation lands.
    straight(q,tail[-1]['end']);routes['W001']=finish(q,tail)
    fr_allocation=allocate_front_arch(routes)
    result={}
    for n,q in routes.items():
        ends=json.loads(json.dumps(rows[n]['current_ends']))
        for e in ends:
            if e['role'].startswith('G1.'):e['point_mm']=g1['ports'][str(G1_PORT[n])]
            if e['role']=='FR_G.1':e['point_mm']=[-10.5,-88,79.5]
            if e['role'] in ('RL_G.1','RR_G.1'):e['point_mm']=[109.75,90 if e['role']=='RL_G.1' else -90,79.5]
            if n=='W060' and e['role']=='MAIN.GND':e['point_mm']=oldmain['bare_pad_parts']['W060'][-1]['end']
        try:
            start=next(e for e in ends if math.dist(e['point_mm'],q[0]['start'])<1e-5)
            end=next(e for e in ends if math.dist(e['point_mm'],q[-1]['end'])<1e-5)
        except StopIteration:raise ValueError((n,q[0]['start'],q[-1]['end'],[(e['role'],e['point_mm']) for e in ends]))
        radius=12.4 if n=='W001' else 11.1 if n=='W060' else R
        try:check_path(q,min_radius=radius,start=start['point_mm'],end=end['point_mm'])
        except AssertionError as exc:raise AssertionError(n+': '+str(exc)) from exc
        result[n]=dict(parts=q,radius_mm=1.55 if n=='W001' else 1.05 if n=='W060' else 2.1,
          SKU='LAPP0107001 black12AWG' if n=='W001' else 'Joy-IT K-1474 retained18AWG' if n=='W060' else 'TKD2500125 black4mm2',guide_mm=sum(s['length_mm'] for s in q),
          endpoints=[start['role'],end['role']],strip_mm=[5,14] if n=='W001' else [14,3] if n=='W060' else [11,14] if n in ('W025','W036') else [14,11] if n=='W061' else [11,11],actual_cut_mm=None)
    return dict(status='WHOLE_G1_AND_GROUND_TREE_PLAN_ONLY',routes=result,G1=g1,selected=False,W5_complete=False,physical_pass=False,
      rear_ground_same_rail_mapping={'1':4,'2':1,'3':2,'4':3,'5':5},
      FR_ground_same_rail_mapping={'1':5,'2':2,'3':3,'4':4,'5':1},
      G1_same_ground_port_mapping=G1_PORT,
      front_ground_station=dict(name='FR_G',centre_mm=[-20,-88,70],casing_mm=[-35,-92.5,60.5,-5,-83.5,79.5],
        entry_axis=U,ports={str(i):[-29.5+4.75*(i-1),-88,79.5] for i in range(1,6)},native_mount='OPEN'),
      front_whole_approach_capacity=fr_allocation,
      rear_gallery={n:dict(centre_mm=[x,y,70],
        casing_mm=[x-15,y-4.5,60.5,x+15,y+4.5,79.5],entry_axis=U,
        ports={str(i):[x-9.5+4.75*(i-1),y,79.5]
          for i in range(1,6)},native_mount='OPEN')
        for n,x,y in [('RL_G',105,90),('RR_G',105,-90),('D_RL',145,80),('D_RR',145,-80)]},
      retained_MAIN_bare_parts={'W060':oldmain['bare_pad_parts']['W060']},
      fixed_R_mm=21,not_dynamic_radius=True,
      allocation='One fixed ground tree: two front returns joinG1; G1.4 feedsG2.1; G2.2/3 independently feed rear rails. Both MTA exits avoid rearG columns. FR ground whole rail moved outside its obstructed exit row. RearD remains UP; data must turn east BELOW MTA before rising. Project ports, not supplier cavity datums. Functional arches up to263mm are open-prototype space, NOT closed160mm shell fit.',
      open=['Shared retained material/wires and moving head/legs; this plan does not prove them',
        'Independent9mm insulation seats and shared native load paths, lever/tools/service',
        'All remaining source/data/branch feeders and12moving looms; final lengths/stock/E3'],
      source_sha256={q.relative_to(ROOT).as_posix():SHA(q) for q in (Path(__file__),f,OUT/'main-pi-plan.json',
        ROOT/'tools/cad/screen_current_remaining_routes.py',ROOT/'tools/cad/open_prototype_path_preflight.py')})

if __name__=='__main__':
    t=time.monotonic();p=plan();p['planning_seconds']=time.monotonic()-t
    (OUT/'ground-tree-plan.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(routes={n:round(r['guide_mm'],3) for n,r in p['routes'].items()},seconds=p['planning_seconds'])))
