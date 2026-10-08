"""Whole eight-tail simplification, cheap planning only; never native acceptance.

The previous routes made eight extra joints before establishing that they were
needed. Test a common direct-tail topology against length and received sections
first. Factory100mm/OD4/bend radius remain DELIVERY assumptions. Unallocated
source/ground stations and S1 prevent a CAD build or a stock selection.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import math
import time
from open_prototype_wiring_endpoints import ROOT, BASE, read, sha
from open_prototype_distribution_allocation import input_recipe
from open_prototype_entry_chambers import occupancy

OUT = BASE / 'wiring-checkpoint'
MAP = OUT / 'obstacle-map-current.json'
PRIOR = OUT / 'power-harness-plan.json'
DEST = OUT / 'direct-mta-plan.json'
ENDPOINTS = OUT / 'endpoint-plan.json'
SCOPE = OUT / 'routing-scope-plan.json'


def bind_ports(rows):
    """Bijections inside the same copper bus, never port duplication.

    Unallocated upper cases get NO inherited coordinate. Rebinding an ID is
    not a physical route or proof that a moved station retains its old mount.
    """
    ports={}
    permutation={}
    for bus in ('P_FRONT','P_REAR'):
        permutation.update({f'{bus}.{a}':f'{bus}.{b}' for a,b in [(1,2),(2,5),(3,1),(4,4),(5,3)]})
    for bus in ('FL_P','FR_P'):
        permutation.update({f'{bus}.1':f'{bus}.5',f'{bus}.5':f'{bus}.1'})
    left=['FL_P','FR_P','FL_G','RL_P','RR_P']
    right=['FR_G','D_FR','D_FL','RL_G','RR_G']
    for sign,roles in [(1,left),(-1,right)]:
        for index,bus in enumerate(roles):
            x=-62+37*index
            for n in range(1,6):
                ports[f'{bus}.{n}']=dict(point_mm=[x+(n-3)*4.75,sign*65.5,67.99],
                    departure=[0,-sign,0],basis='Reallocated415 envelope entry allowance, NOT delivered cavity datum')
    for bus,x in [('P_FRONT',-59),('P_REAR',79.5)]:
        for n in range(1,6):
            ports[f'{bus}.{n}']=dict(point_mm=[x-(n-3)*6.5,-30,120],departure=[0,1,0],
                basis='Reallocated615 rotated180 envelope entry allowance, NOT delivered cavity datum')
    endpoint=read(ENDPOINTS);scope=read(SCOPE)
    loads=occupancy(scope,permutation)
    all_buses={r['role'].split('.')[0] for r in read(PRIOR)['ports']}
    all_ports=[]
    for bus in sorted(all_buses):
        for n in range(1,6):
            role=f'{bus}.{n}'
            assert len(loads[role])<=1,(role,loads[role])
            all_ports.append(dict(role=role,occupied=bool(loads[role]),
                datum=ports.get(role),spatial_status='CANDIDATE_DATUM' if role in ports else 'OPEN_UPPER_STATION_NO_OLD_COORDINATE_REUSE'))
    assert len(all_ports)==100 and sum(r['occupied'] for r in all_ports)==86
    ends=[]
    main={r['id']:r for r in rows}
    for wire in endpoint['body_conductors']:
        for old in wire['ends']:
            original=old['role'];current=permutation.get(original,original)
            record=dict(wire=wire['id'],original_role=original,current_role=current,net=wire['net'])
            if '.' in current and current.split('.')[0] in all_buses:
                record.update(datum=ports.get(current),status='CANDIDATE_STATION' if current in ports else 'OPEN_STATION')
            elif wire['id'] in main:
                record.update(datum=dict(point_mm=main[wire['id']]['recipe']['segments'][0]['start']),
                    status='CANDIDATE_MTA_EXIT_NOT_SUPPLIER_PIN')
            else:
                record.update(datum=None,status='RETAINED_ROLE_REQUIRES_COMPLETE_SHARED_ROUTE')
            ends.append(record)
    assert len(ends)==160
    for ident,r in main.items():
        selected=[e for e in ends if e['wire']==ident and e['current_role']==r['target']]
        assert len(selected)==1 and math.dist(selected[0]['datum']['point_mm'],r['recipe']['segments'][-1]['end'])<1e-7
    return dict(same_bus_permutation=permutation,ports=all_ports,body_ends=ends,
        occupied_ports=86,NC_ports=14,body_ends_count=160,
        unallocated_upper_roles=sorted(all_buses-{r.split('.')[0] for r in ports}),
        no_partial_wiring_credit=True)


def vector(a, b, scale=1):
    return [x + scale*y for x,y in zip(a,b)]


def samples(parts, step=1):
    """Sample exact declared arcs for a NEGATIVE planning screen, not a sweep."""
    points = []
    for p in parts:
        a, b = p['start'], p['end']
        if p['kind'] == 'line':
            count = max(1, math.ceil(math.dist(a,b)/step))
            points.extend(vector(a, [y-x for x,y in zip(a,b)], k/count) for k in range(count+1))
        else:
            c, u, v = p['centre'], p['radial_start'], p['radial_tangent']
            count = max(1, math.ceil(p['radius_mm']*p['angle_rad']/step))
            for k in range(count+1):
                t = p['angle_rad']*k/count
                points.append(vector(c, [p['radius_mm']*(x*math.cos(t)+y*math.sin(t)) for x,y in zip(u,v)]))
    return points


def route(start, end, radius):
    recipe = input_recipe(start,end,[0,1 if end[1]>start[1] else -1,0],radius)
    # Derive the true circle basis from the same S-curve construction. This
    # avoids the old helper's hard-coded R6 when using a larger output radius.
    parts = recipe['segments']; d = [0,1 if end[1]>start[1] else -1,0]
    delta = [b-a for a,b in zip(start,end)]
    along = sum(x*y for x,y in zip(delta,d))
    lateral = [x-along*y for x,y in zip(delta,d)]
    shift = math.sqrt(sum(x*x for x in lateral)); side = [x/shift for x in lateral]
    angle = math.radians(recipe['arc_angle_deg'])
    arcs = [p for p in parts if p['kind']=='arc']
    first, second = arcs
    first.update(centre=vector(first['start'],side,radius),
                 radial_start=[-x for x in side],radial_tangent=d,
                 radius_mm=radius,angle_rad=angle)
    # Its radial direction at the second arc's start follows the receiving
    # arc backwards; tangent is still in the forward path direction.
    radial = [x*math.sin(angle)-y*math.cos(angle) for x,y in zip(d,side)]
    second.update(centre=vector(second['start'],radial,radius),
                  radial_start=[-x for x in radial],
                  radial_tangent=[x*math.cos(angle)+y*math.sin(angle) for x,y in zip(d,side)],
                  radius_mm=radius,angle_rad=angle)
    return recipe


def inside(point, rings):
    """Even/odd planar contour fill; 0.25mm map approximation, not BRep."""
    x,y = point; result = False
    for ring in rings:
        for a,b in zip(ring,ring[1:]+ring[:1]):
            if (a[1]>y)!=(b[1]>y) and x < (b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:
                result = not result
    return result


def section_screen(rows, space):
    hits={};outside={};events=0
    for row in rows:
        pts=samples(row['recipe']['segments'])
        for section in space['sections']:
            z=section['z_mm']; groups={}
            for c in section['contours']:
                if c['kind'] in ('candidate_station','replaceable_support'):continue
                groups.setdefault(c['part'],[]).append(c['xy_mm'])
            for a,b in zip(pts,pts[1:]):
                if not min(a[2],b[2])<=z<=max(a[2],b[2]):continue
                # Source tails lie entirely on Z120: skipping coplanar edges
                # would silently omit half of this coupled planning screen.
                if abs(a[2]-b[2])<1e-9:
                    p=a
                else:p=vector(a,[v-u for u,v in zip(a,b)],(z-a[2])/(b[2]-a[2]))
                events+=1
                if not inside(p[:2],groups.get('TorsoEnvelope',[])):
                    outside.setdefault((row['id'],z),dict(wire=row['id'],point_mm=p,section_z_mm=z))
                for name,rings in groups.items():
                    if name!='TorsoEnvelope' and inside(p[:2],rings):
                        hits.setdefault((row['id'],name,z),dict(wire=row['id'],part=name,point_mm=p,section_z_mm=z))
    return dict(events=events,centreline_planning_overlaps=list(hits.values()),
        centreline_outside_section=list(outside.values()),
        basis='Polyline interpolation at received10 planes/0.25mm contours; centerline ONLY, no pipe radius, no continuous clearance, no BRep contact claim')


def build():
    tick=time.monotonic(); prior=read(PRIOR); space=read(MAP)
    assert not space['errors'] and space['bank_reference_count']==48
    for path,h in space['source_sha256'].items():assert sha(ROOT/path)==h,path
    # Simultaneous reallocation, not an isolated screw/route shift. Four
    # output roles share one row. Their displaced equal415 ground/data roles
    # must be reallocated before any full-layout gate.
    main=[('FL',-50,-52.5,'W041','P_FRONT.5',-72,'W026','FL_P.5'),
          ('FR',-15.5,-15.5,'W042','P_FRONT.1',-46,'W037','FR_P.5'),
          ('RL',39.5,39.5,'W044','P_REAR.5',66.5,'W045','RL_P.1'),
          ('RR',76.5,76.5,'W052','P_REAR.1',92.5,'W053','RR_P.1')]
    rows=[]
    for leg,x,outx,source_id,source_role,sx,output_id,output_role in main:
        for ident,side,start,end,radius,strip,target in [
            (source_id,'source',[x,-.5,120],[sx,-30,120],6,14,source_role),
            (output_id,'output',[x,34.5,120],[outx,65.5,67.99],9.5,11,output_role)]:
            r=route(start,end,radius); blank=r['centreline_mm']+strip
            rows.append(dict(id=ident,leg=leg,side=side,target=target,recipe=r,
                strip_allowance_mm=strip,required_factory_blank_mm=blank,
                nominal_fit_blank_mm=math.ceil(blank),factory_limit_assumed_mm=100,
                length_fits_assumption=blank<=100,independent_grip='Last9mm straight before terminal, separate from WAGO lever',
                replaced_joint_kind='solder_lap' if side=='source' else 'installed_WAGO221-412',
                not_selected=True))
    assert {r['id'] for r in rows}==set(prior['main_targets'])
    return dict(status='PARTIAL_MACRO_SIMPLIFICATION_NOT_READY_FOR_CAD',
        selected=False,stage_completed=False,physical_pass=False,
        preserved=['P0','E6','15drives','MG92B replaceable provisional adapters','bankR47 design','325x200x160','MAIN46.52'],
        changed_cause='Straight-through factory tails replace source return loops and output return loops; all4 MTA centers and both sides allocated together',
        mta_centres_mm={leg:[x,17,120] for leg,x,*_ in main},
        mta_rotation_z_deg=90,
        receiving_cases=dict(P_FRONT=dict(centre_mm=[-59,-41,120],rotation_z_deg=180),
            P_REAR=dict(centre_mm=[79.5,-41,120],rotation_z_deg=180)),
        candidate_lower_left_roles=['FL_P','FR_P','FL_G','RL_P','RR_P'],
        candidate_lower_right_roles=['FR_G','D_FR','D_FL','RL_G','RR_G'],
        rows=rows,port_binding=bind_ports(rows),section_screen=section_screen(rows,space),
        conditional_reductions=dict(main_HELU_extensions=8,covered_solder_laps=4,output_joint_roles=4,
            stock_not_reduced=True,existing_output_joint_parts_retained_until_selection=True),
        delivery_gates=['MTA actual usable length/side, OD and bend radius unknown: L140 is NOT100mm each side',
            '4mm2 factory lead current/insulation qualification retained; no substitute cross-section',
            'WAGO port positions provisional, not delivered cavity datums'],
        before_next_CAD=['Resolve all remaining10 upperWAGO and fiveFHAC with BOTH complete exits',
            'Allocate four fullS1 routes including replaced920mm; no down-loop through P0',
            'Rebind all100ports/86occupied and160body ends without duplicate connections',
            'Matched native bank/station support and tool access; old mounts are invalidated, not waived',
            'Full tube/grip/mutual/torso qualification: section screen is not clearance'],
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (MAP,PRIOR,ENDPOINTS,SCOPE,Path(__file__),
            ROOT/'tools/cad/open_prototype_distribution_allocation.py',ROOT/'tools/cad/open_prototype_entry_chambers.py')},
        worker_seconds=time.monotonic()-tick,finished_utc=datetime.now(timezone.utc).isoformat())


if __name__=='__main__':
    result=build()
    DEST.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=result['status'],tails=len(result['rows']),
        blanks=[round(r['required_factory_blank_mm'],3) for r in result['rows']],
        screen=result['section_screen'],seconds=result['worker_seconds'])),flush=True)
