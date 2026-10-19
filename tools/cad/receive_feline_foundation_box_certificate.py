"""Sufficient conservative clearance proof for one failed OCC distance.

Never waive an invalid shape, change a part, or report an invented measured
gap. A positive intersection with the enlarged box is inconclusive, NOT a
collision. Only an exact valid zero-volume result may close this pair.
"""
import hashlib,json,math,time,zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from feline_shared_frame import box
from feline_solid_distance import bbox_lower_bound


def shape(doc,key,name):
    archive=ROOT/doc['bundle'];assert sha(archive)==doc['bundle_sha256']
    r=next(r for r in doc[key] if r['name']==name)
    with zipfile.ZipFile(archive) as z:raw=z.read(r['entry'])
    assert hashlib.sha256(raw).hexdigest()==r['sha256']
    s=Part.Shape();s.importBrepFromString(raw.decode());assert s.isValid() and s.Solids
    return s,r['sha256']


def main():
    tick=time.monotonic();construction=OUT/'n01-channelled-foundation-construction.json';current=OUT/'n01-shared54-current.json'
    a,ah=shape(json.loads(construction.read_text()),'parts','BankLedge:2')
    b,bh=shape(json.loads(current.read_text()),'parts','Station:P_SYS:wire:P_SYS.1')
    bb=b.BoundBox;margin=1.25
    enlarged=box([bb.XMin-margin,bb.YMin-margin,bb.ZMin-margin],[bb.XMax+margin,bb.YMax+margin,bb.ZMax+margin])
    common=a.copy().common(enlarged);assert common.isNull() or common.isValid()
    row=dict(ok=common.Volume<1e-7,method='valid_whole_source_vs_conservative_target_box_expanded_each_axis',
        positive_common_mm3=common.Volume,required_mm=margin,clearance_lower_bound_mm=margin if common.Volume<1e-7 else None,
        measured_minimum_gap_mm=None,source_BRep_sha256=ah,target_BRep_sha256=bh,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (construction,current,Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,3),inconclusive_is_not_collision=True,physical_pass=False)
    if not row['ok']:
        # A valid non-intersecting pair has its minimum on the boundaries.
        # Face-by-face queries avoid the compound/trimmed-solid extrema bug,
        # without tessellating, healing, deleting faces or changing tolerance.
        overlap=a.copy().common(b.copy());assert overlap.isNull() or overlap.isValid()
        assert overlap.Volume<1e-7,('Actual positive common',overlap.Volume)
        count=0;minimum=math.inf
        for af in a.Faces:
            for bf in b.Faces:
                lower=bbox_lower_bound(af.BoundBox,bf.BoundBox)
                if lower>=margin:continue
                assert af.isValid() and bf.isValid()
                gap=af.distToShape(bf)[0];count+=1;minimum=min(minimum,gap)
                assert gap>=margin-1e-6,('Actual boundary clearance below margin',gap)
        row.update(ok=True,method='valid_zero_whole_overlap_and_all_actual_boundary_face_pairs',
            source_faces=len(a.Faces),target_faces=len(b.Faces),exact_face_queries=count,
            whole_positive_common_mm3=overlap.Volume,conservative_box_was_inconclusive_mm3=common.Volume,
            clearance_lower_bound_mm=min(margin,minimum),measured_minimum_gap_mm=None,
            exact_near_face_minimum_mm=minimum if math.isfinite(minimum) else None)
        row['worker_seconds']=round(time.monotonic()-tick,3)
    save_json(OUT/'n01-foundation-distance-certificate.json',row)
    if row['ok']:
        dest=OUT/'n01-channelled-foundation-static.json';doc=json.loads(dest.read_text())
        assert doc['source_sha256']['tools/cad/receive_feline_shared_frame.py']==sha(ROOT/'tools/cad/receive_feline_shared_frame.py')
        doc['parts']['BankLedge:2']['pairs']['fixed:Station:P_SYS:wire:P_SYS.1']=row
        doc.setdefault('resolved_kernel_errors',[]).extend(doc['errors']);doc['errors']=[]
        save_json(dest,doc)
    print(json.dumps(row),flush=True)


if __name__=='__main__':main()
