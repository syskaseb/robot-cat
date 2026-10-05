"""Receive one coupled four-frame landing correction using exact faces.

R1 completed, not canceled: three proposed outer axes missed Deck material.
Move both front feet toX-85 and rear feet toX123 with10mm hole spacing,
using the recorded inner-side material; no repeated native geometry search.
"""
from pathlib import Path
import json
from servo_fuse_inputs_r1 import sha

BASE_SCRIPT=Path(__file__).with_name('w5_loom_attachment_plan.py')


def measure(A, Part, shape, x, y):
    levels=[];candidate_faces=0;curved_faces=0
    for face in shape.Faces:
        b=face.BoundBox
        if not (b.XMin-1e-6<=x<=b.XMax+1e-6 and b.YMin-1e-6<=y<=b.YMax+1e-6):
            continue
        candidate_faces+=1
        if isinstance(face.Surface,Part.Plane):
            n=face.normalAt(0,0)
            if abs(n.z)<1e-10:continue
            p=face.Surface.Position
            z=p.z-((x-p.x)*n.x+(y-p.y)*n.y)/n.z
            if 0<=z<=200 and face.isInside(A.Vector(x,y,z),1e-6,True):levels.append(z)
        else:
            curved_faces+=1
            line=Part.makeLine(A.Vector(x,y,max(0,b.ZMin-1)),A.Vector(x,y,min(200,b.ZMax+1)))
            common=line.common(face)
            levels.extend(v.Point.z for v in common.Vertexes)
    unique=[]
    for z in sorted(levels):
        if not unique or abs(z-unique[-1])>1e-5:unique.append(z)
    intervals=[]
    for low,high in zip(unique,unique[1:]):
        if high-low>1e-6 and shape.isInside(A.Vector(x,y,(low+high)/2),1e-6,False):
            intervals.append([low,high])
    return intervals,candidate_faces,curved_faces


def main():
    import FreeCAD as A, Part
    import w5_loom_attachment_plan as initial
    prior_path=initial.OUT/'plan.json';prior=initial.read(prior_path)
    assert prior['exact_root_axes_in_material']==5 and not prior['all_four_root_planes_match']
    assert all(sha(initial.ROOT/p)==h for p,h in prior['source_sha256'].items())
    # Check the lightweight measurement against all eight RECEIVED exact
    # whole-solid ray results before using it for the coupled correction.
    deck=Part.read(str(initial.DECK))
    for group in prior['groups']:
        for row in group['screw_stack_material']:
            x,y=row['axis_xy_mm'];values,_,_=measure(A,Part,deck,x,y)
            expected=row['actual_Deck_material_intervals_z_mm']
            assert len(values)==len(expected),(x,y,values,expected)
            assert all(abs(a-b)<1e-5 for p,q in zip(values,expected) for a,b in zip(p,q))
    source=BASE_SCRIPT.read_text(encoding='utf-8')
    source=source.replace("OUT = BASE/'w5-loom-attachment-plan-r1'", "OUT = BASE/'w5-loom-attachment-plan-r2'")
    source=source.replace("root_x=-92 if leg.startswith('F') else 130", "root_x=-85 if leg.startswith('F') else 123")
    source=source.replace("for dx in (-7,7):", "for dx in (-5,5):")
    old='''            line=Part.makeLine(A.Vector(x,y,0),A.Vector(x,y,200))
            common=line.common(deck)
            intervals=sorted([[min(e.valueAt(e.FirstParameter).z,e.valueAt(e.LastParameter).z),
                               max(e.valueAt(e.FirstParameter).z,e.valueAt(e.LastParameter).z)]
                              for e in common.Edges])'''
    assert old in source
    source=source.replace(old,"            intervals,candidates,curved=_measure(A,Part,deck,x,y)")
    source=source.replace("upper_material_plane_mm=max((p[1] for p in intervals),default=None)))",
        "upper_material_plane_mm=max((p[1] for p in intervals),default=None), candidate_faces=candidates, curved_faces=curved))")
    source=source.replace("pins =", "pins =")
    source=source.replace("pins=[Path(__file__),CONNECTION/'plan.json',DECK,CORRIDORS,SOURCE_MAP]",
        "pins=[Path(__file__),_base_script,_prior_path,CONNECTION/'plan.json',DECK,CORRIDORS,SOURCE_MAP]")
    source=source.replace("candidate_new_M3_attachment_count=8,selected_new_fasteners=0,",
        "candidate_new_M3_attachment_count=8,selected_new_fasteners=0, received_exact8ray_method=True, measurement_method='Actual plane/face crossings and solid classification; eight initial full-ray results reproduced before correction.',")
    ctx=dict(__file__=str(Path(__file__).resolve()),__name__='loom_attachment_received',
        _measure=measure,_base_script=BASE_SCRIPT,_prior_path=prior_path)
    exec(compile(source,str(BASE_SCRIPT),'exec'),ctx)
    ctx['main']()


if __name__=='__main__':main()
