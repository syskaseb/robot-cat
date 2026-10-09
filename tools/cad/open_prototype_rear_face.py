"""One shared source/receiver topology: separate rings, north-facing rear bus.

All four rear arrivals change together, including both MTA factory inputs.
No washer stacks, guessed connector hardware or native model writes.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, math, time, sys
import open_prototype_source_bypass as G

B=G.B;ROOT=G.ROOT;OUT=G.OUT
ORDERED_COLUMNS='--ordered-columns' in sys.argv
JOINT_ENTRIES='--joint-entries' in sys.argv or ORDERED_COLUMNS
STEM='source-rear-ordered-columns' if ORDERED_COLUMNS else 'source-rear-joint-entries' if JOINT_ENTRIES else 'source-rear-face'
PLAN=OUT/(STEM+'-plan.json');PROOF=OUT/(STEM+'-space.json')
REUSE_PROOF=None

def parts(route):
    return [dict(kind=s['kind'],start=s['start_mm'],end=s['end_mm'],
        **(dict(mid=s['mid_mm']) if s['kind']=='arc' else {})) for s in route.row['segments']]

def build_geometry(joint_entries=False,ordered_columns=False):
    joint_entries=joint_entries or ordered_columns
    p=G.build_geometry(bus_undercross=True,allocated_ports=True)
    # Stop bending adjacent metal barrels into one another. The front goes
    # WEST; the rear keeps its original NORTH orientation. This requires the
    # complete rear WAGO family to accept SOUTH arrivals rather than UP.
    for r in p['s1_module']['rings']:
        if r['terminal'] not in (3,6):continue
        r['direction']=B.WEST if r['terminal']==3 else B.NORTH
        r['ring_rotation_z_deg']=0 if r['terminal']==3 else 90
        r['barrel_mm']=B.add(r['eye_mm'],B.mul(r['direction'],22.123))
    case=next(s for s in p['stations'] if s['role']=='P_REAR')
    target_y=24.123 if joint_entries else 34.123
    case.update(centre_mm=[68.8,target_y-11,138],size_mm=[37,22,11],rotation='identity/NORTH entry')
    for i in range(1,6):
        port=p['ports'][f'P_REAR.{i}']
        port.update(point_mm=[68.8+(i-3)*6.5,target_y,138],departure=B.NORTH[:])
    remap={'P_REAR.4':'P_REAR.5','P_REAR.5':'P_REAR.4'}
    if joint_entries:
        # Allocate all entries together: shortened MTA north runs no longer
        # pass through the AUX outlet. The AUX vertical hairpin occupies the
        # gap between those inputs, with its NORTH-side arrival on slot4.
        remap={'P_REAR.4':'P_REAR.5','P_REAR.5':'P_REAR.3','P_REAR.3':'P_REAR.4'}
    if ordered_columns:
        # Left-to-right arrival columns: AUX, NC, RL, RR, S1. Move RR
        # laterally below the receiving bus, not across S1 at its entry Z.
        # Both MTA routes turn UP then SOUTH in their own column.
        remap={'P_REAR.1':'P_REAR.3','P_REAR.3':'P_REAR.1'}
    p['permutation']={k:remap.get(v,v) for k,v in p['permutation'].items()}
    for e in p['body_ends']:
        e['current_role']=remap.get(e['current_role'],e['current_role'])
        e['datum']=p['ports'].get(e['current_role'])
    for row in p['s1_routes']:
        if row['wire'] not in ('W064','W065'):continue
        ring=next(r for r in p['s1_module']['rings'] if r['terminal']==row['terminal'])
        target=remap.get(row['target'],row['target']);end=p['ports'][target]['point_mm']
        r=G.Route(row['wire'],ring['barrel_mm'],ring['direction'],4.2,25.2,28.452,[])
        lands=[]
        def land(n,label):
            a=r.p[:];r.line(n);lands.append(dict(label=label,start_mm=a,end_mm=r.p[:]))
        land(9,'S1 upstream insulation')
        if row['wire']=='W064':
            r.shift([0,9,0],25.2)
            G.short_line(r,r.p[0]-54.2)
            r.turn(B.UP,25.2)
            land(105.8-r.p[2],'Front vertical insulation')
            r.turn(B.WEST,25.2);r.shift([0,12,0],25.2)
            land(r.p[0]-end[0],'P_FRONT incoming insulation')
            r.finish(end,B.WEST)
        else:
            r.turn(B.UP,25.2)
            land(end[2]-25.2-r.p[2],'Rear vertical insulation outside bank X extent')
            r.turn(B.WEST,25.2)
            if r.p[0]-(end[0]+25.2)>1e-7:G.short_line(r,r.p[0]-(end[0]+25.2))
            r.turn(B.SOUTH,25.2)
            land(r.p[1]-end[1],'P_REAR incoming insulation')
            r.finish(end,B.SOUTH)
        seg=parts(r);length=B.check_path(seg,ring['barrel_mm'],end,25.2)
        row.update(target=target,segments=seg,barrel_mm=ring['barrel_mm'],barrel_direction=ring['direction'],
            centreline_mm=length,nominal_fit_blank_mm=math.ceil(length+28.452),insulation_grip_lands=lands)
    # Both MTA input wires have identical macro paths and equal lengths.
    # The short 1/2 mm internal lands are NOT restraint seats.
    for row in p['tails']:
        if row['wire'] not in ('W044','W052'):continue
        target=remap.get(row['target'],row['target'])
        end=p['ports'][target]['point_mm'];start=row['segments'][0]['start']
        r=G.Route(row['wire'],start,B.NORTH,4,6,14,[])
        if ordered_columns:
            if row['wire']=='W052':
                r.line(9);r.shift([end[0]-r.p[0],0,0],10)
            G.short_line(r,target_y+2-r.p[1]) if row['wire']=='W052' else r.line(target_y+2-r.p[1])
            r.turn(B.UP,6);r.line(9);r.turn(B.SOUTH,6)
        else:
            r.line(target_y+2-start[1]);r.turn(B.UP,6);r.line(9);r.turn(B.WEST,6)
            G.short_line(r,r.p[0]-(end[0]+6));r.turn(B.SOUTH,6)
        G.short_line(r,r.p[1]-end[1]);r.finish(end,B.SOUTH)
        seg=parts(r);length=B.check_path(seg,start,end,6)
        assert length+14<=row['assumed_factory_limit_mm']
        grip_segments=[s for s in seg if s['kind']=='line' and B.segment_geometry(s)[0]>=9-1e-7]
        row.update(target=target,segments=seg,centreline_mm=length,required_blank_mm=length+14,
            independent_grip_lands=[dict(start_mm=s['start'],end_mm=s['end']) for s in grip_segments],short_entry_is_not_grip=True)
    h=next(h for h in p['holders'] if h['role']=='F_AUX')
    h['input_target']=remap.get(h['input_target'],h['input_target'])
    end=p['ports'][h['input_target']]['point_mm']
    r=G.Route('F_AUX/input',h['input_mm'],B.EAST,4,6,11,[])
    if ordered_columns:
        r.line(9);r.turn(B.UP,6);r.line(132-r.p[2]);r.turn(B.WEST,6)
        r.line(r.p[0]-(end[0]+6));r.turn(B.SOUTH,6)
    elif joint_entries:
        r.line(end[0]+6-h['input_mm'][0]);r.turn(B.SOUTH,6);r.turn(B.UP,6)
        r.line(132-r.p[2]);r.turn(B.WEST,6);r.turn(B.SOUTH,6)
    else:
        r.line(15);r.turn(B.UP,6);r.line(132-r.p[2]);r.turn(B.WEST,6)
        G.short_line(r,r.p[0]-(end[0]+6));r.turn(B.SOUTH,6)
    G.short_line(r,r.p[1]-end[1]);r.finish(end,B.SOUTH)
    seg=parts(r);length=B.check_path(seg,h['input_mm'],end,6)
    assert length+11<=h['factory_minimum_mm']
    h.update(input_segments=seg,input_blank_mm=length+11,
        input_grip_lands=[dict(start_mm=s['start'],end_mm=s['end']) for s in seg if s['kind']=='line' and B.segment_geometry(s)[0]>=9-1e-7],short_entry_is_not_grip=True)
    p.update(changed_case_names=['P_REAR'],changed_path_names=['W064','W065','W067','W068','W044','W052','F_AUX/input'],
        source_topology='Separated original NORTH rear ring and WEST front ring; complete NORTH-face rear receiving family',
        invalidated=['S1 native mount and source grips','P_REAR native retention and all four receiving grips',
            'W066 approach to reallocated P_SYS.5; other remaining wires and stock OPEN'],selected=False,stage_completed=False)
    return p

def build():
    q=B.read(PLAN)
    for n,h in q['source_sha256'].items():assert B.sha(ROOT/n)==h,n
    return q['family']

def main():
    assert not PLAN.exists(),'Do not repeat unchanged geometry'
    tick=time.monotonic();p=build_geometry(JOINT_ENTRIES,ORDERED_COLUMNS);screen=G.S.F.F.proximity(p)
    bad=[r for r in screen['near_pairs'] if r['status']=='REJECT_PLANNING_PROXIMITY']
    files=[Path(__file__),Path(G.__file__),Path(G.T.__file__),Path(G.S.__file__),G.T.PLAN,
        OUT/'obstacle-map-current.json',OUT/'endpoint-plan.json']
    q=dict(family=p,geometry_digest=G.T.R.geometry_digest(p),mutual_preflight=screen,known_mutual_conflicts=bad,
        status='REJECTED_MUTUAL_PREFLIGHT' if bad else 'SHARED_REAR_FACE_REQUIRES_MATERIAL_GATE',
        source_sha256={f.relative_to(ROOT).as_posix():B.sha(f) for f in files},
        worker_seconds=round(time.monotonic()-tick,6),finished_utc=datetime.now(timezone.utc).isoformat(),
        selected=False,stage_completed=False,physical_pass=False)
    PLAN.write_text(json.dumps(q,separators=(',',':'))+'\n',encoding='utf-8')
    print(json.dumps({k:q[k] for k in ('status','known_mutual_conflicts','worker_seconds')}),flush=True)

if __name__=='__main__':main()
