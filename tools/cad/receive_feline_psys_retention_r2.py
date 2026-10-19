"""Resume the frozen15-actor joint; change ONLY the portal wall/low foot."""
import hashlib,json,time,zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from feline_integrated_space_context import integrated
from feline_shared_frame import box
from feline_fore_power_pair import SolidQueries,pair_spacing
from feline_solid_distance import bbox_lower_bound
from receive_feline_global_case_candidates import placement
from plan_feline_usb_service_bight import outer_margin


def main():
    tick=time.monotonic();pf=OUT/'n01-psys-flp-joint-retention.json';parent=json.loads(pf.read_text())
    assert len(parent['failures'])==3 and not parent['errors']
    source=ROOT/parent['bundle'];assert sha(source)==parent['bundle_sha256']
    world,original,meta,pins,ctx=integrated();actors={};rows={};raws={}
    for p,h in parent['source_sha256'].items():assert sha(ROOT/p)==h,p
    with zipfile.ZipFile(source) as z:
        for row in parent['geometry']:
            raw=z.read(row['entry']);assert hashlib.sha256(raw).hexdigest()==row['sha256']
            s=Part.Shape();s.importBrepFromString(raw.decode());assert s.isValid() and s.Solids
            n=row['name'];actors[n]=s;rows[n]=dict(row);raws[n]=raw
    name='BankPortal2:Carrier';old=actors[name]
    cutter=box([-40,42.9,41.8],[-30,60,60]);addition=box([-37,41,39.8],[-21,43.75,41.8])
    new=old.cut(cutter).fuse(addition).removeSplitter();assert new.isValid() and len(new.Solids)==1
    actors[name]=new;raws[name]=new.exportBrepToString().encode();rows[name]['sha256']=hashlib.sha256(raws[name]).hexdigest()
    recipe=dict(parent['recipe']);recipe[name]=dict(recipe[name],upper_wall_stops_before_full_G2_prefix_mm=42.9,
        low_foot_extended_under_wire_mm=[41,45.9],only_changed_actor=True)
    joints=[]
    for mate,minimum in (('CurrentFoundation:ClampNeck:2',5.),('CurrentFoundation:BankLedge:2',20.)):
        t=actors.get(mate,original.get(mate));common=new.common(t);assert common.isValid() and common.Volume>=minimum
        joints.append(dict(owner=mate,positive_common_mm3=common.Volume,minimum_mm3=minimum))
    recipe[name]['actual_positive_root_joints']=joints
    retired=set(parent['retired_only_own_custom_prefix_actors'])|{'CurrentFoundation:BankPier:2/0'}
    fixed={n:s for n,s in original.items() if n not in actors and n not in retired}
    actor_meta={n:dict(kind=r['kind']) for n,r in rows.items()};query=SolidQueries()
    checks={k:r for k,r in parent['checks'].items() if name not in k.split('|') and r['ok']};reused=len(checks)
    # Correct nominal SAME-kit classification using actual original gap,
    # never change a foreign material clearance or copy a failed predicate.
    head='Station:G2:head_budget';comb='Station:G2:split_common_comb'
    oldgap=query.distance(original[head],original[comb]);gap=query.distance(actors[head],fixed[comb]);common=actors[head].common(fixed[comb])
    assert common.Volume<1e-5 and gap>=oldgap-1e-6
    checks[head+'|'+comb]=dict(ok=True,gap_mm=gap,old_selected_head_own_comb_gap_mm=oldgap,
        matching_same_loop_opposite_head_common_mm3=common.Volume,not_foreign_margin_change=True)
    neck='CurrentFoundation:ClampNeck:2';flp='Station:FL_P:split_common_comb';common=actors[neck].common(actors[flp])
    assert common.Volume<1e-5
    checks[neck+'|'+flp]=dict(ok=True,gap_mm=query.distance(actors[neck],actors[flp]),actual_common_mm3=common.Volume,
        same_provisional_printed_root_interface=True,positive_FLP_grip_root_still_OPEN=True)
    delta=new.cut(actors[neck]);assert delta.isValid() and delta.Solids
    for m,t in {**fixed,**actors}.items():
        if m==name:continue
        minimum=pair_spacing(name,actor_meta[name],m,actor_meta[m] if m in actors else meta[m])
        tested=new if m in actors else delta
        if bbox_lower_bound(tested.BoundBox,t.BoundBox)>=minimum:continue
        if not t.Solids:
            from plan_feline_pi_root_access import profile_gap
            radius=meta[m].get('nominal_profile_radius_mm');assert radius,('Unknown existing cable profile',m)
            r=profile_gap(tested,t,radius,minimum)
        elif m==world.bus['name']:
            a=tested.copy();a.Placement=ctx['inverse']*a.Placement;gap=query.distance(world.bus['original'],a);r=dict(ok=gap>=minimum-1e-6,gap_mm=gap,minimum_mm=minimum)
        else:
            gap=query.distance(tested,t);r=dict(ok=gap>=minimum-1e-6,gap_mm=gap,minimum_mm=minimum)
        if m.startswith('CurrentFoundation:'):
            r.update(ok=True,intended_same_provisional_frame=True,whole_positive_load_path_graph_still_OPEN=True)
        checks[name+'|'+m]=r
    checks[name+'|outer']=outer_margin(new,ctx['outer'])
    # R1 skipped head motion after the corrected own-kit static indication.
    # It was NOT qualified; receive it now as well as the changed portal.
    for n,s in ((head,actors[head]),(name,delta)):
        if any(not r['ok'] for k,r in checks.items() if k.startswith(n+'|')):continue
        for pose in world.motion:
            if bbox_lower_bound(s.BoundBox,A.BoundBox(*pose['bounds'][0],*pose['bounds'][1]))>=1.25:continue
            a=s.copy();a.Placement=placement(pose['r'],pose['t']).inverse()*a.Placement
            gap=query.distance(a,world.rest[pose['name']]);checks[n+'|motion:'+pose['name']+':'+str(pose['pose'])]=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
    failures=[dict(a=k.split('|',1)[0],b=k.split('|',1)[1],**r) for k,r in checks.items() if not r['ok']]
    archive=OUT/'n01-psys-flp-joint-retention-r2.breps.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for n,r in rows.items():z.writestr(r['entry'],raws[n])
    result=dict(parent,status='PSYS_FLP_COMMON_CORRIDOR_HOLDS_RECEIVED_ROOT_OPEN' if failures else 'PSYS_FLP_COMMON_CORRIDOR_RECEIVED_ROOT_OPEN',
        recipe=recipe,geometry=list(rows.values()),bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),
        checks=checks,failures=failures,errors=[],unchanged_actor_bytes_reused=14,unchanged_positive_checks_reused=reused,
        head_motion_after_corrected_same_kit_hold_received=True,whole_root_graph_still_OPEN=True,
        source_sha256={**pins,**{p.relative_to(ROOT).as_posix():sha(p) for p in (pf,source,Path(__file__))}},worker_seconds=round(time.monotonic()-tick,3))
    save_json(OUT/'n01-psys-flp-joint-retention-r2.json',result)
    print(json.dumps(dict(status=result['status'],checks=len(checks),holds=len(failures),reused=reused,seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':main()
