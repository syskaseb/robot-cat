"""Compact integrity/selection check, not repeated geometric qualification."""
from pathlib import Path
import json,hashlib

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/mounting-checkpoint'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    reports={n:json.loads((OUT/n).read_text(encoding='utf-8')) for n in
        ['main-expression-checks.json','board-mount-plan.json','board-mount-checks.json',
         'board-hardware-checks.json','board-rear-tool-checks.json']}
    pins_checked=0
    for name,r in reports.items():
        pins=r.get('source_sha256',{})
        if isinstance(pins,str):
            pins={r['source'].replace('\\','/'):pins,r['native'].replace('\\','/'):r['native_sha256'],
                  'tools/cad/open_prototype_mounts.py':r['script_sha256']}
        for rel,h in pins.items():
            assert sha(ROOT/rel)==h,(name,rel)
            pins_checked+=1
    base=reports['board-mount-checks.json'];hardware=reports['board-hardware-checks.json'];lateral=reports['board-rear-tool-checks.json']
    assert base['status']=='COMMON_BOARD_MOUNT_LOCAL_CHECKS_CLEAR' and not base['contacts'] and not base['errors']
    assert sha(OUT/'BoardMounts.FCStd')==base['native_sha256']
    assert sha(OUT/'BoardMountAssembly.FCStd')==hardware['native_sha256']
    assert lateral['status']=='LATERAL_REAR_NUT_ACCESS_CLEAR' and not lateral['contacts'] and not lateral['errors']
    replacements={r['id'] for r in lateral['tool_paths']}
    assert {r['a'] for r in hardware['contacts']}==replacements and not hardware['errors']
    assert all(t['clear'] or t['id'] in replacements for t in hardware['tools'])
    assert len(hardware['fasteners'])==25
    assert all(f['nominal_nut_engagement_mm']>0 and f['protrusion_mm']>=0 for f in hardware['fasteners'])
    assert len(hardware['clamp_bearings'])==4 and all(b['bearing_area_mm2']>60 for b in hardware['clamp_bearings'])
    exports=lateral['exports']+[r for r in base['exports'] if r['part']!='LowerCarrier']
    assert len(exports)==5 and sum(r['quantity'] for r in exports)==14
    assert len({r['part'] for r in exports})==5
    for r in exports:
        assert sha(ROOT/r['path'])==r['sha256']
        assert max(r['bounds_with_5mm_brim_mm'])<256
    current=dict(status='BOARD_MOUNT_LOCAL_CANDIDATE_CURRENT_SET_NOT_STAGE_RELEASE',
        selected=False,stage_completed=False,physical_pass=False,
        current_native='BoardMountAssembly.FCStd',native_sha256=hardware['native_sha256'],
        inherited_main_native='Mounts.FCStd',current_print_parts=exports,
        print_quantity_total=14,unique_print_geometries=5,
        excluded_from_current_prints=['LowerCarrier.stl (replaced by captive-nut carrier)'],
        quantities=hardware['quantities'],assembly=hardware['installation'],
        rear_nut_tool=lateral['tool_paths'],
        remaining_stage2=['Populated supplier boards/underside/components versus mounts and connectors',
            'Distribution supports/insulation/actual attachment/assembly integration',
            'One common integrated native/export selection for this stage'],
        result_count=3,result_denominator=20,result_percent=15,
        no_M5_W1_W5_or_whole_phase_credit=True)
    (OUT/'mount-current-set.json').write_text(json.dumps(current,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='MOUNT_PROGRESS_INTEGRITY_CLEAR',pins_checked=pins_checked,
        current_export_count=5,physical_print_quantity=14,fastener_count=25,stage_completed=False,result_percent=15)))

if __name__=='__main__':main()
