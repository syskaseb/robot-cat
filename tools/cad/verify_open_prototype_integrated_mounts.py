"""Current development mounting set, preserved proof chain and fail-closed gates.

No repeated CAD checks or credit for the unresolved U1 adapter support.
"""
from pathlib import Path
import json, hashlib
from datetime import datetime, timezone
from release_check import verify

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/mounting-checkpoint'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def save(name,value):
    (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    names=['main-expression-checks.json','board-mount-plan.json','board-mount-checks.json',
        'board-hardware-checks.json','board-rear-tool-checks.json','distribution-mount-plan.json',
        'distribution-mount-checks.json','pwm-mount-isolation-checks.json','pwm-flat-insulator-checks.json']
    reports={n:json.loads((OUT/n).read_text(encoding='utf-8')) for n in names}
    dependencies={};pins_checked=0
    for name,r in reports.items():
        pins=r.get('source_sha256',{})
        if isinstance(pins,str):
            pins={r['source'].replace('\\','/'):pins,r['native'].replace('\\','/'):r['native_sha256'],
                'tools/cad/open_prototype_mounts.py':r['script_sha256']}
        for rel,value in pins.items():
            assert sha(ROOT/rel)==value,(name,rel)
            assert rel not in dependencies or dependencies[rel]==value,(name,'inconsistent source',rel)
            dependencies[rel]=value;pins_checked+=1
        dependencies[(OUT/name).relative_to(ROOT).as_posix()]=sha(OUT/name)
    base=reports['board-mount-checks.json'];hw=reports['board-hardware-checks.json']
    lateral=reports['board-rear-tool-checks.json'];distribution=reports['distribution-mount-checks.json']
    insulating=reports['pwm-mount-isolation-checks.json'];flat=reports['pwm-flat-insulator-checks.json']
    assert base['status']=='COMMON_BOARD_MOUNT_LOCAL_CHECKS_CLEAR' and not(base['contacts'] or base['errors'])
    assert lateral['status']=='LATERAL_REAR_NUT_ACCESS_CLEAR' and not(lateral['contacts'] or lateral['errors'])
    replaced={r['id'] for r in lateral['tool_paths']}
    assert {r['a'] for r in hw['contacts']}==replaced and not hw['errors']
    assert distribution['status']=='SHARED_DISTRIBUTION_MOUNTS_LOCAL_CLEAR'
    assert not(distribution['material_contacts'] or distribution['errors'] or distribution['nominal_reservation_contacts'])
    assert distribution['valid_BUS_solid_count']==117 and not distribution['invalid_BUS_solids']
    assert distribution['distribution_role_count']==20 and all(r['clear'] for r in distribution['side_tools'])
    assert insulating['status']=='PWM_MOUNT_ISOLATION_NOMINAL_CLEAR' and not(insulating['material_contacts'] or insulating['component_case_reservation_contacts'] or insulating['errors'])
    assert insulating['population_cases']==19 and flat['status']=='FLAT_INSULATING_WASHERS_NOMINAL_CLEAR'
    assert flat['added_volume_mm3']<1e-7 and flat['removed_volume_mm3']>0 and flat['minimum_radial_wall_mm']>=1.3
    native_files={'BoardMounts.FCStd':base,'BoardMountAssembly.FCStd':hw,
        'DistributionMounts.FCStd':distribution,'InsulatedMounts.FCStd':insulating,'MountsCurrent.FCStd':flat}
    for name,r in native_files.items():
        assert sha(OUT/name)==r['native_sha256'],name
        dependencies[(OUT/name).relative_to(ROOT).as_posix()]=r['native_sha256']
    exports=[r for r in base['exports'] if r['part']!='LowerCarrier']+distribution['exports']+flat['exports']
    assert len(exports)==8 and len({r['part'] for r in exports})==8
    assert sum(r['quantity'] for r in exports)==22
    for r in exports:
        assert sha(ROOT/r['path'])==r['sha256'] and max(r['bounds_with_5mm_brim_mm'])<256
        dependencies[r['path']]=r['sha256']
        r.setdefault('orientation','Flat base +Z, PETG; supports/actual printer profile assessed in phase2, not slicer-approved')
    quantities=dict(hw['quantities'])
    for name,value in reports['distribution-mount-plan.json']['fasteners_added'].items():
        quantities[name]=quantities.get(name,0)+value
    quantities['M2_washer']-=2;quantities['printed_PETG_insulating_washer']=2
    quantities['distribution_T18I']=40
    bolts=sum(quantities[n] for n in ['M3x14','M3x45','M3x30','M2x12','M2x14']);assert bolts==29
    blockers=[dict(id='U1_SUPPORT',status='OPEN',component='Kamami575070/SN74LVC8T245PW',
        known='30.48x17.78mm outline, nominal2.54mm header pitch; reservation above upper passives only',
        missing='Delivered PCB thickness, both-side pad/solder and keepout map, safe supported bearing/retention sites',
        impact='No complete rigid PWM/U1 module mounting; cannot close whole stage2',
        evidence='hardware/electronics/full-cat/pwm-carrier-r3/population.json:adapter_stack/u1_integration',
        source_checked_date_utc='2026-10-07',
        source_url='https://kamami.pl/en/Adapters-SMD-DIP/575070-sop24-pcb-adapter-for-dip24-5906623456895.html',
        source_result='Product description confirms outline/pitch only; no support/thickness/pad drawing. No alternative product substituted.'),
        dict(id='DISTRIBUTION_RETENTION',status='OPEN',
            known='20 nominal WAGO bodies in two accessible side rails,40 tie slots/roles,8 nominal side tools clear',
            missing='Tie paths/support bearing against actual casing and lever keepouts; two ties per body is a recipe, not verified retention',
            impact='Side rails are development geometry; not certified mount or lever-service proof'),
        dict(id='POPULATED_FIT',status='OPEN',
            known='117 placed BUS solids checked separately, supplier mounting-hole patterns,19 PWM component maximum-case reservations',
            missing='Delivered underside solder/projections, actual USB/tool and AUX populated-side fit; nominal allowances explicit',
            impact='Physical fit conditions, no energized or physical PASS')]
    current=dict(status='INTEGRATED_DEVELOPMENT_MOUNTS_STAGE2_BLOCKED_NOT_PRINT_READY',
        current=True,selected=False,stage_completed=False,physical_pass=False,current_native='MountsCurrent.FCStd',
        native_sha256=flat['native_sha256'],inherited_main_native='Mounts.FCStd',
        current_print_parts=exports,print_quantity_total=22,unique_print_geometries=8,
        excluded_from_current_prints=['LowerCarrier.stl','LowerCarrierAssembly.stl',
            'PwmInsulatingShoulderWasher.stl (unnecessary thin centering neck removed)'],
        quantities=quantities,fastener_total=bolts,
        assembly=reports['distribution-mount-plan.json']['assembly']+[
            'Fit two FLAT PETG washers OD5/bore2.4/thickness1 above PWM1608 copper; no centering shoulder. M2x14 underhead85.3202, original lower nuts unchanged. Isolated source; fit/no crush/creep/insulation coupons required.',
            'Do not install U1 on guessed pads or close stage2 until explicit adapter support/retention is resolved'],
        rear_nut_tool=lateral['tool_paths'],changed_PWM_stacks=[{k:v for k,v in r.items() if k!='shoulder_od_mm'} for r in insulating['stacks']],
        blockers=blockers,proof_scope='Inherited unchanged interfaces pinned; only changed parts/stack checks added. No full wiring/stock/lever credit.',
        BUS_note_correction='distribution-mount-checks.json known_bounds literal116 is stale; numerical valid_BUS_solid_count=117 with no invalid placed solids. Raw vendor compound remains invalid, never used as one BOP operand.',
        result_count=3,result_denominator=20,result_percent=15,no_M5_W1_W5_or_whole_phase_credit=True)
    save('mount-current-set.json',current)
    for path in [OUT/'mount-current-set.json',OUT/'README.md',Path(__file__),ROOT/'tools/cad/release_check.py',ROOT/'.gitattributes',
        ROOT/'hardware/reference/wago-221415-access-2026-10-02/source.json',
        ROOT/'hardware/reference/wago-221415-access-2026-10-02/221-415-WAGO-2021.pdf']:
        dependencies[path.relative_to(ROOT).as_posix()]=sha(path)
    gates={n:dict(status='open',reason=reason) for n,reason in dict(
        geometry='Known mounting geometry has local proofs; whole U1 support/populated fit remains open',
        assembly='Known mounts have staged tools and fastener stacks; adapter and WAGO retention not completed',
        fit='Actual printer/nozzle/profile/parts/USB/tools not physically fitted',
        petg='Layer/support/creep/insulating washer coupons not tested; no slicer run',
        loads='No physical bearing, torque or creep/load acceptance',
        electrical='Unpowered prototype only, no insulation/thermal/branch qualification',
        service='ATO/R47 retained; current tie/lever motion and full wiring still open').items()}
    release=dict(schema_version=1,readiness='prototype',stage_completed=False,physical_pass=False,
        scope='Current Stage2 mounting development checkpoint, not full-phase/print handoff',
        tools=dict(FreeCAD='1.1.3 Windows x86_64 py311',execution='Versioned scripts; structured PartDesign bodies/owned prints and supplier snapshots'),
        gates=gates,files=[dict(path=rel,sha256=value) for rel,value in sorted(dependencies.items())],
        current_set='mount-current-set.json',blockers=blockers)
    save('mount-release.json',release)
    passed=verify(ROOT,release);refusal=verify(ROOT,release,True)
    assert passed['integrity_ok'] and not refusal['integrity_ok'],(passed,refusal)
    result=dict(status='INTEGRATED_MOUNT_CHECKPOINT_INTEGRITY_CLEAR_STAGE_OPEN',
        verified_utc=datetime.now(timezone.utc).isoformat(),source_pins_checked=pins_checked,
        current_native_sha256=flat['native_sha256'],current_export_count=8,physical_print_quantity=22,
        fastener_count=bolts,result_percent=15,stage_completed=False,
        prototype_release_check=passed,print_ready_correctly_refused=refusal,
        BUS_valid_placed_solids=117,own_workers_wall_seconds=dict(distribution=distribution['worker_wall_seconds'],
            isolation=insulating['worker_wall_seconds'],simplification=flat['worker_wall_seconds']))
    save('mount-integrity-checks.json',result)
    print(json.dumps(result))

if __name__=='__main__':main()
