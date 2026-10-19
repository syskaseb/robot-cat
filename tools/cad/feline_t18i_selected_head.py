"""Selected T18I upper-tolerance head, not an arbitrary generic6cube.

Head is anchored at the same outside face of the unchanged nominal strap.
Wire,9mmgroove,wall,case and band stay byte-construction-identical. No native
or physical supplier-fit claim; compare the actual full head with neighbours.
"""
import json
import numpy as np
import FreeCAD as A
from check_main_p0_placement import ROOT,sha
from feline_shared_straight_combs import unit as original_unit
from feline_underplate_station_templates import box

SOURCE=ROOT/'hardware/reference/cable-ties/t18i-111-02370/head-envelope.json'


def source():
    doc=json.loads(SOURCE.read_text())
    for r in doc['drawing_receipts']:assert sha(SOURCE.parent/r['file'])==r['sha256']
    return doc


def unit(st,slot):
    result=original_unit(st,slot);old=result['parts']['head_budget'];b=old.BoundBox
    D,E,H=4.3,5.,5.3
    centre=b.Center
    lo=np.array([b.XMin if slot['side']>0 else b.XMax-D,centre.y-E/2,centre.z-H/2])
    new=box(lo,lo+np.array([D,E,H]))
    assert new.isValid() and len(new.Solids)==1
    delta=new.cut(old);assert delta.isNull() or delta.isValid()
    assert delta.Volume<1e-7,'Changed head is not inside prior conservative budget'
    result['parts']['head_budget']=new
    result['selected_T18I_head']=dict(source=SOURCE.relative_to(ROOT).as_posix(),source_sha256=sha(SOURCE),
        local_radial_tangent_axial_upper_mm=[D,H,E],volume_mm3=new.Volume,
        exact_subset_of_prior6cube=True,all_other_geometry_unchanged=True,physical_pass=False)
    return result
