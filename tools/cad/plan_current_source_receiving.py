"""Whole five-port receiving station, both S1 inputs and both PI fuse exits.

The historical source family is used as a recipe, never as current clearance.
All current roles stay explicit. S0/MAIN continuations and native grips OPEN.
"""
import json,math,time
from pathlib import Path
from plan_current_s1_outputs import current_ring
from plan_current_main_sources import ROOT,BASE,OUT,R,E,W,N,S,U,entry,turn,straight,offset,finish,SHA,add,mul,curve

def plan():
    af=BASE/'wiring-checkpoint/source-group-allocation.json';ep=BASE/'wiring-checkpoint/endpoint-plan.json'
    pose=json.loads(af.read_text())['source_pose_allocation'];ends=json.loads(ep.read_text())
    rings={n:current_ring(n,ends,pose) for n in ('W067','W068')}
    ps=dict(centre_mm=[32,47.8,161.4],casing_mm=[13.5,36.8,155.9,50.5,58.8,166.9],entry_axis=N,
            ports={str(i):[32-(i-3)*6.5,58.8,161.4] for i in range(1,6)},
            roles={'1':'W066 S0.out','2':'W067 S1.2','3':'W068 S1.5','4':'NC','5':'W043 F_PI.in'},
            native_mount='OPEN_UNSELECTED_REPLACEMENT')
    routes={}
    ring=rings['W067']['point_mm'];top=239.6;tail=entry(ring,N,6)
    # Upper north ring rises EAST of the lower output's overhead run,
    # not through it. Both complete ring departures are allocated together.
    turn(tail,N,E);turn(tail,E,U)
    straight(tail,[tail[-1]['end'][0],tail[-1]['end'][1],top-R]);turn(tail,U,W)
    q=entry(ps['ports']['2'],N,3);turn(q,N,U)
    straight(q,[q[-1]['end'][0],q[-1]['end'][1],top-R]);turn(q,U,S)
    straight(q,[q[-1]['end'][0],q[-1]['end'][1]-9,top]);turn(q,S,E);turn(q,E,N)
    straight(q,[q[-1]['end'][0],tail[-1]['end'][1]-R,top]);turn(q,N,E)
    straight(q,tail[-1]['end']);routes['W067']=finish(q,tail)
    # Rise between the E2 sidewall and tail BEFORE entering the tail's X
    # span. A diagonal full-radius bend and tangent return to UP replace
    # the rejected low horizontal run alongside the tail.
    ring=rings['W068']['point_mm'];top=234.8;tail=entry(ring,S,3)
    vx=.3;vz=math.sqrt(1-vx*vx);v=[vx,0,vz];turn(tail,S,v);a=math.asin(vx);start=tail[-1]['end'];normal=[-vz,0,vx]
    def at(t):return add(add(start,mul(v,R*math.sin(t))),mul(normal,R*(1-math.cos(t))))
    tail.append(curve(start,at(a),at(a/2),R,a))
    straight(tail,[tail[-1]['end'][0],tail[-1]['end'][1],top-R]);turn(tail,U,W)
    q=entry(ps['ports']['3'],N,3);turn(q,N,U)
    straight(q,[q[-1]['end'][0],q[-1]['end'][1],top-R]);turn(q,U,S)
    straight(q,[q[-1]['end'][0],tail[-1]['end'][1]+R,top]);turn(q,S,E)
    delta=tail[-1]['end'][1]-q[-1]['end'][1]
    if abs(delta)>1e-7:offset(q,E,N if delta>0 else S,abs(delta))
    straight(q,tail[-1]['end'])
    routes['W068']=finish(q,tail)
    # Two complete families failed: the old central bay intersects W4/E2,
    # the south horizontal bay occupies the actual ATO inserts/MTA joints.
    # Use a NORTH OUTBOARD vertical fuse bay, outside the retained carrier
    # edge and between the F_HP and rear MTA families. Both exits included.
    from plan_current_mta_interfaces import line
    ip=[line([19,85.5,148.9],[19,85.5,155.4])]
    k=math.sqrt(.5)
    ip.append(curve([19,85.5,155.4],[19,79.5,161.4],[19,85.5-6*(1-k),155.4+6*k],6,math.pi/2))
    ip.append(line([19,79.5,161.4],ps['ports']['5']))
    op=[line([19,85.5,97.9],[19,85.5,94.9])]
    op.append(curve([19,85.5,94.9],[25,85.5,88.9],[19+6*(1-k),85.5,94.9-6*k],6,math.pi/2))
    op.append(line([25,85.5,88.9],[43,85.5,88.9]))
    assert math.dist(ip[-1]['end'],ps['ports']['5'])<1e-6
    # 221-615 specifies12..14mm. Use12 here, not a fictitious shorter lead
    # or relaxed prefuse limit. Other rail strips remain their chosen14mm.
    pi_strip=12;blank=sum(a['length_mm'] for a in ip)+pi_strip;assert blank<=50
    result=dict(status='SOURCE_RECEIVING_SHARED_PLAN_ONLY',selected=False,W5_complete=False,physical_pass=False,
        allocation_revision=7,rejected_first_cause='Historical low vertical F_PI/P_SYS family collides with actual current E2/W1/W4.',
        rejected_second_cause='Horizontal south bay collides with actual ATO inserts and RR MTA joint. Change whole bay/axis/load-path: north outboard standing fuse outside carrierY54, no ATO row or MTA volume removed.',
        rejected_third_cause='North outboard cases clear, but SOUTH entry sent whole source curves through ATO row and approached F_PI rail from its interior. Rail now NORTH-facing ABOVE ATOs; both input bends/head grips allocated together. S1 upper south feed turns EAST before E2 sidewall, then rises beyond existing MTA/tail/whole operator outerX198.7.',
        rejected_fourth_cause='North Y97.2 columns cross qualified W064 overhead and RL source rise. Allocate receiving rail, all roles, fuse and approach together: rail mouthY58.8 creates columnsY87 before the RL lane; fuse uses far-west fifth port rather than crossing RL factory lead.',
        rejected_fifth_cause='Receiving case and lower entries occupy the FL factory arc atZ151.4. Whole rail now ABOVE factory band, fuse below it and its fifth-port approach west of retained RL rise. Functional rail top166.9 is above omitted160 cosmetic shell; not a closed-shell fit.',
        independent_grip_design='W067/W068 rail departures3mm;9mm grips downstream on straight upper runs, not connector levers. F_PI input UP6.5/quarterR6/SOUTH20.7 +12strip=48.6248mm;9mm grip on horizontal approach. Entire fuse lies north of TE maxY74.1181 and below factory insulation minZ149.3. Minimum nominal case margins0.382/0.4mm require unpowered fit; native whole load path OPEN.',
        P_SYS=ps,rings=rings,F_PI=dict(casing_mm=[8.875,74.5,97.9,29.125,96.5,148.9],
            input_mm=ip[0]['start'],output_mm=op[0]['start'],input_port='P_SYS.5',
            input_factory_blank_mm=blank,input_source_limit_mm=50,
            output_sleeve_mm=[29,83.1,86.5,49,87.9,91.3],
            output_factory_tip_mm=[43,85.5,88.9],output_custom_tip_mm=[35,85.5,88.9],
            output_custom_insulation_start_mm=[43,85.5,88.9],
            output_custom_entry_mm=[58,85.5,88.9],output_overlap_mm=8,
            output_sleeve_SKU='RNF-100-3/16-0-STK',output_sleeve_blank_mm=20,
            output_joint_basis='Retained MAIN positive opposed8mm16/18AWG solder lap,20mm RNF sleeve,6mm coverage both sides; actual fit/thermal/pull gate after delivery. Full custom continuation/native grips OPEN.',native_mount='OPEN'),
        routes={n:dict(parts=q,radius_mm=2.1,sku='HELU23802',guide_mm=sum(a['length_mm'] for a in q),rail_strip_mm=14,
            ring_barrel_allowance_mm=14.452,actual_crimp_strip_mm=None,actual_cut_mm=None) for n,q in routes.items()},
        factory_routes={'W043':dict(parts=ip,radius_mm=2,rail_strip_mm=pi_strip),
                        'W077_PREFIX':dict(parts=op,radius_mm=2,prefix_only=True)},
        source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in (Path(__file__),af,ep)},
        open=['Actual all-current material/mutual clearance','Full W066/S0 and W077/W078 MAIN continuation, F0/battery and ground feeds',
              'Native grips/retention/lever access, all remaining W5 and whole stock'],
        fit_gates=['Receiving entries are envelope-derived nominal project datums, not manufacturer cavities.',
          'F_PI50mm is retained project prefuse limit, not relaxed to supplied84.5mm.',
          'Supplied crimp strip/OD/assembly and unpowered fit remain phase2.'])
    for n,r in result['routes'].items():
        assert math.dist(r['parts'][-1]['end'],rings[n]['point_mm'])<1e-6
        assert all(math.dist(a['end'],b['start'])<1e-6 for a,b in zip(r['parts'],r['parts'][1:]))
    return result

if __name__=='__main__':
    tick=time.monotonic();p=plan();p['planning_seconds']=time.monotonic()-tick
    (OUT/'source-receiving-plan.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':p['status'],'guides_mm':{n:r['guide_mm'] for n,r in p['routes'].items()},'prefuse_blank_mm':p['F_PI']['input_factory_blank_mm']}))
