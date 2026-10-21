"""Same E2 case and source side; module full9 land on its existing R12.4 arc."""
import math
import numpy as np
import FreeCAD as A
import Part
from receive_feline_global_case_candidates import placement
from receive_feline_underplate_return_gallery import bend, forward
from feline_source_restraint_plan import box
from plan_feline_n01_shared import pipe
from connect_feline_four_factory_sources import options


def construct(base):
    R = 12.4
    p = np.array([86.6999984741211, 0., 50.])
    theta = 9/R
    actors = {}
    caps = {}
    def at(s):
        a = s/R
        return (p+[-R*math.sin(a), R*(1-math.cos(a)), 0],
                np.array([-math.cos(a), math.sin(a), 0]),
                np.array([math.sin(a), math.cos(a), 0]))
    for w, z in (('XP02.module', 51.5), ('XP03.module', 48.5)):
        rows = []
        end, tangent = bend(rows, [p[0], 0, z], [-1, 0, 0], [0, 1, 0], R, theta)
        actors['JPWMSource:'+w] = pipe(rows, .925)
        caps[w] = dict(point_mm=end.tolist(),outward_axis=tangent.tolist(),
                       prefix_length_mm=9.,parts=rows)
    def swept(a, b, u0, u1, v0, v1):
        q, t, u = at(a)
        v = np.cross(t, u)
        corners = [A.Vector(*(q+y*u+z*v)) for y,z in
                   ((u0,v0),(u1,v0),(u1,v1),(u0,v1),(u0,v0))]
        edge = Part.Arc(A.Vector(*at(a)[0]), A.Vector(*at((a+b)/2)[0]),
                        A.Vector(*at(b)[0])).toShape()
        return Part.Wire([edge]).makePipeShell([Part.Wire(Part.makePolygon(corners).Edges)],True,False)
    r, h = 1.075, 2.575
    pad = swept(0,9,r,r+2,-h,h)
    band = swept(3.25,5.75,-r-1.2,r+3.2,-h-1.2,h+1.2).cut(
        swept(3.15,5.85,-r,r+2,-h,h))
    q,t,u = at(4.5)
    head = box([-2.5,r+3.2,-2.65],[2.5,r+7.5,2.65])
    frame = placement(np.column_stack((t,u,np.cross(t,u))),q)
    head.Placement = frame*head.Placement
    assert abs(head.Volume-5*4.3*5.3)<1e-5
    assert len(band.fuse(head).Solids)==1
    for k,s in dict(pad=pad,band=band,head=head).items():
        actors['JPWMGrip:module:'+k] = s
    assert all(s.isValid() and len(s.Solids)==1 for s in actors.values())
    return actors, dict(caps=caps,full_curved_land_mm=9.,R_mm=R,
                        full_T18I_head_mm=[5,4.3,5.3],
                        case_and_source_prefixes_unchanged=True,
                        external_pinout_changed=False,N01_complete=False)


def module_routes(original, caps):
    routes = {}
    R = 12.4
    for w, lift, z in (('XP02.module',6.,51.5),('XP03.module',3.,48.5)):
        source = original[w]
        y = source['parts'][0]['start'][1]
        start = np.array([88.75,y,41.18])
        corner = np.array([106.275,y,41.18+lift])
        rows = options(start,[1,0,0],corner,[1,0,0])[0]
        q,d = bend(rows,corner,[1,0,0],[0,-1,0],R)
        # Remain north of the complete rear-left motor until the pair is
        # west of its true X106.8 boundary, under the complete bank bed.
        middle = np.array([100.,42.175,q[2]])
        rows += options(q,d,middle,[0,-1,0])[0]
        landing = np.array([74.2999984741211,12.4,z])
        rows += options(middle,[0,-1,0],landing,[0,-1,0])[0]
        q,d = bend(rows,landing,[0,-1,0],[1,0,0],R,math.pi/2-9/R)
        assert np.linalg.norm(q-caps[w]['point_mm'])<1e-6
        needed = source['factory_debit_mm']+sum(r['length_mm'] for r in rows)
        assert needed<=220,(w,needed)
        routes[w] = dict(parts=rows,factory_debit_mm=source['factory_debit_mm'],
                         required_factory_mm=needed,minimum_stock_margin_mm=220-needed)
    return routes
