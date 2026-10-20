"""Whole transverse source bay above battery end; two rejected topologies frozen.

Changed cause: full F0 in the battery/rear-frame gap, both exits above side
rails, lid toward the space ABOVE the battery, not into tail or bank.
No generic pose search, no mount detail before all own interfaces pass.
"""
import hashlib,itertools,json,time,zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_battery_f0_joint import path,pose
from plan_feline_n01_shared import pipe
from fit_feline_current_usb_space import biarc_join
from receive_feline_existing_lower_caps import current
from feline_main_hung_context import compose
from receive_feline_rrp_shared_height import load
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from plan_feline_usb_service_bight import outer_margin
from feline_atomic_save import save_json


def smooth(p,q):
    r=biarc_join(np.array(p),np.array([0,1,0]),np.array(q),np.array([0,1,0]),1.,True)
    assert r and r['minimum_R_mm']>=12.4 and r['length_mm']+21<=89.5
    pieces=[]
    for a in r['arcs']:
        points=np.asarray(a['points_mm'][::-1] if a['reverse'] else a['points_mm'])
        pieces.append(dict(kind='arc',start=points[0].tolist(),mid=points[len(points)//2].tolist(),end=points[-1].tolist(),R_mm=a['R_mm']))
    return dict(parts=pieces,length_mm=r['length_mm'],minimum_R_mm=r['minimum_R_mm'])


def construction(parts,ends):
    names={'F0':'Ref_Material_F0_CP2_0_0','XT60':'Ref_Material_XT60_CP2_0_0','POST':'Ref_Material_PostF0Splice_CP2_0_0'}
    actors={};tf={}
    actors[names['F0']],tf['F0']=pose(parts[names['F0']],[68,0,-13.75],
        A.Rotation(A.Vector(0,1,0),-90)*A.Rotation(A.Vector(0,0,1),45),[94.5,0,42.75])
    actors[names['XT60']],tf['XT60']=pose(parts[names['XT60']],[142.999996948242,0.000003051758,-35],
        A.Rotation(A.Vector(0,0,1),90)*A.Rotation(A.Vector(1,0,0),90),[98,-56.95,44.5])
    actors[names['POST']],tf['POST']=pose(parts[names['POST']],[143.000000762939,-35,42],A.Rotation(A.Vector(0,1,0),-90),[96,54.5,44.5])
    datums={role:list(tf[group].multVec(A.Vector(*ends[id]['point_mm']))) for role,group,id in (
        ('BAT_plus','XT60','W075/retained0/start'),('BAT_minus','XT60','W001/retained0/start'),
        ('F0_in','F0','W075/retained0/end'),('F0_out','F0','W076/retained0/start'),
        ('POST1','POST','W076/retained0/end'),('POST2','POST','W076/retained1/start'))}
    recipes={'W075_factory':smooth(datums['BAT_plus'],datums['F0_in']),
        'W076_factory':smooth(datums['F0_out'],datums['POST1']),
        'W001_ground_prefix':path(datums['BAT_minus'],[0,1,0],[('turn',[1,0,0]),('line',9)],12.4),
        'W076_custom_prefix':path(datums['POST2'],[0,-1,0],[('turn',[1,0,0]),('line',9)],25.2)}
    for n,r in recipes.items():actors[n]=pipe(r['parts'],2.1 if n=='W076_custom_prefix' else 1.55)
    mouths={frozenset((names['F0'],n)) for n in ('W075_factory','W076_factory')}
    mouths.update(frozenset((names['XT60'],n)) for n in ('W075_factory','W001_ground_prefix'))
    mouths.update(frozenset((names['POST'],n)) for n in ('W076_factory','W076_custom_prefix'))
    own={}
    for a,b in itertools.combinations(actors,2):
        s,t=actors[a],actors[b];minimum=0. if frozenset((a,b)) in mouths else 1.25
        gap=s.distToShape(t)[0];c=s.common(t);assert c.isNull() or c.isValid()
        own[a+'|'+b]=dict(ok=gap>=minimum-1e-6 and c.Volume<1e-5,gap_mm=gap,minimum_mm=minimum,common_mm3=c.Volume,
            exact_own_mouth=frozenset((a,b)) in mouths)
    return actors,recipes,own,names,datums


def main():
    tick=time.monotonic();dest=OUT/'n01-BAT-F0-transverse-joint.json';assert not dest.exists()
    _,ends,files=current();ends={r['id']:r for r in ends}
    world,parts,meta,pins,docs=compose();print('WORLD_LOADED',round(time.monotonic()-tick,3),flush=True)
    mf=OUT/'n01-MTA-low-stop-cradles.json';mr=json.loads(mf.read_text());rf=mf.with_name(mf.stem+'-scene.json');rr=json.loads(rf.read_text())
    assert not rr['failures'] and len(rr['completed_static'])==len(rr['completed_motion'])==72
    for rec in (mr,rr):
        for p,h in rec['source_sha256'].items():assert sha(ROOT/p)==h,p
    effective={n:s for n,s in parts.items() if n not in mr['retired']};effective.update(load(mr))
    actors,recipes,own,names,datums=construction(parts,ends)
    for n in names.values():effective.pop(n)
    facts=OUT/'n01-F0-selected-supplier-facts.json'
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (mf,ROOT/mr['bundle'],rf,ROOT/rr['pair_rows'],facts,*files,
        ROOT/'tools/cad/plan_feline_battery_f0_joint.py',ROOT/'tools/cad/fit_feline_current_usb_space.py',Path(__file__))})
    result=dict(status='RUNNING_TRANSVERSE_SOURCE_TOPOLOGY',source_sha256=pins,recipes=recipes,current_nominal_datums=datums,
        own_whole_kit_checks=own,checks={},outer={},failures=[k for k,v in own.items() if not v['ok']],geometry={},
        factory_length_budgets={n:dict(nominal_catalog_mm=89.5,curve_mm=recipes[n]['length_mm'],strip_mm=8.73 if n=='W075_factory' else 11.,rework_mm=10.,
            nominal_unused_mm=89.5-recipes[n]['length_mm']-(8.73 if n=='W075_factory' else 11.)-10.,manufacturer_tolerance_unknown=True)
            for n in ('W075_factory','W076_factory')},
        no_native_or_selected_SKU_change=True,N01_complete=False,physical_pass=False,
        missing=['full independent grips/roots','battery supplied lead reach and body retention','assembly/tools','sampled motion','shared123 capacity'],
        lid_design_direction_minus_X_not_verified_opening=True,datum_kind='current_project_GUIDE_nominal_NOT_supplier_verified')
    archive=dest.with_suffix('.breps.zip')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for i,(n,s) in enumerate(actors.items()):
            raw=s.exportBrepToString().encode();entry=str(i)+'.brep';z.writestr(entry,raw);result['geometry'][n]=dict(entry=entry,sha256=hashlib.sha256(raw).hexdigest())
    result.update(bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive))
    def save():result['worker_seconds']=round(time.monotonic()-tick,3);save_json(dest,result)
    save()
    if result['failures']:result['status']='TRANSVERSE_SOURCE_OWN_KIT_REJECTED_BEFORE_WORLD';save();print(result['status'],result['failures'],flush=True);return
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
        for m,t in world.rest.items():
            if bbox_lower_bound(s.BoundBox,t.BoundBox)>=1.25:continue
            gap=query.distance(s,t);key=n+'|rest:'+m;result['checks'][key]=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
            if gap<1.25-1e-6:result['failures'].append(key)
        save();print('RECEIVED',n,'holds',len(result['failures']),round(time.monotonic()-tick,3),flush=True)
    result['status']='TRANSVERSE_SOURCE_REJECTED_NO_DETAIL' if result['failures'] else 'TRANSVERSE_SOURCE_OUTER_STATIC_ONLY_ROOTS_MOTION_ASSEMBLY_OPEN'
    save();print(result['status'],result['failures'],result['worker_seconds'],flush=True)


if __name__=='__main__':main()
