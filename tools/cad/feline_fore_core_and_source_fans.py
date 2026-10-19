"""Receive changed core only AFTER full six-source space allocation.

The nearby printed frame is a real shared parent, not an obstacle to notch.
Bridge its complete2mm face into the cuff's existing2mm wall. Preserve all
bought modules, straight9mm receivers, roots and factory4MTA sources.
"""
import hashlib
import json
import time
import zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_six_source_space import allocation
from feline_fore_power_pair import all_current_blockers


PARENT='StructureReserve:ForeNegativeBankConnection'


def named_parent():
    for filename in ('n01-full-material-scene.json','n01-lower-bay-world-probe.json',
                     'n01-common-restraint-world-probe.json','n01-remaining-selected-inventory.json'):
        path=OUT/filename;doc=json.loads(path.read_text())
        record=next((r for r in doc['parts'] if r['name']==PARENT),None)
        if record is None:continue
        assert sha(ROOT/doc['bundle'])==doc['bundle_sha256']
        with zipfile.ZipFile(ROOT/doc['bundle']) as z:raw=z.read(record['entry'])
        assert hashlib.sha256(raw).hexdigest()==record['sha256']
        s=Part.Shape();s.importBrepFromString(raw.decode())
        assert s.isValid() and len(s.Solids)==1
        return s,dict(file=path.relative_to(ROOT).as_posix(),sha256=sha(path),record=record)
    raise AssertionError('Missing actual named shared parent')


def shared_root(cuff,parent,band):
    b=parent.optimalBoundingBox();c=cuff.optimalBoundingBox()
    # The whole cuff's Ymax belongs to its retained root, NOT the U rim.
    # After two failed constructor fuses, locate the actual named9x2 rim
    # face and prove positive overlap there, rather than another offset.
    faces=[f for f in cuff.Faces if type(f.Surface).__name__=='Plane' and abs(f.CenterOfMass.z-c.ZMax)<1e-5]
    rim=max(faces,key=lambda f:f.CenterOfMass.y);rb=rim.optimalBoundingBox()
    assert abs(rb.XLength-9)<1e-5 and abs(rb.YLength-2)<1e-5 and abs(rim.Area-18)<1e-5
    # Positive0.5mm overlap with the existing1mm lip ABOVE the strap slot.
    # A coplanar face-only fuse was not a valid single solid; don't fill
    # the lower strap channel just to make a Boolean succeed.
    lo=[b.XMin,rb.YMin,rb.ZMax-.5];hi=[rb.XMax,b.YMin+2,b.ZMin+3]
    assert all(y>x for x,y in zip(lo,hi))
    bridge=Part.makeBox(*(y-x for x,y in zip(lo,hi)),A.Vector(*lo))
    result=cuff.fuse(bridge).removeSplitter()
    assert result.isValid() and len(result.Solids)==1
    # Full stock loop, not only the old top notch. The inherited root
    # crossed43.8mm3 of nylon; preserve that as a failure before correcting
    # this SAME interface with one complete clearance cut.
    old_common=cuff.common(band).Volume
    clearance=band.makeOffsetShape(.25,1e-5,join=2)
    assert clearance.isValid() and len(clearance.Solids)==1
    result=result.cut(clearance).removeSplitter()
    assert result.isValid() and len(result.Solids)==1
    assert result.common(band).Volume<1e-5 and result.distToShape(band)[0]>=.25-1e-6
    common=result.common(parent);assert common.isValid()
    expectedlo=[lo[0],b.YMin,b.ZMin];expectedhi=[hi[0],hi[1],hi[2]]
    volume=(hi[0]-lo[0])*2*3
    assert abs(common.Volume-volume)<1e-5
    return result,dict(part='BundleCuff:FR',other=PARENT,kind='NAMED_SHARED_FRAME_BRIDGE',
        intersection_bounds_mm=[expectedlo,expectedhi],expected_union_mm3=volume,
        bridge_bounds_mm=[lo,hi],full2mm_connection_not_a_point_or_sliver=True,
        actual_rim_face_centre_mm=list(rim.CenterOfMass),actual_rim_face_area_mm2=rim.Area,
        full_strap_clearance=dict(previous_positive_common_mm3=old_common,current_positive_common_mm3=result.common(band).Volume,
            nominal_gap_mm=result.distToShape(band)[0],required_mm=.25,whole_loop_not_only_top_notch=True),
        same_proposed_PETG_frame_native_connection_pending_N03=True,physical_pass=False)


def main():
    tick=time.monotonic();dest=OUT/'n01-six-source-current-core.json';assert not dest.exists()
    fanspath=OUT/'n01-six-source-shared-lanes.json';fans=json.loads(fanspath.read_text())
    assert len(fans['complete_ports'])==6 and all(fans['domains'].values()) and not fans['errors']
    assert sha(ROOT/fans['bundle'])==fans['bundle_sha256']
    src,parent,parts,rows,mouths,choices,facts=allocation()
    mate,pin=named_parent();parts['BundleCuff:FR'],relation=shared_root(parts['BundleCuff:FR'],mate,parts['BundleTie:FR'])
    changed={n for n in parts if rows[n]['group']=='S1'}|{'BundleCuff:FR'}
    doc={k:v for k,v in parent.items() if k not in ('all_current_blockers','bundle','bundle_sha256','parts','worker_seconds')}
    doc.update(status='SIX_FAN_DOMAINS_RECEIVED_CORE_CHANGED_PAIRS_RUNNING',N01_complete=False,
        source_fan_domains_file=fanspath.relative_to(ROOT).as_posix(),source_fan_domains_sha256=sha(fanspath),
        source_fan_mutual_assignment_and_shared47_NOT_qualified=True,
        equivalent_prior_packet=src.relative_to(ROOT).as_posix(),equivalent_prior_packet_sha256=sha(src),
        changed_parts=sorted(changed),six_source_allocation=facts,
        planned_own_relations=parent['planned_own_relations']+[relation],shared_frame_parent=pin)
    archive=dest.with_suffix('.breps.zip');records=[];oldrows={r['name']:r for r in parent['parts']}
    with zipfile.ZipFile(ROOT/parent['bundle']) as srczip,zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for i,(n,s) in enumerate(parts.items()):
            raw=s.exportBrepToString().encode() if n in changed else srczip.read(oldrows[n]['entry'])
            entry=f'{i:03d}.brep';z.writestr(entry,raw)
            records.append(dict(oldrows[n],entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    doc.update(bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),parts=records,
        source_sha256={**parent['source_sha256'],fanspath.relative_to(ROOT).as_posix():sha(fanspath),
            Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},worker_seconds=round(time.monotonic()-tick,3))
    dest.write_text(json.dumps(doc,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Core source121, changed11; frame union',relation['expected_union_mm3'],flush=True)
    all_current_blockers(dest)


if __name__=='__main__':
    import os
    print('WORKER_PID',os.getpid(),flush=True);main()
