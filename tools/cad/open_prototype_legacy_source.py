"""Joint battery/F0/post-F0/ground gate against the current OPEN mounts.

Reuse three pinned source snapshots, not the obsolete ground landing or920mm.
No supplier pin claim, native rebuild, stock selection or physical acceptance.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import math
import time

import open_prototype_bundle_spines as B
from whole_cat_source_bay_plan import Route
import whole_cat_source_bay_plan as R
from open_prototype_wiring_endpoints import ROOT, BASE, read, sha, bounds

OUT = BASE/'wiring-checkpoint'
CONTEXT = BASE/'OpenPrototypePlan.FCStd'
MOUNTS = OUT/'LocalStationsAssembly.FCStd'
META = BASE.parent/'interfaces.json'


def build_plan():
    ep = read(OUT/'endpoint-plan.json')
    ground = next(r for r in ep['body_conductors'] if r['id']=='W001')
    start, end = [e['point_mm'] for e in ground['ends']]
    assert math.dist(start, [-73,-58.8,57]) < 1e-7
    assert math.dist(end, [-89,-73.75,100.99]) < 1e-7
    assert ground['ends'][1]['departure']==[0,1,0]
    # One common lower-source bay: two turns rise north of F0, then turn
    # toward the CURRENT inward-facing G1 port. Not the old vertical landing.
    route=Route('W001',start,[1,0,0],3.1,12.4,19,[ground['a'],ground['b']])
    route.line(10);route.turn([0,1,0],12.4);route.turn([0,0,1],12.4)
    route.line(end[2]-route.p[2]-12.4);route.turn([-1,0,0],12.4)
    route.line(route.p[0]-end[0]-12.4);route.turn([0,-1,0],12.4)
    route.line(route.p[1]-end[1]);route.finish(end,[0,-1,0])
    # Adjacent orthogonal circular bends are tangent-continuous without a
    # zero-length edge. The generic polyline helper deliberately disallows
    # touching offset budgets; use explicit arcs, not a wire micro-offset.
    parts=[dict(kind=s['kind'],start=s['start_mm'],end=s['end_mm'],
        **(dict(t0=s['tangent'],t1=s['tangent']) if s['kind']=='line' else
           dict(mid=s['mid_mm'],t0=s['start_tangent'],t1=s['end_tangent'],
                angle=s['angle_rad']))) for s in route.row['segments']]
    length = sum(math.dist(s['start'],s['end']) if s['kind']=='line'
                 else s['angle']*12.4 for s in parts)
    metadata = {r['id']:r for r in read(META)['nominal_source_wires']}
    rows = []
    for name in ('W075','W076_FACTORY','W076_EXTENSION'):
        m = metadata[name]
        rows.append(dict(id=name,native=name+'_CP2',a=m['a'],b=m['b'],
            OD_mm=m['OD_mm'],centreline_mm=m['centerline_length_mm'],
            termination_allowance_mm=m['termination_allowance_in_blank_mm'],
            required_blank_mm=m['nominal_blank_mm'],
            nominal_fit_blank_mm=math.ceil(m['nominal_blank_mm']),
            limit_mm=m['limit_mm'],basis=m['dimension_basis'],
            snapshot_reuse_requires_volume_and_current_mount_gate=True))
    rows.append(dict(id='W001',native='W001_CurrentRoute',a=ground['a'],b=ground['b'],
        OD_mm=3.1,minimum_radius_mm=12.4,segments=parts,centreline_mm=length,
        termination_allowance_mm=19,required_blank_mm=length+19,
        nominal_fit_blank_mm=math.ceil(length+19),
        old150mm_limit_exceeded=length+19>150,
        basis='Retained LAPP0107001/R12.4;14mm WAGO strip plus5mm solder allowance; cup/entry positions provisional'))
    files=[CONTEXT,MOUNTS,META,OUT/'endpoint-plan.json',OUT/'routing-scope-plan.json',
           OUT/'TailLocalCurrent.FCStd',Path(__file__),Path(B.__file__),Path(R.__file__)]
    return dict(status='JOINT_LEGACY_SOURCE_PLAN_NOT_SELECTED',rows=rows,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in files},
        retained_distribution_casings=20,extra_electrical_connections=0,
        W076_factory_and_extension_are_one_logical_conductor=True,
        unknown_U1_not_connected=True,old920mm_not_a_current_stock_total=True,
        independent_restraints_and_whole_stage_stock_open=True,
        selected=False,stage_completed=False,physical_pass=False,
        assembly=['Battery and balance/monitor connections absent; no energized work.',
            'Prepare marked robot XT60 cups, both F0 factory tails and protected post-F0 extension on bench; never splice before F0.',
            'Retain two allocated S0 rings; route to current G1 entry, not old vertical landing.',
            'Provide independent insulation grips at both ends before connector mating; WAGO pad is not a wire restraint.',
            'Qualify delivered lead/cup/strip/heat/fit/ATO access in phase2; do not cut hardware from these nominal values.'])


def main():
    import FreeCAD as A
    import Part
    tick=time.monotonic();plan=build_plan()
    (OUT/'legacy-source-plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
    docs=[A.openDocument(str(p)) for p in (CONTEXT,MOUNTS,OUT/'TailLocalCurrent.FCStd')]
    ctx,mount,tail=docs
    result=dict(status='PENDING',contacts=[],errors=[],outside_torso=[],
        rows=[],tested_pairs=0,source_sha256=plan['source_sha256'],
        native_exports_rebuilt=0,selected=False,stage_completed=False,physical_pass=False)
    try:
        targets={}
        for o in mount.Objects:
            if 'Shape' not in o.PropertiesList or o.Shape.isNull() or o.Name=='BUS_CP2':continue
            if o.TypeId in ('PartDesign::Body','App::Link') or o.Name.endswith(('_CurrentReference','NominalPCB','_CP2')) or o.Name.startswith('BUSsupplier'):
                targets['current/'+o.Name]=o.Shape
        base_names={'XT60_CP2','F0_CP2','PostF0Splice_CP2','S0_body_CP2',
            'S0_neck_CP2','S0_key_CP2','S0_ring_IN','S0_ring_OUT'}
        for o in ctx.Objects:
            if 'Shape' in o.PropertiesList and not o.Shape.isNull() and (
                o.Name in base_names or o.Name.startswith(('P0_','Head_','TailBridge','MTA_'))):
                if o.Name!='P0_MG92BMount29':targets['retained/'+o.Name]=o.Shape
        targets['tail/CurrentTailSupport']=tail.CurrentTailSupport.Shape
        shapes={}
        for row in plan['rows']:
            if 'segments' not in row:
                shape=ctx.getObject(row['native']).Shape.copy()
            else:
                edges=[Part.makeLine(A.Vector(*s['start']),A.Vector(*s['end']))
                    if s['kind']=='line' else Part.Arc(A.Vector(*s['start']),
                    A.Vector(*s['mid']),A.Vector(*s['end'])).toShape() for s in row['segments']]
                path=Part.Wire(edges)
                assert abs(path.Length-row['centreline_mm'])<1e-6
                section=Part.Wire([Part.makeCircle(row['OD_mm']/2,
                    path.Edges[0].valueAt(path.Edges[0].FirstParameter),
                    path.Edges[0].tangentAt(path.Edges[0].FirstParameter))])
                shape=path.makePipeShell([section],True,False)
            assert shape.isValid() and len(shape.Solids)==1 and not shape.check(True)
            # Sanity check the reused constant-section capped tube against
            # its recorded path length; this is not a physical wire measure.
            implied=shape.Volume/(math.pi*(row['OD_mm']/2)**2)
            assert abs(implied-row['centreline_mm'])<1e-4,(row['id'],implied)
            shapes[row['id']]=shape
            result['rows'].append(dict(id=row['id'],nominal_fit_blank_mm=row['nominal_fit_blank_mm'],
                centreline_mm=row['centreline_mm'],volume_length_match=True))
        def check(n,s,m,t):
            if not s.BoundBox.intersect(t.BoundBox):return
            result['tested_pairs']+=1
            try:
                assert s.isValid() and t.isValid()
                hit=s.common(t);assert hit.isValid()
                if hit.Volume>1e-5:result['contacts'].append(dict(a=n,b=m,
                    volume_mm3=hit.Volume,bounds_mm=bounds(hit)))
            except Exception as e:result['errors'].append(dict(a=n,b=m,error=str(e)))
        for i,(n,s) in enumerate(shapes.items()):
            outside=s.cut(ctx.TorsoEnvelope.Shape);assert outside.isValid()
            if outside.Volume>1e-5:result['outside_torso'].append(dict(wire=n,
                volume_mm3=outside.Volume,bounds_mm=bounds(outside)))
            for m,t in targets.items():check(n,s,m,t)
            for m,t in list(shapes.items())[i+1:]:check(n,s,m,t)
        # Record the WHOLE preserved distribution occupation for the next
        # shared source/body plan. Bounds select pairs only, never clearance.
        result['distribution_occupation']=[dict(native=o.Name,bounds_mm=bounds(o.Shape))
            for o in mount.Objects if o.Name.endswith('_CP2') and o.Name.rsplit('_CP2',1)[0]
            in ('FL_P','FL_G','D_FL','RL_P','RL_G','P_SYS','P_FRONT','P_REAR','D_RL','G2',
                'FR_P','FR_G','D_FR','RR_P','RR_G','G1','D_RR','P_AUX','G_AUX','G_TAIL')]
        assert len(result['distribution_occupation'])==20
        result['status']='LEGACY_SOURCE_STATIC_CLEAR_RESTRAINTS_OPEN' if not any(
            result[k] for k in ('contacts','errors','outside_torso')) else 'LEGACY_SOURCE_COMMON_BAY_CHANGE_REQUIRED'
    finally:
        for d in docs:A.closeDocument(d.Name)
    assert all(sha(ROOT/p)==h for p,h in plan['source_sha256'].items())
    result.update(worker_seconds=time.monotonic()-tick,
        finished_utc=datetime.now(timezone.utc).isoformat())
    (OUT/'legacy-source-checks.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('status','contacts','errors','outside_torso','rows','tested_pairs','worker_seconds')}),flush=True)


if __name__=='__main__':main()
