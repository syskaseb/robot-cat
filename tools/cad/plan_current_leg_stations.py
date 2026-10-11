"""One twelve-station plan and four complete main-output continuations.

Only planning: native retention, every small fan, leg motion and stock OPEN.
Port centres are provisional project datums, not supplier cavity measurements.
"""
import json,time,math
from pathlib import Path
from plan_current_main_sources import ROOT,BASE,OUT,R,E,W,N,S,U,D,entry,turn,straight,offset,SHA,finish,add,mul,curve
from open_prototype_source_group import check_path

def plan():
    source=OUT/'mta-interface-plan.json';p=json.loads(source.read_text())
    owners=OUT/'owner-plan.json';ep=json.loads(owners.read_text())
    joints={r['id'].removesuffix('_Joint'):r for r in p['joints']}
    stations={};ports={}
    for leg,sign in [('FL',1),('FR',-1),('RL',1),('RR',-1)]:
        front=leg.startswith('F')
        allocation=([('P',-60),('D',35),('G',-20)] if leg=='FR' else
          [('P',-60),('D',-95),('G',-130)] if front else [('P',115),('G',65),('D',110)])
        for kind,x in allocation:
            vertical=True;axis=U
            z=10 if kind=='P' else 103 if leg=='FL' else 99 if front else 20
            name='D_'+leg if kind=='D' else leg+'_'+kind
            y=sign*80 if kind=='P' else -79 if leg=='FR' else 84 if leg=='FL' else sign*15
            physical={str(i):(5 if i==1 else 1 if i==5 else i) if kind=='P' and not front else i for i in range(1,6)}
            stations[name]=dict(casing_mm=[x-15,y-4.5,z-9.5,x+15,y+4.5,z+9.5] if vertical else [x-9.5,y-15,z-4.5,x+9.5,y+15,z+4.5],
              centre_mm=[x,y,z],entry_axis=axis,SKU='WAGO221-415',native_mount='OPEN',
              logical_to_physical_common_rail_cavity=physical,
              ports={str(i):[x+(physical[str(i)]-3)*4.75,y,z+9.5] if vertical else [x+9.5,y+(i-3)*4.75,z] for i in range(1,6)})
            for i,point in stations[name]['ports'].items():ports[name+'.'+i]=dict(point_mm=point,wire=None)
    for row in ep['body_conductors']:
        for role in (row['a'],row['b']):
            if role in ports:
                assert ports[role]['wire'] is None,role
                ports[role]['wire']=row['id']
    routes={};factory_override={}
    for leg,wid in [('FL','W026'),('FR','W037')]:
        # Entire front receiving family stands north/south of the actual
        # Foundation edge with mouths UP. The WHOLE FR group is now in
        # the mid-body south bay, away from the neck/FHY/XS13. Mouths at
        # Y-79 sit outside the TE row (outermost Y-74.118). FR power port
        # X60.5 lies outside both input inline cases. P/D/G are allocated
        # together, not moved independently after a collision.
        target=stations[leg+'_P']['ports']['1'];z=target[2]
        if leg=='FL':
            # The inherited FL inline points into the moving head bay.
            # Replace its WHOLE factory exit and opposed joint. Retain the
            # MTA body/input, seven other factory exits and old source files.
            v=U
            f=entry([-32.5,80.5,151.4],W);turn(f,W,v)
            straight(f,add(f[-1]['end'],mul(v,9)))
            mouth=f[-1]['end'];custom=add(mouth,mul(v,35.5))
            corners=[add(add(mouth,[dx,0,0]),add(mul(v,y),mul([0,-1,0],dz)))
              for dx in (-4.05,4.05) for y in (0,35.5) for dz in (-4.45,4.45)]
            factory_override=dict(replaces='W026_FACTORY and W026_Joint ONLY',
              parts=f,radius_mm=2.1,guide_mm=sum(a['length_mm'] for a in f),
              usable_lead_assumption_mm=84.5,actual_delivered_cut_mm=None,
              joint=dict(id='W026_Joint',sku='WAGO221-2411',
                casing_mm=[min(a[i] for a in corners) for i in range(3)]+[max(a[i] for a in corners) for i in range(3)],
                local_casing_mm=[-4.05,0,-4.45,4.05,35.5,4.45],
                rotation_x_degrees=90,
                factory_entry_mm=mouth,custom_entry_mm=custom,custom_departure_axis=v),
              native_mount='OPEN',selected=False)
            # A vertical whole joint avoids both unchanged P_FRONT feed
            # landings and the diagonal case crossing W042 atZ201.8/Y40.
            # Its custom upper return stays north of the RR Z247 source.
            q=entry(custom,U,3);turn(q,U,E);turn(q,E,S);turn(q,S,W)
            straight(q,add(q[-1]['end'],mul(W,2.8)));turn(q,W,N)
            outside_y=94.5
            straight(q,[target[0],outside_y-R,q[-1]['end'][2]]);turn(q,N,D)
            straight(q,[target[0],outside_y,180]);offset(q,D,S,outside_y-target[1])
            straight(q,target);routes[wid+'_CUSTOM']=q
            continue
        q=entry(joints[wid]['custom_entry_mm'],W,27)
        # FL rises in its original joint lane BEFORE transferring north.
        # Transferring first pushed the entire low bend into the moving Fork.
        outer_y=-84 if leg=='FR' else q[-1]['end'][1]
        delta=outer_y-q[-1]['end'][1]
        if abs(delta)>1e-7:offset(q,W,N if delta>0 else S,abs(delta))
        turn(q,W,U);turn(q,U,E)
        # The FR descent transfers19mm south BELOW the elevated RR source
        # column. Its upper EAST run stays north of that retained column.
        approach_y=-96 if leg=='FR' else target[1]
        delta=approach_y-q[-1]['end'][1]
        if abs(delta)>1e-7:offset(q,E,N if delta>0 else S,abs(delta))
        straight(q,[target[0]-R,approach_y,q[-1]['end'][2]]);turn(q,E,D)
        if leg=='FR':
            # Descend outside the whole MTA and Foundation rim; move inward
            # only below them, not diagonally through the fuse body.
            straight(q,[target[0],approach_y,70]);offset(q,D,N,target[1]-approach_y)
        straight(q,target);routes[wid+'_CUSTOM']=q
    # Rear six mouths now UP, outside the ATO rows. No under-tail hairpin
    # or passage through an adjacent flat rail. Both take elevated corridors
    # then descend directly into their own vertical receiving mouth.
    # Complete rising diagonal stays east of W068's column; the WHOLE RL
    # transfer goes around the right-rear aisle, not across the north/source
    # columns. Its208.5 lane is below S1out215.2 and above RRout201.8.
    q=entry(joints['W045']['custom_entry_mm'],S,3)
    v=[-math.sqrt(.91),0,.3];turn(q,S,v)
    a=math.acos(.3);start=q[-1]['end'];normal=[.3,0,math.sqrt(.91)]
    def at(t):return add(add(start,mul(v,R*math.sin(t))),mul(normal,R*(1-math.cos(t))))
    q.append(curve(start,at(a),at(a/2),R,a))
    column_x=q[-1]['end'][0]
    straight(q,[column_x,q[-1]['end'][1],183.3]);turn(q,U,N)
    # Two north-wall descents intersect S1's retained ring exits. Use the
    # complete rear corner, east of MTA/RL and south of that ring corridor.
    target=stations['RL_P']['ports']['1'];descent_x=155;descent_y=70
    transfer=math.hypot(descent_x-target[0],descent_y-target[1])
    rise=math.sqrt(4*R*transfer-transfer**2)
    p=entry(target,U,80-rise-target[2])
    offset(p,U,[(descent_x-target[0])/transfer,(descent_y-target[1])/transfer,0],transfer)
    straight(p,[descent_x,descent_y,183.3]);turn(p,U,S)
    offset(q,N,E,descent_x-column_x);straight(q,p[-1]['end'])
    routes['W045_CUSTOM']=finish(q,p)
    q=entry(joints['W053']['custom_entry_mm'],N,2.5);turn(q,N,U);turn(q,U,W)
    target=stations['RR_P']['ports']['1']
    straight(q,[target[0]+R,q[-1]['end'][1],q[-1]['end'][2]]);turn(q,W,S)
    straight(q,[target[0],-95+R,q[-1]['end'][2]]);turn(q,S,D)
    straight(q,[target[0],-95,70]);offset(q,D,N,15)
    straight(q,target);routes['W053_CUSTOM']=q
    for n,q in routes.items():check_path(q,min_radius=R)
    return dict(status='TWELVE_LEG_STATIONS_AND_FOUR_OUTPUT_GUIDES_PLAN_ONLY',selected=False,
      W5_complete=False,physical_pass=False,stations=stations,ports=ports,
      factory_override=factory_override,
      routes={n:dict(parts=q,radius_mm=2.1,SKU='HELU23802',guide_mm=sum(s['length_mm'] for s in q),
        strip_mm=[11,11],actual_cut_mm=None) for n,q in routes.items()},
      access='All12cases stand with mouths UP. Rear ground/data share the CENTRAL lower galleryX65/110,Y+/-15,Z20, not side galleries occupied by P0 servo housings. Four power cases stay in outer lower gallery. Independent insulation saddles, no ties through levers. Actual lever/tool/removal/native mounts/full end fans OPEN.',
      retained='Existing current W1/E2/W2/W3/W4 and source guides; old twenty-station mounts superseded, not a clearance source.',
      allocation_reason='One lower receiving gallery: four UP-mouth power rails atZ19.5/Y+/-80 leave three5mm separated fan layers, avoiding upper U-loops crossing factory exits. Complete LAPP inputs rise continuously from low rails to DOWN-facing TE mouths. Rear common-rail logical1 uses physical5 so inputs fan away from main output. Rear D/G are central vertical banks below boards, away from side servo housings/mounts and tail bridge. Front source interfaces unchanged except FL output override. All modified cases/curves, leg motion, native underfloor load paths and Foundation passages must pass together; not selected.',
      open=['All actual current cases/curves and moving-head/leg clearance',
        'Twelve ATO inputs and outputs, ground/data fans,12factory leg looms/dynamic slack',
        'Native retention/load paths/strain relief and actual wire cut/stock ledger'],
      delivery_gates=['221-415 nominal casing and cavity pitch; actual plug/lever fit',
        '34172 factory servo loom OD/Cu/cavity order/usable length and moving bend limits unknown; do not manufacture these facts'],
      source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in (Path(__file__),source,owners)})

if __name__=='__main__':
    tick=time.monotonic();p=plan();p['planning_seconds']=time.monotonic()-tick
    (OUT/'leg-stations-plan.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(stations=len(p['stations']),ports=len(p['ports']),routes={n:r['guide_mm'] for n,r in p['routes'].items()},seconds=p['planning_seconds'])))
