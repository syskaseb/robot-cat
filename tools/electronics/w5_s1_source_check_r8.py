"""Receive the shared five-route source interface, native Carrier included."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
receiver=ROOT/'tools/electronics/w5_s1_source_check_r7.py'
source=receiver.read_text(encoding='utf-8').replace('check-r7','check-r8').replace('layout-r7','layout-r8')
namespace=dict(__file__=str(Path(__file__).resolve()),__name__='r8_receiver')
exec(compile(source,str(Path(__file__).resolve()),'exec'),namespace)
if __name__=='__main__':
    namespace['namespace']['main']()
    from servo_fuse_inputs_r1 import save,sha
    import json
    p=ROOT/'hardware/electronics/full-cat/w5-s1-source-check-r8/checks.json'
    r=json.loads(p.read_text(encoding='utf-8'))
    for q in [receiver,ROOT/'tools/electronics/w5_s1_source_check_r4.py']:
        r['source_sha256'][q.relative_to(ROOT).as_posix()]=sha(q)
    r.update(five_routes_include_reopened_XA01=True,received_native_carrier_passages=True,new_cover_required=True)
    save(p,r)
