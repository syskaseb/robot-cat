"""One whole outward-output hypothesis; complete rigid case kits stay together.

Factory tails stay straight. One full custom grip is AFTER the first bend.
No production roots, final custom cuts, stock selection or N01 award implied.
"""
import gzip, hashlib, json, os, time, zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT, sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from feline_profile_corrected_context import compose
from feline_selected_material_contract import load as profiles
from receive_feline_underplate_return_gallery import WIRES, factory_axis, forward, bend, minimum_for
from plan_feline_n01_shared import pipe
from receive_feline_positive_service_deck import open_grip
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from plan_feline_pi_root_access import profile_gap
from plan_feline_usb_service_bight import outer_margin
from receive_feline_global_case_candidates import placement
from receive_feline_psys_frame_load_paths import load


def build_paths(f, centre_x, radius):
    p=np.asarray(f['parts'][0]['start']);d,error=factory_axis(p,f['parts'][0]['end'])
    centre=np.array([centre_x,p[1],-34.]);factory_end=centre-17.75*d
    ff=[];q=forward(ff,p,d,float((factory_end-p)@d))
    assert np.linalg.norm(q-factory_end)<1e-4
    mouth=centre+17.75*d;cc=[];q=forward(cc,mouth,d,.25)
    q,t=bend(cc,q,d,[0,0,1],radius);grip=q.copy()
    q=forward(cc,q,t,45.26-radius-q[2]);assert (q-grip)[2]>=9
    q,t=bend(cc,q,t,-d,radius)
    length=sum(x['length_mm'] for x in ff);assert length+21<=100
    return dict(factory=ff,custom=cc,centre=centre,factory_end=factory_end,
        custom_grip=grip,custom_exit=q,custom_axis=t,d=d,axis_roundoff=error,
        factory_required_mm=length+21,factory_margin_mm=100-length-21)


def main(revision=None, dest_name='n01-end-bay-outputs', extra_pins=(), reuse_receipt=None, changed_actors=()):
    tick=time.monotonic();world,parts,meta,pins,docs=compose();contract,cf,df=profiles()
    lf=OUT/'n01-full-lower-bay-plan-r3.json';lower=json.loads(lf.read_text());factory={r['wire']:r for r in lower['factory_routes']}
    dest=OUT/(dest_name+'.json');pairs=dest.with_suffix('.pairs.json.gz')
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (lf,cf,df,Path(__file__),ROOT/'tools/cad/receive_feline_underplate_return_gallery.py',ROOT/'tools/cad/receive_feline_positive_service_deck.py',*extra_pins)})
    retired=[]
    for w in WIRES:
        for row in lower['parts']:
            n=row['name']
            if n in ('Ref_Material_'+w+'_Joint_0_0','Factory:'+w,'CustomPrefix:'+w) or n.startswith(('Seat:'+w+':','TieLoop:Seat:'+w+':','TieHead:Seat:'+w+':')):retired.append(n)
        retired += ['CaseBase:'+w+'_Joint','CaseCap:'+w+'_Joint']
        retired += [k+':'+w+'_Joint:'+str(i) for k in ('CapScrew','CapNut') for i in (0,1)]
    assert len(retired)==72 and len(set(retired))==72
    assert all(n in parts for n in retired)
    old={n:parts[n] for n in retired};fixed={n:s for n,s in parts.items() if n not in retired}
    actors={};ameta={};owner={};original={};recipes={};checks={}
    result=dict(status='RUNNING_END_BAY_WHOLE_OUTPUTS',source_sha256=pins,retired_current_actors=retired,
        completed_static=[],completed_motion=[],selected=False,N01_complete=False,physical_pass=False,
        new_grip_load_paths_and_full_custom_routes_OPEN=True)
    def save():
        pairs.write_bytes(gzip.compress(json.dumps(checks,separators=(',',':')).encode(),mtime=0))
        result.update(worker_seconds=round(time.monotonic()-tick,3),pair_rows=pairs.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(pairs))
        save_json(dest,result)
    if dest.exists():
        result=json.loads(dest.read_text());assert result['source_sha256']==pins
        assert sha(pairs)==result['pair_rows_sha256'];checks=json.loads(gzip.decompress(pairs.read_bytes()))
        actors=load(result,'geometry');ameta=result['actor_meta'];owner=result['actor_owner'];original=result['actor_original'];recipes=result['recipes']
    else:
        def add(n,s,w,kind,source=None):
            assert s.isValid() and s.Solids,n
            actors[n]=s;owner[n]=w;ameta[n]=dict(kind=kind)
            if source:original[n]=source
            if n.endswith((':band',':head')):ameta[n]['material_role']='selected_T18I_nylon_budget'
        for w in WIRES:
            f=factory[w];profile=contract['portions'][w+'/custom'];assert profile['project_radius_mm']>=2.1
            r=build_paths(f,-90.75 if w in WIRES[:2] else 132.,profile['minimum_project_R_mm'])
            oldcase='Ref_Material_'+w+'_Joint_0_0';shift=r['centre']-np.array(list(old[oldcase].BoundBox.Center))
            for src in [n for n in retired if n==oldcase or n.startswith(('CaseBase:'+w+'_Joint','CaseCap:'+w+'_Joint','CapScrew:'+w+'_Joint:','CapNut:'+w+'_Joint:'))]:
                s=old[src].copy();s.translate(A.Vector(*shift));add('EndBay:'+src,s,w,meta[src].get('kind','proposal_material'),src)
            add('EndFactory:'+w,pipe(r['factory'],f['radius_mm']),w,'wire','Factory:'+w)
            add('EndCustom:'+w,pipe(r['custom'],profile['project_radius_mm']),w,'wire','CustomPrefix:'+w)
            outward=np.array([0,1 if r['centre'][1]>0 else -1,0.])
            for typ,start,axis,side in (('Factory',r['factory_end']-9.25*r['d'],r['d'],outward),('Custom',r['custom_grip'],np.array([0,0,1.]),-r['d'])):
                kit=open_grip(start,axis,side,4.5);kit['pad'].translate(A.Vector(*(-.25*side)))
                for k,s in kit.items():add('EndGrip:'+typ+':'+w+':'+k,s,w,'proposal_material' if k=='pad' else 'project_stock_reservation')
            recipes[w]={k:(v.tolist() if isinstance(v,np.ndarray) else v) for k,v in r.items()}
            recipes[w].update(held_kit_translation_mm=shift.tolist(),strip_mm=11,rework_mm=10,custom_prefix_mm=sum(x['length_mm'] for x in r['custom']),final_cut_and_stock_OPEN=True)
        if revision:result['revision']=revision(actors,ameta,owner,original,recipes,old,fixed,parts,meta)
        archive=dest.with_suffix('.breps.zip');geometry=[]
        with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
            for i,(n,s) in enumerate(actors.items()):
                raw=s.exportBrepToString().encode();entry=str(i)+'.brep';z.writestr(entry,raw);geometry.append(dict(name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
        result.update(geometry=geometry,bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),actor_meta=ameta,actor_owner=owner,actor_original=original,recipes=recipes)
        if reuse_receipt:
            prior=json.loads(reuse_receipt.read_text());assert sha(ROOT/prior['pair_rows'])==prior['pair_rows_sha256']
            # Only these constructor/receiver files changed. The distance,
            # material margin and intentional-pair policies are unchanged.
            constructor_files={'tools/cad/receive_feline_end_bay_outputs.py','tools/cad/receive_feline_rooted_end_bays.py'}
            for p,h in prior['source_sha256'].items():
                if p not in constructor_files:assert pins[p]==h and sha(ROOT/p)==h,('Changed fixed source',p)
            previous={r['name']:r for r in prior['geometry']};changed=set(changed_actors)
            assert changed and changed<=set(actors) and set(previous)==set(actors)
            unchanged=[]
            for r in geometry:
                if r['name'] not in changed:
                    assert r['sha256']==previous[r['name']]['sha256'],('Unexpected geometry change',r['name'])
                    assert ameta[r['name']]==prior['actor_meta'][r['name']]
                    unchanged.append(r['name'])
            prior_checks=json.loads(gzip.decompress((ROOT/prior['pair_rows']).read_bytes()))
            checks={k:v for k,v in prior_checks.items() if not changed.intersection(k.split('|'))}
            result['completed_static']=[n for n in prior['completed_static'] if n in unchanged]
            result['completed_motion']=[n for n in prior['completed_motion'] if n in unchanged]
            result['reused_receipt']=dict(path=reuse_receipt.relative_to(ROOT).as_posix(),sha256=sha(reuse_receipt),
                byte_identical_actors=unchanged,changed_actors=sorted(changed),reused_pair_count=len(checks),fixed_source_pins_verified=True,
                original_receiver_source_preserved_commit='ab3b8aa9',pair_policies_unchanged=True)
        save();print('Saved whole construction',len(actors),flush=True)
    bounds={n:s.BoundBox for n,s in {**fixed,**actors}.items()};query=SolidQueries()
    def pair(n,s,m,t):
        minimum=minimum_for(n,ameta[n],m,ameta.get(m,meta.get(m,{})))
        if bbox_lower_bound(bounds[n],bounds[m])>=minimum:return None
        # Complete held kits have the identical rigid transform, not new fits.
        if n.startswith('EndBay:') and m.startswith('EndBay:') and owner[n]==owner[m] and not result.get('revision'):return dict(ok=True,reused_identical_rigid_kit=True)
        if m==world.bus['name']:
            a=s.copy();a.Placement=docs['inverse']*a.Placement;gap=query.distance(world.bus['original'],a)
        elif t.Solids:gap=query.distance(s,t)
        else:return profile_gap(s,t,meta[m]['nominal_profile_radius_mm'],minimum)
        r=dict(ok=gap>=minimum-1e-6,gap_mm=gap,minimum_mm=minimum)
        if m in actors and owner[n]==owner[m]:
            wire=n if n.startswith(('EndFactory:','EndCustom:')) else m if m.startswith(('EndFactory:','EndCustom:')) else None
            rigid=m if wire==n else n
            same_grip=n.rsplit(':',1)[0]==m.rsplit(':',1)[0] and n.startswith('EndGrip:')
            own_grip=wire and rigid.startswith('EndGrip:'+('Factory' if wire.startswith('EndFactory') else 'Custom')+':'+owner[wire]+':')
            if wire and rigid.startswith('EndBay:') or n.startswith('EndBay:') and m.startswith('EndBay:'):
                left,right=(wire,rigid) if wire else (n,m)
                prior=query.distance(old[original[left]],old[original[right]]);common=s.common(t)
                baseline=old[original[left]].common(old[original[right]])
                assert (common.isNull() or common.isValid()) and (baseline.isNull() or baseline.isValid())
                r.update(ok=common.Volume<=baseline.Volume+1e-5 and gap>=min(prior,minimum)-1e-6,baseline_gap_mm=prior,common_mm3=common.Volume,baseline_common_mm3=baseline.Volume)
            elif own_grip or same_grip:
                common=s.common(t);r.update(ok=common.Volume<1e-5,own_grip_common_mm3=common.Volume)
        if n.startswith('EndFactory:') and factory[owner[n]]['source_group'] in m:
            common=s.common(t);prior=old[original[n]].common(t)
            difference=common.cut(prior).Volume+prior.cut(common).Volume
            r.update(ok=difference<1e-5,source_ingress_difference_mm3=difference)
        # Relocated base must still overlap its original printed root panel.
        if n.startswith('EndBay:CaseBase:') and m.startswith('LowerBay:'):
            common=s.common(t)
            if common.Volume>1e-5:r.update(ok=True,intended_PETG_root_overlap_mm3=common.Volume)
        for a,b in ((n,m),(m,n)):
            if b in result.get('revision',{}).get('root_mates',{}).get(a,[]):
                common=s.common(t);assert common.isNull() or common.isValid()
                r.update(ok=common.Volume>1e-5,intended_positive_PETG_root_mm3=common.Volume)
        for group in result.get('revision',{}).get('planned_print_unions',[]):
            if n in group['members'] and m in group['members']:
                assert group['union_solids']==1
                r.update(ok=True,intended_features_of_single_received_print=group['panel'])
        if [n,m] in result.get('revision',{}).get('captured_nut_panel_pairs',[]) or [m,n] in result.get('revision',{}).get('captured_nut_panel_pairs',[]):
            common=s.common(t);assert common.isNull() or common.isValid()
            r.update(ok=common.Volume<1e-5,captured_nut_with_own_root_panel_no_penetration_mm3=common.Volume)
        return r
    try:
        for n,s in actors.items():
            if n in result['completed_static']:continue
            checks[n+'|outer']=outer_margin(s,docs['outer'])
            for m,t in {**fixed,**actors}.items():
                if n==m:continue
                key='|'.join(sorted((n,m))) if m in actors else n+'|'+m
                if key not in checks:
                    r=pair(n,s,m,t)
                    if r is not None:checks[key]=r
            result['completed_static'].append(n);save()
            print('Static',n,'holds',sum(not r['ok'] for r in checks.values()),flush=True)
            if time.monotonic()-tick>225:raise TimeoutError('Saved complete actor; resume identical sources')
        bad=[k for k,r in checks.items() if not r['ok']]
        if not bad:
            for n,s in actors.items():
                if n in result['completed_motion']:continue
                for pose in world.motion:
                    key=n+'|motion:'+pose['name']+':'+str(pose['pose'])
                    if key in checks or bbox_lower_bound(bounds[n],A.BoundBox(*pose['bounds'][0],*pose['bounds'][1]))>=1.25:continue
                    a=s.copy();a.Placement=placement(pose['r'],pose['t']).inverse()*a.Placement;gap=query.distance(a,world.rest[pose['name']])
                    checks[key]=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
                result['completed_motion'].append(n);save()
                if time.monotonic()-tick>225:raise TimeoutError('Saved complete moving-neighbour receipt')
        result.update(status='END_BAY_OUTPUTS_HOLDS' if any(not r['ok'] for r in checks.values()) else 'END_BAY_OUTPUTS_RECEIVED_ROOTS_OPEN')
    except TimeoutError as e:result.update(status='PARTIAL_END_BAY_OUTPUTS',slice_note=str(e))
    result.update(failures=[k for k,r in checks.items() if not r['ok']],checks=len(checks),full_changed_motion_received=len(result['completed_motion'])==len(actors))
    save();print(result['status'],result['checks'],len(result['failures']),result['worker_seconds'],flush=True)


if __name__=='__main__':print('WORKER_PID',os.getpid(),flush=True);main()
