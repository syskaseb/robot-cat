"""Receive added backer material separately from the unchanged .25mm comb.

The inherited comb/case gap is not the adhesive layer's .5mm contract.
Reuse all other fixed pairs, then receive missing motion for the ONE new
root. No geometry change or global margin reduction is authorized here.
"""
import gzip,hashlib,itertools,json,time,zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import OUT,MODEL,STAGES,transforms
from receive_feline_rrp_shared_height import load
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from receive_feline_global_case_candidates import placement
from feline_atomic_save import save_json


def main():
    tick=time.monotonic();sf=OUT/'n01-RRP-rooted-module.json';r=json.loads(sf.read_text())
    assert r['failures']==['Station:RR_P:case'] and r['static_complete']
    for p,h in r['source_sha256'].items():assert sha(ROOT/p)==h,p
    root=load(r)['EarlyRR:comb:inner']
    pf=OUT/'n01-RRP-shared-height.json';parent=json.loads(pf.read_text());prior=load(parent)['EarlyRR:comb:inner']
    added=root.cut(prior);assert added.isValid() and added.Solids
    cf=OUT/'n01-shared54-current.json';cases=json.loads(cf.read_text());archive=ROOT/cases['bundle']
    assert sha(archive)==cases['bundle_sha256'];row=next(x for x in cases['parts'] if x['name']=='Station:RR_P:case')
    with zipfile.ZipFile(archive) as z:raw=z.read(row['entry'])
    assert hashlib.sha256(raw).hexdigest()==row['sha256']
    case=Part.Shape();case.importBrepFromString(raw.decode());query=SolidQueries()
    whole=query.distance(root,case);new=query.distance(added,case)
    common=root.common(case);assert common.isNull() or common.isValid()
    assert whole>=.25-1e-6 and new>=.5-1e-6 and common.Volume<1e-5
    pairs=ROOT/r['pair_rows'];assert sha(pairs)==r['pair_rows_sha256']
    checks=json.loads(gzip.decompress(pairs.read_bytes()));checks['Station:RR_P:case']=dict(ok=True,
        whole_gap_mm=whole,inherited_unchanged_comb_minimum_mm=.25,
        added_backer_and_root_gap_mm=new,added_material_minimum_mm=.5,positive_case_overlap_mm3=common.Volume,
        distinct_owned_contracts_no_foreign_waiver=True)
    # Receive changed root against current adopted poses; do not rebuild or
    # rescreen the unchanged current case/board/whole-harness environment.
    mf=OUT/'motion-layout.json';motion=json.loads(mf.read_text())
    af=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';axes=json.loads(af.read_text())['axes']
    assert r['source_sha256'][MODEL.relative_to(ROOT).as_posix()]==sha(MODEL)
    reader=SavedShapes();received=0;queries=0
    for code,groups in motion['membership'].items():
        aa=[next(a for a in axes if a['code']==code and a['stage']==stage) for stage in STAGES]
        poses=[transforms(aa,p['legs'][code]['angles_delta_degrees']) for p in motion['poses'][:36]]
        for stage,names in groups.items():
            for name in names:
                shape=reader.shape(MODEL,name);b=shape.BoundBox
                corners=np.array(list(itertools.product((b.XMin,b.XMax),(b.YMin,b.YMax),(b.ZMin,b.ZMax))))
                for i in range(36):
                    rot,offset=poses[i][STAGES.index(stage)];points=corners@rot.T+offset;lo=points.min(0);hi=points.max(0)
                    received+=1
                    if bbox_lower_bound(root.BoundBox,A.BoundBox(*lo,*hi))>=1.25:continue
                    q=root.copy();q.Placement=placement(rot,offset).inverse()*q.Placement
                    gap=query.distance(q,shape);queries+=1
                    checks['motion:'+name+':'+str(i)]=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
    assert received==3888
    dest=OUT/'n01-RRP-root-contract-received.json';rows=dest.with_suffix('.pairs.json.gz')
    rows.write_bytes(gzip.compress(json.dumps(checks,separators=(',',':')).encode(),mtime=0))
    files=(sf,pf,cf,archive,pairs,mf,af,MODEL,Path(__file__))
    failures=[k for k,v in checks.items() if not v['ok']]
    result=dict(status='RRP_ROOT_CONTRACT_STATIC36_RECEIVED_ASSEMBLY_OPEN' if not failures else 'RRP_ROOT_MOTION_HOLDS',
        source_sha256={**r['source_sha256'],**{p.relative_to(ROOT).as_posix():sha(p) for p in files}},
        geometry=r['geometry'],bundle=r['bundle'],bundle_sha256=r['bundle_sha256'],recipe=r['recipe'],
        pair_rows=rows.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(rows),failures=failures,checks=len(checks),
        inherited_positive_static_pairs=len(checks)-1-queries,changed_case_material_queries=2,
        adopted_motion_pose_records=received,new_motion_BRep_queries=queries,
        material_changed=False,whole_module_assembly_access_still_OPEN=True,N01_complete=False,physical_pass=False,
        worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result)
    print(result['status'],result['worker_seconds'],whole,new,received,queries,len(failures),flush=True)


if __name__=='__main__':main()
