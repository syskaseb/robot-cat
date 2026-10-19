"""Constructive torso contour for the shared fore layout, not final N06 skin.

Piecewise ruled rounded sections deliberately avoid spline overshoot. No
native master edits; containment/3.25 budget are real BRep queries. The
outline cannot award N01 without all other modules/ends/roots/access.
"""
import json
import math
import time
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_central_pi_wedge import packed


STATIONS=[(-141.5,160),(-128,196),(-65,196),(55,196),(112,188),(145,166),(168,100),(183.5,40)]


def section(x,width,zlo=-48,zhi=112,r=12):
    h=width/2;c=math.sqrt(.5);p=lambda y,z:A.Vector(x,y,z)
    points=[p(h-r,zhi),p(-h+r,zhi),p(-h,zhi-r),p(-h,zlo+r),
            p(-h+r,zlo),p(h-r,zlo),p(h,zlo+r),p(h,zhi-r)]
    mids=[p(-h+r-r*c,zhi-r+r*c),p(-h+r-r*c,zlo+r-r*c),
          p(h-r+r*c,zlo+r-r*c),p(h-r+r*c,zhi-r+r*c)]
    edges=[]
    for i in range(4):
        a,b=2*i,(2*i+1)%8
        edges.append(Part.makeLine(points[a],points[b]))
        edges.append(Part.Arc(points[b],mids[i],points[(b+1)%8]).toShape())
    w=Part.Wire(edges);assert w.isValid() and w.isClosed();return w


def contour(stations=None):
    s=Part.makeLoft([section(x,w) for x,w in (stations or STATIONS)],True,True)
    assert s.isValid() and len(s.Solids)==1 and not s.check(True)
    b=s.optimalBoundingBox()
    assert abs(b.XLength-325)<1e-5 and b.YLength<=200+1e-5 and abs(b.ZLength-160)<1e-5
    return s


def main():
    tick=time.monotonic();src=OUT/'n01-supported-fore-layout.json'
    doc,parts,rows=packed(src);dest=OUT/'n01-supported-fore-outline.json'
    assert not dest.exists(),'Receive existing contour before any repeat'
    outer=contour();path=OUT/'n01-supported-fore-outline.brep';outer.exportBrep(str(path))
    surface=Part.makeCompound(outer.Shells)
    result=dict(status='RUNNING_TORSO_CONTAINMENT',selected=False,N01_complete=False,physical_pass=False,
        dimensions_mm=[325,196,160],stations_X_width_mm=STATIONS,corner_radius_mm=12,
        construction='Ruled rounded-section planning boundary; final editable wall/panels remain N06',
        minimum_budget_mm=3.25,budget_basis='2mm planned skin plus1.25mm nominal internal air, not manufacturing/physical approval',
        queries=[],failures=[],errors=[],source_sha256={src.relative_to(ROOT).as_posix():sha(src),
            doc['bundle']:doc['bundle_sha256'],Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        brep=path.relative_to(ROOT).as_posix(),brep_sha256=sha(path),
        open=['All other47 kits and current246ends','Head/neck/tail contours and limb openings',
              'Frame roots/tools/assembly plan','N06 wall thickness, panel segmentation and256cube exports'])
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    save()
    for n,s in parts.items():
        try:
            outside=s.copy().cut(outer.copy());assert outside.isNull() or outside.isValid()
            gap=float(s.distToShape(surface)[0]) if outside.Volume<1e-5 else None
            row=dict(part=n,outside_mm3=outside.Volume,boundary_gap_mm=gap)
            result['queries'].append(row)
            if outside.Volume>1e-5 or gap<3.25-1e-5:result['failures'].append(row)
        except Exception as e:result['errors'].append(dict(part=n,error=repr(e)))
        save()
    result['status']='CURRENT107_TORSO_BUDGET_CLEAR_OTHER_N01_OPEN' if not result['failures'] and not result['errors'] else 'TORSO_BUDGET_REQUIRES_SHARED_REASSESSMENT'
    save();print(json.dumps(dict(status=result['status'],parts=len(result['queries']),failures=result['failures'],errors=result['errors'],seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':main()
