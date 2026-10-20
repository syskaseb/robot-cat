"""Change rear vertical tower to a shared low inline F0 source topology.

No mount detail or native promotion. Geometry first checks its own full
polarity curves and port alignment; actual assembly and factory battery
lead reach remain explicit open gates. No selected SKU/order change.
"""
import hashlib,json,time,zipfile
from pathlib import Path
import FreeCAD as A
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_battery_f0_joint import path,pose
from plan_feline_n01_shared import pipe
from receive_feline_existing_lower_caps import current
from feline_main_hung_context import compose
from receive_feline_rrp_shared_height import load
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from plan_feline_usb_service_bight import outer_margin
from feline_atomic_save import save_json


def construction(parts,ends):
    names={'F0':'Ref_Material_F0_CP2_0_0','XT60':'Ref_Material_XT60_CP2_0_0','POST':'Ref_Material_PostF0Splice_CP2_0_0'}
    actors={};tf={};R=12.4
    # AUX startsX132; preserve1.25foreign clearance behind the whole
    #23.9mm connector. Clock both cavities sideways, not above each other.
    mouthX=132-1.25-23.9
    actors[names['F0']],tf['F0']=pose(parts[names['F0']],[68,0,-13.75],A.Rotation(A.Vector(0,0,1),135),[68,0,-13.75])
    actors[names['XT60']],tf['XT60']=pose(parts[names['XT60']],[142.999996948242,0.000003051758,-35],
        A.Rotation(A.Vector(0,0,1),180)*A.Rotation(A.Vector(1,0,0),90),[mouthX+11.95,3.5,-13.75])
    mouth=list(tf['XT60'].multVec(A.Vector(*ends['W075/retained0/start']['point_mm'])))
    groundmouth=list(tf['XT60'].multVec(A.Vector(*ends['W001/retained0/start']['point_mm'])))
    inlet=list(tf['F0'].multVec(A.Vector(*ends['W075/retained0/end']['point_mm'])))
    outlet=list(tf['F0'].multVec(A.Vector(*ends['W076/retained0/start']['point_mm'])))
    assert abs(mouth[1])+abs(mouth[2]+13.75)<1e-4
    positive=path(mouth,[-1,0,0],[('line',mouth[0]-inlet[0])],R)
    assert (A.Vector(*positive['end'])-A.Vector(*inlet)).Length<1e-4
    ground=path(groundmouth,[-1,0,0],[('turn',[0,1,0]),('line',9)],R)
    output=path(outlet,[-1,0,0],[('line',25.5)],R)
    post1=output['end'];postcentre=[post1[0]-9.5,post1[1],post1[2]-1.5]
    actors[names['POST']],tf['POST']=pose(parts[names['POST']],[143.000000762939,-35,42],A.Rotation(A.Vector(0,0,1),90),postcentre)
    assert (tf['POST'].multVec(A.Vector(*ends['W076/retained0/end']['point_mm']))-A.Vector(*post1)).Length<1e-4
    post2=list(tf['POST'].multVec(A.Vector(*ends['W076/retained1/start']['point_mm'])))
    custom=path(post2,[1,0,0],[('turn',[0,-1,0]),('line',9)],25.2)
    recipes={'W075_factory':positive,'W076_factory':output,'W001_ground_prefix':ground,'W076_custom_prefix':custom}
    for n,r in recipes.items():actors[n]=pipe(r['parts'],2.1 if n=='W076_custom_prefix' else 1.55)
    # The two source polarities and two F0 leads are different conductors.
    # This gate precedes any whole-world operation, unlike the tower trial.
    mutual={}
    for a,b in (('W075_factory','W001_ground_prefix'),('W075_factory','W076_factory'),
                ('W075_factory','W076_custom_prefix'),('W001_ground_prefix','W076_factory'),
                ('W001_ground_prefix','W076_custom_prefix'),('W076_factory','W076_custom_prefix')):
        gap=actors[a].distToShape(actors[b])[0]
        mutual[a+'|'+b]=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
    return actors,recipes,mutual,names,dict(F0_in=inlet,F0_out=outlet,BAT_plus=mouth,BAT_minus=groundmouth,POST1=post1,POST2=post2)


def main():
    tick=time.monotonic();dest=OUT/'n01-BAT-F0-low-inline-joint.json';assert not dest.exists()
    # Receive pinned negative parent, not its obsolete geometry as a current source.
    pf=OUT/'n01-BAT-F0-vertical-joint.json';prior=json.loads(pf.read_text())
    assert prior['status']=='JOINT_BAT_F0_REJECTED_NO_MOUNT_DETAIL' and len(prior['failures'])==17
    _,ends,files=current();ends={r['id']:r for r in ends}
    world,parts,meta,pins,docs=compose();print('WORLD_LOADED',round(time.monotonic()-tick,3),flush=True)
    mf=OUT/'n01-MTA-low-stop-cradles.json';mr=json.loads(mf.read_text());rf=mf.with_name(mf.stem+'-scene.json');rr=json.loads(rf.read_text())
    assert not rr['failures'] and len(rr['completed_static'])==len(rr['completed_motion'])==72
    for rec in (mr,rr):
        for p,h in rec['source_sha256'].items():assert sha(ROOT/p)==h,p
    effective={n:s for n,s in parts.items() if n not in mr['retired']};effective.update(load(mr))
    actors,recipes,mutual,names,datums=construction(parts,ends)
    for n in names.values():effective.pop(n)
    facts=OUT/'n01-F0-selected-supplier-facts.json';catalog=json.loads(facts.read_text())
    assert catalog['selected_sku']=='FHAC0002ZXJ' and catalog['nominal_each_factory_lead_mm']==89.5
    budgets={n:dict(nominal_catalog_mm=89.5,curve_mm=recipes[n]['length_mm'],strip_mm=8.73 if n=='W075_factory' else 11.,rework_mm=10.,
        tolerance_and_delivered_OD_gate=True) for n in ('W075_factory','W076_factory')}
    for b in budgets.values():b['nominal_unused_mm']=89.5-b['curve_mm']-b['strip_mm']-b['rework_mm'];assert b['nominal_unused_mm']>=0
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (mf,ROOT/mr['bundle'],rf,ROOT/rr['pair_rows'],pf,facts,*files,
        ROOT/'tools/cad/plan_feline_battery_f0_joint.py',Path(__file__))})
    result=dict(status='RUNNING_LOW_INLINE_SOURCE_TOPOLOGY',source_sha256=pins,recipes=recipes,current_nominal_datums=datums,
        factory_length_budgets=budgets,mutual_wire_checks=mutual,checks={},outer={},failures=[k for k,v in mutual.items() if not v['ok']],geometry={},
        rejected_parent_NOT_passed=prior['failures'],no_native_or_selected_SKU_change=True,N01_complete=False,physical_pass=False,
        missing=['full independent grips/roots','installed source and battery factory-lead reach','own case ingress and full internal kit','assembly/tools','sampled motion','shared123 capacity'],
        low_bay_not_vertical_tail_tower=True,datum_kind='current_project_GUIDE_nominal_NOT_supplier_verified',historical920_NOT_extra_BAT_wire=True)
    archive=dest.with_suffix('.breps.zip')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for i,(n,s) in enumerate(actors.items()):
            raw=s.exportBrepToString().encode();entry=str(i)+'.brep';z.writestr(entry,raw);result['geometry'][n]=dict(entry=entry,sha256=hashlib.sha256(raw).hexdigest())
    result.update(bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive))
    def save():result['worker_seconds']=round(time.monotonic()-tick,3);save_json(dest,result)
    save()
    if result['failures']:result['status']='LOW_INLINE_SOURCE_MUTUAL_REJECTED_BEFORE_WORLD';save();print(result['status'],result['failures'],flush=True);return
    query=SolidQueries()
    for n,s in actors.items():
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
        # Resting actual legs are part of the shared scene, not only motion checks later.
        for m,t in world.rest.items():
            if bbox_lower_bound(s.BoundBox,t.BoundBox)>=1.25:continue
            gap=query.distance(s,t);key=n+'|rest:'+m;result['checks'][key]=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
            if gap<1.25-1e-6:result['failures'].append(key)
        save();print('RECEIVED',n,'holds',len(result['failures']),round(time.monotonic()-tick,3),flush=True)
    result['status']='LOW_INLINE_SOURCE_REJECTED_NO_DETAIL' if result['failures'] else 'LOW_INLINE_SOURCE_OUTER_STATIC_ONLY_ROOTS_MOTION_ASSEMBLY_OPEN'
    save();print(result['status'],result['failures'],result['worker_seconds'],flush=True)


if __name__=='__main__':main()
