"""Run the unchanged shared-support checker with an explicit Knee replacement.

Dependency injection changes ONLY the Knee data passed to scene_parts. The
original geometry checker/support recipe remain byte-for-byte unchanged.
Pin the replacement and this adapter in the resulting combined receipt.
Merge exact same-geometry pair receipts to avoid redoing inherited checks.
"""
import json
from pathlib import Path
import check_low_hip_loom_layout as P
from immutable_bounds import ImmutableBounds
from joint_support_current_allocation import allocate


def run():
    planfile=P.OUT/'outboard-knee-planes-plan.json';gatefile=P.OUT/'outboard-knee-planes-checks.json'
    plan=json.loads(planfile.read_text());gate=json.loads(gatefile.read_text())
    assert gate['status']=='KNEE_PLANES_SAMPLED_MATERIAL_CLEAR_NATIVE_ROOTS_OPEN'
    assert gate['cases']==108 and not gate['contacts'] and not gate['errors']
    for source in (plan,gate):
        for n,h in source['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    rows={r['section']:r for r in plan['knees']};assert len(rows)==8
    target=P.OUT/'joint-support-pair-cache.json';extra=P.OUT/'outboard-knee-pair-cache.json'
    a=json.loads(target.read_text());b=json.loads(extra.read_text())
    assert a['checker_sha256']==b['checker_sha256']==P.SHA(Path(P.__file__).with_name('exact_pair_receipts.py'))
    for n,result in b['records'].items():
        if n in a['records']:assert a['records'][n]==result,('Conflicting exact receipt',n)
        a['records'][n]=result
    target.write_text(json.dumps(a,separators=(',',':'))+'\n',encoding='utf-8')
    original=P.scene_parts
    def current_knee(row,hip,knee,axes):
        assert row['section'] in rows
        return original(rows[row['section']],hip,knee,axes)
    P.scene_parts=current_knee;original_near=P.W.near;bounds=ImmutableBounds()
    original_allocate=P.allocate;P.allocate=allocate
    P.W.near=bounds.near
    try:P.run()
    finally:P.scene_parts=original;P.W.near=original_near;P.allocate=original_allocate
    output=P.OUT/'low-hip-shared-layout.json';report=json.loads(output.read_text())
    report['Knee_data_replacement']=dict(plan=planfile.relative_to(P.ROOT).as_posix(),exact_Knee_cases=108,
        section_ids=sorted(rows),scope='Only Knee row data replaced; full original shared checker and support geometry unchanged. No contact exclusions or radius changes.')
    report['immutable_bounds_profile']=bounds.profile()
    report['case_attachment_change']='Prototype bonded upper cap: actual main casing top minus50mm2 exposed gap-fill allocation. No case band or hidden chassis cut. Six independent jacket ties perleg carry wire restraint into cap, not WAGO. Adhesive product/PETG-case adhesion/load/creep/cut-removal phase2 gates remain OPEN; this is material-fit, not retention strength proof.'
    report['assembly'][1]='Dry-fit cap and independently restrained jacket lands; hold cap using assembly fixture while curing exposed casing-to-cap adhesive patch. Only bond actual main casing, not seam/shaft/connector/PCB/vent. Verify adhesive compatibility/load before moving or powering; no quick removal or guaranteed residue-free release. Deep service: support loom, cut sacrificial cured bead, release replaceable cuff. No factory-case screw assumed.'
    report['provisional']=[v for v in report['provisional'] if 'case strap' not in v and 'Case head' not in v]
    report['provisional'] += ['Gap-filled50mm2 bond on actual exposed main housing is a prototype candidate. DOWSIL3145 is manufacturer-described electronics stabilizing RTV, NOT a validated PETG/servo-case bond or chosen purchase. No load/peel/creep strength claimed. Small jacket heads remain6x6x5mm project reservations.']
    report['adhesive_reference']='https://www.dow.com/en-us/pdp.dowsil-3145-rtv-mil-a-46146-adhesive-sealant.01059548z.html'
    report['rear_root_relief_basis']='Current exact inverse-motion witnessZmax32.3493670273126 atHip-15 plus0.5mm project margin, matching existing frontHip+15 root relief. Cap/bond/pivots/routes unchanged.'
    report['source_sha256'].update({p.relative_to(P.ROOT).as_posix():P.SHA(p) for p in (planfile,gatefile,P.OUT/'harness-interfaces-plan.json',Path(__file__),Path(__file__).with_name('immutable_bounds.py'),Path(__file__).with_name('joint_support_current_allocation.py'))})
    output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':run()
