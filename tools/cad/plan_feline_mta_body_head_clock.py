"""Constrain one complete FL T18I head on the inboard straight loop side.

Outboard placement hits bought W044. Find a continuous centre-Z interval
from the full band face, every fixed neighbor and36motion, not a scalar
microshift. Keep band/collar/floors/wires and71other overlay actors identical.
"""
import copy,hashlib,itertools,json,time,zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_main_hung_context import compose
from receive_feline_rrp_shared_height import load
from receive_feline_factory_saddle_plan import box
from plan_feline_factory_joint_bay import subtract
from receive_feline_global_case_candidates import placement
from receive_feline_underplate_return_gallery import minimum_for
from plan_feline_usb_service_bight import outer_margin
from feline_fore_power_pair import SolidQueries
from feline_atomic_save import save_json
from feline_solid_distance import bbox_lower_bound


def bb(b):return [[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]]


def main():
    tick=time.monotonic();world,parts,meta,pins,docs=compose()
    sf=OUT/'n01-MTA-body-retention.json';prior=json.loads(sf.read_text());actors=load(prior)
    observedfile=sf.with_name(sf.stem+'-scene.json');observed=json.loads(observedfile.read_text())
    assert observed['failures']==['CaseTie:FLHead|Ref_Material_W044_Joint_0_0']
    for r in (prior,observed):
        for p,h in r['source_sha256'].items():assert sha(ROOT/p)==h,p
    name='CaseTie:FLHead';band='CaseTie:FL';case=prior['body_ties']['FL']['case'];parent=prior['body_ties']['FL']['parent']
    b=actors[band].optimalBoundingBox(False,False);x=prior['body_ties']['FL']['station_X_mm'];yhi=b.YMin;ylo=yhi-4.3
    initial=[(b.ZMin+2.65,b.ZMax-2.65)];intervals=initial[:];proof=[];clips=0
    effective={n:s for n,s in parts.items() if n not in prior['retired']};effective.update(actors)
    fm={**meta,**{r['name']:r for r in prior['geometry']}}
    sources=[(n,s,None,None,fm[n]) for n,s in effective.items() if n not in (name,band)]
    sources.extend(('motion:'+p['name']+':'+str(p['pose']),world.rest[p['name']],p['bounds'],placement(p['r'],p['t']),dict(kind='rigid')) for p in world.motion)
    for n,s,posed,tf,mr in sources:
        margin=minimum_for(name,fm[name],n,mr);radius=0 if s.Solids else mr.get('nominal_profile_radius_mm') or mr.get('radius_mm')
        assert radius is not None,n
        margin+=radius;bounds=bb(s.BoundBox) if posed is None else posed
        low=min(a for a,c in intervals);high=max(c for a,c in intervals)
        if bounds[1][0]<x-2.5-margin or bounds[0][0]>x+2.5+margin or bounds[1][1]<ylo-margin or bounds[0][1]>yhi+margin or bounds[1][2]<low-2.65-margin or bounds[0][2]>high+2.65+margin:continue
        roi=box([x-2.5-margin,ylo-margin,low-2.65-margin],[x+2.5+margin,yhi+margin,high+2.65+margin])
        if n==world.bus['name']:s=world.bus['original'];tf=docs['inverse'].inverse()
        if tf is not None:roi.Placement=tf.inverse()*roi.Placement
        assert s.isValid(),n
        cut=s.common(roi);assert cut.isNull() or cut.isValid(),n;clips+=1
        if cut.isNull() or not cut.Vertexes:continue
        cb=cut.optimalBoundingBox(False,False)
        if tf is not None:
            xyz=np.array([list(tf.multVec(A.Vector(*v))) for v in itertools.product((cb.XMin,cb.XMax),(cb.YMin,cb.YMax),(cb.ZMin,cb.ZMax))]);zmin,zmax=xyz[:,2].min(),xyz[:,2].max()
        else:zmin,zmax=cb.ZMin,cb.ZMax
        forbidden=[float(zmin-2.65-margin),float(zmax+2.65+margin)];after=subtract(intervals,forbidden)
        if after!=intervals:proof.append(dict(source=n,forbidden_head_centre_Z_mm=forbidden,actual_clip_mm3=cut.Volume,actual_clip_bounds=bb(cb),bbox_overlap_NOT_contact=True));intervals=after
        if not intervals:break
    dest=OUT/'n01-MTA-body-head-clock.json';assert not dest.exists()
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (sf,ROOT/prior['bundle'],observedfile,ROOT/observed['pair_rows'],Path(__file__))})
    planning=dict(initial_band_face_centre_Z_mm=initial,free_centre_Z_mm=intervals,head_X_mm=x,inboard_head_Y_mm=[ylo,yhi],
        actual_clip_queries=clips,projection_rows=proof,full_head_budget_mm=[5,4.3,5.3],source_part_count=len(sources))
    if not intervals:
        save_json(dest,dict(status='NO_CONSERVATIVE_HEAD_CLOCK_ZONE_NOT_GLOBAL_IMPOSSIBLE',planning=planning,source_sha256=pins,N01_complete=False,native_changed=False,worker_seconds=round(time.monotonic()-tick,3)));print('NO_CONSERVATIVE_HEAD_CLOCK_ZONE_NOT_GLOBAL_IMPOSSIBLE',proof,flush=True);return
    a,c=max(intervals,key=lambda v:v[1]-v[0]);z=(a+c)/2;head=box([x-2.5,ylo,z-2.65],[x+2.5,yhi,z+2.65])
    assert abs(head.Volume-actors[name].Volume)<1e-5
    unit=head.fuse(actors[band]);assert unit.isValid() and len(unit.Solids)==1
    outer=outer_margin(head,docs['outer']);assert outer['ok'],outer
    query=SolidQueries();contracts=copy.deepcopy(prior['named_interface_pairs'])
    for key in list(contracts):
        if name in key.split('|'):contracts.pop(key)
    for other,minimum,field in ((band,0,'exact_same_T18I_budget_unit'),(case,.2,'exact_own_body_insulating_retention_pair'),(parent,.2,'exact_own_body_retention_slot_pair')):
        s=actors.get(other,effective.get(other));common=head.common(s);assert common.isNull() or common.isValid()
        gap=query.distance(head,s);assert common.Volume<1e-5 and gap>=minimum-1e-6,(other,gap,common.Volume)
        contracts['|'.join(sorted((name,other)))]=dict(ok=True,gap_mm=gap,minimum_mm=minimum,whole_common_mm3=common.Volume,
            **{field:[name,other]},foreign_margin_NOT_changed_mm=1.25)
    actors[name]=head;planning.update(chosen_centre_Z_mm=z,actual_whole_head_outer=outer,nominal_head_band_fuse_solids=1)
    archive=dest.with_suffix('.breps.zip');geometry=[]
    with zipfile.ZipFile(ROOT/prior['bundle']) as src,zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as target:
        for i,r in enumerate(prior['geometry']):
            n=r['name'];raw=head.exportBrepToString().encode() if n==name else src.read(r['entry'])
            if n!=name:assert hashlib.sha256(raw).hexdigest()==r['sha256']
            entry=str(i)+'.brep';target.writestr(entry,raw);geometry.append(dict(r,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    ties=copy.deepcopy(prior['body_ties']);ties['FL'].update(head_radial_sign=-1,head_clock='INBOARD_FREE_Z_DOMAIN',head_centre_Z_mm=z)
    result=dict(prior,status='RUNNING_ONE_BODY_HEAD_REST',source_sha256={**prior['source_sha256'],**pins},planning=planning,body_ties=ties,
        geometry=geometry,bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),named_interface_pairs=contracts,
        changed_actors=[name],completed_rest=[n for n in prior['completed_rest'] if n!=name],completed_static=[],completed_motion=[],
        byte_identical_actors_from_prior=71,reuse_scene=dict(path=observedfile.relative_to(ROOT).as_posix(),sha256=sha(observedfile)),
        rest_checks={},failures=[],checks=0,N01_complete=False,native_changed=False,physical_pass=False)
    for n,s in world.rest.items():
        if bbox_lower_bound(head.BoundBox,s.BoundBox)>=1.25:continue
        gap=query.distance(head,s);result['rest_checks'][name+'|rest:'+n]=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
        if gap<1.25-1e-6:result['failures'].append(name+'|rest:'+n);break
    if not result['failures']:result['completed_rest'].append(name)
    result.update(status='MTA_HEAD_CLOCK_REST_HOLD' if result['failures'] else 'COMPLETE_MTA_KIT_REST_RECEIVED_STATIC_MOTION_ACCESS_OPEN',
        worker_seconds=round(time.monotonic()-tick,3),checks=len(result['rest_checks']));save_json(dest,result)
    print(result['status'],intervals,z,'clips',clips,'seconds',result['worker_seconds'],flush=True)


if __name__=='__main__':main()
