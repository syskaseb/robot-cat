"""Exact outline and mutual gate for one shared pair; not whole-scene receipt."""
import json,time,zipfile,hashlib,os
from pathlib import Path
import FreeCAD
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from receive_feline_W024_shared_body import solid
from plan_feline_usb_service_bight import outer_margin
from feline_atomic_save import save_json


def run():
    tick=time.monotonic();folder=OUT/'W009-W069-harness-corridor';dest=folder/'pair-outline.json'
    assert not dest.exists()
    pf=folder/'W009-saved-portals.json';qf=folder/'pair-preflight.json'
    p=next(r for r in json.loads(pf.read_text())['proposals'] if r['end_heading']==4)
    q=json.loads(qf.read_text())['paths']['W069/body']
    actors={w:solid(r['parts'],r['radius_mm']) for w,r in [('W009',p),('W069',q)]}
    outerpath=OUT/'n01-service-gallery.outer.brep';outer=Part.Shape();outer.read(str(outerpath))
    result=dict(status='RUNNING_PAIR_OUTLINE',checks={},N01_complete=False,physical_pass=False,
        source_sha256={x.relative_to(ROOT).as_posix():sha(x) for x in (pf,qf,outerpath,Path(__file__))})
    for name,s in actors.items():
        result['checks'][name]=outer_margin(s,outer);save_json(dest,result)
        print('OUTLINE',name,result['checks'][name],flush=True)
    gap=actors['W009'].distToShape(actors['W069'])[0]
    result['mutual']=dict(gap_mm=gap,minimum_mm=.2,ok=gap>=.2-1e-6)
    archive=folder/'pair-proposal.breps.zip';records=[]
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for name,s in actors.items():
            raw=s.exportBrepToString().encode();entry=name+'.brep';z.writestr(entry,raw)
            records.append(dict(name=name,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    result.update(status='PAIR_OUTLINE_AND_MUTUAL_POSITIVE' if all(r['ok'] for r in result['checks'].values()) and result['mutual']['ok'] else 'PAIR_OUTLINE_OR_MUTUAL_HOLD',
        geometry=records,bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),
        whole_static_motion_assembly_OPEN=True,worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result);print(result['status'],result['mutual'],result['worker_seconds'],flush=True)

if __name__=='__main__':print('WORKER_PID',os.getpid(),flush=True);run()
