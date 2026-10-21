"""Reuse recorded source addresses, not another archive search, for W009."""
import json,hashlib,zipfile,time,os
import FreeCAD
import Part
from check_main_p0_placement import ROOT,sha
from pathlib import Path
from receive_feline_rrp_shared_height import load
from plan_feline_layout import OUT
from feline_current_shared_plan_context import compose
from compose_feline_current_body_routes import current
from check_feline_harness_proposal import check


def run():
    tick=time.monotonic();world,parts,meta,pins,docs=compose()
    expected=json.loads((OUT/'joint-corridor-space-20261021/owner-source-cache-bridge.json').read_text())['source_geometry_sha256']
    prior=json.loads((OUT/'n01-W009-W069-recovered-subset-check.json').read_text())
    scene={n:s for n,s in parts.items() if n in expected and hashlib.sha256(s.exportBrepToString().encode()).hexdigest()==expected[n]}
    opened={}
    try:
        for n,(path,entry,digest) in prior['source_records'].items():
            if n.startswith('CurrentMiddle:'):
                packet=json.loads(Path(path).read_text())
                assert packet['bundle']==entry and packet['bundle_sha256']==digest and sha(ROOT/entry)==digest
                scene[n]=load(packet)[n]
                continue
            if path not in opened:opened[path]=zipfile.ZipFile(path)
            raw=opened[path].read(entry);assert hashlib.sha256(raw).hexdigest()==digest,n
            s=Part.Shape();s.importBrepFromString(raw.decode())
            if n in expected:
                assert digest==expected[n] or hashlib.sha256(s.exportBrepToString().encode()).hexdigest()==expected[n],n
            else:assert n in ('CurrentMiddle:W020','CurrentMiddle:W022','CurrentMiddle:W024')
            scene[n]=s
    finally:
        for z in opened.values():z.close()
    assert len(scene)==1251,('Unexpected recovery coverage',len(scene))
    _,ends,_=current();folder=OUT/'W009-W069-harness-corridor'
    recipe=next(r for r in json.loads((folder/'W009-saved-portals.json').read_text())['proposals'] if r['end_heading']==4)
    print('RECOVERED_RECORDED_SUBSET',len(scene),time.monotonic()-tick,flush=True)
    result,actor=check(scene,meta,expected,ends,'W009',recipe)
    print('TOTAL_SECONDS',time.monotonic()-tick,flush=True)
    return result

if __name__=='__main__':print('WORKER_PID',os.getpid(),flush=True);run()
