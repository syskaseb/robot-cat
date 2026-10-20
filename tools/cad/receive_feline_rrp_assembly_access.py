"""Constructive RR_P installation and opened-panel service envelopes.

Conservative box proves the full foreign cap stroke; own curved mating
interfaces are checked at six poses, NOT claimed as a continuous sweep.
The pointed cutting-tool budget is provisional, not a selected tool drawing.
"""
import gzip,json,time
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_rrp_rooted_context import compose
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from feline_atomic_save import save_json


def main():
    tick=time.monotonic();world,parts,meta,pins,docs=compose()
    cap=parts['EarlyRR:comb:outer'];b=cap.BoundBox
    sweep=Part.makeBox(b.XLength,b.YLength,b.ZLength+5,A.Vector(b.XMin,b.YMin,b.ZMin))
    head=parts['EarlyRR:head_budget'];p=head.BoundBox.Center
    tool=Part.makeCylinder(1,8,p).fuse(Part.makeCylinder(3,20,p+A.Vector(0,0,8)))
    assert sweep.isValid() and tool.isValid()
    mates={'EarlyRR:comb:outer','EarlyRR:comb:inner',*docs['RRP_received']['recipes']}
    cut_stock={'EarlyRR:band_budget','EarlyRR:head_budget'}
    checks={};query=SolidQueries()
    for label,actor in (('cap_full_foreign_stroke',sweep),('pointed_tool_full_approach',tool)):
        for n,s in parts.items():
            if label=='cap_full_foreign_stroke' and n in mates|cut_stock:continue
            if label=='pointed_tool_full_approach' and n in cut_stock:continue
            minimum=.25 if label=='cap_full_foreign_stroke' and n=='Station:RR_P:case' else 1.25
            if bbox_lower_bound(actor.BoundBox,s.BoundBox)>=minimum:continue
            q=actor
            if n==world.bus['name']:
                q=actor.copy();q.Placement=docs['inverse']*q.Placement;s=world.bus['original']
            if not s.Solids:
                checks[label+'|'+n]=dict(ok=False,unresolved_curve_budget=n);continue
            gap=query.distance(q,s);checks[label+'|'+n]=dict(ok=gap>=minimum-1e-6,gap_mm=gap,minimum_mm=minimum)
    for height in (0.,1.,2.,3.,4.,5.):
        moved=cap.copy();moved.translate(A.Vector(0,0,height))
        for n in mates-{'EarlyRR:comb:outer'}:
            minimum=.25 if n=='EarlyRR:comb:inner' else .15
            gap=query.distance(moved,parts[n]);checks['own_mate_sample:'+str(height)+'|'+n]=dict(ok=gap>=minimum-1e-6,gap_mm=gap,minimum_mm=minimum)
    files=(Path(__file__),ROOT/'tools/cad/feline_rrp_rooted_context.py')
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in files})
    failures=[k for k,v in checks.items() if not v['ok']]
    dest=OUT/'n01-RRP-assembly-access.json';rf=dest.with_suffix('.pairs.json.gz')
    rf.write_bytes(gzip.compress(json.dumps(checks,separators=(',',':')).encode(),mtime=0))
    result=dict(status='RRP_CONSTRUCTIVE_ASSEMBLY_ACCESS_RECEIVED_WITH_GATES' if not failures else 'RRP_ASSEMBLY_ACCESS_HOLDS',
        failures=failures,checks=len(checks),pair_rows=rf.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(rf),source_sha256=pins,
        cap_lift_mm=5,foreign_stroke_conservative_box_not_part_contact=True,own_mating_translation_samples_mm=[0,1,2,3,4,5],
        own_mating_continuous_stroke_not_certified=True,top_skin_panel_must_be_removed=True,
        pointed_tool_project_tip_diameter_mm=2,pointed_tool_tip_length_mm=8,project_upper_shank_diameter_mm=6,
        unpowered_bench_assembly_only=True,no_routine_WAGO_disconnect_for_ATO=True,
        assembly_sequence=['Print the bankbed/lowercomb/root as one <250mm planning union; native manufacturing gate remains N03.',
            'Install unchanged R47 holders and existing bankbed fasteners; no new hole in purchased parts.',
            'Delivery dry-fit the .5mm case-only adhesive backer; never use lever side as a clamp.',
            'Lay four jackets in individual full9 curved channels; install upper half and the complete selected T18I; trim tail.',
            'With power disconnected and upper skin panel removed, cut/remove own nylon stock, then lift upper half +5mm.',
            'ATO fuses retain their received lateral withdrawal/tool envelopes; this sequence does not require74 WAGO disconnects.'],
        delivery_and_later_gates=['Actual adhesive/insulation OD and each jacket pull test','Native split details/parameter/save-reopen N03',
            'Own mating path continuous detailed validation','Chosen hand tool/skin aperture fit'],
        N01_complete=False,native_changed=False,physical_pass=False,worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result);print(result['status'],result['checks'],len(failures),result['worker_seconds'],failures,flush=True)


if __name__=='__main__':main()
