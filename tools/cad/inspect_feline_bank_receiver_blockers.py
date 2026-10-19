"""One full critical-interface diagnostic before changing any more receivers.

Read only selected saved solids. Inspect ALL stock, not first failing cap.
This is a bounded diagnostic, never full-world acceptance or N01 completion.
"""
import hashlib
import json
import time
import zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_remaining_kits import candidates
from feline_bank_receiving_grips import both_after_candidates,both_after_materialise
from feline_station_zone_domains import materialise as station_material
from feline_above_hardware_grip import unit as above_unit
from feline_fore_power_pair import SolidQueries,pair_spacing
from feline_solid_distance import bbox_lower_bound
from feline_atomic_save import save_json


def main():
    tick=time.monotonic();targets={};meta={};pins={}
    wanted={'CurrentBUS:DGSharedRelief','Ref_Material_S0_key_CP2_0_0','Ref_Material_F_PI_new_0_0'}
    for name in ('n01-full-material-scene.json','n01-six-source-current-core.json'):
        p=OUT/name;doc=json.loads(p.read_text());bundle=ROOT/doc['bundle'];assert sha(bundle)==doc['bundle_sha256']
        pins[p.relative_to(ROOT).as_posix()]=sha(p);pins[doc['bundle']]=doc['bundle_sha256']
        with zipfile.ZipFile(bundle) as z:
            for r in doc['parts']:
                if r['name'] not in wanted:continue
                raw=z.read(r['entry']);assert hashlib.sha256(raw).hexdigest()==r['sha256']
                s=Part.Shape();s.importBrepFromString(raw.decode());assert s.isValid() and s.Solids
                targets[r['name']]=s;meta[r['name']]=r
    assert set(targets)==wanted
    stfile=OUT/'n01-flat-station-architecture.json';choicefile=OUT/'n01-two-lane-comb-joint.json'
    stations={s['ref']:s for s in json.loads(stfile.read_text())['stations']};chosen=json.loads(choicefile.read_text())['chosen']
    c=chosen['P_SYS'];parts,kinds=station_material(stations['P_SYS'],c['slot'],c['recipe'])
    targets['P_SYS:case']=parts['case'];meta['P_SYS:case']=dict(kind=kinds['case'])
    c=chosen['D_FL'];model=above_unit(stations['D_FL'],dict(slot=c['slot'],base_recipe=c['recipe']))
    for n,s in model['parts'].items():targets['D_FL:'+n]=s;meta['D_FL:'+n]=dict(kind=model['kinds'][n])
    groups,_=candidates();recipes=both_after_candidates(groups);query=SolidQueries();records={}
    for group,rows in recipes.items():
        records[group]=[]
        for recipe in rows:
            parts,kinds=both_after_materialise(group,recipe);failures=[]
            for n,s in parts.items():
                for other,t in targets.items():
                    minimum=pair_spacing(group+':'+n,dict(kind=kinds[n]),other,meta[other])
                    if bbox_lower_bound(s.BoundBox,t.BoundBox)>=minimum:continue
                    gap=query.distance(s,t)
                    if gap>=minimum-1e-6:continue
                    row=dict(part=n,other=other,gap_mm=gap,required_mm=minimum)
                    if gap<1e-8:
                        common=s.copy().common(t.copy());assert common.isNull() or common.isValid()
                        row['positive_common_mm3']=common.Volume
                        if common.Volume>1e-7:
                            centre=sum((s.CenterOfMass*s.Volume for s in common.Solids),A.Vector())/common.Volume
                            row['common_center_mm']=list(centre)
                    else:
                        pts=s.distToShape(t)[1]
                        if pts:row['closest_points_mm']=[list(v) for v in pts[0]]
                    failures.append(row)
            records[group].append(dict(head=recipe['base_recipe'].get('complete_band_head_degrees',recipe['base_recipe'].get('head_degrees')),failures=failures))
        rejected={r['other']+':'+r['part'] for rec in records[group] for r in rec['failures']}
        print(group,'critical-clear-heads',[r['head'] for r in records[group] if not r['failures']],'blockers',sorted(rejected),flush=True)
    for p in (Path(__file__),stfile,choicefile,Path(__file__).with_name('feline_bank_receiving_grips.py'),Path(__file__).with_name('feline_above_hardware_grip.py')):pins[p.relative_to(ROOT).as_posix()]=sha(p)
    result=dict(status='FULL_BANK_CRITICAL_INTERFACE_DIAGNOSTIC_NOT_WHOLE_WORLD',source_sha256=pins,units=records,
        target_names=list(targets),N01_complete=False,physical_pass=False,worker_seconds=round(time.monotonic()-tick,3))
    save_json(OUT/'n01-bank-critical-interfaces.json',result);print('Critical diagnostic seconds',result['worker_seconds'],flush=True)


if __name__=='__main__':main()
