"""One whole four-feed topology around the bank, not another case offset.

Preserve current receiving modules and both MTA exits. Two same-potential
SYS receiving ports are reassigned before routes are built. No native writes.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, math, time, sys
import open_prototype_rl_tail_group as T
import open_prototype_s1_shared_routes as S
from whole_cat_source_bay_plan import Route

B=T.B;ROOT=T.ROOT;OUT=T.OUT
LAYER_SEPARATED='--layer-separated' in sys.argv
ALLOCATED_PORTS='--allocated-ports' in sys.argv
BUS_UNDERCROSS='--bus-undercross' in sys.argv or ALLOCATED_PORTS
STEM='source-allocated-ports' if ALLOCATED_PORTS else 'source-bus-undercross' if BUS_UNDERCROSS else 'source-layer-separated' if LAYER_SEPARATED else 'source-bank-bypass'
PLAN=OUT/(STEM+'-plan.json')
PROOF=OUT/(STEM+'-space.json')
REUSE_PROOF=None

def short_line(r, length):
    assert length>0
    end=B.add(r.p,B.mul(r.u,length))
    r.row['segments'].append(dict(kind='line',start_mm=r.p,end_mm=end,
        tangent=r.u,length_mm=length))
    r.p=end

def build_geometry(layer_separated=False,bus_undercross=False,allocated_ports=False):
    p=T.build()
    # F_PI remains on SYS.1. W066 is still unqualified and moves to SYS.5.
    # Both four-mm2 switched feeds use the west slots; NC remains exactly one.
    remap={'P_SYS.4':'P_SYS.2','P_SYS.5':'P_SYS.3',
           'P_SYS.2':'P_SYS.5','P_SYS.3':'P_SYS.4'}
    if allocated_ports:
        # Slot2's curved approach crosses the retained F_PI/input, despite
        # the end itself being free. Use the next two same-potential slots;
        # the input fuse stays on1, W066 on5 and the one NC moves to2.
        remap={'P_SYS.4':'P_SYS.3','P_SYS.5':'P_SYS.4',
               'P_SYS.2':'P_SYS.5','P_SYS.3':'P_SYS.2'}
    p['permutation']={k:remap.get(v,v) for k,v in p['permutation'].items()}
    for e in p['body_ends']:
        e['current_role']=remap.get(e['current_role'],e['current_role'])
        e['datum']=p['ports'].get(e['current_role'])
    assert len({e['current_role'] for e in p['body_ends'] if e['current_role'].startswith('P_SYS.')})==4
    spec=p['s1_module'];plane=68.25;dz=plane-85
    spec['translation_mm']=B.add(spec['translation_mm'],[0,0,dz])
    for r in spec['rings']:
        r['eye_mm']=B.add(r['eye_mm'],[0,0,dz])
        angle=45 if r['terminal']==3 else 50 if r['terminal']==6 else 0
        direction=[-math.sin(math.radians(angle)),math.cos(math.radians(angle)),0] if angle else B.SOUTH
        if bus_undercross and r['terminal']==2:
            direction=[-math.sin(math.radians(15)),-math.cos(math.radians(15)),0]
            angle=-15
        r.update(direction=direction,barrel_mm=B.add(r['eye_mm'],B.mul(direction,22.123)),
            ring_rotation_z_deg=r['ring_rotation_z_deg']+angle)
    spec.update(body_bounds_mm=[114.2,-21,plane+4,138.2,21,plane+41],
                operator_bounds_mm=[112.2,-14,plane+41,140.2,14,plane+75])
    rows=[]
    for wire,terminal,target in S.source_specs(p):
        ring=next(r for r in spec['rings'] if r['terminal']==terminal)
        end=p['ports'][target]['point_mm'];arrival=B.mul(p['ports'][target]['departure'],-1)
        r=Route(wire,ring['barrel_mm'],ring['direction'],4.2,25.2,28.452,[])
        grips=[]
        def land(n,label):
            a=r.p[:];r.line(n);grips.append(dict(label=label,start_mm=a,end_mm=r.p[:]))
        if wire=='W064':
            land(9,'S1 upstream');r.turn(B.UP,25.2)
            r.line(end[2]-25.2-r.p[2]);r.turn(B.WEST,25.2)
            r.shift([0,end[1]-r.p[1],0],25.2)
            land(r.p[0]-end[0],'P_FRONT incoming')
        elif wire=='W065':
            land(9,'S1 upstream');r.turn(B.UP,25.2)
            r.shift([end[0]-r.p[0],end[1]-r.p[1],0],25.2)
            land(end[2]-r.p[2],'P_REAR incoming')
        elif wire=='W067':
            # Short source entry is not a restraint. Both independent lands
            # are on long straight insulation before/after the vertical loop.
            short_line(r,2);r.turn(B.WEST,25.2)
            if bus_undercross:
                # Cross below G_AUX, not through the complete W045 elbow.
                # Move south only after that factory elbow has been passed.
                land(9,'S1 low-gallery insulation');r.shift([0,0,62.25-r.p[2]],25.2)
                r.line(r.p[0]-40);r.shift([0,-46.8-r.p[1],0],25.2)
            elif layer_separated:
                land(9,'S1 low-gallery insulation');r.shift([0,0,7],25.2)
            east_turn_start=end[0]-25.2
            west_turn_start=east_turn_start-11
            land(r.p[0]-west_turn_start,'S1 upstream low gallery')
            r.turn(B.UP,25.2);r.line(end[2]-25.2-r.p[2]);r.turn(B.EAST,25.2)
            land(11,'P_SYS upstream before entry bend');r.turn(B.NORTH,25.2)
            short_line(r,end[1]-r.p[1])
        else:
            land(9,'S1 upstream');r.turn(B.WEST,25.2)
            if layer_separated or bus_undercross:
                # Factory W045 centre67.99, OD4. Native F0 top61.
                # Between them this4.2mm conductor has only a nominal
                # 63.10..63.89mm centre-height window, NOT a fit guarantee.
                land(9,'S1 low-gallery insulation');r.shift([0,0,63.5-r.p[2]],25.2)
            column_x=-72
            land(r.p[0]-(column_x+25.2),'Low gallery before bank')
            r.turn(B.UP,25.2);r.line(end[2]-25.2-r.p[2]);r.turn(B.EAST,25.2)
            r.line(end[0]-25.2-r.p[0]);r.turn(B.NORTH,25.2)
            land(end[1]-r.p[1],'P_SYS incoming')
        r.finish(end,arrival)
        parts=[dict(kind=s['kind'],start=s['start_mm'],end=s['end_mm'],
            **(dict(mid=s['mid_mm']) if s['kind']=='arc' else {})) for s in r.row['segments']]
        length=B.check_path(parts,ring['barrel_mm'],end,25.2)
        rows.append(dict(wire=wire,terminal=terminal,target=target,segments=parts,
            eye_mm=ring['eye_mm'],barrel_mm=ring['barrel_mm'],barrel_direction=ring['direction'],
            OD_mm=4.2,min_radius_mm=25.2,centreline_mm=length,
            termination_allowance_mm=28.452,nominal_fit_blank_mm=math.ceil(length+28.452),
            insulation_grip_lands=grips,native_grips_open=True,
            allowance_basis='14 WAGO plus14.452 retained TE130171 allowance; nominal delivery fit only',
            short_entry_is_not_grip=wire=='W067'))
    p.update(s1_routes=rows,changed_case_names=[],s1_geometry_changed=True,
        changed_path_names=[r['wire'] for r in rows],
        source_topology='Full routes around/below bank, westward vertical rises; receiving modules unchanged',
        low_galleries_separated_from_W045=layer_separated,
        W067_undercrosses_G_AUX_before_southward_swerve=bus_undercross,
        invalidated=['S1 native mounting/control access and four source grips',
                     'W066 current SYS approach remains OPEN after same-net port reassignment'],
        selected=False,stage_completed=False)
    return p

def build():
    d=B.read(PLAN)
    assert d['family'] is not None,'No coherent four-feed family'
    for n,h in d['source_sha256'].items():assert B.sha(ROOT/n)==h,n
    return d['family']

def main():
    assert not PLAN.exists(),'Do not repeat unchanged topology'
    tick=time.monotonic();p=build_geometry(LAYER_SEPARATED,BUS_UNDERCROSS,ALLOCATED_PORTS);report=S.F.F.proximity(p)
    bad=[r for r in report['near_pairs'] if r['status']=='REJECT_PLANNING_PROXIMITY']
    files=[Path(__file__),Path(T.__file__),Path(S.__file__),T.PLAN,
        OUT/'obstacle-map-current.json',OUT/'endpoint-plan.json']
    result=dict(status='KNOWN_MUTUAL_CONFLICTS_NOT_READY_FOR_CAD' if bad else 'FOUR_COMPLETE_SOURCE_RECIPES_REQUIRE_MATERIAL_GATE',
        family=p,mutual_preflight=report,known_mutual_conflicts=bad,
        geometry_digest=T.R.geometry_digest(p),source_sha256={f.relative_to(ROOT).as_posix():B.sha(f) for f in files},
        selected=False,stage_completed=False,physical_pass=False,
        worker_seconds=round(time.monotonic()-tick,6),finished_utc=datetime.now(timezone.utc).isoformat())
    PLAN.write_text(json.dumps(result,separators=(',',':'))+'\n',encoding='utf-8')
    print(json.dumps(dict(status=result['status'],known_mutual_conflicts=bad,
        lengths=[(r['wire'],r['nominal_fit_blank_mm']) for r in p['s1_routes']],worker_seconds=result['worker_seconds'])),flush=True)

if __name__=='__main__':main()
