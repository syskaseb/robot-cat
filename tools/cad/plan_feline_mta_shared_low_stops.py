"""Shared low-stop height from every current fixed/moving foreign material.

Use the six actual rail footprints, not the cradle's empty middle bbox.
Clipped material projections give sufficient clearance; empty domains are
not global infeasibility. No case, wire, adhesive or floor translation.
"""
import hashlib,json,time,zipfile
from pathlib import Path
import FreeCAD as A
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_main_hung_context import compose
from receive_feline_rrp_shared_height import load
from receive_feline_factory_saddle_plan import box
from receive_feline_underplate_return_gallery import minimum_for
from receive_feline_global_case_candidates import placement
from feline_fore_power_pair import SolidQueries
from feline_atomic_save import save_json


def main():
    tick=time.monotonic();world,parts,meta,pins,docs=compose()
    sf=OUT/'n01-MTA-owned-case-bays.json';r=json.loads(sf.read_text());actors=load(r)
    observed=sf.with_name(sf.stem+'-scene.json');previous=json.loads(observed.read_text())
    assert previous['failures']==['MTACradle:RL|Ref_Material_W041_Joint_0_0']
    for rec in (r,previous):
        for p,h in rec['source_sha256'].items():assert sha(ROOT/p)==h,p
    effective={n:s for n,s in parts.items() if n not in r['retired']};effective.update(actors)
    fm={**meta,**{p['name']:p for p in r['geometry']}};plans={};changed=set();query=SolidQueries()
    for code,p in r['bonded_rear_cases'].items():
        name=p['cradle'];case=parts[p['case']];b=case.optimalBoundingBox(False,False);old=actors[name]
        floor=old.BoundBox.ZMin;initial=old.BoundBox.ZMax;limit=initial
        rails=[(b.XMin-2.6,b.XMax+2.6,b.YMin-2.6,b.YMin-.2),
               (b.XMin-2.6,b.XMax+2.6,b.YMax+.2,b.YMax+2.6)]
        rails.extend((a,c,d,e) for a,c in ((b.XMin-2.6,b.XMin-.2),(b.XMax+.2,b.XMax+2.6))
                     for d,e in ((b.YMin-2.6,b.YMin+3),(b.YMax-3,b.YMax+2.6)))
        own=set(r['print_groups']['LowerBay:RearPanel'])|{p['case'],name}
        sources=[(n,s,None,None,fm[n]) for n,s in effective.items() if n not in own]
        sources.extend(('motion:'+a['name']+':'+str(a['pose']),world.rest[a['name']],a['bounds'],placement(a['r'],a['t']),dict(kind='rigid')) for a in world.motion)
        clips=0;reductions=[];cache={}
        for n,s,bounds,tf,m in sources:
            margin=minimum_for(name,fm[name],n,m)
            if not s.Solids:margin+=m.get('nominal_profile_radius_mm') or m.get('radius_mm') or 0
            bb=s.BoundBox
            lo=[bb.XMin,bb.YMin,bb.ZMin] if bounds is None else bounds[0]
            hi=[bb.XMax,bb.YMax,bb.ZMax] if bounds is None else bounds[1]
            if hi[2]<floor or lo[2]>limit+margin:continue
            active=[a for a in rails if hi[0]>=a[0]-margin and lo[0]<=a[1]+margin and hi[1]>=a[2]-margin and lo[1]<=a[3]+margin]
            if not active:continue
            key=(limit,margin,tuple(active))
            if key not in cache:
                masks=[box([a-margin,c-margin,floor],[b+margin,d+margin,limit+margin]) for a,b,c,d in active]
                roi=masks[0].multiFuse(masks[1:]) if len(masks)>1 else masks[0]
                assert roi.isValid();cache[key]=roi
            roi=cache[key].copy()
            if n==world.bus['name']:s=world.bus['original'];tf=docs['inverse'].inverse()
            if tf is not None:roi.Placement=tf.inverse()*roi.Placement
            assert s.isValid(),n
            cut=s.common(roi);assert cut.isNull() or cut.isValid(),n;clips+=1
            if cut.isNull() or not cut.Vertexes:continue
            if tf is not None:cut.Placement=tf*cut.Placement
            low=max(floor,cut.optimalBoundingBox(False,False).ZMin)
            bound=low-margin
            if bound<limit:
                reductions.append(dict(source=n,actual_material_clip_volume_mm3=cut.Volume,material_low_Z_mm=low,
                    required_margin_mm=margin,sufficient_wall_top_Z_mm=bound,bbox_overlap_NOT_contact=True))
                limit=bound
            if limit<=b.ZMin+1.5:break
        chosen=limit-.25 if limit<initial-1e-6 else initial
        plans[code]=dict(original_stop_top_Z_mm=initial,sufficient_top_bound_Z_mm=limit,chosen_top_Z_mm=chosen,
            minimum_case_XY_stop_height_mm=chosen-b.ZMin,actual_clip_queries=clips,reductions=reductions,
            all_current_fixed_and36motion_considered=True,material_projection_is_sufficient_not_global_infeasibility=True)
        assert chosen>=b.ZMin+1.5,(code,'No sufficient low-stop domain',plans[code])
        bb=old.BoundBox;new=old.cut(box([bb.XMin-.1,bb.YMin-.1,chosen],[bb.XMax+.1,bb.YMax+.1,bb.ZMax+.1]))
        assert new.isValid() and len(new.Solids)==1
        extra=new.cut(old);assert (extra.isNull() or extra.isValid()) and extra.Volume<1e-5
        actors[name]=new;changed.add(name)
        plans[code]['new_material_outside_old_mm3']=extra.Volume
        for row in reductions:
            if row['source'] in effective:
                other=effective[row['source']];gap=query.distance(new,other)
                assert gap>=row['required_margin_mm']-1e-6,(name,row['source'],gap)
                row['new_actual_whole_cradle_gap_mm']=gap
    parent='LowerBay:RearPanel';unit=actors[parent].multiFuse([actors[n] if n in actors else parts[n] for n in r['print_groups'][parent] if n!=parent])
    assert unit.isValid() and len(unit.Solids)==1
    b=unit.BoundBox;size=[b.XLength,b.YLength,b.ZLength];assert max(size)<250
    dest=OUT/'n01-MTA-low-stop-cradles.json';assert not dest.exists();archive=dest.with_suffix('.breps.zip');geometry=[]
    with zipfile.ZipFile(ROOT/r['bundle']) as src,zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as target:
        for i,row in enumerate(r['geometry']):
            n=row['name'];raw=actors[n].exportBrepToString().encode() if n in changed else src.read(row['entry'])
            if n not in changed:assert hashlib.sha256(raw).hexdigest()==row['sha256']
            entry=str(i)+'.brep';target.writestr(entry,raw);geometry.append(dict(row,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (sf,ROOT/r['bundle'],observed,ROOT/previous['pair_rows'],Path(__file__))})
    result=dict(r,status='COMPLETE_MTA_KIT_REST_RECEIVED_STATIC_MOTION_ACCESS_OPEN',source_sha256={**r['source_sha256'],**pins},
        geometry=geometry,bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),changed_actors=sorted(changed),removed_actor_aliases=[],
        byte_identical_actors_from_prior=70,shared_low_stop_domains=plans,rear_print_union_solids=1,rear_print_envelope_mm=size,
        rest_and_outline_inherited_by_actual_material_subset=True,reuse_scene=dict(path=observed.relative_to(ROOT).as_posix(),sha256=sha(observed)),
        completed_static=[],completed_motion=[],N01_complete=False,native_changed=False,physical_pass=False,worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result);print('SHARED_LOW_STOPS_CONSTRUCTIVE',plans,size,result['worker_seconds'],flush=True)


if __name__=='__main__':main()
