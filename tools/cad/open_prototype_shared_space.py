"""One torso-aware replacement topology; no support rebuild or selection.

Reuses transported packing, but not the obsolete Z178/186/194 routing levels.
The accepted open top is NOT permission to silently redefine the torso datum.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import math
import time

import open_prototype_bundle_spines as B
from open_prototype_wiring_endpoints import ROOT, BASE, read, sha, bounds

OUT = BASE/'wiring-checkpoint'
SOURCE = OUT/'LocalStationsAssembly.FCStd'
EXPECTED = '8cc935807900955b2e8bf50efbc70a13647e22e80910897117b6e63dcc868883'


def build_plan():
    # All three groups change together; endpoints/net assignments stay fixed.
    # HY goes south of the retained source key, HP stays in one horizontal
    # plane, TY uses a 45-degree descent rather than overlapping R15.1 bends.
    specs = [
        ('HY', [[-8,-40,134],[-8,-10,134],[-76,-10,134],
                [-76,-56.8,134],[-76,-56.8,85.2],[-112,-56.8,85.2]],
         [0,1,0], [('XB12',-1.05,-B.N),('XB13',1.05,-B.N),('XS13',0,2*B.N)]),
        ('HP', [[20,-42,149],[-52,-42,149],[-52,26,149]],
         [1,0,0], [('XB22',-1.05,-B.N),('XB23',1.05,-B.N),('XS23',0,2*B.N)]),
        ('TY', [[120,10,142],[-10,10,142],[-10,-45,142],
                [15,-45,142],[39,-45,118],[68,-45,118]],
         [0,1,0], [('XB32',0,2*B.N),('XB33',1.05,-B.N),('XS33',-1.05,-B.N)]),
    ]
    # Separate entire transported cross-sections, not just their centre lines.
    # The first preflight used levels138/146/149: HP/TY crossed only3mm apart
    # and four real contacts followed. This mandatory shared planning invariant
    # now rejects that cause BEFORE FreeCAD; no per-wire offset/fillet retry.
    levels=sorted(points[0][2] for _,points,_,_ in specs)
    bundle_diameter=2*(1.05+2*B.N)
    assert min(b-a for a,b in zip(levels,levels[1:])) >= bundle_diameter+2
    groups = []
    for name, points, frame, packing in specs:
        cuts, _ = B.corner_offsets(points, B.RADIUS)
        parts = B.segments(points)
        first = math.dist(points[0],points[1])-cuts[1]
        last = math.dist(points[-2],points[-1])-cuts[-2]
        assert min(first,last) >= 9-1e-8, (name,first,last)
        groups.append(dict(group=name,centre_points_mm=points,first_free_mm=first,
            last_free_mm=last,rows=[dict(wire=n,segments=B.offsets(parts,frame,s,h))
                                  for n,s,h in packing]))
    paths = [SOURCE, BASE/'OpenPrototypePlan.FCStd',OUT/'TailLocalCurrent.FCStd',
             OUT/'bundle-spines-checks.json',Path(__file__),Path(B.__file__)]
    return dict(status='TORSO_AWARE_SHARED_TOPOLOGY_NOT_SELECTED',groups=groups,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in paths},
        torso_world_bounds_mm=[-120,-100,-2,205,100,158],
        torso_source='OpenPrototypePlan.FCStd/TorsoEnvelope',
        upper_cosmetic_cover_required=False,body_widening=False,
        old_routes_disposition='Z178/186/194 are locally clear reservations ONLY; not torso-contained feeds. Preserve previous sources, do not assemble their exports yet.',
        containment_policy='Report actual swept material outside the valid torso. HY final head transition may cross the boundary deliberately; no other spill is automatically waived. Open-top access is not enclosure acceptance.',
        shared_level_separation=dict(levels_mm=levels,bundle_diameter_mm=bundle_diameter,
            minimum_centre_gap_mm=min(b-a for a,b in zip(levels,levels[1:])),
            required_clear_margin_mm=2),
        previous_preflight=dict(contacts=4,tested_pairs=73,errors=0,worker_seconds=24.938,
            cause='HP/TY complete cross sections crossed only3mm apart; no commercial/printed-part contacts. HY outside volume is at retained head exit, not a whole-body spill waiver.'),
        source_fanouts_and_independent_restraints_open=True,
        pitch_fixed_station_and_moving_loop_above_roof_need_reconciliation=True,
        selected=False,stage_completed=False,physical_pass=False)


def main():
    import FreeCAD as A
    import Part
    tick=time.monotonic()
    assert sha(SOURCE)==EXPECTED, 'Receive any changed source before starting'
    plan=build_plan()
    (OUT/'shared-space-plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
    docs=[A.openDocument(str(p)) for p in (SOURCE,BASE/'OpenPrototypePlan.FCStd',OUT/'TailLocalCurrent.FCStd')]
    doc,ctx,tail=docs
    result=dict(status='PENDING',contacts=[],errors=[],outside_torso=[],wire_rows=[],
        tested_changed_pairs=0,source_sha256=plan['source_sha256'],
        selected=False,stage_completed=False,physical_pass=False)
    try:
        torso=ctx.TorsoEnvelope.Shape
        assert torso.isValid() and len(torso.Solids)==1 and not torso.check(True)
        result['actual_torso_bounds_mm']=bounds(torso)
        targets={}
        for o in doc.Objects:
            if 'Shape' not in o.PropertiesList or o.Shape.isNull() or o.Name=='BUS_CP2':continue
            if o.TypeId in ('PartDesign::Body','App::Link') or o.Name.endswith(('_CurrentReference','NominalPCB','_CP2')) or o.Name.startswith('BUSsupplier'):
                targets['mount/'+o.Name]=o.Shape
        for o in ctx.Objects:
            if 'Shape' in o.PropertiesList and not o.Shape.isNull() and o.Name.startswith(('P0_','Head_','TailBridge')) and o.Name!='P0_MG92BMount29':
                targets['context/'+o.Name]=o.Shape
        targets['tail/CurrentTailSupport']=tail.CurrentTailSupport.Shape
        pipes={};paths={}
        for group in plan['groups']:
            for row in group['rows']:
                edges=[]
                for s in row['segments']:
                    p,q=A.Vector(*s['start']),A.Vector(*s['end'])
                    edges.append(Part.makeLine(p,q) if s['kind']=='line' else Part.Arc(p,A.Vector(*s['mid']),q).toShape())
                for a,b in zip(edges,edges[1:]):
                    assert (a.valueAt(a.LastParameter)-b.valueAt(b.FirstParameter)).Length<1e-7
                    assert a.tangentAt(a.LastParameter).dot(b.tangentAt(b.FirstParameter))>1-1e-7
                minimum=min(e.Curve.Radius for e in edges if isinstance(e.Curve,Part.Circle))
                assert minimum>=12.6-1e-7
                path=Part.Wire(edges);first=edges[0]
                section=Part.Wire([Part.makeCircle(1.05,first.valueAt(first.FirstParameter),first.tangentAt(first.FirstParameter))])
                pipe=path.makePipeShell([section],True,False)
                assert pipe.isValid() and len(pipe.Solids)==1 and not pipe.check(True)
                outside=pipe.cut(torso)
                assert outside.isValid(), 'Invalid subtraction is not containment'
                if outside.Volume>1e-5:
                    result['outside_torso'].append(dict(wire=row['wire'],group=group['group'],
                        volume_mm3=outside.Volume,bounds_mm=bounds(outside),
                        disposition='Inspect real head exit' if group['group']=='HY' else 'Not automatically allowed by open top'))
                pipes[row['wire']]=pipe;paths[row['wire']]=path
                result['wire_rows'].append(dict(wire=row['wire'],group=group['group'],length_mm=path.Length,
                    minimum_actual_radius_mm=minimum,start_mm=row['segments'][0]['start'],
                    end_mm=row['segments'][-1]['end']))
        def check(n,s,m,t):
            if not s.BoundBox.intersect(t.BoundBox):return
            result['tested_changed_pairs']+=1
            try:
                assert s.isValid() and t.isValid(),'Invalid BRep cannot prove clearance'
                hit=s.common(t);assert hit.isValid()
                if hit.Volume>1e-5:result['contacts'].append(dict(a=n,b=m,volume_mm3=hit.Volume,bounds_mm=bounds(hit)))
            except Exception as e:result['errors'].append(dict(a=n,b=m,error=str(e)))
        for i,(n,s) in enumerate(pipes.items()):
            for m,t in targets.items():check(n,s,m,t)
            for m,t in list(pipes.items())[i+1:]:check(n,s,m,t)
        for group in plan['groups']:
            names=[r['wire'] for r in group['rows']]
            for i,n in enumerate(names):
                for m in names[i+1:]:
                    assert paths[n].distToShape(paths[m])[0]>=2.1-1e-6
        result['status']='TOPOLOGY_PREFLIGHT_CLEAR_WITH_RECORDED_CONTAINMENT' if not result['contacts'] and not result['errors'] else 'SHARED_TOPOLOGY_REQUIRES_LAYOUT_CHANGE'
        # No native/support export from a failed or unclassified envelope gate.
        result['full_wiring_or_enclosure_acceptance']=False
    finally:
        for d in docs:A.closeDocument(d.Name)
    result.update(worker_wall_seconds=time.monotonic()-tick,finished_utc=datetime.now(timezone.utc).isoformat())
    (OUT/'shared-space-checks.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=result['status'],contacts=result['contacts'],errors=result['errors'],
        outside_torso=result['outside_torso'],tested_pairs=result['tested_changed_pairs'],
        worker_seconds=result['worker_wall_seconds'])),flush=True)


if __name__=='__main__':main()
