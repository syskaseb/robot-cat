"""Move complete cable split boundaries toward receivers, not scalar loop fixes.

The previous Y185..205 virtual joins unnecessarily prolonged both the dynamic
bundle and the static return. Evaluate whole body-side joins for the four open
families, preserving actual moving exits, receiving ports, R31 and factory
capacity. This bounded math gate emits no CAD and does not select whole W5.
"""
import copy
import itertools
import json
import math
import time
from pathlib import Path

from plan_current_moving_looms import OUT, ROOT, SHA, add, sub, mul, norm, cross, poles, metrics, curve_length, best_span, exact_turn_to, exact_quarter, vertical_s
from plan_current_mta_interfaces import line
from screen_current_moving_looms import pose_row
from route_current_leg_fanouts import sampling_parts
from screen_current_remaining_routes import route_rows
from open_prototype_path_preflight import samples


OPEN = ('FL3', 'RL2', 'RL3', 'RR2')


class SharedMotionSpace:
    """Plan against all retained wires AND the same leg's matching poses.

    Sampled separation is a cheap rejection gate, not a BRep or full travel
    qualification. Never hide the other two cables' actual servo departures.
    """
    def __init__(self, fixed, chosen):
        self.fixed=fixed;self.chosen=chosen;self.grids={}
        self.roof_cells={}
        for row in fixed:
            for _,point in samples(sampling_parts(row['segments'])):
                cell=tuple(math.floor(x/10) for x in point[:2])
                self.roof_cells[cell]=max(self.roof_cells.get(cell,-math.inf),point[2]+row['OD_mm']/2+5)

    def roof_floor(self,start,end):
        # Conservative PLANNING reservation only: horizontal arch above all
        # retained wire samples in its XY footprint, not bbox collision proof.
        lo=[math.floor((min(a,b)-7)/10) for a,b in zip(start[:2],end[:2])]
        hi=[math.floor((max(a,b)+7)/10) for a,b in zip(start[:2],end[:2])]
        return max([start[2],end[2]]+[self.roof_cells.get((x,y),-math.inf)
                   for x in range(lo[0],hi[0]+1) for y in range(lo[1],hi[1]+1)])

    def clear(self, candidate):
        leg=candidate['loom'][:2]
        for pose in candidate['poses']:
            own={};travel=0;previous=None
            for _,point in samples(pose_row(candidate,pose)['segments']):
                if previous is not None:travel+=math.dist(previous,point)
                previous=point;cell=tuple(math.floor(x/7) for x in point)
                for delta in itertools.product((-1,0,1),repeat=3):
                    for other,at in own.get(tuple(a+b for a,b in zip(cell,delta)),()):
                        if travel-at>12 and math.dist(point,other)<6:
                            return False,dict(other='SELF_NONLOCAL',angles=pose['angles'],point_mm=point,other_point_mm=other)
                own.setdefault(cell,[]).append((point,travel))
            angles=pose['angles'];key=(leg,tuple(angles))
            if key not in self.grids:
                rows=list(self.fixed)
                for loom in self.chosen:
                    desired=angles[:1] if loom['motion_stage'].endswith('_Hip') else angles
                    if loom['loom'].startswith(leg) and len(desired)==len(loom['poses'][0]['angles']):
                        value=next(p for p in loom['poses'] if p['angles']==desired)
                    else:value=next(p for p in loom['poses'] if not any(p['angles']))
                    rows.append(pose_row(loom,value))
                grid={}
                for row in rows:
                    for _,point in samples(sampling_parts(row['segments'])):
                        cell=tuple(math.floor(x/7) for x in point)
                        grid.setdefault(cell,[]).append((point,row['OD_mm']/2,row['wire']))
                self.grids[key]=grid
            grid=self.grids[key]
            for _,point in samples(pose_row(candidate,pose)['segments']):
                cell=tuple(math.floor(x/7) for x in point)
                for delta in itertools.product((-1,0,1),repeat=3):
                    for other,radius,name in grid.get(tuple(a+b for a,b in zip(cell,delta)),()):
                        if math.dist(point,other)<3+radius:
                            return False,dict(other=name,angles=angles,point_mm=point,other_point_mm=other)
        return True,None


def rear_fold(pose, dock, target=None):
    """Whole R31 rolling S-fold after turning the actual exit tangent UP.

    The previous one-cubic family tried to reverse an outward tangent in the
    same span as a rising inboard return. Two complete semicircles provide
    explicit slack capacity instead. Extra drop adds exactly twice its length
    (down land plus rising return), retaining the endpoint and both tangents.
    This is a geometric candidate, NOT permission to protrude below the feet.
    """
    original = pose['spans_mm'][0]; start = original[0]
    axis = sub(original[1], start); axis = mul(axis, 1 / norm(axis))
    up, down, inward = [0, 0, 1], [0, 0, -1], [-1, 0, 0]
    lead = exact_turn_to(start, axis, up, 31)
    a = lead['end']; end = add(a, [-124, 0, 0])
    delta = sub(dock, end); height = delta[2]; delta[2] = 0
    distance = norm(delta)
    required = 62 if distance >= 62 else 62 * math.sqrt(max(0, 1 - (1 - distance / 62) ** 2))
    mandatory = max(0, required - height)
    def parts_for(drop):
        parts = [lead]
        parts.append(exact_quarter(parts[-1]['end'], up, inward, 31))
        parts.append(exact_quarter(parts[-1]['end'], inward, down, 31))
        if drop > 1e-8:
            parts.append(line(parts[-1]['end'], add(parts[-1]['end'], mul(down, drop))))
        parts.append(exact_quarter(parts[-1]['end'], down, inward, 31))
        parts.append(exact_quarter(parts[-1]['end'], inward, up, 31))
        tail = vertical_s(parts[-1]['end'], dock, 31)
        assert tail is not None
        return parts + tail
    parts = parts_for(mandatory)
    length = sum(q['length_mm'] for q in parts)
    if target is not None:
        if target < length - 1e-5:return None
        parts = parts_for(mandatory + max(0, target - length) / 2)
        length = sum(q['length_mm'] for q in parts)
        assert abs(length - target) < 1e-5
    return parts, length


def rear_family(loom, dock):
    values = [rear_fold(p, dock) for p in loom['poses']]
    target = max(v[1] for v in values) + 5
    result = []
    for pose in loom['poses']:
        parts, length = rear_fold(pose, dock, target)
        result.append(dict(angles=pose['angles'], start=pose['start'], flex_start=pose['flex_start'],
                           departure_parts_mm=[], transition_parts_mm=parts, spans_mm=[], return_parts_mm=[],
                           body_arrival_axis_mm=[0,0,1], flex_length_mm=length,
                           sampled_minimum_R_mm=31))
    return dict(body_dock_mm=dock, fixed_bundle_guide_mm=target, poses=result,
                topology='Exact R31 outward-to-UP transition plus two fore-aft semicircles and rising S')


def ankle_rise_basis(loom,east_land=40,inner_land=0):
    """Finish the whole outward escape before any return toward receivers.

    A direct diagonal from the U exit to the body ran through the other
    Knee-owned cable's outlet in motion. Turn UP first, retaining the
    original fore/aft U and its9mm moving housing-grip land.
    """
    changed=copy.deepcopy(loom)
    for pose in changed['poses']:
        if loom['loom']=='FL3':
            # Both front routes used the same fore/aft floor corridor.
            # Reversing that plane met the opposite Ankle instead. Allocate
            # a whole UP U in the moving knee frame, then lateral escape.
            # This changes the cause, not another downstream displacement.
            first=pose['departure_parts_mm'][0];radius=first['radius_mm']
            axis=pose['axis'];fore=sub(mul(sub(first['end'],first['start']),1/radius),axis)
            fore=cross(fore,axis);fore=mul(fore,1/norm(fore))
            q=exact_quarter(pose['flex_start'],axis,fore,radius)
            land=line(q['end'],add(q['end'],mul(fore,9)))
            last=exact_quarter(land['end'],fore,mul(axis,-1),radius)
            pose['departure_parts_mm']=[q,land,last]
            end=last['end'];pose['spans_mm']=[[end,add(end,mul(axis,-30)),end,end]]
        original=pose['spans_mm'][0];start=original[0]
        axis=sub(original[1],start);axis=mul(axis,1/norm(axis))
        if loom['loom']=='FL3':
            # The measured head-wire references all end at X<=-50.95.
            # Cross below them toward the aft body bay, THEN rise at X~0;
            # a vertical column at X~-62 intersects their full yaw envelope.
            east=exact_turn_to(start,axis,[1,0,0],31)
            pose['departure_parts_mm'].append(east)
            # Cross below the Foundation to its AFT side (X>24), rather
            # than spending160mm on an outboard-and-back head-wire bypass.
            land=line(east['end'],add(east['end'],[east_land,0,0]));pose['departure_parts_mm'].append(land)
            # The peripheral riser crosses W028's low bank-input gallery.
            # Return into the central body bay BELOW that gallery first;
            # do not keep moving an occupied peripheral vertical column.
            inner=exact_quarter(land['end'],[1,0,0],[0,-1,0],31)
            pose['departure_parts_mm'].append(inner)
            if inner_land:
                inner=line(inner['end'],add(inner['end'],[0,-inner_land,0]));pose['departure_parts_mm'].append(inner)
            lead=exact_quarter(inner['end'],[0,-1,0],[0,0,1],31)
        else:lead=exact_turn_to(start,axis,[0,0,1],31)
        pose['departure_parts_mm'].append(lead)
        a=lead['end'];rise=line(a,add(a,[0,0,60 if loom['loom']=='FL3' else 100]));pose['departure_parts_mm'].append(rise)
        a=rise['end'];pose['spans_mm']=[[a,add(a,[0,0,30]),add(a,[0,0,60]),add(a,[0,0,90])]]
    return changed


def ankle_fold_family(loom,dock,away):
    """Offset fore/aft slack fold AFTER the moving outlet's high escape.

    Two offset semicircles do NOT return to the original XY/stem. Extra down land is compensated
    by the final UP return, so total cable length does not change with pose.
    """
    up,down=[0,0,1],[0,0,-1]
    def parts_for(pose,drop):
        a=pose['spans_mm'][0][0];parts=[]
        parts.append(exact_quarter(a,up,away,31))
        parts.append(exact_quarter(parts[-1]['end'],away,down,31))
        if drop>1e-8:parts.append(line(parts[-1]['end'],add(parts[-1]['end'],mul(down,drop))))
        parts.append(exact_quarter(parts[-1]['end'],down,away,31))
        parts.append(exact_quarter(parts[-1]['end'],away,up,31))
        tail=vertical_s(parts[-1]['end'],dock,31)
        return None if tail is None else parts+tail
    candidates=[]
    for pose in loom['poses']:
        a=add(pose['spans_mm'][0][0],mul(away,124));horizontal=math.dist(a[:2],dock[:2])
        required=62 if horizontal>=62 else 62*math.sqrt(max(0,1-(1-horizontal/62)**2))
        mandatory=max(0,required-(dock[2]-a[2]))
        parts=parts_for(pose,mandatory)
        if parts is None:return None
        prefix=sum(q['length_mm'] for q in pose['departure_parts_mm'])
        length=prefix+sum(q['length_mm'] for q in parts)
        candidates.append((pose,mandatory,length))
    target=max(q[2] for q in candidates)+5;poses=[]
    for pose,mandatory,length in candidates:
        parts=parts_for(pose,mandatory+(target-length)/2)
        exact=sum(q['length_mm'] for q in pose['departure_parts_mm']+parts)
        assert abs(exact-target)<1e-5
        poses.append(dict(angles=pose['angles'],start=pose['start'],flex_start=pose['flex_start'],
                          departure_parts_mm=pose['departure_parts_mm'],transition_parts_mm=parts,
                          spans_mm=[],return_parts_mm=[],body_arrival_axis_mm=up,flex_length_mm=exact,
                          sampled_minimum_R_mm=31))
    return dict(body_dock_mm=dock,fixed_bundle_guide_mm=target,poses=poses,
                topology='High outward escape, opposed semicircle slack fold, then rising body return',fold_axis_mm=away)


def arch_family(loom,dock,roof_floor):
    """Analytic fixed-length UP-to-DOWN arch; no cubic handle search.

    Virtual breakout arrival is free to be DOWN. Two R31 quarters and
    horizontal/vertical lands have an exact length; varying roof height
    takes up the moving prefix's change without moving the body endpoint.
    """
    catalog=[]
    for pose in loom['poses']:
        start=pose['spans_mm'][0][0];d=sub(dock,start);d[2]=0;distance=norm(d)
        if distance<62:return None
        prefix=sum(q['length_mm'] for q in pose['departure_parts_mm'])
        low=prefix+2*roof_floor(start,dock)-start[2]-dock[2]+distance-62+math.pi*31
        catalog.append((pose,start,mul(d,1/distance),distance,prefix,low))
    target=max(r[-1] for r in catalog)+5;poses=[]
    for pose,start,direction,distance,prefix,low in catalog:
        roof=(target-prefix+start[2]+dock[2]-distance+62-math.pi*31)/2
        assert roof>=max(start[2],dock[2])
        parts=[line(start,[start[0],start[1],roof])]
        parts.append(exact_quarter(parts[-1]['end'],[0,0,1],direction,31))
        if distance>62+1e-8:parts.append(line(parts[-1]['end'],add(parts[-1]['end'],mul(direction,distance-62))))
        parts.append(exact_quarter(parts[-1]['end'],direction,[0,0,-1],31))
        parts.append(line(parts[-1]['end'],dock))
        length=prefix+sum(q['length_mm'] for q in parts)
        assert abs(length-target)<1e-5
        poses.append(dict(angles=pose['angles'],start=pose['start'],flex_start=pose['flex_start'],
                          departure_parts_mm=pose['departure_parts_mm'],transition_parts_mm=parts,
                          spans_mm=[],return_parts_mm=[],body_arrival_axis_mm=[0,0,-1],
                          flex_length_mm=length,sampled_minimum_R_mm=31))
    return dict(body_dock_mm=dock,fixed_bundle_guide_mm=target,poses=poses,
                topology='Exact R31 UP to DOWN roof arch with analytic height takeup')


def family(loom, dock, maximum=650,arrival=None):
    """Intersect feasible sampled length ranges, then solve actual lengths.

    Reject disconnected handle intervals; do not infer that min/max samples
    imply all intermediate lengths are feasible. Validate every solved curve
    at dense curvature samples and its true integrated length.
    """
    arrival=[0,0,1] if arrival is None else arrival
    outward=mul(arrival,-1);catalog = []
    for pose in loom['poses']:
        original = pose['spans_mm'][0]
        start = original[0]
        axis = sub(original[1], start)
        axis = mul(axis, 1 / norm(axis))
        prefix = sum(q['length_mm'] for q in pose['departure_parts_mm'])
        candidates = []
        for h, b in itertools.product((30, 60, 100, 150, 210), repeat=2):
            q = poles(start, axis, dock, outward, h, b)
            length, radius, bounds = metrics(q, 30)
            if radius >= 32 and prefix + length <= maximum:
                candidates.append((prefix + length, radius))
        if not candidates:
            return None
        catalog.append((pose, start, axis, prefix, candidates))
    low = max(min(t[0] for t in row[-1]) for row in catalog)
    high = min(max(t[0] for t in row[-1]) for row in catalog)
    if high < low:
        return None
    for target in (low + .001, (low + high) / 2, high - .001):
        result = []
        for pose, start, axis, prefix, candidates in catalog:
            curve = best_span(start, axis, dock, outward, target - prefix)
            if curve is None:
                break
            _, length, radius, bounds, q = curve
            exact, radius, bounds = metrics(q, 240)
            if radius < 31 or abs(prefix + exact - target) > 1e-4:
                break
            result.append(dict(angles=pose['angles'], start=pose['start'], flex_start=pose['flex_start'],
                               departure_parts_mm=pose['departure_parts_mm'], spans_mm=[q],
                               transition_parts_mm=[], return_parts_mm=[], body_arrival_axis_mm=arrival,
                               flex_length_mm=prefix + exact, sampled_minimum_R_mm=radius))
        if len(result) == len(loom['poses']):
            return dict(body_dock_mm=dock, fixed_bundle_guide_mm=target, poses=result)
    return None


def front_shared_corridor(raw,space,receivers,stations):
    """Bounded whole-corridor search; reject occupied risers BEFORE arches.

    Coarse40mm macro bays, not serial manual wire nudges. All nine matching
    moving poses, all retained wires and the other two same-leg cables are
    present. Geometry radius/stock limits never change to obtain a result.
    """
    rejected=[];capacity=[];tried=0
    for east,inner in itertools.product((60,80,100,120,140),(20,40,60,0,80)):
        loom=ankle_rise_basis(raw,east,inner)
        prefix=dict(loom=loom['loom'],motion_stage=loom['motion_stage'],poses=[dict(
            p,spans_mm=[],transition_parts_mm=[],return_parts_mm=[]) for p in loom['poses']])
        clear,hit=space.clear(prefix)
        if not clear:
            rejected.append(dict(loom='FL3',corridor_land_mm=[east,inner],scope='WHOLE_SOURCE_PREFIX',**hit));continue
        for floor,dock in itertools.product((160,190,220,250),stations):
            tried+=1;candidate=arch_family(loom,list(dock),lambda start,end:max(start[2],end[2],floor))
            if candidate is None:continue
            necessary=max(math.dist(dock,p) for p in receivers)
            blank=14+loom['initial_land_mm']+candidate['fixed_bundle_guide_mm']+necessary+21
            if blank>850:
                capacity.append(dict(loom='FL3',corridor_land_mm=[east,inner],dock_mm=dock,
                                     necessary_blank_lower_bound_mm=blank));continue
            proposal=dict(loom='FL3',motion_stage=loom['motion_stage'],**candidate,
                          initial_land_mm=loom['initial_land_mm'],cores=loom['cores'],
                          minimum_complete_blank_lower_bound_mm=blank,corridor_land_mm=[east,inner],
                          receiving_roles=[])
            clear,hit=space.clear(proposal)
            if clear:return proposal,rejected,capacity,tried
            rejected.append(dict(loom='FL3',corridor_land_mm=[east,inner],dock_mm=dock,roof_floor_mm=floor,**hit))
    return None,rejected,capacity,tried


def run():
    tick = time.monotonic()
    source = OUT / 'joined-leg-looms-plan.json'
    previous_source = OUT / 'bundle-slack-planes-plan.json'
    previous = json.loads(previous_source.read_text())
    for name, digest in previous['source_sha256'].items():
        assert SHA(ROOT / name) == digest, name
    ends_source = OUT / 'leg-terminations-plan.json'
    basis = json.loads(source.read_text())
    ends = {q['wire']: q for q in json.loads(ends_source.read_text())['wires']}
    fixed,pins=route_rows(tuple(OUT/(t+'-plan.json') for t in
                              ('ground-tree','data-bridges','positive-source','s0-in-extension','BUS-routes')))
    hf=OUT/'head-wire-screen-reference.json';heads=json.loads(hf.read_text())
    for name,digest in heads['source_sha256'].items():assert SHA(ROOT/name)==digest,name
    retained=list(fixed.values())+heads['rows']
    looms = [copy.deepcopy(r) for r in previous['looms'] if r['loom'] not in OPEN]
    rejected = []; trials = {};screen_rejections=[];capacity_rejections=[];analytic_short_span_rejections=[]
    for name in ('RL2','RR2','FL3','RL3'):
        loom=next(r for r in basis['looms'] if r['loom']==name)
        if name=='RL3':loom=ankle_rise_basis(loom)
        space=SharedMotionSpace(retained,looms)
        receivers = [ends[q['wire']]['body_point_mm'] for q in loom['cores'].values()]
        centre = [sum(p[j] for p in receivers) / 3 for j in range(3)]
        side = 1 if centre[1] > 0 else -1
        # A spatial REGION relative to real receiver locations, not four
        # successive manual xyz nudges. Join still is not a printed clamp.
        xs = (centre[0] - 35, centre[0], centre[0] + 35)
        ys = (side * 85, side * 100)
        if name=='FL3':ys=(40,60)
        zs = (80, 120, 160)
        stations = list(itertools.product(xs, ys, zs))
        stations.sort(key=lambda p: math.dist(p, centre))
        accepted = None; tried = 0
        single_span_failed = False
        if name=='FL3':
            accepted,hits,short,tried=front_shared_corridor(loom,space,receivers,stations)
            screen_rejections.extend(hits);capacity_rejections.extend(short)
        for dock in ([] if name.endswith('3') else stations):
            tried += 1
            candidate = family(loom, list(dock))
            if candidate:
                # Fanouts are invalidated by this changed split boundary.
                # Capacity here uses only straight-distance lower bounds,
                # so it is necessary, NOT sufficient, for a complete cable.
                necessary = max(math.dist(dock, p) for p in receivers)
                blank = 14 + loom['initial_land_mm'] + candidate['fixed_bundle_guide_mm'] + necessary + 21
                if blank <= 850:
                    proposal = dict(loom=loom['loom'],motion_stage=loom['motion_stage'], **candidate,
                                    minimum_complete_blank_lower_bound_mm=blank,
                                    receiving_roles=[ends[q['wire']]['body_role'] for q in loom['cores'].values()])
                    clear,hit=space.clear(proposal)
                    if clear:accepted=proposal;break
                    screen_rejections.append(dict(loom=loom['loom'],dock_mm=dock,**hit))
        if name=='RL3':
            fore=[-1 if name.startswith('F') else 1,0,0]
            # Virtual breakout has no mandated UP approach. A DOWN arrival
            # permits one high arch instead of another whole bundle U.
            # Static core fanouts must be regenerated with that tangent.
            if name=='FL3':
                # Search whole horizontal free levels, NOT a box enclosing
                # every high wire in the footprint. The max-height-only
                # reservation needed>=1015mm and was rejected, not a real
                # collision or justification to replace the900mm cable.
                for floor,dock in itertools.product((160,190,220,250),stations):
                    tried+=1;candidate=arch_family(loom,list(dock),lambda start,end:max(start[2],end[2],floor))
                    if candidate is None:
                        analytic_short_span_rejections.append(dict(loom=name,dock_mm=dock,minimum_horizontal_mm=min(math.dist(p['spans_mm'][0][0][:2],dock[:2]) for p in loom['poses'])))
                        continue
                    necessary=max(math.dist(dock,p) for p in receivers)
                    blank=14+loom['initial_land_mm']+candidate['fixed_bundle_guide_mm']+necessary+21
                    if blank>850:
                        capacity_rejections.append(dict(loom=name,dock_mm=dock,roof_floor_mm=floor,necessary_blank_lower_bound_mm=blank,fixed_bundle_mm=candidate['fixed_bundle_guide_mm']))
                        continue
                    proposal=dict(loom=name,motion_stage=loom['motion_stage'],**candidate,
                                  minimum_complete_blank_lower_bound_mm=blank,
                                  receiving_roles=[ends[q['wire']]['body_role'] for q in loom['cores'].values()])
                    clear,hit=space.clear(proposal)
                    if clear:accepted=proposal;break
                    screen_rejections.append(dict(loom=name,dock_mm=dock,roof_floor_mm=floor,arrival_axis_mm=[0,0,-1],**hit))
            for away,dock in ([] if accepted or name=='FL3' else itertools.product((fore,mul(fore,-1),[0,side,0]),stations)):
                tried+=1;candidate=ankle_fold_family(loom,list(dock),away)
                if candidate is None:continue
                necessary=max(math.dist(dock,p) for p in receivers)
                blank=14+loom['initial_land_mm']+candidate['fixed_bundle_guide_mm']+necessary+21
                if blank>850:continue
                proposal=dict(loom=name,motion_stage=loom['motion_stage'],**candidate,
                              minimum_complete_blank_lower_bound_mm=blank,
                              receiving_roles=[ends[q['wire']]['body_role'] for q in loom['cores'].values()])
                clear,hit=space.clear(proposal)
                if clear:accepted=proposal;break
                screen_rejections.append(dict(loom=name,dock_mm=dock,fold_axis_mm=away,**hit))
        if accepted is None and loom['loom'] in ('RL2', 'RR2'):
            single_span_failed = True
            for dock in stations:
                candidate = rear_family(loom, list(dock))
                necessary = max(math.dist(dock, p) for p in receivers)
                blank = 14 + loom['initial_land_mm'] + candidate['fixed_bundle_guide_mm'] + necessary + 21
                if blank <= 850:
                    proposal = dict(loom=loom['loom'],motion_stage=loom['motion_stage'], **candidate,
                                    minimum_complete_blank_lower_bound_mm=blank,
                                    receiving_roles=[ends[q['wire']]['body_role'] for q in loom['cores'].values()])
                    clear,hit=space.clear(proposal)
                    if clear:accepted=proposal;break
                    screen_rejections.append(dict(loom=loom['loom'],dock_mm=dock,**hit))
        trials[loom['loom']] = tried
        if accepted:
            accepted.update({k:copy.deepcopy(loom[k]) for k in ('initial_land_mm', 'motion_stage', 'cores')})
            accepted['single_cubic_receiver_region_rejected_before_changed_topology'] = single_span_failed
            looms.append(accepted)
        else:
            rejected.append(dict(loom=loom['loom'], cause='NO_SHARED_MOTION_CLEAR_R31_FIXED_FAMILY_IN_BODY_RECEIVER_REGION'))
        print('Body-side family', loom['loom'], 'trials', tried,
              'fixed', None if accepted is None else round(accepted['fixed_bundle_guide_mm'], 3), flush=True)
    report = dict(status='BODY_JOIN_FIXED_LENGTH_MATH_ONLY' if not rejected else 'REJECTED_BODY_JOIN_MATH',
                  looms=looms, rejected=rejected, station_trials=trials,shared_motion_station_rejections=screen_rejections,
                  capacity_rejections=capacity_rejections,analytic_short_span_rejections=analytic_short_span_rejections,
                  source_sha256={p.relative_to(ROOT).as_posix(): SHA(p) for p in
                                 pins|{source, previous_source, ends_source,hf,Path(__file__), ROOT / 'tools/cad/plan_current_moving_looms.py',ROOT/'tools/cad/screen_current_moving_looms.py',ROOT/'tools/cad/route_current_leg_fanouts.py'}},
                  worker_seconds=time.monotonic() - tick,
                  invalidated='Previous12fanouts of these four looms and their BUS/leg proximity relationship; not silently retained as qualified',
                  unchanged='Eight other loop families, physical factory exits and all electrical receiving port assignments',
                  independent_insulation_grips_open=True, actual_nominal_material_and_motion_open=True,
                  complete_factory_capacity_open=True, native_open=True, selected=False, W5_complete=False, physical_pass=False)
    (OUT / 'leg-body-joins-plan.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(status=report['status'], rejected=rejected, seconds=report['worker_seconds'])), flush=True)


if __name__ == '__main__':
    run()
