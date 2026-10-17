"""Receive completed pair checks after a closeDocument bookkeeping error.

Never rerun completed geometry checks merely to repair report/reopen handling.
"""
import json
import time
import hashlib
import zipfile
import shutil
import FreeCAD as A
from check_main_p0_placement import ROOT, SavedShapes, sha
from plan_feline_layout import BASE, OUT, MODEL


def main():
    tick=time.monotonic()
    old=json.loads((OUT/'interior-native-checks.json').read_text())
    assert old['pairs']==262 and len(old['contacts'])==184
    # Receive the actual saved output, not the intended destination. The
    # original source is immutable and recoverable from the tagged payload.
    wrong=ROOT/old['native']
    assert sha(wrong)==old['native_sha256']
    path=OUT/'FelineInteriorFirstRejected.FCStd'
    shutil.copy2(wrong,path)
    original_name='hardware/cad/studies/head-p7/yaw-r1/YawCarrier.FCStd'
    expected='f6dfdd21652ab4c61f187092a2554ef24c46387d6128635730a4ebc48c32ff5f'
    with zipfile.ZipFile(BASE/'phase1-whole-assembly/Phase1CurrentPayload.zip') as z:
        data=z.read(original_name)
    assert hashlib.sha256(data).hexdigest()==expected
    (ROOT/original_name).write_bytes(data)
    assert sha(ROOT/original_name)==expected
    old['source_recovery']=dict(source=original_name,restored_sha256=expected,
        archive='phase1-whole-assembly/Phase1CurrentPayload.zip',
        wrong_saved_native_preserved_as=path.relative_to(ROOT).as_posix(),
        reason='Loop variable path accidentally replaced output path. No geometry pair rerun.')
    doc=A.openDocument(str(path))
    try:
        names=[n for g in old['groups'] for n in g['objects']]
        assert len(names)==485
        assert all(doc.getObject(n) is not None for n in names)
        s=SavedShapes().shape(MODEL,'Ref_Material_BUSsupplier25_0_0')
        old.update(status='COMMON_INTERIOR_INTERFACES_REJECTED',
            fresh_native_reopen_verified=True,
            native=path.relative_to(ROOT).as_posix(),
            report_repair_only_no_pairs_repeated=True,
            supplier25=dict(valid=s.isValid(),solids=len(s.Solids),faces=len(s.Faces),
                edges=len(s.Edges),volume_mm3=s.Volume,
                assessment='Source validity is distinct from interference; not silently accepted.'),
            receiver_seconds=round(time.monotonic()-tick,3))
        (OUT/'interior-first-rejected.json').write_text(json.dumps(old,indent=2)+'\n')
        print(json.dumps(dict(pairs=old['pairs'],contacts=len(old['contacts']),
            errors=old['errors'],supplier25=old['supplier25'],seconds=old['receiver_seconds'])),flush=True)
    finally:
        A.closeDocument(doc.Name)


if __name__=='__main__':main()
