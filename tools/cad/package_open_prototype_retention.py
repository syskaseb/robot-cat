"""One provisional Stage2 mounting set; reuse proofs, never rerun baseline CAD.

Delivered adapter/adhesive/physical fit gates remain OPEN. This package closes
only the user-authorized provisional mounting preparation, not E1/W1/W5/M5.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, subprocess
from release_check import verify
from open_prototype_u1_side_support import ROOT, OUT, deadline


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(name):return json.loads((OUT/name).read_text(encoding='utf-8'))
def save(name,value):(OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def main():
    deadline();deps={};pin_count=0
    names=['main-expression-checks.json','board-mount-plan.json','board-mount-checks.json',
        'board-hardware-checks.json','board-rear-tool-checks.json','distribution-mount-plan.json',
        'distribution-mount-checks.json','pwm-mount-isolation-checks.json','pwm-flat-insulator-checks.json',
        'u1-side-support-checks.json','wago-retention-checks.json','shared-retention-mount-checks.json']
    reports={n:read(n) for n in names}
    for name,r in reports.items():
        pins=r.get('source_sha256',{})
        if isinstance(pins,str):
            pins={r['source'].replace('\\','/'):pins,r['native'].replace('\\','/'):r['native_sha256'],
                'tools/cad/open_prototype_mounts.py':r['script_sha256']}
        for rel,val in pins.items():
            assert sha(ROOT/rel)==val,(name,rel)
            assert rel not in deps or deps[rel]==val,(name,'conflicting pin',rel)
            deps[rel]=val;pin_count+=1
        deps[(OUT/name).relative_to(ROOT).as_posix()]=sha(OUT/name)
    shared=reports['shared-retention-mount-checks.json'];wago=reports['wago-retention-checks.json']
    assert shared['status']=='SHARED_RETENTION_MOUNTS_GEOMETRY_CLEAR_PROVISIONAL'
    for key in ['material_contacts','nominal_reservation_contacts','assumed_pad_keepout_contacts','errors']:assert not shared[key],key
    assert shared['relocated_reopen'] and not shared['delivered_adapter_fit_qualified']
    assert not(wago['nominal_reservation_contacts'] or wago['errors'])
    assert all(abs(r['bearing_fraction']-r['expected_full_rim_fraction'])<1e-6 for r in shared['spacer_bearing'])
    assert not reports['board-mount-checks.json']['contacts']
    assert not reports['board-rear-tool-checks.json']['contacts']
    assert not reports['distribution-mount-checks.json']['material_contacts']
    assert reports['distribution-mount-checks.json']['valid_BUS_solid_count']==117
    assert reports['pwm-flat-insulator-checks.json']['status']=='FLAT_INSULATING_WASHERS_NOMINAL_CLEAR'
    # Baseline selection comes from its OWN committed snapshot, so repeated
    # packaging cannot double-count newly added prints/hardware or ties.
    rel=(OUT/'mount-current-set.json').relative_to(ROOT).as_posix()
    baseline=json.loads(subprocess.check_output(['git','show','7e1e64f:'+rel],cwd=ROOT))
    assert baseline['print_quantity_total']==22 and baseline['fastener_total']==29
    exports=[r for r in baseline['current_print_parts'] if r['part']!='UpperCarrier']+shared['exports']
    assert len(exports)==10 and len({r['part'] for r in exports})==10
    assert sum(r['quantity'] for r in exports)==26
    for r in exports:
        assert sha(ROOT/r['path'])==r['sha256'] and max(r['bounds_with_5mm_brim_mm'])<256
        deps[r['path']]=r['sha256']
    for name,r in [('MountsCurrent.FCStd',reports['pwm-flat-insulator-checks.json']),
        ('U1SideSupportCandidate.FCStd',reports['u1-side-support-checks.json']),
        ('RetentionMountsCandidate.FCStd',wago),('RetentionMountsAssembly.FCStd',shared)]:
        assert sha(OUT/name)==r['native_sha256'],name
        deps[(OUT/name).relative_to(ROOT).as_posix()]=r['native_sha256']
    q=dict(baseline['quantities']);q.update(M2x10=2,distribution_T18I=0,
        U1_printed_spacer=2,U1_printed_top_insulator=2,WAGO_underbody_pairs=20,WAGO_underbody_cut_pieces=40)
    q['M2_nut']+=2
    assembly=[
        'Physically disconnect/remove source including monitor feed; S0 off alone is not isolation. No power in this preparation.',
        'Fit captive lower PCB nuts, then P0 frame clamps/lower carrier and side-rail supports before Pi. Retain known bearing surfaces.',
        'Fit side spacers/rails and their staged bolts before WAGO; then Pi/BUS and negative-Y monitor before upper carrier.',
        'Bench mount PWM/AUX on upper carrier. Two retained flat PWM insulating washers, original M2x14/nuts; no metal washer on copper.',
        'Measure delivered U1 hole/pad map FIRST and regenerate provisional hole pattern/spacers if needed. No drilling supplied PCB or clamping unknown pad rows.',
        'Top-load U1 captive nuts, foot/stem spacers, measured adapter, top insulators and two M2x10 screws BEFORE above MTA/bank. Only light controlled clamp load.',
        'Fit upper carrier/frame nuts using retained lateral AF5.5 access. Nominal short AF1.5 U1 L-key uses negativeY60degree sector and3mm seated-screw indexing lift; delivered tool fit OPEN.',
        'After unpowered bond qualification, fit lower WAGO then upper WAGO on20 underbody SJ4570 pairs.40pieces20x10, no ties/adhesive on levers/ports. Hold body while operating; independent wire strain relief belongs to next stage.',
        'Retain R47/4MTA and both exits; place above MTA only AFTER U1. Full routes/stock and actual local<=50mm leads require separate next-stage authorization.',
        'For full U1 screw/board removal first isolate source and remove above MTA module, then adapter. No claim of independent connected service/74routine disconnects.',
        'Stop before physical/powered use unless delivered fit, PETG, adhesion, insulation and electrical gates have passed.'
    ]
    gates=[dict(id='DELIVERED_U1',status='OPEN',required_before='Print/assemble provisional local attachment',
        checks=read('u1-shared-mount-plan.json')['delivery_gates']),
        dict(id='WAGO_BOND_AND_LEVERS',status='OPEN',required_before='Use body retention',
            checks=read('wago-retention-plan.json')['phase2_gates']),
        dict(id='POPULATED_FIT',status='OPEN',required_before='Physical acceptance',
            checks=['Delivered spines/solder/USB/AUX/actual tools','PETG coupon, insulation, bearing/creep/torque',
                'Assembly order: U1 before above MTA; full screw extraction requires MTA absent']),
        dict(id='LATER_WIRING',status='OUTSIDE_STAGE2',required_before='Powered prototype',
            checks=['Actual adapter continuity/pin map and every local route <=50mm including ends/bends',
                'Independent wire strain relief, all wire endpoints reflect WAGO rise2.49..3mm',
                'Full wiring/stock/E3 and connected service remain unqualified'])]
    current=dict(status='STAGE2_PROVISIONAL_MOUNT_PREPARATION_COMPLETE_DELIVERY_GATES_OPEN',
        current=True,selected=False,selected_for_provisional_mount_preparation=True,
        stage_completed=True,physical_pass=False,print_approved=False,
        scope='Stage2 only; user-authorized adjustable/regeneratable attachment with delivered fit gate',
        current_native='RetentionMountsAssembly.FCStd',native_sha256=shared['native_sha256'],
        retained_historical_native='MountsCurrent.FCStd',retained_baseline_commit='7e1e64f',
        current_print_parts=exports,print_quantity_total=26,unique_print_geometries=10,
        quantities=q,fastener_total=31,assembly=assembly,delivery_gates=gates,
        local_lead_routes_qualified=False,result_count=3,result_denominator=20,result_percent=15,
        no_M5_W1_W5_or_whole_phase_credit=True,
        mount_hardware_nominal_not_stock_selection=True,
        WAGO_candidate_product='SJ4570;20pairs/40pieces20x10mm, not bought/adhesion-approved',
        tool_scope=shared['tool_scope'],rear_nut_tool=baseline['rear_nut_tool'],changed_PWM_stacks=baseline['changed_PWM_stacks'],
        replaced_exports=['UpperCarrier.stl','UpperCarrierU1Candidate.stl','U1InsulatingSpacerU1Candidate.stl'],
        historical_releases='mount-release.json/current-set from7e1e64f are historical; use retention-release.json now')
    save('mount-current-set.json',current)
    for p in [OUT/'mount-current-set.json',OUT/'u1-shared-mount-plan.json',OUT/'wago-retention-plan.json',
        OUT/'README.md',Path(__file__),ROOT/'tools/cad/release_check.py',ROOT/'tools/cad/open_deck_p0_plate.py',
        ROOT/'tools/cad/open_deck_p0_supports.py']:
        deps[p.relative_to(ROOT).as_posix()]=sha(p)
    release=dict(schema_version=1,readiness='prototype',stage_completed=True,physical_pass=False,
        current_set='mount-current-set.json',scope=current['scope'],delivery_gates=gates,
        gates={n:dict(status='open',reason=r) for n,r in dict(
            geometry='Changed local geometry clear; delivered adapter pad/support map is still unknown',
            assembly='Nominal hardware/staged tools complete; delivered tools and U1 bearing fit untested',
            fit='Delivered adapter/casings/solder/USB fit gates OPEN; do not print guessed local attachment before measuring',
            petg='Layer/support/creep/insulating coupon and actual profile OPEN; no slicer',
            loads='No physical bond/peel/creep/torque qualification',
            electrical='No power; E3 and actual adapter continuity/map OPEN',
            service='Nominal key sector clear; full connected harness/service and actual lever operation OPEN').items()},
        files=[dict(path=k,sha256=v) for k,v in sorted(deps.items())])
    save('retention-release.json',release)
    passed=verify(ROOT,release);refused=verify(ROOT,release,True)
    assert passed['integrity_ok'] and not refused['integrity_ok'],(passed,refused)
    result=dict(status='STAGE2_PROVISIONAL_PACKAGE_INTEGRITY_CLEAR_PRINT_READY_REFUSED',
        checked_utc=datetime.now(timezone.utc).isoformat(),source_pins_checked=pin_count,
        stage_completed=True,physical_pass=False,result_percent=15,geometry_count=10,print_quantity=26,
        bolt_quantity=31,prototype_check=passed,print_ready_refusal=refused,
        own_worker_seconds=dict(u1_first=reports['u1-side-support-checks.json']['worker_wall_seconds'],
            wago=wago['worker_wall_seconds'],shared_final=shared['worker_wall_seconds'],bearing_diagnosis=19.313))
    save('retention-integrity-checks.json',result)
    print(json.dumps(result,ensure_ascii=False),flush=True)


if __name__=='__main__':main()
