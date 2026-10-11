"""Pin the five shared MAIN/Pi guides without selecting incomplete W5."""
import json,time
from pathlib import Path
from plan_current_main_pi_wiring import ROOT,OUT,SHA

def run():
    tick=time.monotonic();f=OUT/'main-pi-plan.json';g=OUT/'main-pi-checks.json';s=OUT/'main-pi-screen.json'
    plan,gate,screen=[json.loads(q.read_text()) for q in (f,g,s)]
    assert gate['status']=='MAIN_PI_SHARED_MATERIAL_ONLY_NATIVE_OPEN' and not gate['contacts'] and not gate['errors']
    assert screen['status']=='MAIN_PI_PROXIMITY_ONLY_REAL_MATERIAL_OPEN'
    pins={Path(__file__),f,g,s,ROOT/'tests/test_current_main_pi.py',ROOT/'tests/test_current_harness_interfaces.py'}
    for source in (plan,gate,screen):
        for n,h in source['source_sha256'].items():
            assert SHA(ROOT/n)==h,n;pins.add(ROOT/n)
    data=dict(status='FIVE_MAIN_PI_GUIDES_MATERIAL_RECEIPT_NATIVE_OPEN',selected=False,W5_complete=False,physical_pass=False,
      retained_score=dict(count=11,total=20,percent=55,change_pp=0),
      guides={n:dict(nominal_mm=v['guide_mm'],actual_cut_mm=None) for n,v in plan['routes'].items()},
      bare_MAIN_pieces=4,shared_pairs=gate['pairs'],contacts=0,
      worker_seconds=gate['worker_seconds'],pure_tests=dict(count=8,measured_seconds=[.005,.032]),
      supersession='Only protected F_PI output factory lap now SOUTH; case/input remain. Four MAIN direct-pad wires and two free USB pigtail datums are project allowances, not measured pins.',
      rejected_causes=['First shared actual gate77.563s/107pairs found S0 tangency and protected WEST lap entering retained F_HP.',
        'Changed complete MAIN paired route to NORTH concentric bends and protected F_PI lap to SOUTH. Cheap screen caught the initially reversed radius ordering before a second native-scene load. Corrected concentric circle centres, no scalar case nudge.'],
      open=['Four-pad insulation grip, paired plug grip, both lap grips and supplier/delivered fit',
        'Whole body/leg harness, installed service and wire/fault/material reconciliation'],
      source_sha256={q.relative_to(ROOT).as_posix():SHA(q) for q in pins})
    data['verification_seconds']=round(time.monotonic()-tick,6)
    (OUT/'main-pi-manifest.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(pins=len(pins),guides=5,pairs=gate['pairs'],seconds=data['verification_seconds'])))

if __name__=='__main__':run()
