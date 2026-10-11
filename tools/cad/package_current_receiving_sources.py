"""Preserve qualified receiving guides without claiming whole W5 selection."""
import hashlib,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype'
OUT=BASE/'body-harness-checkpoint'
SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def run():
    tick=time.monotonic();p=json.loads((OUT/'source-receiving-plan.json').read_text());g=json.loads((OUT/'source-receiving-checks.json').read_text())
    assert not g['contacts'] and not g['errors'] and g['status']=='RECEIVING_INPUTS_AND_FUSE_PREFIX_SPACE_ONLY_W5_OPEN'
    assert not p['selected'] and not p['W5_complete']
    pins={}
    for data in (p,g):
        for n,h in data['source_sha256'].items():
            assert SHA(ROOT/n)==h,n
            assert n not in pins or pins[n]==h,n
            pins[n]=h
    for f in [Path(__file__),OUT/'source-receiving-plan.json',OUT/'source-receiving-checks.json',
              ROOT/'tests/test_current_source_receiving.py',OUT/'source-guides-manifest.json']:
        pins[f.relative_to(ROOT).as_posix()]=SHA(f)
    m=dict(status='TWO_RECEIVING_GUIDES_AND_FUSE_PREFIXES_SPACE_ONLY_NOT_W5',selected=False,W5_complete=False,
      physical_pass=False,result_count=11,fixed_total=20,percent=55,pairs=g['pairs'],head_poses=9,
      gate_seconds=g['worker_seconds'],native_parts_created=0,STL_created=0,
      nominal_guides_mm={n:r['guide_mm'] for n,r in p['routes'].items()},
      F_PI_prefuse_blank_mm=p['F_PI']['input_factory_blank_mm'],
      changed_port_assignment=p['P_SYS']['roles'],
      limitations=['Nominal project cavity datums, not measured supplier ports',
        'Receiving rail casing extends toZ166.9 above OMITTED160 cosmetic shell; not a closed-shell fit',
        'Fuse nominal TE/factory margins0.382/0.4mm require unpowered delivered fit',
        'No full S0/MAIN/source/leg/body/local wiring, native restraint or stock selection',
        'Known whole guide receipts are reused; subsequent changed interfaces still need qualification'],
      source_sha256=dict(sorted(pins.items())),verification_seconds=time.monotonic()-tick)
    (OUT/'receiving-sources-manifest.json').write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=m['status'],pins=len(pins),seconds=m['verification_seconds'])))
if __name__=='__main__':run()
