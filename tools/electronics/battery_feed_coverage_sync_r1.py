"""Synchronize inherited coverage metadata with the 12 actual R48 cut rows."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/cad'),str(ROOT/'tools/electronics')]
from servo_fuse_inputs_r1 import save,sha
from release_check import verify
batch=ROOT/'hardware/manufacturing/one-batch-prototype-r48'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def main():
    manifest=read(batch/'manifest.json');assert verify(ROOT,manifest)['integrity_ok']
    selection=read(batch/'selection.json');path=ROOT/selection['body_harness'];body=read(path)
    actual=sum(r.get('nominal_selected_blank_mm') is not None for r in body['conductors'])
    assert actual==12 and len(body['conductors'])==80
    assert body['coverage']['selected_nominal_cuts']==10
    body['coverage'].update(selected_nominal_cuts=actual,remaining_body_ledger_cuts=80-actual)
    save(path,body);selection['body_harness_sha256']=sha(path);save(batch/'selection.json',selection)
    pins={r['path']:r['sha256'] for r in manifest['files']}
    for p in (path,batch/'selection.json',Path(__file__)):pins[p.relative_to(ROOT).as_posix()]=sha(p)
    manifest['files']=[dict(path=p,sha256=h) for p,h in sorted(pins.items())]
    check=verify(ROOT,manifest);assert check['integrity_ok'];save(batch/'manifest.json',manifest)
    validation=read(batch/'validation.json');validation['integrity']=check;save(batch/'validation.json',validation)
    print(json.dumps(dict(selected_cuts=actual,remaining_cuts=80-actual,phase1_percent=70,integrity=True)))
if __name__=='__main__':main()
