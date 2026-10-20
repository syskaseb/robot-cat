"""Receive one already-constructed complete source proposal; no pose search.

All own pairs precede fixed-world calls. Exact unchanged source bodies are
reported as inherited, not moved to rescue a cable. Invalid geometry holds.
"""
import hashlib,itertools,json,time,zipfile
from pathlib import Path
import FreeCAD as A
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from receive_feline_existing_lower_caps import current
from feline_main_hung_context import compose
from receive_feline_rrp_shared_height import load
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from plan_feline_usb_service_bight import outer_margin
from feline_atomic_save import save_json


def receive(builder,source,destname):
    tick=time.monotonic();dest=OUT/destname;assert not dest.exists()
    _,ends,files=current();ends={r['id']:r for r in ends}
    world,parts,meta,pins,docs=compose();print('WORLD_LOADED',round(time.monotonic()-tick,3),flush=True)
    mf=OUT/'n01-MTA-low-stop-cradles.json';mr=json.loads(mf.read_text());rf=mf.with_name(mf.stem+'-scene.json');rr=json.loads(rf.read_text())
    assert not rr['failures'] and len(rr['completed_static'])==len(rr['completed_motion'])==72
    for rec in (mr,rr):
        for p,h in rec['source_sha256'].items():assert sha(ROOT/p)==h,p
    effective={n:s for n,s in parts.items() if n not in mr['retired']};effective.update(load(mr))
    actors,recipes,own,names,datums,extra=builder(parts,ends)
    inherited=set(extra['unchanged_existing_body_names'])
    for n in names.values():effective.pop(n)
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (mf,ROOT/mr['bundle'],rf,ROOT/rr['pair_rows'],*files,
        OUT/'n01-F0-selected-supplier-facts.json',ROOT/'tools/cad/plan_feline_battery_f0_joint.py',
        ROOT/'tools/cad/fit_feline_current_usb_space.py',Path(source),Path(__file__))})
    result=dict(status='RUNNING_SHARED_SOURCE',source_sha256=pins,recipes=recipes,current_nominal_datums=datums,
        own_whole_kit_checks=own,checks={},outer={},failures=[k for k,v in own.items() if not v['ok']],geometry={},
        factory_length_budgets={n:dict(nominal_catalog_mm=89.5,curve_mm=recipes[n]['length_mm'],strip_mm=8.73 if n=='W075_factory' else 11.,rework_mm=10.,
            nominal_unused_mm=89.5-recipes[n]['length_mm']-(8.73 if n=='W075_factory' else 11.)-10.,manufacturer_tolerance_unknown=True)
            for n in ('W075_factory','W076_factory')},
        N01_complete=False,native_changed=False,selected_SKUs_changed=False,physical_pass=False,
        missing=['independent full grips and roots','installed battery supplied leads','assembly/tool access','sampled motion','shared123 capacity'],**extra)
    assert all(b['nominal_unused_mm']>=0 for b in result['factory_length_budgets'].values())
    archive=dest.with_suffix('.breps.zip')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for i,(n,s) in enumerate(actors.items()):
            raw=s.exportBrepToString().encode();entry=str(i)+'.brep';z.writestr(entry,raw);result['geometry'][n]=dict(entry=entry,sha256=hashlib.sha256(raw).hexdigest())
    result.update(bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive))
    def save():result['worker_seconds']=round(time.monotonic()-tick,3);save_json(dest,result)
    save()
    if result['failures']:result['status']='SHARED_SOURCE_OWN_KIT_REJECTED_BEFORE_WORLD';save();print(result['status'],result['failures'],flush=True);return
    query=SolidQueries()
    for n,s in actors.items():
        if n in inherited:continue
        result['outer'][n]=outer_margin(s,docs['outer'])
        if not result['outer'][n]['ok']:result['failures'].append(n+'|outer')
        for m,t in effective.items():
            if bbox_lower_bound(s.BoundBox,t.BoundBox)>=1.25:continue
            a=s;b=t
            if m==world.bus['name']:a=s.copy();a.Placement=docs['inverse']*a.Placement;b=world.bus['original']
            if not b.Solids:row=dict(ok=False,unreceived_profile=True)
            else:
                gap=query.distance(a,b);row=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
                if not row['ok']:
                    _,pts,_=a.distToShape(b);row['witness_mm']=[[list(x),list(y)] for x,y in pts[:1]]
            if not row['ok']:result['failures'].append(n+'|'+m)
            result['checks'][n+'|'+m]=row
        for m,t in world.rest.items():
            if bbox_lower_bound(s.BoundBox,t.BoundBox)>=1.25:continue
            gap=query.distance(s,t);key=n+'|rest:'+m;result['checks'][key]=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
            if gap<1.25-1e-6:result['failures'].append(key)
        save();print('RECEIVED',n,'holds',len(result['failures']),round(time.monotonic()-tick,3),flush=True)
    result['status']='SHARED_SOURCE_REJECTED_NO_DETAIL' if result['failures'] else 'SHARED_SOURCE_CHANGED_OUTER_STATIC_ONLY_ROOTS_MOTION_ASSEMBLY_OPEN'
    save();print(result['status'],result['failures'],result['worker_seconds'],flush=True)
