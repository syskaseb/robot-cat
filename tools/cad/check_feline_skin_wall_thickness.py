"""Exact base-wall separation, independent of unresolved mounting topology.

Loft side surfaces only: end caps are intentional neck/tail openings, not zero
wall defects. Does NOT qualify narrow webs at portal edges, tabs or print loads.
"""
import json,time
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import OUT


def main():
    tick=time.monotonic();reader=SavedShapes();meta=json.loads((OUT/'shared-skin-exact.json').read_text())
    native=ROOT/meta['native'];assert sha(native)==meta['native_sha256']
    sides={};caps={}
    for name in ('OuterNative','InnerNative'):
        s=reader.shape(native,name);assert s.isValid() and len(s.Solids)==1
        selected=[];removed=[]
        for index,face in enumerate(s.Faces):
            b=face.optimalBoundingBox()
            if b.XLength<1e-6:removed.append(dict(face=index,x_mm=b.XMin))
            else:selected.append(face)
        assert len(removed)==2 and selected
        sides[name]=Part.makeShell(selected);caps[name]=removed
    separation,pairs,features=sides['OuterNative'].distToShape(sides['InnerNative'])
    result=dict(status='BASE_LOFT_SIDE_WALL_EXACT_SEPARATION_ONLY',native_changed=False,selected=False,
        physical_pass=False,native=native.relative_to(ROOT).as_posix(),native_sha256=sha(native),
        nominal_section_offset_mm=2,exact_lateral_surface_minimum_mm=separation,
        minimum_is_global_brep_distance_not_bbox=True,excluded_intentional_open_end_caps=caps,
        witness_points_mm=[[[v.x,v.y,v.z] for v in pair] for pair in pairs],
        side_face_counts={k:len(s.Faces) for k,s in sides.items()},
        full_print_wall_qualification=False,
        open=['Narrow material webs at portal intersections','Mount tabs/fastener stress','PETG print orientation/physical fit/load','Neck and tail cowl seams'],
        source_sha256={native.relative_to(ROOT).as_posix():sha(native),Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,3))
    (OUT/'skin-base-wall-thickness.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','exact_lateral_surface_minimum_mm','side_face_counts','worker_seconds')}),flush=True)


if __name__=='__main__':main()
