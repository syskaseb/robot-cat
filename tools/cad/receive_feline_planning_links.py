"""Whole-scene receipt for constructed N01 links, not production wire cuts."""
import gzip,hashlib,json,time,zipfile
import FreeCAD as A
import numpy as np
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from plan_feline_n01_shared import pipe
from feline_fore_power_pair import SolidQueries
from receive_feline_underplate_return_gallery import minimum_for
from feline_solid_distance import bbox_lower_bound
from plan_feline_pi_root_access import profile_gap
from plan_feline_usb_service_bight import outer_margin
from receive_feline_global_case_candidates import placement
from reconcile_feline_source_portal_contracts import own_channel


def receive(stem,links,context,source_pins):
    tick=time.monotonic();world,fixed,meta,pins,docs=context;pins.update(source_pins)
    actors={r['name']:pipe(r['parts'],r['radius_mm']) for r in links};rows={r['name']:r for r in links}
    boxes={n:s.BoundBox for n,s in {**fixed,**actors}.items()};query=SolidQueries();checks={}
    result=dict(status='RUNNING_CONSTRUCTIVE_LINK_RECEIPT',source_sha256=pins,links=links,
        completed_static=[],completed_motion=[],N01_complete=False,physical_pass=False,selected=False,
        only_constructive_space_plan_not_final_custom_cuts_or_native_N04=True)
    archive=OUT/(stem+'.breps.zip');dest=OUT/(stem+'.json');pairfile=OUT/(stem+'.pairs.json.gz')
    geometry=[]
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for i,(n,s) in enumerate(actors.items()):
            raw=s.exportBrepToString().encode();entry=str(i)+'.brep';z.writestr(entry,raw);geometry.append(dict(name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    result.update(geometry=geometry,bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive))
    def save():
        pairfile.write_bytes(gzip.compress(json.dumps(checks,separators=(',',':')).encode(),mtime=0))
        result.update(pair_rows=pairfile.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(pairfile),
            failures=[k for k,v in checks.items() if not v['ok']],checks=len(checks),receiver_seconds=round(time.monotonic()-tick,3))
        save_json(dest,result)
    for n,s in actors.items():
        r=rows[n];checks[n+'|outer']=outer_margin(s,docs['outer'])
        for m,t in {**fixed,**actors}.items():
            if n==m:continue
            key='|'.join(sorted((n,m))) if m in actors else n+'|'+m
            if key in checks:continue
            mr=dict(kind='wire') if m in actors else meta[m]
            minimum=minimum_for(n,dict(kind='wire'),m,mr)
            if m not in actors:minimum=min(minimum,own_channel(r['target_endpoint'],m))
            if bbox_lower_bound(boxes[n],boxes[m])>=minimum:continue
            if m==world.bus['name']:
                a=s.copy();a.Placement=docs['inverse']*a.Placement;gap=query.distance(a,world.bus['original'])
            elif t.Solids:gap=query.distance(s,t)
            else:
                radius=mr.get('nominal_profile_radius_mm') or mr.get('radius_mm')
                checks[key]=profile_gap(s,t,radius,minimum) if radius else dict(ok=False,unresolved_curve_budget_owner=m)
                continue
            check=dict(ok=gap>=minimum-1e-6,gap_mm=gap,minimum_mm=minimum)
            if m in r['joins']:
                common=s.common(t);fused=s.fuse(t)
                assert (common.isNull() or common.isValid()) and fused.isValid()
                check.update(ok=common.Volume<1e-5 and len(fused.Solids)==1,matched_same_wire_cap_join=True,
                    additional_same_wire_overlap_mm3=common.Volume,joined_solids=len(fused.Solids))
            checks[key]=check
        result['completed_static'].append(n);save();print('Constructive link',n,'holds',len(result['failures']),flush=True)
    if not result['failures']:
        for n,s in actors.items():
            for pose in world.motion:
                if bbox_lower_bound(boxes[n],A.BoundBox(*pose['bounds'][0],*pose['bounds'][1]))>=1.25:continue
                a=s.copy();a.Placement=placement(pose['r'],pose['t']).inverse()*a.Placement;gap=query.distance(a,world.rest[pose['name']])
                checks[n+'|motion:'+pose['name']+':'+str(pose['pose'])]=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
            result['completed_motion'].append(n);save()
    result['status']='CONSTRUCTIVE_LINKS_HOLD_WITNESSES' if result['failures'] else 'CONSTRUCTIVE_LINKS_STATIC36MOTION_RECEIVED_REMAINING_N01_OPEN'
    save();print(result['status'],result['checks'],len(result['failures']),result['receiver_seconds'],flush=True)
    return result
