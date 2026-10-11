"""Both switched S1 outputs together, retaining the qualified MTA sources.

The two P_SYS inputs are not guessed; those remain a coupled receiving/fuse
station task. Old920mm is a historical four-wire subtotal, not new stock.
"""
import json,math,time
from pathlib import Path
from plan_current_main_sources import ROOT,BASE,OUT,R,E,W,N,S,U,D,entry,turn,straight,offset,finish,SHA,add,mul,curve

def current_ring(wid,ep,pose):
    r=next(r for r in ep['body_conductors'] if r['id']==wid)
    e=next(e for e in r['ends'] if e['role'].startswith('S1.'))
    a=math.radians(pose['yaw_deg']);cs,sn=math.cos(a),math.sin(a)
    pivot=[126.2,55.5,85];x,y,z=[v-p for v,p in zip(e['point_mm'],pivot)]
    centre=pose['centre_mm'];point=[centre[0]+cs*x-sn*y,centre[1]+sn*x+cs*y,centre[2]+z]
    dx,dy,dz=e['departure'];axis=[cs*dx-sn*dy,sn*dx+cs*dy,dz]
    return dict(role=e['role'],point_mm=point,departure=axis,native=e['native'],
                source_frame='Current CP2 S1 centre/yaw applied once to old ring barrel end; not a new supplier pin')

def plan():
    source=OUT/'main-source-plan.json';gate=OUT/'main-source-checks.json'
    p=json.loads(source.read_text());g=json.loads(gate.read_text())
    assert not g['contacts'] and not g['errors'] and g['source_sha256'][source.relative_to(ROOT).as_posix()]==SHA(source)
    allocation=BASE/'wiring-checkpoint/source-group-allocation.json'
    epfile=BASE/'wiring-checkpoint/endpoint-plan.json'
    pose=json.loads(allocation.read_text())['source_pose_allocation'];ep=json.loads(epfile.read_text())
    assert pose['yaw_deg']==-90 and pose['centre_mm']==[146.2,35.5,105],pose
    rings={wid:current_ring(wid,ep,pose) for wid in ('W064','W065')}
    assert math.dist(rings['W064']['departure'],N)<1e-8 and math.dist(rings['W065']['departure'],S)<1e-8
    routes={};top=215.2
    # North output exits beyond the complete RL casing before rising.
    ring=rings['W064']['point_mm'];tail=entry(ring,N,6)
    turn(tail,N,U);straight(tail,[ring[0],tail[-1]['end'][1],top-R]);turn(tail,U,W)
    q=entry(p['P_FRONT']['ports']['1'],W);turn(q,W,U)
    straight(q,[q[-1]['end'][0],q[-1]['end'][1],top-R]);turn(q,U,E)
    offset(q,E,N,tail[-1]['end'][1]-q[-1]['end'][1]);straight(q,tail[-1]['end'])
    routes['W064']=finish(q,tail)
    # Fifth P_REAR cavity leaves SOUTH below the retained AUX station;
    # S1.6 approaches from the opposite end, outside the tail bearing.
    ring=rings['W065']['point_mm'];tail=entry(ring,S)
    turn(tail,S,E);turn(tail,E,U)
    straight(tail,[tail[-1]['end'][0],tail[-1]['end'][1],top-R]);turn(tail,U,W)
    # Rise immediately out of the low E2 band alley. The previous horizontal
    # SOUTH turn crossed two tie heads and XB33; do not preserve that alley.
    q=entry([29,-13,138],E,2.5);v=[0,-.14,math.sqrt(1-.14**2)]
    turn(q,E,v);a=math.asin(.14);start=q[-1]['end'];normal=[0,math.sqrt(1-.14**2),.14]
    def at(t):return add(add(start,mul(v,R*math.sin(t))),mul(normal,R*(1-math.cos(t))))
    q.append(curve(start,at(a),at(a/2),R,a))
    straight(q,[q[-1]['end'][0],q[-1]['end'][1],top-R]);turn(q,U,E)
    delta=tail[-1]['end'][1]-q[-1]['end'][1]
    offset(q,E,N if delta>0 else S,abs(delta));straight(q,tail[-1]['end'])
    routes['W065']=finish(q,tail)
    for n,q in routes.items():
        assert all(math.dist(a['end'],b['start'])<1e-6 for a,b in zip(q,q[1:])),n
        assert math.dist(q[-1]['end'],rings[n]['point_mm'])<1e-6,n
    return dict(status='TWO_S1_OUTPUTS_SHARED_PLAN_ONLY',selected=False,W5_complete=False,
        physical_pass=False,rings=rings,P_FRONT=p['P_FRONT'],P_REAR5=[29,-13,138],
        allocation_revision=3,rejected_first_cause='W065 horizontal SOUTH rail alley crosses retained E2 tie heads/XP03 and W4 XB33; immediate full-radius rising fan replaces complete rail approach, no case cut or unchanged retry',
        rejected_second_cause='Both route families obstructed directly outside P_REAR.5 by two locking heads on SOUTH sides of complete E2 bands. Third attempt changes whole restraint-head architecture: locking heads on TOP of unchanged continuous bands, not another unchanged station-route trial.',
        changed_e2_heads={'TieHead_Input':[32.25,-8.9,140.25,36.75,-4.1,143.75],
                          'TieHead_Fuse1':[43.75,-8.9,142.4,48.25,-4.1,145.9]},
        changed_head_basis='Same nominal T18I4.5x4.8x3.5 locking-head allowance rotated to top of closed band. Native pose/delivered forming/tool fit OPEN. Band and E2 PETG passages unchanged; actual changed contacts with ALL retained curves required.',
        routes={n:dict(parts=q,radius_mm=2.1,sku='HELU23802',
                      nominal_guide_mm=sum(x['length_mm'] for x in q),rail_strip_mm=14,
                      ring_barrel_allowance_mm=14.452,actual_crimp_strip_mm=None,actual_cut_mm=None) for n,q in routes.items()},
        retained=['MTA6 four bodies/eightfactory ends','Qualified four complete MAIN input continuations','W1/W2/W3/W4/E2 fixed material and wiring'],
        open=['Two P_SYS input feedsW067/W068 and complete receiving/F_PI/source group',
              'All native independent grips, installed tool/removal access, old920mm full subtotal/stock',
              'Actual supplied TE crimp strip and factory wire identification'],
        source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in [Path(__file__),source,gate,allocation,epfile]})

def run():
    tick=time.monotonic();p=plan();p['planning_seconds']=time.monotonic()-tick
    (OUT/'s1-output-plan.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':p['status'],'guide_mm':{n:r['nominal_guide_mm'] for n,r in p['routes'].items()},'selected':False}))
if __name__=='__main__':run()
