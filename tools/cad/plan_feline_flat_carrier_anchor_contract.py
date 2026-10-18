"""Receive actual existing four clamp kits before the whole carrier is frozen.

Saved source geometry only, no new holes or unchecked free-anchor claims.
Reuse the prior bearing evidence with its source pins; new carrier connections
and all affected neighbours remain OPEN until the common exact receiver.
"""
import hashlib
import json
import time
import zipfile
from pathlib import Path
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import OUT,BASE


def main():
    tick=time.monotonic();dest=OUT/'n01-flat20-actual-clamp-kits.json'
    assert not dest.exists(),'Receive saved actual source kits, do not repeat'
    history=BASE/'mounting-checkpoint/RetentionMountsAssembly.FCStd'
    oldfile=OUT/'n01-foundation-preflight-r2.json';old=json.loads(oldfile.read_text())
    assert old['source_sha256'][history.relative_to(ROOT).as_posix()]==sha(history)
    assert len(old['root_bearings'])==4
    reader=SavedShapes();bundle=OUT/'n01-flat20-actual-clamp-kits.breps.zip';rows=[]
    with zipfile.ZipFile(bundle,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for i in range(1,5):
            for name in [f'TopClampPad{i}',f'LowerClampJaw{i}']+[
                f'RailClamp{i}'+s for s in ('Screw','TopWasher','BottomWasher','Nut')]:
                shape=reader.shape(history,name);assert shape.isValid() and shape.Solids,name
                bb=shape.BoundBox;blob=shape.exportBrepToString().encode();entry=f'{len(rows):03}.brep'
                z.writestr(entry,blob)
                rows.append(dict(name=name,clamp=i,entry=entry,
                    sha256=hashlib.sha256(blob).hexdigest(),
                    bounds_mm=[[bb.XMin,bb.YMin,bb.ZMin],[bb.XMax,bb.YMax,bb.ZMax]],
                    volume_mm3=shape.Volume,solids=len(shape.Solids),
                    role='existing_clamp_print' if 'Pad' in name or 'Jaw' in name else 'existing_fastener'))
    assert len(rows)==24
    result=dict(status='ACTUAL_EXISTING_CLAMP_KITS_RECEIVED_NEW_CONNECTIONS_OPEN',
        selected=False,N01_complete=False,physical_pass=False,parts=rows,
        bundle=bundle.relative_to(ROOT).as_posix(),bundle_sha256=sha(bundle),
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in
            (history,oldfile,Path(__file__),ROOT/'tools/cad/check_main_p0_placement.py')},
        unchanged_bearing_receipts_reused=old['root_bearings'],
        unchanged_bearings_not_requeried=True,
        identity_and_role_NOT_current_free_space_approval=True,
        required_before_N01=['All24parts present in shared changed scene',
            'Actual current ownership of all four screw axes and driver channels',
            'Carrier bearing/holes/stack/positive roots to all retained functions',
            'Finite split joint and no bought fastener deletion'],
        worker_seconds=round(time.monotonic()-tick,3))
    dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=result['status'],parts=24,seconds=result['worker_seconds'])))


if __name__=='__main__':main()
