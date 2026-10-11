"""Keep exact unchanged leg qualifications; select no whole wiring result."""
import json,hashlib,time,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/body-harness-checkpoint'
SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def preserve():
    p=OUT/'leg-stations-plan.json';g=OUT/'leg-stations-checks.json'
    plan=json.loads(p.read_text());gate=json.loads(g.read_text())
    assert gate['status']=='REJECTED_LEG_OUTPUT_SHARED_LAYOUT' and not gate['errors']
    assert gate['contacts'] and all(r['a']=='W026_CUSTOM' and r['b']=='head/Fork' for r in gate['contacts'])
    for n,h in {**plan['source_sha256'],**gate['source_sha256']}.items():assert SHA(ROOT/n)==h,n
    scripts={n:(ROOT/n).read_text() for n in ('tools/cad/plan_current_leg_stations.py','tools/cad/check_current_leg_stations.py')}
    # Preserve bytes as well as decoded source: Windows newline translation
    # must not weaken old receipt identity.
    import base64
    raw={n:base64.b64encode((ROOT/n).read_bytes()).decode('ascii') for n in scripts}
    value=dict(status='EXACT_UNCHANGED_12_CASES_THREE_OUTPUTS_REUSE_ONLY',
      reference_plan=plan,reference_gate=gate,reference_scripts_base64=raw,
      reference_plan_sha256=SHA(p),reference_gate_sha256=SHA(g),
      excluded_changed_output='W026_CUSTOM',selected=False,W5_complete=False,physical_pass=False)
    (OUT/'leg-retained-evidence.json').write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(retained_cases=12,retained_outputs=3,changed_output='W026_CUSTOM')))

def package():
    tick=time.monotonic();p=OUT/'leg-stations-plan.json';g=OUT/'leg-stations-checks.json'
    plan=json.loads(p.read_text());gate=json.loads(g.read_text())
    assert gate['status']=='LEG_STATIONS_AND_MAIN_OUTPUT_SPACE_ONLY_FANS_NATIVE_OPEN'
    assert not gate['contacts'] and not gate['errors'] and not plan['selected']
    pins={}
    for data in (plan,gate):
        for n,h in data['source_sha256'].items():
            assert SHA(ROOT/n)==h,n
            assert n not in pins or pins[n]==h,n
            pins[n]=h
    for f in (p,g,Path(__file__),ROOT/'tests/test_current_leg_stations.py'):
        pins[f.relative_to(ROOT).as_posix()]=SHA(f)
    v=dict(status='TWELVE_RECEIVING_CASES_FOUR_MAIN_OUTPUT_GUIDES_SPACE_ONLY_NOT_W5',
      selected=False,W5_complete=False,physical_pass=False,result_count=11,fixed_total=20,percent=55,
      cases=12,ports=60,full_output_guides_mm={n:r['guide_mm'] for n,r in plan['routes'].items()},
      factory_override=plan.get('factory_override'),
      native_parts_created=0,STL_created=0,pairs=gate['pairs'],head_poses=9,
      gate_seconds=gate['worker_seconds'],reused_qualifications=gate.get('reused_qualifications',{}),
      open=['24bank departure/load-path plan,12inputs,12factory leg looms,ground/data fans',
        'Full remaining source/body/local wiring, independent native grips and current bank retention',
        'Installed assembly/service, nominal cuts/stock and supplier/delivery/physical gates'],
      source_sha256=dict(sorted(pins.items())),verification_seconds=time.monotonic()-tick)
    (OUT/'leg-stations-manifest.json').write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=v['status'],pins=len(pins),seconds=v['verification_seconds'])))

if __name__=='__main__':preserve() if '--preserve' in sys.argv else package()
