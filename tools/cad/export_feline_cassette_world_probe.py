"""Freeze received70part cassette geometry; no unchanged collision rerun."""
import hashlib
import json
import sys
import time
import zipfile
from pathlib import Path
import FreeCAD
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_n01_central_mta_cassette import main as build


def main():
    tick=time.monotonic();dest=OUT/'n01-cassette-world-probe.json';bundle=OUT/'n01-cassette-world-probe.zip'
    assert not dest.exists() and not bundle.exists()
    sys.argv.append('--bolted-open-frame')
    shapes,kinds,received=build(geometry_only=True)
    rows=[]
    with zipfile.ZipFile(bundle,'x',compression=zipfile.ZIP_DEFLATED) as z:
        for i,(n,s) in enumerate(shapes.items()):
            assert s.isValid() and s.Solids,n
            raw=s.exportBrepToString().encode('utf-8');entry=f'{i:03d}.brep';z.writestr(entry,raw);b=s.BoundBox
            rows.append(dict(name=n,entry=entry,kind=kinds[n],sha256=hashlib.sha256(raw).hexdigest(),
                bounds_mm=[[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]],volume_mm3=s.Volume))
    proof=OUT/'n01-central-mta-cassette-plan-r3.json'
    report=dict(status='RECEIVED_CASSETTE_WORLD_GEOMETRY_NOT_NATIVE_OR_SELECTED',selected=False,physical_pass=False,
        count=len(rows),parts=rows,bundle=bundle.relative_to(ROOT).as_posix(),bundle_sha256=sha(bundle),
        accepted_scope_receipt=proof.relative_to(ROOT).as_posix(),accepted_scope_sha256=sha(proof),
        original_receipt_tool_commit='f90a1383',unchanged_collision_or_motion_rerun=False,
        root_hardware_M2x12_is_candidate=True,actual_joint_seats_assembly_native_stock_and_other_harness_open=True,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (proof,Path(__file__),ROOT/'tools/cad/plan_feline_n01_central_mta_cassette.py')},
        worker_seconds=round(time.monotonic()-tick,3))
    dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(report['status'],report['count'],report['worker_seconds'],flush=True)


if __name__=='__main__':main()
