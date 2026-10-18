"""Receive R2 without unchanged matrix reruns; restore original4mm USB corner.

Freeze current proposed material for later full inventory/route integration.
No motion/native/whole-N01 selection; missing W3/W4/monitor stays explicit.
"""
import hashlib
import json
import sys
import time
import zipfile
from pathlib import Path
import FreeCAD as A
import Part
import numpy as np
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import OUT
from plan_feline_common_restraints import main as build


def main():
    tick=time.monotonic();dest=OUT/'n01-common-restraint-world-probe.json';bundle=dest.with_suffix('.zip')
    assert not dest.exists() and not bundle.exists()
    source=OUT/'n01-common-restraint-material-r2.json';old=json.loads(source.read_text())
    assert old['status']=='SHARED_RETENTION_REJECTED_NO_MOTION_RERUN' and not old['errors']
    assert old['contacts']==[dict(a='CurrentBUS:USB_DiagonalArm',b='CurrentBUS:USB_AfterBendRelief',pose=None,volume_mm3=old['contacts'][0]['volume_mm3'])]
    assert old['wall_failures']==['CurrentBUS:USB_DiagonalArm'] and not old['outside'] and not old['driver_conflicts']
    sys.argv.append('--coherent-retention');new,kinds,owners,scene,meta,p=build(geometry_only=True,restore_usb_corner=True)
    prior={r['name']:r for r in old['parts']};assert set(new)==set(prior)
    fn='CurrentBUS:USB_DiagonalArm';arm=new[fn];q=np.array([135.5,-71.90814337545011,51.60996202870123])
    original=arm.fuse(Part.makeBox(6,6,3,A.Vector(*(q-[3,3,1.5])))).removeSplitter()
    assert original.isValid() and len(original.Solids)==1
    assert abs(original.Volume-prior[fn]['volume_mm3'])<1e-4
    added=arm.cut(original);assert added.isNull() or added.isValid();assert added.Volume<1e-5
    removed=original.cut(arm);assert removed.isNull() or removed.isValid()
    interface=arm.common(scene['CurrentBUS:USB_AfterBendRelief']);assert interface.isValid() and interface.Volume>1e-5
    reader=SavedShapes();outer=reader.shape(OUT/'central-cassette-envelope/FelineLayoutEnvelope.FCStd','TorsoEnvelope')
    outside=arm.cut(outer);assert outside.isNull() or outside.isValid();gap=arm.distToShape(Part.makeCompound(outer.Shells))[0]
    rows=[]
    with zipfile.ZipFile(bundle,'x',compression=zipfile.ZIP_DEFLATED) as z:
        for i,(name,s) in enumerate(new.items()):
            assert s.isValid() and s.Solids
            b=s.BoundBox;bb=[[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]]
            if name!=fn:
                assert np.max(np.abs(np.array(bb)-prior[name]['bounds_mm']))<1e-5,name
                assert abs(s.Volume-prior[name]['volume_mm3'])<1e-4,name
            raw=s.exportBrepToString().encode('utf-8');entry=f'{i:03d}.brep';z.writestr(entry,raw)
            rows.append(dict(name=name,kind=kinds[name],owner=owners[name],entry=entry,
                sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=bb,volume_mm3=s.Volume,solids=len(s.Solids)))
    clear=outside.Volume<1e-5 and gap>=3.65-1e-5
    report=dict(status='COMMON_RETENTION_MATERIAL_RECEIVED_WIRING_INVENTORY_MOTION_NATIVE_OPEN' if clear else 'COMMON_RETENTION_RECEIVED_USB_WALL_BUDGET_OPEN',
        selected=False,N01_complete=False,physical_pass=False,parts=rows,count=len(rows),
        bundle=bundle.relative_to(ROOT).as_posix(),bundle_sha256=sha(bundle),
        source_receipt=source.relative_to(ROOT).as_posix(),source_receipt_sha256=sha(source),
        original_rejection_preserved=True,original_USB4mm_knuckle_restored=True,
        USB_material_added_mm3=added.Volume,USB_material_removed_mm3=removed.Volume,
        USB_full_original_geometry_metrics_match=True,unchanged_parts_metrics_matched=len(rows)-1,
        USB_shared_printed_afterbend_interface_volume_mm3=interface.Volume,
        USB_outside_mm3=outside.Volume,USB_boundary_gap_mm=gap,
        all_new_material_static_clear_in_received_scope=clear,
        unchanged_material_matrix_or_motion_rerun=False,
        assembly_sequence=dict(deep_lower_service_cut_ties=['W026/factory/end','W037/factory/end'],
            replacement_ties_candidate=2,two_panels_tethered=True,full_disconnection_and_parking_list_complete=False,
            routine12ATO_requires_no_such_disconnections=True),
        missing_selected_rigid_inventory=['F_HY','F_HP','F_TY','Monitor5015'],
        required_next='Include all selected W3/W4/monitor parts and all20distribution stations/extra nets, full89body middles/USB and12movinglooms BEFORE native. Received126parts do not complete N01.',
        source_sha256={**reader.hashes,**{f.relative_to(ROOT).as_posix():sha(f) for f in (source,Path(__file__),Path(__file__).with_name('plan_feline_common_restraints.py'))}},
        worker_seconds=round(time.monotonic()-tick,3))
    dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(report['status'],report['count'],report['worker_seconds'],'USB gap',round(gap,4),flush=True)


if __name__=='__main__':main()
