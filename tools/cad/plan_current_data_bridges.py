"""Three complete DATA bridges, with early receiving fans below MTA.

Known LiY OD1.3/staticR5.2 only. Factory leg-looms remain separate unknowns.
One proposal; current retained power guides are never silently moved.
"""
import json,math,time
from pathlib import Path
from plan_current_main_sources import ROOT,BASE,OUT,U,D,E,W,N,S,entry,straight,finish,add,mul,SHA
from plan_current_main_pi_wiring import turn
from open_prototype_source_group import check_path
from screen_current_remaining_routes import route_rows
from open_prototype_path_preflight import screen
R=5.2

def rise(point,role):
    if role.startswith('D_FR'):
        # North transfer ABOVE complete ATO144.8, before the opposed
        # W052 custom fan crosses this former direct vertical column.
        q=entry(point,U);straight(q,[point[0],point[1],146]);turn(q,U,N,R)
        straight(q,add(q[-1]['end'],mul(N,6)));turn(q,N,U,R)
        return q
    side=N if role.startswith('D_RL') else S
    # Whole rear fan goes OUTWARD before rising, not east over neighboring
    # stems or up through TailLocalRail. Five mouths keep their4.75pitch.
    # Y+/-94 leaves2.5mm to the complete MTA side, inside200mm width.
    q=entry(point,U);turn(q,U,side,R)
    straight(q,add(q[-1]['end'],mul(side,3.6)));turn(q,side,U,R)
    return q

def arch(q,tail,top):
    a=q[-1]['end'];b=tail[-1]['end'];v=[b[i]-a[i] if i<2 else 0 for i in range(3)]
    span=math.sqrt(sum(x*x for x in v));assert span>=2*R
    v=[x/span for x in v]
    assert top-R>=max(a[2],b[2])
    straight(q,[a[0],a[1],top-R]);turn(q,U,v,R)
    straight(q,add(q[-1]['end'],mul(v,span-2*R)));turn(q,v,D,R)
    straight(q,b);return finish(q,tail)

def rear_bridge_departure(point):
    # Use free port5 of each common DATA rail. Depart EAST before rising:
    # Whole rear corridor is behind BOTH factory MTA exits (max x178.7),
    # not just their cases. x184.45 includes2.75 wire exclusion +3 reserve.
    # y+/-80 avoids W067's y94.823 low return; no ports1..4 stem crossover.
    q=entry(point,U);turn(q,U,E,R)
    straight(q,[178.7+2.75+3-R,point[1],q[-1]['end'][2]]);turn(q,E,U,R)
    return q

def rear_feed_departure(point):
    # Port1 is leftmost. Its complete west/south dogleg goes around the
    # fixed TailLocalRail arm x136..144 BEFORE rising past z103..115,
    # then outside the whole MTA south face y-91.5 before its z143 band.
    # Keep9mm straight in WEST departure for its independent grip. The
    # Y-98 outer channel keeps the complete upper chord outside the
    # retained RR ground column at109.75/-90 and output at124.5/-94.5.
    q=entry(point,U);turn(q,U,W,R)
    straight(q,add(q[-1]['end'],mul(W,9)));turn(q,W,S,R)
    straight(q,add(q[-1]['end'],mul(S,7.6)));turn(q,S,U,R)
    return q

def plan():
    gf=OUT/'ground-tree-plan.json';lf=OUT/'leg-stations-plan.json'
    ground=json.loads(gf.read_text());leg=json.loads(lf.read_text())
    supplier=ROOT/'hardware/electronics/full-cat/body-data-bridges-r7/interface.json'
    basis=json.loads(supplier.read_text());assert basis['nominal_OD_mm']==1.3 and basis['static_radius_mm']==R
    ports={}
    for name in ('D_FL','D_FR'):
        ports.update({name+'.'+i:p for i,p in leg['stations'][name]['ports'].items()})
    for name in ('D_RL','D_RR'):
        ports.update({name+'.'+i:p for i,p in ground['rear_gallery'][name]['ports'].items()})
    pairs={'W007':('D_FL.5','D_FR.1',198),'W011':('D_FR.5','D_RR.1',184),
      'W012':('D_RL.5','D_RR.5',170)}
    routes={}
    for n,(a,b,top) in pairs.items():
        # Every rear rail has five parallel fan lanes on its original4.75
        # pitch. Do not squeeze five unknown factory looms into two lanes.
        if n=='W012':start,tail=rear_bridge_departure(ports[a]),rear_bridge_departure(ports[b])
        else:
            start=entry(ports[a],U) if a.startswith('D_FL') else rise(ports[a],a)
            tail=rear_feed_departure(ports[b]) if n=='W011' else rise(ports[b],b)
        q=arch(start,tail,top);check_path(q,min_radius=R,start=ports[a],end=ports[b])
        routes[n]=dict(parts=q,radius_mm=.65,guide_mm=sum(s['length_mm'] for s in q),
          endpoints=[a,b],SKU='LAPP4126002S blue LiY0.25mm2',static_R_mm=R,
          strip_mm=[11,11],actual_cut_mm=None)
    rows,pins=route_rows((gf,));new=[dict(wire=n,OD_mm=1.3,segments=r['parts']) for n,r in routes.items()]
    result=screen(dict(tails=list(rows.values()),s1_routes=new,holders=[]))
    bad=[r for r in result['near_pairs'] if r['b'] in routes and r['status']=='REJECT_PLANNING_PROXIMITY']
    return dict(status='REJECTED_DATA_SHARED_PLAN' if bad else 'THREE_DATA_BRIDGES_PLAN_ACTUAL_GATE_OPEN',
      routes=routes,rejected=bad,screen_seconds=result['worker_seconds'],
      rear_fan='W011: port1 WEST9/SOUTH dogleg around TailLocalRail x136..144 before rising atX116.1/Y-98 outside MTA, ground and output columns. W012: both free port5 exits EAST before rising in shared X184.45 plane behind BOTH full factory MTA exits and W065 column; y+/-80 avoids W067 low return. Other factory-looms still OPEN.',
      physical_port_reassignment={'D_RL':{'historical_bridge_port':'1','current_bridge_port':'5','current_NC_port':'1','ports_2_3_4':'unchanged','reason':'Same DATA common rail only; free port5 gives unobstructed EAST departure behind ports1..4. No net merge or external U1 pinout claim.'}},
      front_FR_fan='UP to146/R5.2 north/N6/R5.2 up above ATO; independent9mm grip on initial rising column before MTA band',
      other_factory_looms_not_qualified=True,native_parts_changed=0,selected=False,W5_complete=False,physical_pass=False,
      source_sha256={p.relative_to(ROOT).as_posix():SHA(p) for p in pins|{Path(__file__),gf,lf,supplier}})

if __name__=='__main__':
    tick=time.monotonic();p=plan();p['planning_seconds']=time.monotonic()-tick
    (OUT/'data-bridges-plan.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=p['status'],routes={n:round(r['guide_mm'],3) for n,r in p['routes'].items()},
      rejected=p['rejected'],seconds=p['planning_seconds'])))
