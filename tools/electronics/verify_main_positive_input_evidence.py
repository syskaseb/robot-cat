"""Recover accurate scope/provenance of unselected MAIN candidates.

No repeated current-body collision screen, native build or route search.
Read saved exact centreline geometry and current generators, rejecting stale
unused Bezier metadata as a radius qualification for R2 exact arcs.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys,math
import main_positive_input_route_r2 as R2
R=R2.R;M=R.M;ROOT=R.ROOT
OUT=ROOT/'hardware/electronics/full-cat/main-positive-source-review-r1'

def main():
    import FreeCAD as A
    import Part
    OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'validation.json').exists()
    begin=datetime.now(timezone.utc);paths=R2.geometry();measurements={};hashes={}
    for name,edges in paths.items():
        for i,e in enumerate(edges):
            p=R.OUT/(f'{name}_{i}_CENTERLINE.brep');s=Part.Shape();s.read(str(p));hashes[p.relative_to(ROOT).as_posix()]=M.sha(p)
            assert abs(s.Length-e.Length)<1e-6
            assert len(s.Edges)==1
            assert all((s.Vertexes[j].Point-e.Vertexes[j].Point).Length<1e-6 for j in range(len(e.Vertexes)))
        measurements[name]=sum(e.Length for e in edges)
    pref_radius=R.B.radius_bound(R.PREF)
    exact=[e.Curve.Radius for n,es in paths.items() for e in es if hasattr(e.Curve,'Radius')]
    assert pref_radius>=6 and min(exact)>=6-1e-7
    assert measurements['W043']+22<=40 and measurements['W077']+8<=80 and measurements['W078']+20<=210
    source=ROOT/'hardware/electronics/full-cat/main-positive-source-finish-r1/checks.json'
    failed=json.loads(source.read_text(encoding='utf-8'));assert failed['status']=='REJECTED' and not failed['native_export_complete']
    assert {h['owner'] for h in failed['hits']}=={'P0Support0'}
    parent=ROOT/'hardware/manufacturing/one-batch-prototype-r41/selection.json'
    old_gap=math.hypot(25.5-(-50.5),-50.5-(-11))
    assert old_gap>50
    for p in [source,parent,ROOT/'tools/electronics/main_positive_input_route_common_r2.py',ROOT/'tools/electronics/main_positive_input_route_r2.py',Path(__file__),ROOT/'hardware/reference/fhac0001zxj-2026-10-02/Littelfuse-FHAC-datasheet-mirror.pdf']:
        hashes[p.relative_to(ROOT).as_posix()]=M.sha(p)
    end=datetime.now(timezone.utc)
    result=dict(status='RECOVERED_UNSELECTED_SOURCE_AND_ROUTE_BLOCKER',selected=False,physical_pass=False,W5_complete=False,
        parent_selection='one-batch-prototype-r41',parent_unchanged=True,
        original_prefuse_XY_lower_bound_mm=old_gap,original_prefuse_limit_mm=50,
        holder_model='FHAC0001ZXJ',factory_lead_minimum_mm=84.5,source_body_span_mm=[49,51],
        route_lengths_mm=measurements,nominal_blanks_mm=R.LIMITS,total_nominal_blanks_mm=sum(R.LIMITS.values()),
        proposed_new_blanks_not_selected=True,red_shared_stock_remaining_if_selected_mm=1000-290.24916022252154-210,
        prefuse_Bezier_radius_bound_mm=pref_radius,exact_arc_minimum_radius_mm=min(exact),
        stale_R2_metadata='R1 shared emitter left old unused RISE/FAN Bezier poles,180mm red/300mm input intent. They are NOT R2 geometry or accepted final recipe. Actual saved R2 centreline equals current R2 geometry; exact factoryR10 and finalR6 arcs,40/80/210 blanks.',
        script_recovery='R1 original emitter restored to its executed hash42be9ab2; R2 shared emitter43b75ca5 preserved as main_positive_input_route_common_r2.py. R2 import changed only to this same byte-identical shared emitter. Current dependency hashes and exact geometry verified here, not claimed as a rerun of body checks.',
        source_mount_blocker=failed['hits'],source_mount_not_built=True,new_STLs=0,
        output_open=['W078 Deck intersection needs full passage.',
            'R2 insulated red wire has soft-envelope contacts0.5135508874 and0.1044893523mm3 with R40 black sleeve, not bare copper. Do not claim physical fit or global clearance.',
            'Splice sleeves, two-end strain relief, final MAIN support/insulation and source holder mount remain incomplete.'],
        next_safe_independent_work='K2/K3: concrete missing commercial parts/tools/stock, without selecting these routes or repeating the rejected support corridor.',
        sources_sha256=hashes,started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds())
    M.save(OUT/'validation.json',result)
    print(json.dumps(dict(status=result['status'],source_blocker=result['source_mount_blocker'],old_gap_mm=old_gap,new_STLs=0)),flush=True)

if __name__=='__main__':main()
