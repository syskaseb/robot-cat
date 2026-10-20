"""Receive retained panel interfaces after a proven material-only deletion.

No new geometry. Keep all R2 observations. Named print members come from
the accepted output-bay contract, not from an overlap/bounding-box waiver.
MTA bodies bear on their original insulating floor; ties retain their slot.
"""
import gzip,json,time
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_main_hung_context import compose
from receive_feline_rrp_shared_height import load
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from receive_feline_global_case_candidates import placement
from feline_atomic_save import save_json


def main():
    tick=time.monotonic();world,parts,meta,pins,docs=compose()
    sf=OUT/'n01-factory-saddles-received.json';prior=json.loads(sf.read_text());actors=load(prior)
    for p,h in prior['source_sha256'].items():assert sha(ROOT/p)==h,p
    pf0=ROOT/prior['pair_rows'];assert sha(pf0)==prior['pair_rows_sha256'];checks=json.loads(gzip.decompress(pf0.read_bytes()))
    of=OUT/'n01-rooted-end-bays-caps.json';outputs=json.loads(of.read_text());panel='LowerBay:RearPanel';old=parts[panel];new=actors[panel]
    extra=new.cut(old);assert (extra.isNull() or extra.isValid()) and extra.Volume<1e-5
    # The entire structural floor, not a point or an averaged bbox, remains.
    slab=Part.makeBox(400,200,2.3,A.Vector(-200,-100,-44.3));before=old.common(slab);after=new.common(slab)
    assert before.isValid() and after.isValid();floorloss=before.cut(after).Volume;assert floorloss<1e-5
    group=next(g for g in outputs['revision']['planned_print_unions'] if g['panel']==panel)
    members=group['members']+['StructureReserve:U1CarrierRoot1']
    unit=new.multiFuse([parts[n] for n in members if n!=panel]+[actors[n] for n in prior['single_connected_print_groups'][panel] if n!=panel])
    assert unit.isValid() and len(unit.Solids)==1
    b=unit.BoundBox;assert max(b.XLength,b.YLength,b.ZLength)<250
    inherited={};query=SolidQueries()
    for key in prior['failures']:
        assert key.startswith(panel+'|'),key
        name=key.split('|',1)[1];shape=parts[name]
        c=new.common(shape);baseline=old.common(shape)
        assert (c.isNull() or c.isValid()) and (baseline.isNull() or baseline.isValid())
        added=c.cut(baseline).Volume;assert added<1e-5
        if name in members:
            inherited[key]=dict(checks[key],ok=True,member_of_received_output_print_or_U1_root=True,
                actual_current_combined_unit_solids=1,new_contact_material_mm3=added)
        elif name in ('Ref_Material_MTA_RL_0_0','Ref_Material_MTA_RR_0_0','CaseTie:RL','CaseTie:RR'):
            previous_gap=query.distance(old,shape);current_gap=checks[key]['gap_mm']
            assert c.Volume<1e-5 and current_gap>=previous_gap-1e-6
            inherited[key]=dict(checks[key],ok=True,unchanged_own_case_floor_or_own_tie_slot=True,
                inherited_nominal_floor_or_slot_gap_mm=previous_gap,current_common_mm3=c.Volume,
                structural_floor_removed_mm3=floorloss,ordinary_foreign_margin_NOT_reduced=True)
        else:raise AssertionError(('Foreign material cannot be reclassified',name))
    assert len(inherited)==11;checks.update(inherited)
    dest=OUT/'n01-factory-inputs-current-received.json';pf=dest.with_suffix('.pairs.json.gz')
    result=dict(prior,status='RUNNING_FACTORY_CURRENT_MOTION',source_sha256={**pins,**{p.relative_to(ROOT).as_posix():sha(p) for p in (sf,pf0,ROOT/prior['bundle'],of,Path(__file__))}},
        adopted_static_checks=len(checks),adopted_static_worker_seconds=prior['worker_seconds'],
        panel_contracts_received=inherited,structural_floor_removed_mm3=floorloss,new_panel_outside_old_mm3=extra.Volume,
        retained_root_output_combined_unit_solids=1,combined_print_envelope_mm=[b.XLength,b.YLength,b.ZLength],
        completed_motion=[],N01_complete=False,physical_pass=False,native_changed=False,
        assembly_tools_and_full123_shared_plan_still_OPEN=True)
    if dest.exists():
        current=json.loads(dest.read_text());assert current['source_sha256']==result['source_sha256']
        assert sha(pf)==current['pair_rows_sha256'];checks=json.loads(gzip.decompress(pf.read_bytes()));result=current
    def save():
        pf.write_bytes(gzip.compress(json.dumps(checks,separators=(',',':')).encode(),mtime=0))
        result.update(checks=len(checks),failures=[k for k,v in checks.items() if not v['ok']],pair_rows=pf.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(pf),worker_seconds=round(time.monotonic()-tick,3));save_json(dest,result)
    save()
    for n,s in actors.items():
        if n in result['completed_motion']:continue
        for pose in world.motion:
            if bbox_lower_bound(s.BoundBox,A.BoundBox(*pose['bounds'][0],*pose['bounds'][1]))>=1.25:continue
            key=n+'|motion:'+pose['name']+':'+str(pose['pose'])
            if key in checks:continue
            a=s.copy();a.Placement=placement(pose['r'],pose['t']).inverse()*a.Placement
            gap=query.distance(a,world.rest[pose['name']]);checks[key]=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
        result['completed_motion'].append(n);save()
        if time.monotonic()-tick>220:result['status']='PARTIAL_FACTORY_CURRENT_MOTION_SAVED';save();return
    result['status']='FACTORY_CURRENT_MOTION_HOLDS' if result['failures'] else 'FOUR_FACTORY_INPUTS_ROOTED_STATIC36_RECEIVED_TOOLS_OPEN'
    result['motion_is_sampled_not_continuous']=True;save();print(result['status'],result['checks'],len(result['failures']),result['worker_seconds'],flush=True)


if __name__=='__main__':main()
