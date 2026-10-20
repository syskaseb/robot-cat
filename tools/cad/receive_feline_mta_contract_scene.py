"""Receive a complete typed MTA overlay; job size is not physical part count; reuse saved rest proof.

Current MTA-family only; explicit source argument, not a universal collision engine.
Named print unions, rigid bought kits and independent wire grips have distinct
policies. Ordinary foreign1.25 and jacket.2 remain unchanged. Stop first cause,
save each actual pair; never finish hundreds of poses after a known rejection.
"""
import gzip,json,time,sys,hashlib,subprocess
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_main_hung_context import compose
from receive_feline_rrp_shared_height import load
from receive_feline_mta_whole_corridor import own
from receive_feline_factory_saddle_plan import CASES
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from receive_feline_underplate_return_gallery import minimum_for
from plan_feline_pi_root_access import profile_gap
from plan_feline_usb_service_bight import outer_margin
from receive_feline_global_case_candidates import placement
from feline_atomic_save import save_json


def main():
    tick=time.monotonic();name=sys.argv[1] if len(sys.argv)>1 else 'n01-MTA-body-retention.json'
    assert Path(name).name==name and name.startswith('n01-MTA-') and name.endswith('.json')
    sf=OUT/name;prior=json.loads(sf.read_text())
    assert prior['status'] in ('COMPLETE_MTA_KIT_REST_RECEIVED_STATIC_MOTION_ACCESS_OPEN','REAR_SHOULDER64_REST_RECEIVED_STATIC_MOTION_ACCESS_OPEN')
    assert set(prior['recipes'])=={'CustomPrefix:W041','CustomPrefix:W042','CustomPrefix:W044','CustomPrefix:W052'}
    assert not prior['failures'] and len(prior['completed_rest'])==len(prior['geometry'])
    for p,h in prior['source_sha256'].items():assert sha(ROOT/p)==h,p
    actors=load(prior);world,old,meta,pins,docs=compose()
    for p,h in pins.items():assert prior['source_sha256'][p]==h,p
    fixed={n:s for n,s in old.items() if n not in prior['retired'] and n not in actors}
    ameta={r['name']:r for r in prior['geometry']};combined={**fixed,**actors}
    pins=dict(prior['source_sha256']);pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (sf,ROOT/prior['bundle'],Path(__file__))})
    dest=sf.with_name(sf.stem+'-scene.json');pf=dest.with_suffix('.pairs.json.gz')
    result=dict(prior,status='RUNNING_WHOLE_MTA_SCENE',source_sha256=pins,completed_static=[],completed_motion=[],
        inherited_rest_actor_count=len(actors),inherited_rest_worker_seconds=prior['worker_seconds'],
        assembly_tools_and_common123_capacity_still_OPEN=True)
    checks={};query=SolidQueries()
    if dest.exists():
        result=json.loads(dest.read_text());assert result['source_sha256']==pins
        assert sha(pf)==result['pair_rows_sha256'];checks=json.loads(gzip.decompress(pf.read_bytes()))
        if result['failures']:print('Existing actual failure; change cause before new geometry',result['failures'],flush=True);return
    elif prior.get('reuse_scene'):
        of=ROOT/prior['reuse_scene']['path'];assert sha(of)==prior['reuse_scene']['sha256'];previous=json.loads(of.read_text())
        for p,h in previous['source_sha256'].items():
            assert sha(ROOT/p)==h,p
            if p in prior['source_sha256']:assert prior['source_sha256'][p]==h,p
        before={r['name']:r for r in previous['geometry']};after={r['name']:r for r in prior['geometry']}
        assert set(before)<=set(after)
        changed={n for n in before if before[n]['sha256']!=after[n]['sha256']} | (set(after)-set(before))
        assert changed==set(prior['changed_actors'])
        for n in set(before)-changed:assert before[n]==after[n],n
        oldpairs=ROOT/previous['pair_rows'];assert sha(oldpairs)==previous['pair_rows_sha256']
        oldrows=json.loads(gzip.decompress(oldpairs.read_bytes()))
        checks={k:v for k,v in oldrows.items() if not changed.intersection(k.split('|'))}
        assert all(v['ok'] for v in checks.values());reused=len(checks)
        for key,row in prior['named_interface_pairs'].items():
            assert all(n in combined for n in key.split('|'))
            assert row['ok'] and row['minimum_mm'] in (0,.2) and row['whole_common_mm3']<1e-5
            assert row['foreign_margin_NOT_changed_mm']==1.25
        checks.update(prior['named_interface_pairs'])
        result['unchanged_pair_cache']=dict(source=of.relative_to(ROOT).as_posix(),source_sha256=sha(of),
            byte_identical_actors=len(before)-len(set(before)&changed),changed_actors=sorted(changed),
            reused_pair_count=reused,exact_named_owner_contracts=len(prior['named_interface_pairs']),
            no_completed_static_actor_inherited=True,original_failures_EXCLUDED_not_passed=previous['failures'])
    def save(status=None):
        if status:result['status']=status
        pf.write_bytes(gzip.compress(json.dumps(checks,separators=(',',':')).encode(),mtime=0))
        result.update(checks=len(checks),failures=[k for k,v in checks.items() if not v['ok']],worker_seconds=round(time.monotonic()-tick,3),
            pair_rows=pf.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(pf));save_json(dest,result)
    def pair(n,s,m,t):
        minimum=minimum_for(n,ameta[n],m,ameta.get(m,meta.get(m,{})))
        if bbox_lower_bound(s.BoundBox,t.BoundBox)>=minimum:return None
        if any(n in members and m in members for members in prior['print_groups'].values()):
            return dict(ok=True,named_features_of_actual_single_solid_print=True)
        a=s;b=t;wa,wb=own(n),own(m);same=wa is not None and wa==wb
        samegrip=n.rsplit(':',1)[0]==m.rsplit(':',1)[0] and n.startswith(('ArcGrip:','InputGrip:','EndGrip:'))
        if samegrip:
            c=s.common(t);assert c.isNull() or c.isValid()
            return dict(ok=c.Volume<1e-5,same_independent_grip_common_mm3=c.Volume)
        rigid=lambda x:x.startswith(('Ref_Material_','CaseBase:','CaseCap:','CapScrew:','CapNut:'))
        if same and rigid(n) and rigid(m):
            return dict(ok=True,unchanged_internal_rigid_kit_from_factory_saddles=True,whole_rear_kit_same_translation_mm=-10 if wa in ('W044','W052') else 0)
        wn=n if n.startswith(('Factory:','CustomPrefix:')) else m if m.startswith(('Factory:','CustomPrefix:')) else None
        other=m if wn==n else n;w=own(wn) if wn else None
        matchinggrip=wn and other.startswith(('InputGrip:'+w+':' if wn.startswith('Factory:') else 'ArcGrip:'+w+':'))
        if matchinggrip:minimum=.2
        ownmouth=False
        if wn:
            cable=combined[wn];at=None;direction=None
            if other=='Ref_Material_'+w+'_Joint_0_0':
                ownmouth=True
                if wn.startswith('Factory:'):
                    at=prior['factory_recipes'][w]['parts'][-1]['end'];direction=[-1,0,0] if w in ('W041','W042') else [1,0,0]
                else:at=prior['recipes'][wn]['point_mm'];direction=prior['recipes'][wn]['axis']
            elif wn.startswith('Factory:') and other=='Ref_Material_MTA_'+CASES[w]+'_0_0':
                ownmouth=True;at=prior['factory_recipes'][w]['parts'][0]['start'];direction=[1,0,0] if w in ('W041','W042') else [-1,0,0]
            if ownmouth:
                c=cable.common(combined[other]);assert c.isNull() or c.isValid()
                assert c.Volume<1e-5,('Whole source ingress overlap',wn,other,c.Volume)
                a=cable.cut(Part.makeCylinder(3,2.5,A.Vector(*at),A.Vector(*direction)));b=combined[other]
        if m==world.bus['name']:
            a=a.copy();a.Placement=docs['inverse']*a.Placement;b=world.bus['original']
        row=dict(ok=(gap:=query.distance(a,b))>=minimum-1e-6,gap_mm=gap,minimum_mm=minimum) if b.Solids else profile_gap(a,b,meta[m].get('nominal_profile_radius_mm') or meta[m].get('radius_mm'),minimum)
        if wn and other=='CaseBase:'+w+'_Joint' and wn.startswith('CustomPrefix:'):
            # Same first source arc and own shoe; a remote extra straight
            # does not relax any foreign pair or allow penetration.
            c=combined[wn].common(combined[other]);assert c.isNull() or c.isValid()
            baseline=query.distance(old[wn],old[other]);assert abs(baseline-.3)<1e-5
            row.update(ok=gap>=min(baseline,minimum)-1e-6 and c.Volume<1e-5,
                minimum_mm=min(baseline,minimum),existing_actual_own_shoe_channel_mm=baseline,
                nominal_channel_reference_mm=.3,ordinary_foreign_margin_unchanged_mm=1.25,whole_common_mm3=c.Volume)
        for panel,shape,name,part in ((n,s,m,t),(m,t,n,s)):
            if panel.startswith('LowerBay:') and name in ('Ref_Material_MTA_FL_0_0','Ref_Material_MTA_FR_0_0','Ref_Material_MTA_RL_0_0','Ref_Material_MTA_RR_0_0','CaseTie:FL','CaseTie:FR','CaseTie:RL','CaseTie:RR'):
                baseline=old[panel].common(part);now=shape.common(part)
                assert (baseline.isNull() or baseline.isValid()) and (now.isNull() or now.isValid())
                before=query.distance(old[panel],part);added=now.cut(baseline).Volume
                row.update(ok=now.Volume<1e-5 and added<1e-5 and gap>=min(before,minimum)-1e-6,
                    existing_named_case_floor_or_tie_slot=True,baseline_gap_mm=before,new_contact_mm3=added)
        if not row['ok'] and b.Solids:
            _,pts,_=a.distToShape(b);row['witness_mm']=[[list(x),list(y)] for x,y in pts[:1]]
        return row
    order=sorted(actors,key=lambda n:(not n.startswith('CustomPrefix:'),not n.startswith('ArcGrip:'),n))
    save()
    for n in order:
        if n in result['completed_static']:continue
        s=actors[n];key=n+'|outer'
        if key not in checks:checks[key]=outer_margin(s,docs['outer']);save()
        if not checks[key]['ok']:save('WHOLE_MTA_SCENE_OUTER_HOLD');return
        for m,t in combined.items():
            if n==m:continue
            key='|'.join(sorted((n,m))) if m in actors else n+'|'+m
            if key in checks:continue
            row=pair(n,s,m,t)
            if row is not None:
                checks[key]=row;save()
                if not row['ok']:save('WHOLE_MTA_SCENE_STATIC_HOLD');return
            if time.monotonic()-tick>220:save('PARTIAL_WHOLE_MTA_SCENE_SAVED');return
        result['completed_static'].append(n);save()
    for n in order:
        if n in result['completed_motion']:continue
        s=actors[n]
        for pose in world.motion:
            if bbox_lower_bound(s.BoundBox,A.BoundBox(*pose['bounds'][0],*pose['bounds'][1]))>=1.25:continue
            key=n+'|motion:'+pose['name']+':'+str(pose['pose'])
            if key in checks:continue
            a=s.copy();a.Placement=placement(pose['r'],pose['t']).inverse()*a.Placement
            gap=query.distance(a,world.rest[pose['name']]);checks[key]=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
            save()
            if not checks[key]['ok']:save('WHOLE_MTA_SCENE_MOTION_HOLD');return
            if time.monotonic()-tick>220:save('PARTIAL_WHOLE_MTA_SCENE_SAVED');return
        result['completed_motion'].append(n);save()
    result['motion_is_sampled_not_continuous']=True
    save('WHOLE_MTA_STATIC36_RECEIVED_ASSEMBLY_ACCESS_AND_SHARED123_OPEN')
    print(result['status'],result['checks'],result['worker_seconds'],flush=True)


if __name__=='__main__':main()
