"""Allocate all four source continuations together, not independent offsets.

The qualified factory interface is retained. Functional free wire loops may
rise above the omitted cosmetic shell; this is NOT a closed160mm shell fit.
Complete output, leg/body/local wiring and all native restraints stay open.
"""
import json,math,time
from pathlib import Path
from plan_current_mta_interfaces import ROOT,BASE,OUT,R,add,mul,line,shift,quarter,curve,SHA
E,W,N,S,U,D=[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]
def straight(q,p):
    a=q[-1]['end']
    if math.dist(a,p)>1e-7:q.append(line(a,p))
def turn(q,a,b):q.append(quarter(q[-1]['end'],a,b))
def offset(q,u,v,d):q.extend(shift(q[-1]['end'],u,v,d))
def reverse(q):return [dict(p,start=p['end'],end=p['start']) for p in reversed(q)]
def entry(p,u,length=9):return [line(p,add(p,mul(u,length)))]

def rear_approach(y,degrees,top,land=9):
    # A shared diagonal rise bypasses the occupied low E2 fuse-band alley.
    # Both quarter-arcs retain R25.2; no relaxed bend or case cutout.
    p=entry([29,y,138],E,land)
    if degrees is None:
        turn(p,E,U)
    else:
        # Clear the fixed fuse band, then return to a vertical column.
        # This short rotation is a full-radius arc, not a corner or S-offset
        # extended into the adjacent source column.
        a=math.radians(degrees);v=[0,math.sin(a),math.cos(a)]
        turn(p,E,v);start=p[-1]['end'];normal=[0,-math.cos(a),math.sin(a)]
        def at(t):return add(add(start,mul(v,R*math.sin(t))),mul(normal,R*(1-math.cos(t))))
        p.append(curve(start,at(a),at(a/2),R,a))
    straight(p,[p[-1]['end'][0],p[-1]['end'][1],top-R])
    turn(p,U,W);return p
def finish(q,p):
    assert math.dist(q[-1]['end'],p[-1]['end'])<1e-6,(q[-1],p[-1])
    q.extend(reverse(p));return q
def plan():
    m=json.loads((OUT/'mta-interface-plan.json').read_text())
    gate=json.loads((OUT/'mta-interface-checks.json').read_text())
    assert m['allocation_revision']==6 and not gate['contacts'] and not gate['errors']
    assert gate['source_sha256'][(OUT/'mta-interface-plan.json').relative_to(ROOT).as_posix()]==SHA(OUT/'mta-interface-plan.json')
    j={r['id'].removesuffix('_Joint'):r for r in m['joints']}
    routes={}
    # One explicit new P_FRONT placement, all five ports reserved together.
    # A same-rail module relocation invalidates its old supports/approaches.
    pf=dict(casing_mm=[-61,21.5,145.9,-39,58.5,156.9],
            centre_mm=[-50,40,151.4],entry_axis=W,
            ports={str(i):[-61,40+(3-i)*6.5,151.4] for i in range(1,6)},
            roles={'1':'W064 S1.3','2':'W041 FL input','3':'W042 FR input','4':'NC','5':'NC'},
            native_support='OPEN_REPLACES_UNSELECTED_OLD_P_FRONT_SUPPORT')
    # Front inputs use separate side-by-side upper lanes, then independent
    # vertical drops outside the retained AUX ground/tail crossings.
    p=entry(pf['ports']['2'],W);turn(p,W,U)
    straight(p,[p[-1]['end'][0],46.5,185.6]);turn(p,U,E)
    q=entry(j['W041']['custom_entry_mm'],S,3)
    turn(q,S,U);straight(q,[36.7,-17.4,185.6]);turn(q,U,W)
    turn(q,W,N)
    straight(q,[q[-1]['end'][0],46.5-R,210.8]);turn(q,N,W)
    straight(q,p[-1]['end']);routes['W041_CUSTOM']=finish(q,p)
    q=entry(j['W042']['custom_entry_mm'],E)
    v=[0,.68,math.sqrt(1-.68**2)]
    # Complete the rising diagonal before returning WEST; it transfers
    # above AUX without another vertical column crossing the rear source.
    turn(q,E,v)
    extra=(201.8-151.4-2*R*v[2])/v[2]
    straight(q,add(q[-1]['end'],mul(v,extra)));turn(q,v,W)
    top=q[-1]['end'][2]
    turn(q,W,N)
    straight(q,[q[-1]['end'][0],40-R,top]);turn(q,N,W)
    p=entry(pf['ports']['3'],W);turn(p,W,U)
    straight(p,[p[-1]['end'][0],40,top-R]);turn(p,U,E)
    straight(q,p[-1]['end']);routes['W042_CUSTOM']=finish(q,p)
    # Both P_REAR ends include their complete9mm insulated end land. The
    # lower approach is ABOVE the E2 floor and BELOW the whole F_AUX case.
    p=rear_approach(0,math.degrees(math.asin(.08)),225,3)
    end=p[-1]['end'];q=entry(j['W044']['custom_entry_mm'],W)
    turn(q,W,U);straight(q,[q[-1]['end'][0],80.5,225-R]);turn(q,U,W)
    straight(q,[-40.4,80.5,225]);turn(q,W,S)
    straight(q,[q[-1]['end'][0],end[1]+R,225]);turn(q,S,E)
    straight(q,end);routes['W044_CUSTOM']=finish(q,p)
    p=rear_approach(6.5,None,247,2.5)
    end=p[-1]['end'];q=entry(j['W052']['custom_entry_mm'],W)
    turn(q,W,U);straight(q,[q[-1]['end'][0],-80.5,247-R]);turn(q,U,W)
    if -30.1>end[1]:offset(q,W,S,-30.1-end[1])
    straight(q,[-40.4,q[-1]['end'][1],247]);turn(q,W,N)
    straight(q,[q[-1]['end'][0],end[1]-R,247]);turn(q,N,E)
    straight(q,end);routes['W052_CUSTOM']=finish(q,p)
    for n,q in routes.items():
        assert all(math.dist(a['end'],b['start'])<1e-6 for a,b in zip(q,q[1:])),n
        assert math.dist(q[0]['start'],j[n.removesuffix('_CUSTOM')]['custom_entry_mm'])<1e-6,n
        assert q[0]['length_mm']>=(3 if n=='W041_CUSTOM' else 9) and q[-1]['length_mm']>=(3 if n=='W044_CUSTOM' else 2.5 if n=='W052_CUSTOM' else 9),n
    return dict(status='SHARED_FOUR_SOURCE_CONTINUATION_PLAN_ONLY',selected=False,
        W5_complete=False,physical_pass=False,P_FRONT=pf,
        candidate_port_remap={'W044':{'historical':'P_REAR.2','candidate':'P_REAR.3'},
                              'W052':{'historical':'P_REAR.3','candidate':'P_REAR.2'},
                              'net':'UNCHANGED_BAT_SW_SAME_RAIL',
                              'selected':False,'owner_plan_binding':'PENDING_WHOLE_W5_SELECTION'},
        grip_design={'W041_CUSTOM':{'connector_straight_mm':3,'independent_grip_straight_mm':9,
            'grip_location':'Vertical straight after first bend, NOT connector lever/casing',
            'reason':'9mm grip land is not a manufacturer-required fixed9mm departure; retain full strip11 inside opposed connector.',
            'native_grip':'OPEN'},
          'W052_CUSTOM':{'rail_straight_mm':3,'independent_grip_straight_mm':9,
            'grip_location':'Vertical straight after full return bend; native grip OPEN',
            'reason':'Place independent9mm grip downstream; northern P_REAR port leaves before southern vertical column.'}},
        routes={n:dict(parts=q,radius_mm=2.1,sku='HELU23802',
                      nominal_guide_mm=sum(p['length_mm'] for p in q),
                      nominal_end_strip_mm=[11,14],actual_cut_mm=None) for n,q in routes.items()},
        assumptions=['HELU23802 OD4.2/R25.2 retained project assumption, not measured delivered cable',
          'Loose functional upper loops above omitted cosmetic shell; no closed160shell fit or native loop support claim. New bank retention and support frame remain OPEN.',
          'P_FRONT relocation is unselected; all ports/retention/access must be qualified with whole remaining W5',
          'Current lower end approach floor/case nominal clearances must pass actual solid check, not bbox inference'],
        open=['All four output continuations','All other body/local/leg looms and current bank retention',
              'Native independent wire relief, loop stability, service parking','Complete cut/trim/stock reconciliation'],
        source_sha256={p.relative_to(ROOT).as_posix():SHA(p) for p in
            [Path(__file__),OUT/'mta-interface-plan.json',OUT/'mta-interface-checks.json',
             ROOT/'hardware/reference/parent-fuse-extensions-2026-10-03/facts.json']})
def run():
    tick=time.monotonic();p=plan();p['planning_seconds']=time.monotonic()-tick
    (OUT/'main-source-plan.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':p['status'],'nominal_guides_mm':{n:round(v['nominal_guide_mm'],3) for n,v in p['routes'].items()},'selected':False}))
if __name__=='__main__':run()
