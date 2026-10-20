"""Two complete own floor bays at1.5mm, not a case or wire position retry.

Only ForePanel loses material. Actual case common volumes, all existing load
roots and the complete print union are checked; foreign1.25 stays unchanged.
"""
import hashlib,json,time,zipfile
from pathlib import Path
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_main_hung_context import compose
from receive_feline_rrp_shared_height import load
from receive_feline_factory_saddle_plan import box
from feline_fore_power_pair import SolidQueries
from feline_atomic_save import save_json


def main():
    tick=time.monotonic();world,parts,meta,pins,docs=compose()
    sf=OUT/'n01-MTA-bonded-root-unions.json';r=json.loads(sf.read_text());actors=load(r)
    of=sf.with_name(sf.stem+'-scene.json');observed=json.loads(of.read_text())
    assert observed['failures']==['LowerBay:ForePanel|Ref_Material_W044_Joint_0_0']
    for rec in (r,observed):
        for p,h in rec['source_sha256'].items():assert sha(ROOT/p)==h,p
    panel='LowerBay:ForePanel';before=actors[panel].copy();floor=before.copy();query=SolidQueries();bays={}
    for w in ('W044','W052'):
        n='Ref_Material_'+w+'_Joint_0_0';case=actors[n];b=case.optimalBoundingBox(False,False)
        oldgap=query.distance(before,case);oldcommon=before.common(case)
        assert (oldcommon.isNull() or oldcommon.isValid()) and oldcommon.Volume<1e-5
        assert abs(oldgap-1.2)<1e-5
        cutter=box([b.XMin-1.5,b.YMin-1.5,b.ZMin-1.5],[b.XMax+1.5,b.YMax+1.5,b.ZMax+1.5])
        floor=floor.cut(cutter);assert floor.isValid() and len(floor.Solids)==1
        gap=query.distance(floor,case);common=floor.common(case);assert common.isNull() or common.isValid()
        assert common.Volume<1e-5 and gap>=1.5-1e-6
        bays[w]=dict(old_gap_mm=oldgap,new_gap_mm=gap,whole_case_axis_aligned_bay_margin_mm=1.5,
            actual_common_mm3=common.Volume,bbox_is_intentional_cut_budget_NOT_contact_proof=True)
    extra=floor.cut(before);assert (extra.isNull() or extra.isValid()) and extra.Volume<1e-5
    actors[panel]=floor;roots={}
    for w in ('W044','W052'):
        for prefix in ('CaseBase:'+w+'_Joint','ArcGrip:'+w+':pad','InputGrip:'+w+':pad'):
            c=actors[prefix].common(floor);assert c.isValid() and c.Volume>1e-5
            roots[prefix]=dict(parent=panel,current_positive_overlap_mm3=c.Volume)
    unit=floor.multiFuse([actors[n] if n in actors else parts[n] for n in r['print_groups'][panel] if n!=panel])
    assert unit.isValid() and len(unit.Solids)==1
    b=unit.BoundBox;size=[b.XLength,b.YLength,b.ZLength];assert max(size)<250
    dest=OUT/'n01-MTA-owned-case-bays.json';assert not dest.exists();archive=dest.with_suffix('.breps.zip');geometry=[]
    with zipfile.ZipFile(ROOT/r['bundle']) as src,zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as target:
        for i,row in enumerate(r['geometry']):
            n=row['name'];raw=floor.exportBrepToString().encode() if n==panel else src.read(row['entry'])
            if n!=panel:assert hashlib.sha256(raw).hexdigest()==row['sha256']
            entry=str(i)+'.brep';target.writestr(entry,raw);geometry.append(dict(row,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (sf,ROOT/r['bundle'],of,ROOT/observed['pair_rows'],Path(__file__))})
    result=dict(r,source_sha256={**r['source_sha256'],**pins},geometry=geometry,bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),
        changed_actors=[panel],removed_actor_aliases=[],byte_identical_actors_from_prior=71,
        own_complete_case_bays=bays,case_bay_floor_new_material_mm3=extra.Volume,
        current_fore_floor_root_proofs=roots,current_fore_print_union_solids=1,current_fore_print_envelope_mm=size,
        rest_inherited_by_actual_material_subset=True,reuse_scene=dict(path=of.relative_to(ROOT).as_posix(),sha256=sha(of)),
        completed_static=[],completed_motion=[],N01_complete=False,native_changed=False,physical_pass=False,
        worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result);print('TWO_WHOLE_CASE_BAYS_RECEIVED_UNCHANGED_WIRES',bays,'print',size,result['worker_seconds'],flush=True)


if __name__=='__main__':main()
