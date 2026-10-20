"""Complete two full nylon band bays in ONE printed ForePanel, not a nibble.

Old slots stopped at the floor layer; raised ribs met the full band. Keep all
63 other actors. A proven material subset inherits rest clearance; positive
roots/single connected print are verified again. No geometry move or SKU change.
"""
import copy,hashlib,json,time,zipfile
from pathlib import Path
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_main_hung_context import compose
from receive_feline_rrp_shared_height import load
from receive_feline_factory_saddle_plan import box
from feline_fore_power_pair import SolidQueries
from feline_atomic_save import save_json


def main():
    tick=time.monotonic();world,parts,_,pins,_=compose()
    sf=OUT/'n01-MTA-S1-complete-bypass.json';prior=json.loads(sf.read_text());actors=load(prior)
    scene=OUT/'n01-MTA-S1-complete-bypass-scene.json';observed=json.loads(scene.read_text())
    assert observed['failures']==['ArcGrip:W044:band|LowerBay:ForePanel']
    for r in (prior,observed):
        for p,h in r['source_sha256'].items():assert sha(ROOT/p)==h,p
    panel='LowerBay:ForePanel';before=actors[panel];floor=before.copy();cutters={}
    for w in ('W044','W052'):
        name='ArcGrip:'+w+':band';b=actors[name].BoundBox
        cutter=box([b.XMin-.2,b.YMin-.2,b.ZMin-.2],[b.XMax+.2,b.YMax+.2,b.ZMax+.2])
        cutters[name]=cutter;floor=floor.cut(cutter)
    assert floor.isValid() and len(floor.Solids)==1
    added=floor.cut(before);assert added.isNull() or added.isValid();assert added.Volume<1e-5
    actors[panel]=floor;allparts={m:s for m,s in parts.items() if m not in prior['retired']};allparts.update(actors)
    members=prior['print_groups'][panel];unit=floor.multiFuse([allparts[m] for m in members if m!=panel])
    assert unit.isValid() and len(unit.Solids)==1
    b=unit.BoundBox;assert max(b.XLength,b.YLength,b.ZLength)<250
    roots=copy.deepcopy(prior['positive_roots']);contracts={};query=SolidQueries()
    for w in ('W044','W052'):
        root=actors['ArcGrip:'+w+':pad'].common(floor);assert root.isValid() and root.Volume>1e-5
        roots[w]['parent_actual_overlap_mm3']=root.Volume
        for suffix in ('band','head'):
            name='ArcGrip:'+w+':'+suffix;common=actors[name].common(floor)
            assert common.isNull() or common.isValid()
            gap=query.distance(actors[name],floor);assert gap>=.2-1e-6 and common.Volume<1e-5,(name,gap,common.Volume)
            key='|'.join(sorted((name,panel)))
            contracts[key]=dict(ok=True,gap_mm=gap,minimum_mm=.2,whole_common_mm3=common.Volume,
                exact_own_nylon_slot_pair=[name,panel],full_selected_budget_not_shrunk=True,
                full_height_bay_not_floor_only=True,foreign_margin_NOT_changed_mm=1.25,physical_print_fit_OPEN=True)
    dest=OUT/'n01-MTA-full-band-slots.json';assert not dest.exists(),'Receive existing full-band floor result first'
    archive=dest.with_suffix('.breps.zip');geometry=[]
    with zipfile.ZipFile(ROOT/prior['bundle']) as src,zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for i,r in enumerate(prior['geometry']):
            m=r['name'];raw=floor.exportBrepToString().encode() if m==panel else src.read(r['entry'])
            if m!=panel:assert hashlib.sha256(raw).hexdigest()==r['sha256']
            entry=str(i)+'.brep';z.writestr(entry,raw);geometry.append(dict(r,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (sf,ROOT/prior['bundle'],scene,ROOT/observed['pair_rows'],Path(__file__))})
    result=dict(prior,status='COMPLETE_MTA_KIT_REST_RECEIVED_STATIC_MOTION_ACCESS_OPEN',source_sha256={**prior['source_sha256'],**pins},
        geometry=geometry,bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),positive_roots=roots,
        changed_actors=[panel],byte_identical_actors_from_prior=63,completed_static=[],completed_motion=[],
        inherited_rest_by_material_subset=dict(actor=panel,new_material_outside_original_mm3=added.Volume,
            actual_removed_mm3=before.cut(floor).Volume,valid_single_solid=True,connected_print_solids=1,
            print_envelope_mm=[b.XLength,b.YLength,b.ZLength],all_other_actors_byte_identical=True),
        named_interface_pairs=contracts,reuse_scene=dict(path=scene.relative_to(ROOT).as_posix(),sha256=sha(scene)),
        full_scene_and_tools_still_OPEN=True,N01_complete=False,native_changed=False,physical_pass=False,
        worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result);print('ONE_FORE_PANEL_FULL_BAND_BAYS_RECEIVED',len(contracts),result['worker_seconds'],flush=True)


if __name__=='__main__':main()
