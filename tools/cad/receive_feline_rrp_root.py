"""Ground the whole curved RR_P grip AND case without moving the bank.

One column in the existing nine-mm holder gap, flared foot into the received
bank bed, and a case-only insulating backer. This is planning BRep material,
not native N03 manufacturing or an adhesive/strength/physical qualification.
"""
import gzip,hashlib,json,os,time,zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_rrp_composed_context import compose,received
from receive_feline_rrp_shared_height import load
from feline_common_retention_roots import case_backer
from plan_feline_n01_shared import pipe
from feline_atomic_save import save_json
from feline_fore_power_pair import SolidQueries
from receive_feline_underplate_return_gallery import minimum_for
from feline_solid_distance import bbox_lower_bound
from plan_feline_pi_root_access import profile_gap
from plan_feline_usb_service_bight import outer_margin
from receive_feline_global_case_candidates import placement


def construct(parts,receipt):
    bed=parts['CurrentFoundation:BankBedCurrent:1'];old=parts['EarlyRR:comb:inner']
    housing3=parts['Ref_Material_F_L3_CP2_Housing_0_0'];housing4=parts['Ref_Material_F_L4_CP2_Housing_0_0']
    x=(housing3.BoundBox.XMax+housing4.BoundBox.XMin)/2
    assert abs(housing4.BoundBox.XMin-housing3.BoundBox.XMax-9)<1e-5
    y=60.5;z=bed.BoundBox.ZMax-.5
    column=Part.makeCylinder(2,96-z,A.Vector(x,y,z))
    foot=Part.makeCylinder(3,3,A.Vector(x,y,z));raw=column.fuse(foot)
    case=parts['Station:RR_P:case'];backer,info=case_backer('RR_P',case,{})
    start=A.Vector(x,y,88.5);end=backer.CenterOfMass-A.Vector(0,0,1)
    d=end-start;arm=Part.makeCylinder(1.5,d.Length,start,d).fuse(Part.makeSphere(1.5,end))
    raw=raw.fuse(arm).fuse(backer)
    for rec in receipt['recipes'].values():raw=raw.cut(pipe(rec['parts'],rec['project_radius_mm']+.15))
    root=old.fuse(raw).removeSplitter()
    assert root.isValid() and len(root.Solids)==1
    bed_overlap=root.common(bed);grip_overlap=raw.common(old)
    assert bed_overlap.isValid() and bed_overlap.Volume>10
    assert grip_overlap.isValid() and grip_overlap.Volume>1
    union=root.fuse(bed).removeSplitter();assert union.isValid() and len(union.Solids)==1
    assert max(union.BoundBox.XLength,union.BoundBox.YLength,union.BoundBox.ZLength)<250
    return root,dict(column_axis_mm=[x,y],column_diameter_mm=4,foot_diameter_mm=6,
        bank_bed_positive_union_mm3=bed_overlap.Volume,grip_positive_union_mm3=grip_overlap.Volume,
        combined_bankbed_root_single_Solid=True,combined_envelope_mm=[union.BoundBox.XLength,union.BoundBox.YLength,union.BoundBox.ZLength],
        case_backer=info,adhesive_project_gap_mm=.5,case_and_bank_holders_unchanged=True,
        own_four_jacket_channels_extended_into_root=True,adhesion_pull_strength_and_print_fit_phase2=True)


def main():
    tick=time.monotonic();sf,parent=received();world,parts,meta,pins,docs=compose()
    root,recipe=construct(parts,parent);name='EarlyRR:comb:inner';bed='CurrentFoundation:BankBedCurrent:1'
    fg=OUT/'n01-psys-flp-frame-load-paths.json';graph=json.loads(fg.read_text())
    assert graph['status']=='ALL_CHANGED_FRAME_SOLIDS_REACH_EXISTING_CLAMP_SEATS' and not graph['floating_solids']
    for p,h in graph['source_sha256'].items():assert sha(ROOT/p)==h,p
    sources=(sf,fg,ROOT/parent['bundle'],Path(__file__),ROOT/'tools/cad/feline_common_retention_roots.py')
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in sources})
    dest=OUT/'n01-RRP-rooted-module.json';arc=dest.with_suffix('.breps.zip');pf=dest.with_suffix('.pairs.json.gz')
    assert not dest.exists(),'Receive the existing rooted module result'
    raw=root.exportBrepToString().encode()
    with zipfile.ZipFile(arc,'w',zipfile.ZIP_DEFLATED) as z:z.writestr('root.brep',raw)
    checks={};result=dict(status='RUNNING_RRP_ROOTED_MODULE',recipe=recipe,source_sha256=pins,
        bundle=arc.relative_to(ROOT).as_posix(),bundle_sha256=sha(arc),geometry=[dict(name=name,entry='root.brep',sha256=hashlib.sha256(raw).hexdigest())],
        N01_complete=False,native_changed=False,physical_pass=False,all_other_seven_RRP_actors_unchanged=True,
        complete_whole_harness_roots_tools_installation_still_OPEN=True)
    def save():
        pf.write_bytes(gzip.compress(json.dumps(checks,separators=(',',':')).encode(),mtime=0))
        result.update(pair_rows=pf.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(pf),checks=len(checks),
            failures=[k for k,v in checks.items() if not v['ok']],worker_seconds=round(time.monotonic()-tick,3))
        save_json(dest,result)
    save();query=SolidQueries();checks['outer']=outer_margin(root,docs['outer'])
    for n,s in parts.items():
        if n==name:continue
        minimum=minimum_for(name,{'kind':'proposal_material'},n,meta[n])
        if n in parent['recipes'] or n in ('EarlyRR:band_budget','EarlyRR:head_budget'):minimum=.15
        if n=='Station:RR_P:case':minimum=.5
        if n=='EarlyRR:comb:outer':minimum=.25
        if n==bed:
            checks[n]=dict(ok=True,positive_union_mm3=recipe['bank_bed_positive_union_mm3'],intended_same_print_union=True);continue
        if bbox_lower_bound(root.BoundBox,s.BoundBox)>=minimum:continue
        tested=root
        if n==world.bus['name']:
            tested=root.copy();tested.Placement=docs['inverse']*tested.Placement;s=world.bus['original']
        if s.Solids:
            gap=query.distance(tested,s);checks[n]=dict(ok=gap>=minimum-1e-6,gap_mm=gap,minimum_mm=minimum)
        else:
            radius=meta[n].get('nominal_profile_radius_mm') or meta[n].get('radius_mm')
            checks[n]=profile_gap(tested,s,radius,minimum) if radius else dict(ok=False,unresolved_curve_budget=n)
    save();result['static_complete']=True
    if not result['failures']:
        for pose in world.motion:
            if bbox_lower_bound(root.BoundBox,A.BoundBox(*pose['bounds'][0],*pose['bounds'][1]))>=1.25:continue
            q=root.copy();q.Placement=placement(pose['r'],pose['t']).inverse()*q.Placement
            gap=query.distance(q,world.rest[pose['name']]);checks['motion:'+pose['name']+':'+str(pose['pose'])]=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
        result['sampled_motion_complete']=True
    result['status']='RRP_ROOTED_MODULE_HOLDS' if result['failures'] else 'RRP_ROOTED_GRIP_AND_CASE_STATIC36_RECEIVED_ASSEMBLY_OPEN'
    save();print(result['status'],result['checks'],len(result['failures']),result['worker_seconds'],recipe,flush=True)


if __name__=='__main__':print('WORKER_PID',os.getpid(),flush=True);main()
