"""Correct only three HP source paths to the selected12.6mm bend rule.

Existing actual9mm source grooves, complete JR kit and bought interfaces stay
unchanged. Reuse their reception; receive all changed three paths against the
current composed world. Head sweep/skin/assembly remain explicitly separate.
"""
import gzip,hashlib,json,time,zipfile
from pathlib import Path
import FreeCAD as A
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_integrated_head_neck import positive_channel_candidates
from feline_fore_power_pair import SolidQueries,pair_spacing
from feline_solid_distance import bbox_lower_bound
from receive_feline_global_case_candidates import placement
from plan_feline_pi_root_access import profile_gap
from feline_source_restraint_plan import box
from feline_atomic_save import save_json


def run(world,fixed,meta,pins):
    tick=time.monotonic();dest=OUT/'n01-HP-selected-R12p6-received.json';assert not dest.exists()
    from feline_selected_piece_contract import load as selected_contract
    contract,_=selected_contract()
    for wire in ('XB22','XB23','XS23'):
        roles=[r for r in contract['portions'].values() if r['wire']==wire]
        assert roles and all(r['project_radius_mm']==1.05 and r['minimum_project_R_mm']==12.6 for r in roles)
    rows,bounds=positive_channel_candidates(rooted=True,wire_R=12.6)
    selected=OUT/'n01-selected-piece-profile-contract.json'
    old=OUT/'n01-common-head-root-JR-neck-received.json';olddata=json.loads(old.read_text())
    targets={n:s for n,s in fixed.items() if n not in {r['name'] for r in rows}}
    result=dict(status='RUNNING_HP_SELECTED_R12p6',checks={},failures=[],geometry=[],
        reused_JR_and_full9_grips=True,mutual_continuous_bounds=bounds,
        head_motion_skin_and_assembly_OPEN=True,N01_complete=False,physical_pass=False,
        source_sha256={**pins,**{str(p.relative_to(ROOT)):sha(p) for p in
            (old,selected,Path(__file__),ROOT/'tools/cad/feline_integrated_head_neck.py')}})
    bundle=dest.with_suffix('.breps.zip');q=SolidQueries();pf=dest.with_suffix('.pairs.json.gz');checks={}
    def save():
        pf.write_bytes(gzip.compress(json.dumps(checks,separators=(',',':')).encode(),mtime=0))
        result.update(checks=len(checks),failures=[k for k,v in checks.items() if not v['ok']],
            pair_rows=pf.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(pf),
            worker_seconds=round(time.monotonic()-tick,3))
        save_json(dest,result)
    def check(name,row):
        checks[name]=row
        if not row['ok']:
            result['status']='HP_SELECTED_RADIUS_ACTUAL_HOLD';save();print(result['status'],name,row,flush=True);return False
        return True
    with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
        for i,r in enumerate(rows):
            raw=r['shape'].exportBrepToString().encode();entry=str(i)+'.brep';z.writestr(entry,raw)
            result['geometry'].append(dict({k:v for k,v in r.items() if k not in ('shape','_axis_samples')},entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    result.update(bundle=bundle.relative_to(ROOT).as_posix(),bundle_sha256=sha(bundle))
    save()
    for r in rows:
        s=r['shape'];name=r['name'];pieces=[A.BoundBox(*lo,*hi) for lo,hi in r['swept_piece_bounds_mm']]
        def near(b):return bbox_lower_bound(s.BoundBox,b)<1.25 and any(bbox_lower_bound(p,b)<1.25 for p in pieces)
        for n,t in targets.items():
            if not near(t.BoundBox):continue
            if n.startswith('Ref_Material_head_0_0_') and any(n.endswith('_'+v+'_0_0') for v in ('Rear','FrontLeft','FrontRightPorted','Nose','EarL','EarR')):continue
            if n in ('HPJR:carrier','HPJR:source_band_budget'):
                x=r['start_mm'][0];ya,yb=olddata['proposed_JR_integral_carrier']['source_grip_Y_range_mm']
                outside=s.copy().cut(box([x-1.3,ya-1.25,-11.3],[x+1.3,yb+1.25,-8.7]))
                common=s.copy().common(t.copy()).Volume;gap=q.distance(outside,t);limit=1.25 if n=='HPJR:carrier' else .2
                row=dict(ok=common<1e-5 and gap>=limit-1e-6,common_mm3=common,outside_grip_gap_mm=gap,minimum_mm=limit)
            elif n=='Ref_Material_headref_0_Interface_FixedJR_0_0':
                common=s.copy().common(t.copy()).Volume;row=dict(ok=common<1e-5,common_mm3=common,known_source_end_face=True)
            else:
                limit=pair_spacing(name,dict(kind='proposal_wire',wire=r['wire']),n,meta.get(n,{}));first=s;other=t
                if n==world.bus['name']:first=s.copy();first.Placement=world.bus['inverse']*first.Placement;other=world.bus['original']
                if not other.Solids:
                    radius=meta.get(n,{}).get('nominal_profile_radius_mm') or meta.get(n,{}).get('radius_mm')
                    row=profile_gap(first,other,radius,limit) if radius else dict(ok=False,unknown_profile=True)
                else:
                    gap=q.distance(first,other);row=dict(ok=gap>=limit-1e-6,gap_mm=gap,minimum_mm=limit)
            if not check(name+'|'+n,row):return result
        for actor in world.motion:
            if not near(A.BoundBox(*actor['bounds'][0],*actor['bounds'][1])):continue
            first=s.copy();first.Placement=placement(actor['r'],actor['t']).inverse()*first.Placement
            gap=q.distance(first,world.rest[actor['name']])
            if not check(name+'|motion:'+actor['name']+':'+str(actor['pose']),dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)):return result
        save()
    result['status']='HP_SELECTED_R12p6_STATIC36_RECEIVED_HEAD_SKIN_MOTION_OPEN';save()
    print(result['status'],result['checks'],result['worker_seconds'],flush=True);return result
