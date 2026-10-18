"""Freeze the received full-scene lower bay, without repeating its tests."""
import hashlib
import json
import subprocess
import sys
import time
import zipfile
from pathlib import Path
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_full_lower_bay import main as build


def main():
    tick=time.monotonic();dest=OUT/'n01-lower-bay-world-probe.json'
    bundle=dest.with_suffix('.zip');assert not dest.exists()
    proof=OUT/'n01-full-lower-bay-plan-r3.json';received=json.loads(proof.read_text())
    builder=ROOT/'tools/cad/plan_feline_full_lower_bay.py';relative=builder.relative_to(ROOT).as_posix()
    original=subprocess.run(['git','show','a3526763:'+relative],cwd=ROOT,capture_output=True,check=True).stdout
    assert hashlib.sha256(original).hexdigest()==received['source_sha256'][relative]
    # Verify the complete geometry-construction block is byte-identical to
    # the tool that actually ran the checks, not merely equal bounds/volume.
    section=lambda s:s[s.index('    # Retain the passing lower-root'):s.index('    bounds={n:s.BoundBox')]
    current=builder.read_text();current=current.replace('    if geometry_only:\n        return new,kind,owner,received\n','')
    assert section(current)==section(original.decode('utf-8'))
    for name,h in received['source_sha256'].items():
        if name!=relative:assert sha(ROOT/name)==h,name
    sys.argv.append('--relieved-supports');shapes,kinds,owners,receipt=build(geometry_only=True)
    prior={r['name']:r for r in receipt['parts']};assert set(shapes)==set(prior)
    rows=[]
    # A hardware candidate deliberately contains screw+washers as several
    # solids. Recover an interrupted own ZIP only after byte-checking entries.
    with zipfile.ZipFile(bundle,'a' if bundle.exists() else 'x',compression=zipfile.ZIP_DEFLATED) as z:
        existing=set(z.namelist())
        for i,(name,s) in enumerate(shapes.items()):
            assert s.isValid() and s.Solids,name
            b=s.BoundBox;bb=[[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]]
            assert all(abs(u-v)<1e-5 for a,c in zip(bb,prior[name]['bounds_mm']) for u,v in zip(a,c)),name
            assert abs(s.Volume-prior[name]['volume_mm3'])<1e-4,name
            raw=s.exportBrepToString().encode('utf-8');entry=f'{i:03d}.brep'
            if entry in existing:assert z.read(entry)==raw,(name,'Partial entry differs; not overwritten')
            else:z.writestr(entry,raw)
            rows.append(dict(name=name,entry=entry,kind=kinds[name],owner=owners[name],bounds_mm=bb,
                volume_mm3=s.Volume,solids=len(s.Solids),sha256=hashlib.sha256(raw).hexdigest()))
    report=dict(status='RECEIVED_LOWER_BAY_WORLD_GEOMETRY_NOT_NATIVE_OR_SELECTED',selected=False,
        physical_pass=False,count=len(rows),parts=rows,bundle=bundle.relative_to(ROOT).as_posix(),
        bundle_sha256=sha(bundle),accepted_scope_receipt=proof.relative_to(ROOT).as_posix(),
        accepted_scope_sha256=sha(proof),original_receipt_tool_commit='a3526763',
        geometry_block_byte_identical=True,unchanged_collision_or_motion_rerun=False,
        actual_joint_seats_assembly_native_stock_and_other_harness_open=True,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (proof,Path(__file__),builder)},
        worker_seconds=round(time.monotonic()-tick,3))
    dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(report['status'],report['count'],report['worker_seconds'],flush=True)


if __name__=='__main__':main()
