"""One constructive W052 bypass: complete S1 X datum, shared free-Y domain.

Keep first S/full10mm grip/root/factory and all63 other actors. Derive the
upper angle from all fixed parts+36motion+actual outer, not another guessed
offset from the body only. Projection is conservative free-space, not contact.
"""
import copy,hashlib,itertools,json,math,time,zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_main_hung_context import compose
from receive_feline_rrp_shared_height import load
from plan_feline_factory_joint_bay import subtract
from plan_feline_remaining_factory_inputs import offset
from receive_feline_underplate_return_gallery import forward,bend,minimum_for
from plan_feline_n01_shared import pipe
from plan_feline_usb_service_bight import outer_margin
from receive_feline_global_case_candidates import placement
from feline_fore_power_pair import SolidQueries
from feline_atomic_save import save_json
from feline_solid_distance import bbox_lower_bound


def bounds(b):return [[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]]


def main():
    tick=time.monotonic();world,parts,meta,pins,docs=compose()
    sf=OUT/'n01-MTA-rear-shoulders.json';prior=json.loads(sf.read_text());actors=load(prior)
    assert len(prior['completed_rest'])==64 and not prior['failures']
    for p,h in prior['source_sha256'].items():assert sha(ROOT/p)==h,p
    n='CustomPrefix:W052';fixed={m:s for m,s in parts.items() if m not in prior['retired']};fixed.update(actors);fixed.pop(n)
    fm={**meta,**{r['name']:r for r in prior['geometry']}}
    module={m:s for m,s in fixed.items() if m.startswith('Ref_Material_current_S1_')}
    assert len(module)>=10 and all('Ref_Material_current_S1_ring_'+str(i)+'_0_0' in module for i in (2,3,5,6))
    module_bounds={m:bounds(s.optimalBoundingBox(False,False)) for m,s in module.items()}
    X=min(b[0][0] for b in module_bounds.values())-2.1-1.25-.4
    rows=copy.deepcopy(prior['recipes'][n]['parts'][:3]);d=np.array([-1.,0,0]);q=np.asarray(rows[-1]['end']);q=offset(rows,q,d,[0,-2,0])
    stem=copy.deepcopy(rows);base=float(q[2]+25.2);top=45.26
    def vertical(y):return Part.makeCylinder(2.1,top-base,A.Vector(X,y,base))
    assert outer_margin(vertical(-29),docs['outer'])['ok'],'No nominal vertical in this conservative lateral family'
    lo,hi=29.,79.4
    for _ in range(20):
        mid=(lo+hi)/2
        if outer_margin(vertical(-mid),docs['outer'])['ok']:lo=mid
        else:hi=mid
    intervals=[(-lo,-29.)];initial=copy.deepcopy(intervals);proof=[];clips=0
    sources=[(m,s,None,None,fm[m]) for m,s in fixed.items()]
    sources.extend(('motion:'+p['name']+':'+str(p['pose']),world.rest[p['name']],p['bounds'],placement(p['r'],p['t']),dict(kind='rigid')) for p in world.motion)
    for m,s,posed,tf,mr in sources:
        margin=minimum_for(n,dict(kind='actual_wire'),m,mr)
        radius=0 if s.Solids else mr.get('nominal_profile_radius_mm') or mr.get('radius_mm')
        assert radius is not None,('Missing profile',m)
        margin+=radius;expanded=2.1+margin;b=bounds(s.BoundBox) if posed is None else posed
        low=min(a for a,c in intervals);high=max(c for a,c in intervals)
        if b[1][0]<X-expanded or b[0][0]>X+expanded or b[1][2]<base-margin or b[0][2]>top+margin or b[1][1]<low-expanded or b[0][1]>high+expanded:continue
        roi=Part.makeBox(2*expanded,high-low+2*expanded,top-base+2*margin,A.Vector(X-expanded,low-expanded,base-margin))
        if m==world.bus['name']:s=world.bus['original'];tf=docs['inverse'].inverse()
        if tf is not None:roi.Placement=tf.inverse()*roi.Placement
        assert s.isValid(),m
        cut=s.common(roi);assert cut.isNull() or cut.isValid(),m;clips+=1
        if cut.isNull() or not cut.Vertexes:continue
        cb=cut.optimalBoundingBox(False,False)
        if tf is not None:
            xyz=np.array([list(tf.multVec(A.Vector(*v))) for v in itertools.product((cb.XMin,cb.XMax),(cb.YMin,cb.YMax),(cb.ZMin,cb.ZMax))]);ymin,ymax=xyz[:,1].min(),xyz[:,1].max()
        else:ymin,ymax=cb.YMin,cb.YMax
        forbidden=[float(max(ymin,low-expanded)-expanded),float(min(ymax,high+expanded)+expanded)]
        after=subtract(intervals,forbidden)
        if after!=intervals:proof.append(dict(source=m,forbidden_Y_mm=forbidden,actual_clip_mm3=cut.Volume,actual_clip_bounds=bounds(cb),bbox_overlap_NOT_contact=True));intervals=after
        if not intervals:break
    dest=OUT/'n01-MTA-S1-complete-bypass.json';assert not dest.exists(),'Receive existing S1 bypass first'
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (sf,ROOT/prior['bundle'],Path(__file__))})
    planning=dict(complete_selected_S1_members=module_bounds,complete_module_count=len(module),chosen_X_mm=X,
        vertical_initial_outer_domain_Y_mm=initial,vertical_free_domains_Y_mm=intervals,projection_rows=proof,
        actual_clip_queries=clips,ordinary_foreign_margin_mm=1.25,wire_radius_mm=2.1,
        lower_curve_and_full_scene_NOT_proved_by_vertical_domain=True)
    if not intervals:
        save_json(dest,dict(status='NO_CONSERVATIVE_S1_VERTICAL_Y_DOMAIN_NOT_GLOBAL_IMPOSSIBLE',planning=planning,source_sha256=pins,N01_complete=False,native_changed=False,worker_seconds=round(time.monotonic()-tick,3)))
        print('NO_CONSERVATIVE_S1_VERTICAL_Y_DOMAIN_NOT_GLOBAL_IMPOSSIBLE',X,proof[-1] if proof else None,flush=True);return
    a,b=max(intervals,key=lambda v:v[1]-v[0]);Y=(a+b)/2
    theta=math.pi/4+math.asin(((abs(Y)-29)/25.2-1)/math.sqrt(2));assert 0<theta<math.pi/2
    advance=25.2*(math.sin(theta)+math.cos(theta));lead=q[0]-advance-X;assert lead>0
    q=forward(rows,q,d,lead);q,t=bend(rows,q,d,[0,-1,0],25.2,theta);q,t=bend(rows,q,t,[0,0,1],25.2)
    assert abs(q[0]-X)<1e-6 and abs(q[1]-Y)<1e-6 and abs(q[2]-base)<1e-6
    forward(rows,q,t,top-q[2]);new=pipe(rows,2.1);outer=outer_margin(new,docs['outer'])
    planning.update(chosen_Y_mm=Y,upper_clock_radians=theta,upper_clock_degrees=math.degrees(theta),full_new_wire_outer=outer)
    if not outer['ok']:
        save_json(dest,dict(status='S1_BYPASS_FULL_WIRE_OUTER_HOLD',planning=planning,source_sha256=pins,N01_complete=False,native_changed=False,worker_seconds=round(time.monotonic()-tick,3)));print('S1_BYPASS_FULL_WIRE_OUTER_HOLD',outer,flush=True);return
    recipes=copy.deepcopy(prior['recipes']);recipes[n].update(parts=rows,routing_exit_mm=rows[-1]['end'],route_topology='COMPLETE_S1_DATUM_SHARED_FREE_Y',upper_clock_radians=theta)
    actors[n]=new;archive=dest.with_suffix('.breps.zip');geometry=[]
    with zipfile.ZipFile(ROOT/prior['bundle']) as src,zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for i,r in enumerate(prior['geometry']):
            m=r['name'];raw=new.exportBrepToString().encode() if m==n else src.read(r['entry'])
            if m!=n:assert hashlib.sha256(raw).hexdigest()==r['sha256']
            entry=str(i)+'.brep';z.writestr(entry,raw);geometry.append(dict(r,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    result=dict(prior,status='RUNNING_SINGLE_S1_BYPASS_REST',source_sha256={**prior['source_sha256'],**pins},base_world_source_sha256=world.pins,
        planning=planning,recipes=recipes,geometry=geometry,bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),
        byte_identical_actors_from_prior=63,changed_actors=[n],completed_rest=[m for m in prior['completed_rest'] if m!=n],
        completed_static=[],completed_motion=[],rest_checks={},checks=0,failures=[],N01_complete=False,native_changed=False,
        portal_datums={m:r['routing_exit_mm'] for m,r in recipes.items()})
    query=SolidQueries()
    for m,s in world.rest.items():
        if bbox_lower_bound(new.BoundBox,s.BoundBox)>=1.25:continue
        gap=query.distance(new,s);result['rest_checks'][n+'|rest:'+m]=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
        if gap<1.25-1e-6:result['failures'].append(n+'|rest:'+m);break
    result['status']='S1_BYPASS_REST_HOLD' if result['failures'] else 'COMPLETE_MTA_KIT_REST_RECEIVED_STATIC_MOTION_ACCESS_OPEN'
    if not result['failures']:result['completed_rest'].append(n)
    result.update(checks=len(result['rest_checks']),worker_seconds=round(time.monotonic()-tick,3));save_json(dest,result)
    print(result['status'],X,Y,math.degrees(theta),'clips',clips,'seconds',result['worker_seconds'],flush=True)


if __name__=='__main__':main()
