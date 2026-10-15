"""Provisional three-core pressure bridge, two ties outside the core row.

4.75mm pitch/2mm insulated OD are project datums, not supplier pull ratings.
The0.7mm loose cap gap is a delivery-fit adjustment: measure insulation and
qualify tightening/creep on an unpowered sample. No physical retention PASS.
"""
import FreeCAD as A
import Part
from loom_land_port import box,build as frame_for


def build(lands,normal):
    assert len(lands)==3
    centre=[sum(q['centre_world_mm'][i] for q in lands)/3 for i in range(3)]
    axis=lands[0]['axis'];assert all(max(abs(a-b) for a,b in zip(q['axis'],axis))<1e-7 for q in lands)
    land=dict(id='ThreeCoreBridge',centre_world_mm=centre,axis=axis,length_mm=9)
    frame=frame_for(land,normal)['placement'];inv=frame.inverse()
    coordinates=sorted([list(inv.multVec(A.Vector(*q['centre_world_mm']))) for q in lands],key=lambda p:p[1])
    assert all(abs(p[0])<1e-6 and abs(p[2])<1e-6 for p in coordinates)
    assert max(abs(p[1]-wanted) for p,wanted in zip(coordinates,(-4.75,0,4.75)))<1e-6
    base_bounds=[.7,-12,-4.5,5.5,12,4.5];cap_bounds=[-3.5,-12,-4.5,0,12,4.5]
    entry_bounds=[1.5,-2,-8,5.5,2,-3.5]
    base=box(base_bounds).fuse(box(entry_bounds)).removeSplitter();cap=box(cap_bounds)
    cylinders=[];channels=[]
    for y in (-4.75,0,4.75):
        tool=Part.makeCylinder(1.3,9.2,A.Vector(0,y,-4.6))
        base=base.cut(tool).removeSplitter();cap=cap.cut(tool).removeSplitter()
        cylinders.append(dict(radius_mm=1.3,height_mm=9.2,base_mm=[0,y,-4.6]))
    bands=[]
    for y in (-9.25,9.25):
        base_cut=[4.3,y-1.55,-4.6,5.6,y+1.55,4.6]
        cap_cut=[-3.6,y-1.55,-4.6,-2.3,y+1.55,4.6]
        base=base.cut(box(base_cut)).removeSplitter();cap=cap.cut(box(cap_cut)).removeSplitter()
        outer=[-3.5,y-1.25,-5.7,5.5,y+1.25,5.7]
        inner=[-2.3,y-1.4,-4.5,4.3,y+1.4,4.5]
        band=box(outer).cut(box(inner)).fuse(box([5.5,y-3,-2.5,11.5,y+3,2.5])).removeSplitter()
        bands.append(band);channels.append(dict(base=base_cut,cap=cap_cut,band_outer=outer,band_inner=inner))
    for name,s in [('body',base),('cap',cap),*[(str(i),s) for i,s in enumerate(bands)]]:
        assert s.isValid() and len(s.Solids)==1 and not s.check(True),name
    assert base.common(cap).Volume<1e-6
    for b in bands:
        assert base.common(b).Volume<1e-6 and cap.common(b).Volume<1e-6
        assert base.distToShape(b)[0]<1e-6 and cap.distToShape(b)[0]<1e-6
    recipe=dict(base_bounds_mm=base_bounds,cap_bounds_mm=cap_bounds,entry_bounds_mm=entry_bounds,
        cylinders=cylinders,channels=channels,local_to_world=list(frame.toMatrix().A),
        loose_cap_gap_mm=.7,project_core_OD_mm=2,groove_radius_mm=1.3,pitch_mm=4.75,
        separate_CAP_quantity=1,T18I_quantity=2,physical_fit_tightening_creep_gate_open=True)
    for s in [base,cap,*bands]:s.Placement=frame*s.Placement
    return dict(body=base,cap=cap,bands=bands,recipe=recipe,arrival_world_mm=list(frame.multVec(A.Vector(3.5,0,-6))))
