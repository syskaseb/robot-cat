"""Four occupied ports:3 core grooves+actual outer feed keepout; NC left free.

Two ties wrap the pressure bridge across its width, not between conductors.
Nominal cap gap/tightening and retention/creep require an unpowered sample.
"""
import FreeCAD as A
import Part
from loom_land_port import box,build as frame_for


def build(lands,normal,feeds):
    centre=[sum(q['centre_world_mm'][i] for q in lands)/3 for i in range(3)];axis=lands[0]['axis']
    frame=frame_for(dict(id='OccupiedRail',centre_world_mm=centre,axis=axis,length_mm=9),normal)['placement'];inv=frame.inverse()
    local=[list(inv.multVec(A.Vector(*q['centre_world_mm']))) for q in lands]
    assert sorted(round(p[1],6) for p in local)==[-4.75,0,4.75]
    assert all(abs(p[0])<1e-6 and abs(p[2])<1e-6 for p in local)
    feed_slots=[]
    for item in feeds:
        point=list(inv.multVec(A.Vector(*item['point_world_mm'])))
        assert abs(point[0])<1e-6 and abs(abs(point[1])-9.5)<1e-6,point
        feed_slots.append((1 if point[1]>0 else -1,item['radius_mm']+.4))
    assert 1<=len(feed_slots)<=2 and len({s for s,r in feed_slots})==len(feed_slots)
    radii=dict(feed_slots)
    lo=-(9.5+radii[-1]+1.2) if -1 in radii else -7.25
    hi=9.5+radii[1]+1.2 if 1 in radii else 7.25
    base_bounds=[.7,lo,-4.5,5.5,hi,4.5];cap_bounds=[-5,lo,-4.5,0,hi,4.5];entry_bounds=[1.5,-2,-8,5.5,2,-3.5]
    base=box(base_bounds).fuse(box(entry_bounds)).removeSplitter();cap=box(cap_bounds);cylinders=[];channels=[];bands=[]
    for y,radius in [(-4.75,1.3),(0,1.3),(4.75,1.3)]+[(side*9.5,radius) for side,radius in feed_slots]:
        tool=Part.makeCylinder(radius,9.2,A.Vector(0,y,-4.6));base=base.cut(tool).removeSplitter();cap=cap.cut(tool).removeSplitter()
        cylinders.append(dict(radius_mm=radius,height_mm=9.2,base_mm=[0,y,-4.6]))
    for a in (-2,2):
        bc=[4.5,lo-.1,a-1.4,5.6,hi+.1,a+1.4];cc=[-5.1,lo-.1,a-1.4,-4,hi+.1,a+1.4]
        base=base.cut(box(bc)).removeSplitter();cap=cap.cut(box(cc)).removeSplitter()
        outer=[-5.2,lo-1.2,a-1.25,5.7,hi+1.2,a+1.25];inner=[-4,lo,a-1.4,4.5,hi,a+1.4]
        head_y=3.5 if a>0 else -3.5;head=[5.7,head_y-3,a-2.5,11.7,head_y+3,a+2.5]
        band=box(outer).cut(box(inner)).fuse(box(head)).removeSplitter();bands.append(band)
        channels.append(dict(base=bc,cap=cc,band_outer=outer,band_inner=inner,band_head=head))
    for s in [base,cap,*bands]:assert s.isValid() and len(s.Solids)==1 and not s.check(True)
    assert base.common(cap).Volume<1e-6 and bands[0].common(bands[1]).Volume<1e-6
    for b in bands:
        assert base.common(b).Volume<1e-6 and cap.common(b).Volume<1e-6
        assert base.distToShape(b)[0]<1e-6 and cap.distToShape(b)[0]<1e-6
    recipe=dict(base_bounds_mm=base_bounds,cap_bounds_mm=cap_bounds,entry_bounds_mm=entry_bounds,
        cylinders=cylinders,channels=channels,local_to_world=list(frame.toMatrix().A),feed_slots=feed_slots,
        pitch_mm=4.75,project_core_OD_mm=2,feed_clearance_margin_mm=.4,loose_cap_gap_mm=.7,
        minimum_load_wall_mm=1.2,band_channel_width_mm=2.8,T18I_quantity=2,separate_CAP_quantity=1,
        feed_clearance_not_automatic_feed_retention=True,physical_fit_tightening_creep_gate_open=True)
    for s in [base,cap,*bands]:s.Placement=frame*s.Placement
    return dict(body=base,cap=cap,bands=bands,recipe=recipe,arrival_world_mm=list(frame.multVec(A.Vector(3.5,0,-6))))
