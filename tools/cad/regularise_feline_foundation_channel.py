"""Change the NEW carrier channel topology after two OCC extrema failures.

Enclose one whole wire in a conservative1.251mm expanded box and remove
only new PETG. Never heal/shrink the source, waive margins or replay the
unchanged32 carrier components. The original candidate remains in git79b5acfe.
"""
import hashlib,json,time,zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from feline_shared_frame import box,material_connections
from receive_feline_foundation_box_certificate import shape


def main():
    tick=time.monotonic();file=OUT/'n01-channelled-foundation-construction.json';doc=json.loads(file.read_text())
    assert not doc.get('kernel_topology_cause_change'),'Already received cause change; do not repeat'
    archive=ROOT/doc['bundle'];old_json_sha=sha(file);old_archive_sha=sha(archive)
    current=OUT/'n01-shared54-current.json';wire,wire_sha=shape(json.loads(current.read_text()),'parts','Station:P_SYS:wire:P_SYS.1')
    b=wire.BoundBox;gap=1.251;cutter=box([b.XMin-gap,b.YMin-gap,b.ZMin-gap],[b.XMax+gap,b.YMax+gap,b.ZMax+gap])
    rows={r['name']:r for r in doc['parts']};raws={};parts={}
    with zipfile.ZipFile(archive) as z:
        for n,r in rows.items():
            raw=z.read(r['entry']);assert hashlib.sha256(raw).hexdigest()==r['sha256']
            s=Part.Shape();s.importBrepFromString(raw.decode());assert s.isValid() and len(s.Solids)==1
            raws[n]=raw;parts[n]=s
    name='BankLedge:2';old=parts[name];new=old.copy().cut(cutter.copy())
    assert new.isValid() and len(new.Solids)==1
    outside=new.copy().cut(old.copy());assert outside.isNull() or outside.isValid();assert outside.Volume<1e-7
    common=new.copy().common(cutter.copy());assert common.isNull() or common.isValid();assert common.Volume<1e-7
    parts[name]=new
    # Only the already recorded tiny NEW pier offcut is not in the carrier.
    connected={n:s for n,s in parts.items() if n!='BankPier:2/1'}
    joints=material_connections(connected)
    record=dict(part=name,reason='Two whole/face extrema methods failed on same trimmed topology; conservative whole-wire channel replaces curved pocket only in NEW stock',
        wire='Station:P_SYS:wire:P_SYS.1',wire_BRep_sha256=wire_sha,gap_mm=gap,
        removed_new_PETG_mm3=old.Volume-new.Volume,source_outside_original_mm3=outside.Volume,
        common_with_expanded_target_box_mm3=common.Volume,
        original_construction_sha256=old_json_sha,original_archive_sha256=old_archive_sha,
        original_preserved_commit='79b5acfe',actual_positive_connection_count=len(joints),
        source_code_sha256=sha(Path(__file__)),physical_pass=False)
    newraw=new.exportBrepToString().encode();raws[name]=newraw;rows[name]['sha256']=hashlib.sha256(newraw).hexdigest()
    # Preserve original serialized bytes for every unchanged candidate part.
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for n,r in rows.items():z.writestr(r['entry'],raws[n])
    doc.update(kernel_topology_cause_change=record,bundle_sha256=sha(archive),status='CHANNELLED_CURRENT_CANDIDATE_KERNEL_TOPOLOGY_REVISED_NOT_N01')
    save_json(file,doc)
    receipt=OUT/'n01-channelled-foundation-static.json';received=json.loads(receipt.read_text())
    for p,h in ((file,old_json_sha),(archive,old_archive_sha)):
        assert received['source_sha256'][p.relative_to(ROOT).as_posix()]==h
    # All cached exact interfaces of byte-identical pieces remain applicable.
    received.setdefault('superseded_changed_piece_receipts',[]).append(received['parts'].pop(name))
    received.setdefault('resolved_kernel_errors',[]).extend(received['errors']);received['errors']=[]
    received['source_sha256'][file.relative_to(ROOT).as_posix()]=sha(file)
    received['source_sha256'][archive.relative_to(ROOT).as_posix()]=sha(archive)
    received['kernel_topology_cause_change']=record
    received['construction']['positive_material_connections']=joints
    received['construction']['source_candidate_sha256']=sha(file)
    received['construction']['kernel_topology_cause_change']=record
    received['status']='PARTIAL_COMMON_FOUNDATION'
    save_json(receipt,received)
    record['worker_seconds']=round(time.monotonic()-tick,3)
    save_json(OUT/'n01-foundation-kernel-cause-change.json',record)
    print(json.dumps(record),flush=True)


if __name__=='__main__':main()
