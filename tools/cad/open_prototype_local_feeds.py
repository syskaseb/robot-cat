"""One nine-conductor fixed-feed proposal; no terminal or support invention.

Reuse existing rounded-path mathematics. High shared lanes avoid the ATO/MTA
service plane. Historical pitch endpoints remain provisional until re-anchored.
This is route preflight, not full wiring/native-history or stock acceptance.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import math
import sys
import time
from open_prototype_wiring_endpoints import ROOT, BASE, read, sha, bounds

sys.path.insert(0, str(ROOT/'tools/electronics'))
from w5_rounded_path import corner_offsets, rounded
from w5_path_length import rounded_length

OUT = BASE/'wiring-checkpoint'
SOURCE = OUT/'OutputReliefsAssembly.FCStd'


def route_points(start, direction, end, group, index):
    height = 180 + 3*index
    first = [x+35*a for x,a in zip(start,direction)]
    points = [start, first]
    if direction == [0,0,1]:
        points.append([first[0],first[1]+35,first[2]])
        first = points[-1]
    points.append([first[0], first[1], height])
    trunk_y = {'HY':-10, 'HP':-75, 'TY':10}[group]
    points.append([first[0],trunk_y,height])
    if group == 'HY':
        column_x = end[0]+35+5*index
        points += [[column_x,trunk_y,height],[column_x,end[1],height],
                   [column_x,end[1],end[2]],end]
    elif group == 'HP':
        column_y = end[1]-40-5*index
        points += [[end[0],trunk_y,height],[end[0],column_y,height],
                   [end[0],column_y,end[2]],end]
    else:
        column_x = -10-5*index
        points += [[column_x,trunk_y,height],[column_x,end[1],height],
                   [column_x,end[1],end[2]],end]
    return points


def build_plan():
    local = read(OUT/'local-boundary-plan.json')
    outputs = read(OUT/'branch-output-plan.json')
    ends = {r['holder']:r for r in outputs['output_recipes']}
    pwm = {r['logical_role']:r for r in outputs['chosen_PWM_landings']}
    endpoint = read(OUT/'endpoint-plan.json')
    ports = {k:v for r in endpoint['distribution_boundary'] for k,v in r['resolved_datums'].items()}
    rows = []
    n = 1.05/math.sqrt(3)
    for local_row in local['rows']:
        wire, role = local_row['wire'],local_row['body_role']
        group = {'1':'HY','2':'HP','3':'TY'}[wire[2]]
        index = 0 if role.startswith('F_') else 1 if role.startswith('G_') else 2
        end = local_row['local_boundary_current_candidate_mm'][:]
        if group == 'HY':
            # Individual packing inside the retained seven-mm splice seat.
            side, normal = [(-1.05,-n),(1.05,-n),(0,2*n)][index]
            end[1] += side; end[2] += normal
        if index == 0:
            source = ends[role.split('.')[0]]
            start, direction = source['end_mm'],source['end_departure']
            origin = 'New checked factory-tail insulation boundary; covered lap joint still OPEN'
        elif index == 1:
            source = ports[role]
            start, direction = source['point_mm'],source['departure']
            origin = 'Current WAGO envelope-derived entry; delivery pitch/strip qualification OPEN'
        else:
            source = pwm[role]
            start, direction = source['current_nominal_pad_top_mm'],[0,0,1]
            origin = source['chosen_physical_landing']+' on known1608 copper group; vertical solder departure'
        points = route_points(start,direction,end,group,index)
        cuts, _ = corner_offsets(points,12.6)
        first_free = math.dist(points[0],points[1])-cuts[1]
        last_free = math.dist(points[-2],points[-1])-cuts[-2]
        assert first_free >= 9 and last_free >= 9,(wire,first_free,last_free)
        length = rounded_length(points,12.6)
        rows.append(dict(wire=wire,logical_source=role,group=group,
            material=local_row['material'],area_mm2=.5,insulation_OD_mm=2.1,
            minimum_fixed_radius_mm=12.6,points_mm=points,length_mm=length,
            first_intact_straight_mm=first_free,last_intact_straight_mm=last_free,
            source_basis=origin,endpoint_is_local_insulation_boundary_not_servo_pin=True,
            current_pitch_anchor_open=group=='HP',
            nominal_fit_blank_mm=None,actual_cut_mm=None,route_qualified=False))
    inputs = (SOURCE,OUT/'branch-output-plan.json',OUT/'endpoint-plan.json',
              OUT/'local-boundary-plan.json',OUT/'TailLocalCurrent.FCStd',
              BASE/'OpenPrototypePlan.FCStd',Path(__file__),
              ROOT/'tools/electronics/w5_rounded_path.py',ROOT/'tools/electronics/w5_path_length.py')
    return dict(status='NINE_LOCAL_FIXED_FEEDS_SHARED_PROPOSAL',rows=rows,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in inputs},
        shared_plan='Three separated high lanes180/183/186, separate end columns and preserved local packing. No new connector or factory-lead cut. Remain outside central ATO and below nominal upper body allowance.',
        assembly=['Keep source grips installed; lay loose fixed feed bundles before populated boards.',
            'Keep motor returns on dedicated G_AUX/G_TAIL, not PCB signal ground.',
            'Provide covered factory-tail joins and independent9mm insulation grips before powering.',
            'New fixed pitch anchor and moving-loop qualification required; historical endpoint is not retained support.',
            'AUX delivered padmap remains gate; no candidate wire connected to guessed pads.'],
        remaining=['Common physical restraints and covered joints','Pitch fixed anchor/moving loop',
                   'AUX feed','Rest of80body/legs/legacy920mm','Nominal blanks/whole stock','Final native/export choice'],
        selected=False,stage_completed=False,physical_pass=False)


def main():
    import FreeCAD as A
    import Part
    tick = time.monotonic();plan=build_plan()
    (OUT/'local-feeds-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if '--plan-only' in sys.argv:
        print(json.dumps(dict(status=plan['status'],rows=len(plan['rows']))));return
    d=A.openDocument(str(SOURCE));ctx=A.openDocument(str(BASE/'OpenPrototypePlan.FCStd'))
    tail=A.openDocument(str(OUT/'TailLocalCurrent.FCStd'))
    names=[x.Name for x in (d,ctx,tail)]
    result=dict(status='NINE_LOCAL_FEEDS_PREFLIGHT_PENDING',source_sha256=plan['source_sha256'],
                contacts=[],errors=[],tested_pairs=0,selected=False,physical_pass=False,stage_completed=False)
    try:
        targets={}
        for ob in d.Objects:
            if 'Shape' not in ob.PropertiesList or ob.Shape.isNull():continue
            if ob.TypeId in ('PartDesign::Body','App::Link') or ob.Name.endswith(('_CurrentReference','NominalPCB')) or ob.Name.startswith('BUSsupplier'):
                targets['mount/'+ob.Name]=ob.Shape
        for ob in ctx.Objects:
            if 'Shape' in ob.PropertiesList and not ob.Shape.isNull() and ob.Name.startswith(('P0_','Head_','TailBridge')):
                if ob.Name=='P0_MG92BMount29':continue
                targets['context/'+ob.Name]=ob.Shape
        targets['tail/CurrentTailSupport']=tail.CurrentTailSupport.Shape
        pipes={}
        for row in plan['rows']:
            path=rounded(A,Part,[A.Vector(*p) for p in row['points_mm']],12.6)
            first=path.Edges[0]
            circle=Part.Wire([Part.makeCircle(1.05,first.valueAt(first.FirstParameter),first.tangentAt(first.FirstParameter))])
            shape=path.makePipeShell([circle],True,False)
            assert shape.isValid() and len(shape.Solids)==1 and not shape.check(True),row['wire']
            assert abs(path.Length-row['length_mm'])<1e-6
            pipes[row['wire']]=shape
        def check(n,s,m,t):
            if not s.BoundBox.intersect(t.BoundBox):return
            result['tested_pairs']+=1
            try:
                assert s.isValid() and t.isValid(),'Invalid BRep cannot prove clearance'
                h=s.common(t);assert h.isValid()
                if h.Volume>1e-5:result['contacts'].append(dict(a=n,b=m,volume_mm3=h.Volume,bounds_mm=bounds(h)))
            except Exception as exc:result['errors'].append(dict(a=n,b=m,error=str(exc)))
        for i,(n,s) in enumerate(pipes.items()):
            for m,t in targets.items():check(n,s,m,t)
            for m,t in list(pipes.items())[i+1:]:check(n,s,m,t)
        result.update(status='NINE_FIXED_FEEDS_GEOMETRY_PREFLIGHT_CLEAR' if not result['contacts'] and not result['errors'] else 'NINE_FIXED_FEEDS_SHARED_LAYOUT_CHANGE_REQUIRED',
            rows=len(pipes),radius_mm=12.6,native_wire_histories_not_claimed=True,
            restraints_joints_pitch_motion_and_whole_wiring_open=True)
        if not result['contacts'] and not result['errors']:
            for n,s in pipes.items():
                ob=d.addObject('Part::Feature',n+'_FixedFeedReservation');ob.Shape=s
                ob.addProperty('App::PropertyString','Qualification');ob.Qualification='Fixed route reservation, not editable wire history or restraint/motion acceptance'
            d.saveAs(str(OUT/'LocalFeedsPreflight.FCStd'))
            result['preview_sha256']=sha(OUT/'LocalFeedsPreflight.FCStd')
    finally:
        for name in names:
            if name in A.listDocuments():A.closeDocument(name)
    result.update(worker_wall_seconds=time.monotonic()-tick,finished_utc=datetime.now(timezone.utc).isoformat())
    (OUT/'local-feeds-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False),flush=True)


if __name__=='__main__':main()
