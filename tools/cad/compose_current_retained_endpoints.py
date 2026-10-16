"""Reconcile19 retained guide endpoints without mutating frozen old registers.

Coordinates come from the current pinned route inventory. Older point tables
are comparison evidence only. This is not a whole harness/terminal fit proof.
"""
import copy
import json
import math
import time
from pathlib import Path
from plan_current_harness_interfaces import ROOT,OUT,SHA


def endpoints(segments):
    result=[]
    for i,r in enumerate(segments):
        parts=r['parts'];assert parts
        for a,b in zip(parts,parts[1:]):assert math.dist(a['end'],b['start'])<1e-5
        for side,p in [('start',parts[0]['start']),('end',parts[-1]['end'])]:
            assert len(p)==3 and all(math.isfinite(x) for x in p)
            internal=(i>0 and side=='start') or (i<len(segments)-1 and side=='end')
            result.append(dict(segment_index=i,side=side,point_world_mm=copy.deepcopy(p),
                boundary='Separate recipe portion; DO NOT bridge its connector/splice gap' if internal else 'Current outer guide endpoint; nominal terminal fit remains a gate'))
    return result


def compose(inventory,register,ground):
    older={r['id']:r for r in register['body_conductors']};rows=[]
    for wid,g in sorted(inventory['guides'].items()):
        points=endpoints(g['segments']);old=older[wid]
        for e in points:
            if (e['segment_index']==0 and e['side']=='start') or (e['segment_index']==len(g['segments'])-1 and e['side']=='end'):
                known=[q for q in old['current_ends'] if q.get('point_mm') is not None]
                if known:
                    close=min(known,key=lambda q:math.dist(q['point_mm'],e['point_world_mm']))
                    e['nearest_old_register_role']=close['role']
                    e['distance_to_old_register_mm']=math.dist(close['point_mm'],e['point_world_mm'])
                else:e['old_register_comparison']='No coordinate supplied; never substitute zero'
        if wid in ground.get('G1_same_ground_port_mapping',{}):
            # The same GND rail, explicit existing cavity assignment. Do NOT
            # infer a signal pinout from coordinate order or a case bbox.
            labels=ground['routes'][wid]['endpoints']
            side=next(i for i,label in enumerate(labels) if label.startswith('G1.'))
            point=points[0 if side==0 else -1]
            point['current_G1_cavity']='G1.'+str(ground['G1_same_ground_port_mapping'][wid])
            point['cavity_basis']='Existing ground-tree-plan G1_same_ground_port_mapping and route endpoint side, all on sameGND net'
        rows.append(dict(wire=wid,recipe_file=g['recipe_file'],nominal_geometry_endpoints=points,
            older_register_roles=old['roles'],older_register_points_are_NOT_current_coordinate_authority=True))
    assert len(rows)==19 and sum(len(r['nominal_geometry_endpoints']) for r in rows)==40
    return rows


def run():
    tick=time.monotonic();files=[OUT/'retained-body-guides-inventory.json',OUT/'harness-interfaces-plan.json',OUT/'ground-tree-plan.json',Path(__file__)]
    inventory,register,ground=[json.loads(f.read_text()) for f in files[:3]]
    # Every embedded route must match the existing nominal material receipt;
    # there is no interpolation of old points or silently shortened wire.
    for name,digest in inventory['source_sha256'].items():assert SHA(ROOT/name)==digest,name
    rows=compose(inventory,register,ground)
    files.extend(OUT/g['recipe_file'] for g in inventory['guides'].values())
    result=dict(status='CURRENT19_RETAINED_GUIDE_ENDPOINTS_RECONCILED_NOT_WHOLE_W5',
        nets=19,guide_portions=20,guide_endpoints=40,rows=rows,
        source_priority='Current pinned actual recipe parts, explicit same-rail mappings; older register points only compared, never reused as final world coordinates.',
        old_outer_points_differing=sum(e.get('distance_to_old_register_mm',0)>1e-5 for r in rows for e in r['nominal_geometry_endpoints']),
        excludes='36 servo core/flex interfaces and remaining25 fixed nets have their separate current receipts. This count is guide boundaries, NOT a new physical cut/connector count.',
        open=['Bind current native cases/terminal fit and final whole assembly selection',
              'Current combined mounting/service/stock/W5'],
        source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in set(files)},
        worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,physical_pass=False)
    (OUT/'current-retained-endpoints.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('nets','guide_portions','guide_endpoints','old_outer_points_differing','worker_seconds')}))


if __name__=='__main__':run()
