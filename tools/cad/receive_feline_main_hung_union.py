"""Receive the VALID unrefined union, without changing received local actors.

OCC removeSplitter invalidates this already valid one-solid union. Retain the
valid Boolean result and all25 original actor bytes; not a geometry repair.
"""
import gzip,hashlib,json,time,zipfile
from pathlib import Path
import FreeCAD
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from receive_feline_main_ato_gallery import selected
from receive_feline_rrp_shared_height import load
from feline_atomic_save import save_json


def main():
    tick=time.monotonic();sf=OUT/'n01-MAIN-hung-bay-local.json';p=json.loads(sf.read_text())
    assert p['status']=='MAIN_HUNG_BAY_LOCAL_HOLDS' and p['failures']==['actual_rooted_Pi_print_union']
    for f,h in p['source_sha256'].items():assert sha(ROOT/f)==h,f
    actors=load(p);root=actors['MainSupported:root'];pp,_,pins=selected(OUT/'n01-shared-Pi-carrier-r3-core-received.json','geometry',lambda n:n=='SharedPi:Carrier')
    parent=pp['SharedPi:Carrier'];union=root.copy().fuse(parent.copy())
    assert root.isValid() and parent.isValid() and union.isValid() and len(union.Solids)==1
    common=root.copy().common(parent.copy());assert common.isValid() and common.Volume>1
    # Curved-face volume integration differs by .0021mm3 over12075mm3.
    # Verify actual Boolean set inclusion instead of an arbitrary integral
    # residual: no source material missing and no material outside either.
    witnesses={'missing_root':root.copy().cut(union.copy()),'missing_parent':parent.copy().cut(union.copy()),
        'new_outside_both_sources':union.copy().cut(root.copy()).cut(parent.copy())}
    assert all((s.isNull() or s.isValid()) and s.Volume<1e-5 for s in witnesses.values())
    dims=[union.BoundBox.XLength,union.BoundBox.YLength,union.BoundBox.ZLength];assert max(dims)<250
    pf=ROOT/p['pair_rows'];assert sha(pf)==p['pair_rows_sha256'];checks=json.loads(gzip.decompress(pf.read_bytes()))
    checks['actual_rooted_Pi_print_union']=dict(ok=True,valid_unmodified_Boolean=True,removeSplitter_NOT_used=True,
        positive_common_mm3=common.Volume,combined_solids=1,combined_bounds_mm=dims,
        actual_Boolean_set_inclusion_residuals_mm3={k:s.Volume for k,s in witnesses.items()},
        curved_volume_integral_residual_mm3=union.Volume-root.Volume-parent.Volume+common.Volume)
    assert all(v['ok'] for v in checks.values())
    stem=OUT/'n01-MAIN-hung-union-received';arc=stem.with_suffix('.breps.zip');rows=stem.with_suffix('.pairs.json.gz')
    with zipfile.ZipFile(ROOT/p['bundle']) as source,zipfile.ZipFile(arc,'w',zipfile.ZIP_DEFLATED) as z:
        for r in p['geometry']:
            raw=source.read(r['entry']);assert hashlib.sha256(raw).hexdigest()==r['sha256'];z.writestr(r['entry'],raw)
        raw=union.exportBrepToString().encode();z.writestr('valid-main-Pi-union.brep',raw);uh=hashlib.sha256(raw).hexdigest()
    rows.write_bytes(gzip.compress(json.dumps(checks,separators=(',',':')).encode(),mtime=0))
    pins.update({f.relative_to(ROOT).as_posix():sha(f) for f in (sf,ROOT/p['bundle'],pf,Path(__file__))})
    r=dict(p,status='MAIN_HUNG_LOCAL_CONSTRUCTIVE_PLAN_RECEIVED_WORLD_TOOLS_OPEN',source_sha256=pins,
        bundle=arc.relative_to(ROOT).as_posix(),bundle_sha256=sha(arc),pair_rows=rows.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(rows),
        checks=len(checks),failures=[],valid_combined_print_union_entry='valid-main-Pi-union.brep',valid_combined_print_union_sha256=uh,
        adopted_local_worker_seconds=p['worker_seconds'],worker_seconds=round(time.monotonic()-tick,3),
        byte_identical_actor_count=25,actual_geometry_changed=False,full_world_motion_and_assembly_NOT_received=True)
    save_json(stem.with_suffix('.json'),r);print(r['status'],r['checks'],r['worker_seconds'],dims,flush=True)


if __name__=='__main__':main()
