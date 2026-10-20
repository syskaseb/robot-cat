"""One whole MAIN service bay in a NEW copy of the printed Pi carrier.

No purchased material edited. Removal cannot create a new collision; retain
the complete old PWM root, every current Pi interface and one connected solid.
"""
import gzip,hashlib,json,os,time,zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from receive_feline_main_ato_gallery import selected
from receive_feline_rrp_shared_height import load
from feline_solid_distance import bbox_lower_bound
from feline_fore_power_pair import SolidQueries
from feline_atomic_save import save_json

PI='SharedPi:Carrier'


def main():
    tick=time.monotonic();sf=OUT/'n01-MAIN-ATO-gallery-local.json';parent=json.loads(sf.read_text())
    assert parent['status']=='MAIN_ATO_GALLERY_LOCAL_HOLDS' and len(parent['failures'])==2
    for p,h in parent['source_sha256'].items():assert sha(ROOT/p)==h,p
    actors=load(parent)
    pp,pr,pins=selected(OUT/'n01-shared-Pi-carrier-r3-core-received.json','geometry',lambda n:True)
    old=pp[PI];changed=old.copy();cuts=[]
    for n,s in actors.items():
        if n=='MainSupported:root':continue
        b=s.BoundBox;margin=1.25
        cutter=Part.makeBox(b.XLength+2*margin,b.YLength+2*margin,b.ZLength+2*margin,A.Vector(b.XMin-margin,b.YMin-margin,b.ZMin-margin))
        if bbox_lower_bound(old.BoundBox,cutter.BoundBox)>0:continue
        changed=changed.cut(cutter);cuts.append(dict(owner=n,margin_mm=margin,construction='whole_actor_conservative_service_box_NOT_contact_evidence'))
    changed=changed.removeSplitter();assert changed.isValid() and len(changed.Solids)==1
    missing=changed.cut(old);assert missing.isNull() or missing.isValid();assert missing.Volume<1e-6
    removed=old.cut(changed);assert removed.isValid() and removed.Volume>0
    frame,_,fp=selected(OUT/'n01-channelled-foundation-static.json','geometry',lambda n:n=='CurrentFoundation:RetainedPWMCarrier','CurrentFoundation:')
    anchor=frame['CurrentFoundation:RetainedPWMCarrier'];lost=anchor.cut(changed);assert lost.isNull() or lost.isValid()
    checks={'entire_original_PWM_root_preserved':dict(ok=lost.Volume<1e-5,removed_from_root_mm3=lost.Volume),
        'new_carrier_valid_single_Solid_subset':dict(ok=True,new_material_outside_parent_mm3=missing.Volume,removed_mm3=removed.Volume)}
    query=SolidQueries();protected=0
    for n,s in pp.items():
        if n==PI:continue
        # Preserve all bearing/jacket seats within2mm of the current physical
        # Pi kit; unrelated BUS actors are conservatively protected as well.
        if bbox_lower_bound(removed.BoundBox,s.BoundBox)>=2:continue
        gap=query.distance(removed,s);checks['preserve_Pi_interface:'+n]=dict(ok=gap>=2-1e-6,gap_mm=gap,project_protected_neighborhood_mm=2);protected+=1
    pf=ROOT/parent['pair_rows'];assert sha(pf)==parent['pair_rows_sha256']
    previous=json.loads(gzip.decompress(pf.read_bytes()));reused={k:v for k,v in previous.items() if k not in parent['failures']}
    assert all(v['ok'] for v in reused.values())
    for key in parent['failures']:
        n=key.rsplit('|',1)[0];gap=query.distance(actors[n],changed)
        checks[key]=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
    stem=OUT/'n01-MAIN-shared-Pi-bay';arc=stem.with_suffix('.breps.zip');rows=stem.with_suffix('.pairs.json.gz');geometry=[]
    with zipfile.ZipFile(ROOT/parent['bundle']) as source,zipfile.ZipFile(arc,'w',zipfile.ZIP_DEFLATED) as z:
        for r in parent['geometry']:
            raw=source.read(r['entry']);assert hashlib.sha256(raw).hexdigest()==r['sha256'];z.writestr(r['entry'],raw);geometry.append(r)
        raw=changed.exportBrepToString().encode();z.writestr('PiBay.brep',raw)
        geometry.append(dict(name=PI,entry='PiBay.brep',sha256=hashlib.sha256(raw).hexdigest(),kind='proposal_material'))
    checks={**reused,**checks};rows.write_bytes(gzip.compress(json.dumps(checks,separators=(',',':')).encode(),mtime=0))
    sources=(sf,ROOT/parent['bundle'],pf,Path(__file__))
    pins.update(fp);pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in sources})
    r=dict(status='MAIN_SHARED_PI_BAY_HOLDS' if any(not v['ok'] for v in checks.values()) else 'MAIN_SHARED_PI_BAY_LOCAL_RECEIVED_WORLD_AND_TOOLS_OPEN',
        source_sha256=pins,geometry=geometry,bundle=arc.relative_to(ROOT).as_posix(),bundle_sha256=sha(arc),
        pair_rows=rows.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(rows),checks=len(checks),failures=[k for k,v in checks.items() if not v['ok']],
        recipes=parent['recipes'],retired=parent['retired']+[PI],cuts=cuts,reused_local_pairs=len(reused),
        byte_identical_MAIN_actors=25,Pi_carrier_material_removed_mm3=removed.Volume,protected_interface_queries=protected,
        retained_Pi_root_and_whole_carrier_connectivity_required=True,all_other_static_motion_clearance_inherited_for_carrier_subset_only=True,
        other_MAIN_world_interfaces_not_yet_received=True,native_changed=False,N01_complete=False,physical_pass=False,worker_seconds=round(time.monotonic()-tick,3))
    save_json(stem.with_suffix('.json'),r);print(r['status'],r['worker_seconds'],len(r['failures']),flush=True)
    print(json.dumps({k:v for k,v in checks.items() if not v['ok']},indent=2),flush=True)


if __name__=='__main__':print('WORKER_PID',os.getpid(),flush=True);main()
