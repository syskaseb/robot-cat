"""N01 rear MTA cradle/fork: existing T18I closes an external neck.

No strap crosses the roof below F0. Positive XY stops and two roof corners
retain the nominal case; no pressure on a guessed latch or electrical pad.
Provisional delivered-case/lid fit and structural pull tests remain phase2.
"""
import FreeCAD as A
import Part


def box(lo,hi):return Part.makeBox(*(b-a for a,b in zip(lo,hi)),A.Vector(*lo))


def joined(shapes):
    s=shapes[0].multiFuse(shapes[1:]) if len(shapes)>1 else shapes[0]
    assert s.isValid() and len(s.Solids)==1
    return s


def build(case_bounds,cap_bounds,bolt_X,side):
    assert side in (-1,1) and len(bolt_X)==2
    b=case_bounds;x0,x1=b.XMin,b.XMax
    y0,y1=sorted((side*b.YMin,side*b.YMax));assert y0>0
    cap_edge=max(side*cap_bounds.YMin,side*cap_bounds.YMax)
    x=sum(bolt_X)/2;y=cap_edge+1.25+4.4+.25
    floor=-44.3;under=b.ZMin-.2;split=-30.;roof=b.ZMax+.2;top=roof+2.4
    wall_top=cap_bounds.ZMin-1.5
    assert floor<under<wall_top<split<roof<top
    # Full walls below the adjacent cap; corner stops leave both tail mouths.
    base_features=[box([x0-2.6,y0-2.6,floor],[x1+2.6,y0-.2,wall_top]),
        box([x0-2.6,y1+.2,floor],[x1+2.6,y1+2.6,wall_top])]
    for xa,xb in ((x0+1,x0+4),(x1-4,x1-1)):
        base_features.append(box([xa,y0-2.6,floor],[xb,y1+2.6,under]))
    for xa,xb in ((x0-2.6,x0-.2),(x1+.2,x1+2.6)):
        for ya,yb in ((y0-2.6,y0+3),(y1-3,y1+2.6)):
            base_features.append(box([xa,ya,floor],[xb,yb,wall_top]))
    base_features.extend((box([x-4,y1+.2,floor],[x+4,y+3,under]),
        box([x-4,y-3,floor],[x+4,y+3,split])))
    base=joined(base_features)
    low=split-5.2
    tunnel=box([x-1.45,y-3.4,low-1.4],[x+1.45,y+3.4,low+.2])
    base=base.cut(tunnel);assert base.isValid() and len(base.Solids)==1
    features=[box([x0+.5,y-1.5,roof],[x1-.5,y+1.5,top]),
        box([x-4,y-3,split],[x+4,y+3,roof+.2]),
        box([x-6.6,y-3,split],[x+6.6,y+3,split+2.4])]
    for cx in (x0+2,x1-2):features.append(box([cx-1.5,y1-2,roof],[cx+1.5,y+1.5,top]))
    for a,c in ((x-6.6,x-4.2),(x+4.2,x+6.6)):
        features.append(box([a,y-3,split-3],[c,y+3,split+2.4]))
    fork=joined(features)
    inner=box([x-1.5,y-3.2,low],[x+1.5,y+3.2,top+.2])
    band=box([x-1.25,y-4.4,low-1.2],[x+1.25,y+4.4,top+1.4]).cut(inner)
    head=box([x-2.5,y+4.4,split-1.65],[x+2.5,y+8.7,split+3.65])
    actors=dict(base=base,fork=fork,band=band,head=head)
    if side<0:
        actors={n:s.mirror(A.Vector(),A.Vector(0,1,0)) for n,s in actors.items()}
        features=[s.mirror(A.Vector(),A.Vector(0,1,0)) for s in features]
        base,fork,band,head=(actors[n] for n in ('base','fork','band','head'))
    for s in actors.values():assert s.isValid() and len(s.Solids)==1
    nylon=band.fuse(head);assert nylon.isValid() and len(nylon.Solids)==1
    assembled=base.fuse(fork);assert assembled.isValid() and len(assembled.Solids)==1
    common=base.common(fork);assert common.isNull() or common.isValid();assert common.Volume<1e-5
    loop=2*(6.4+1.2+(top+.2-low)+1.2);assert loop<100
    return actors,dict(post_centre_mm=[x,side*y,split],roof_mm=roof,roof_capture_mm=2,
        wall_top_mm=wall_top,floor_mm=floor,nominal_bearing_face_mm2=48,
        minimum_post_tunnel_side_wall_mm=(8-2.9)/2,working_loop_mm=loop,working_loop_budget_mm=100,
        selected_T18I_length_mm=145,selected_T18I_width_mm=2.5,selected_T18I_thickness_mm=1.2,
        full_head_budget_mm=[5,4.3,5.3],full_fork_features=features,
        delivered_case_lid_and_retention_pull_fit_phase2=True)
