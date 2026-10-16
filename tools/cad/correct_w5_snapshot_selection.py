"""Remove sampled-pose duplicates from saved assembly, not rebuild its CAD.

The original snapshot and receipt are retained as diagnostic provenance.
Only the explicitly changed neutral-name filter may differ from its pins.
"""
import json,shutil,tempfile,time
from pathlib import Path
import FreeCAD as A
from plan_current_harness_interfaces import ROOT,OUT,SHA
from current_rest_pose import is_rest
from current_work_guard import check
from build_current_w5_assembly import signature


def close_owned():
    for name in list(A.listDocuments()):A.closeDocument(name)


def run():
    check();tick=time.monotonic();folder=OUT/'current-w5-assembly'
    oldfile=folder/'manifest.json';old=json.loads(oldfile.read_text());filter_key='tools/cad/current_rest_pose.py'
    assert old['relocated_reopen'] and not old['errors']
    for n,h in old['source_sha256'].items():
        if n!=filter_key:assert SHA(ROOT/n)==h,n
    assert SHA(ROOT/old['native'])==old['native_sha256']
    remove=[r for r in old['reference_objects'] if not is_rest(r['name'])]
    assert remove,'No selection defect to repair'
    final=folder/'CurrentW5AssemblyNeutral.FCStd';receipt=folder/'neutral-manifest.json'
    assert not final.exists() and not receipt.exists(),'Receive existing corrected assembly'
    doc=A.openDocument(str(ROOT/old['native']))
    try:
        for r in remove:
            check();assert doc.getObject(r['object']);doc.removeObject(r['object'])
        # Cached native geometry is already qualified. No source-history edits.
        for r in old['printed_body_support_links']:
            o=doc.getObject(r['object']);assert o.LinkedObject and o.Shape.isValid()
            assert all(abs(a-b)<1e-5 for a,b in zip(signature(o.Shape),r['signature'])),r['part']
        doc.recompute();doc.saveAs(str(final))
    finally:close_owned()
    print('Corrected saved snapshot',len(remove),'motion duplicates removed',flush=True)
    with tempfile.TemporaryDirectory(prefix='robot-cat-w5-neutral-') as td:
        root=Path(td);sources={ROOT/r['native'] for r in old['printed_body_support_links']}
        for f in sources|{final}:
            dest=root/f.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dest)
        doc=A.openDocument(str(root/final.relative_to(ROOT)))
        try:
            for r in old['printed_body_support_links']:
                check();o=doc.getObject(r['object']);assert o and o.LinkedObject
                assert Path(o.LinkedObject.Document.FileName).resolve().is_relative_to(root.resolve())
                assert all(abs(a-b)<1e-5 for a,b in zip(signature(o.Shape),r['signature'])),r['part']
            assert all(doc.getObject(r['object']) is None for r in remove)
        finally:close_owned()
    result=dict(old)
    result.update(native=final.relative_to(ROOT).as_posix(),native_sha256=SHA(final),
        reference_objects=[r for r in old['reference_objects'] if is_rest(r['name'])],
        removed_sampled_pose_objects=remove,previous_snapshot_manifest=dict(path=oldfile.relative_to(ROOT).as_posix(),sha256=SHA(oldfile)),
        filter_replacement=dict(path=filter_key,previous_sha256=old['source_sha256'][filter_key],current_sha256=SHA(ROOT/filter_key),
            reason='Splice/branch IDs precede actual pose angles. Keep only0pose for explicit Band/Root/Source/chosen namespaces.'),
        worker_seconds=round(time.monotonic()-tick,3),original_assembly_build_seconds=old['worker_seconds'])
    result['source_sha256']=dict(old['source_sha256']);result['source_sha256'][filter_key]=SHA(ROOT/filter_key)
    for f in (Path(__file__),oldfile):result['source_sha256'][f.relative_to(ROOT).as_posix()]=SHA(f)
    receipt.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(native_links=14,removed=len(remove),references=len(result['reference_objects']),seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':run()
