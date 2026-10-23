"""Constructive two-piece keyed sleeve inside the received service reservation.

Nominal PETG fit/strength remains a physical gate. Ties close the sleeve;
shoulders and D flats, rather than friction alone, carry axial/torsional loads.
"""
import FreeCAD as A
import Part
from receive_feline_pi_split_service_space import independent


def build(frame):
    def d_collar(radius, flat, start, length):
        return Part.makeCylinder(radius,length,A.Vector(0,0,start)).common(
            Part.makeBox(10+flat,20,length+2,A.Vector(-10,-10,start-1)))
    outer=Part.makeCylinder(3.65,24,A.Vector(0,0,-12))
    bore=Part.makeCylinder(1.65,26,A.Vector(0,0,-13))
    collars={}
    for side in (-1,1):
        z=6*side
        collars[side]=d_collar(2.5,1.9,z-1,2)
        bore=bore.fuse(d_collar(2.65,2.05,z-1.15,2.3))
    sleeve=outer.cut(bore)
    halves={}
    bounds={}
    for side in (-1,1):
        clip=Part.makeBox(10,20,26,A.Vector(.125 if side>0 else -10.125,-10,-13))
        halves[side]=sleeve.common(clip)
        bounds[side]=outer.common(clip)
    for shapes in (collars,halves,bounds):
        for side,shape in shapes.items():
            assert shape.isValid() and len(shape.Solids)==1
            shape.Placement=frame*shape.Placement
    return collars,halves,bounds


def attach(fixed,mobile,collars):
    result={}
    for name,part,collar in [('fixed',fixed,collars[-1]),('mobile',mobile,collars[1])]:
        result[name]=independent(part).fuse(independent(collar)).removeSplitter()
        assert result[name].isValid() and len(result[name].Solids)==1
    return result


def cradle(frame,fixed,mobile):
    from check_feline_service_translation import sweep_convex_case
    collars,_,_=build(A.Placement())
    outer=Part.makeCylinder(3.65,24,A.Vector(0,0,-12))
    bore=Part.makeCylinder(1.65,26,A.Vector(0,0,-13))
    pocket=Part.makeCylinder(2.65,2.3,A.Vector(0,0,4.85)).common(
        Part.makeBox(12.05,20,4.3,A.Vector(-10,-10,3.85)))
    shell=outer.cut(bore.fuse(pocket))
    lower=Part.makeBox(20,10,26,A.Vector(-10,-10.125,-13))
    upper=Part.makeBox(20,10,26,A.Vector(-10,.125,-13))
    # Integral fixed-side bridge carries the cradle, not friction on a rod.
    bridge=Part.makeCylinder(3.65,4,A.Vector(0,0,-8)).common(lower)
    shapes={'cradle':shell.common(lower).fuse(bridge).removeSplitter(),
            'lid':shell.common(upper), 'collar':collars[1],
            'lid_budget':outer.common(upper)}
    # The rod is inclined but the unit withdraws vertically. The lower
    # cradle's opening follows that trajectory; the removed lid retains
    # the close axial shoulders/D flat during normal operation.
    pocket_world=independent(pocket);pocket_world.Placement=frame*pocket_world.Placement
    escape=sweep_convex_case(independent(pocket_world),[0,0,20])
    for s in shapes.values():
        assert s.isValid() and len(s.Solids)==1
        s.Placement=frame*s.Placement
    shapes['cradle']=independent(shapes['cradle']).cut(independent(escape)).removeSplitter()
    shapes['fixed']=independent(fixed).fuse(independent(shapes['cradle'])).removeSplitter()
    shapes['mobile']=independent(mobile).fuse(independent(shapes['collar'])).removeSplitter()
    assert all(s.isValid() and len(s.Solids)==1 for s in shapes.values())
    return shapes


def receive(shapes,frame,checks,stops,twist,subsets,extra):
    import hashlib,time,zipfile
    from pathlib import Path
    from check_main_p0_placement import ROOT,sha
    from plan_feline_layout import OUT
    from feline_atomic_save import save_json
    tick=time.monotonic();dest=OUT/'n01-Pi-open-cradle-joint.json'
    assert not dest.exists()
    assert all(not r['errors'] and not r['failures'] for r in checks.values())
    assert all(v<1e-7 for v in subsets.values())
    assert all(v>1e-4 for v in stops.values())
    assert all(sum(v.values())>1e-4 for v in twist.values())
    archive=dest.with_suffix('.breps.zip');geometry=[]
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
        for name,s in shapes.items():
            assert s.isValid() and len(s.Solids)==1
            data=s.exportBrepToString().encode();entry=str(len(geometry))+'.brep'
            z.writestr(entry,data);geometry.append(dict(name=name,entry=entry,sha256=hashlib.sha256(data).hexdigest()))
    paths=[Path(__file__),OUT/'n01-Pi-split-service-space.json',OUT/'n01-Pi-split-coupler-sampled36.json']
    result=dict(status='CONSTRUCTIVE_OPEN_CRADLE_CANDIDATE_CABLE_RELEASE_OPEN',
        frame=dict(position=list(frame.Base),rotation=list(frame.Rotation.Q)),
        checks=checks,axial_stops_at_2mm=stops,twist_stops_at_15degrees=twist,
        exact_subset_outside_mm3=subsets,geometry=geometry,bundle=archive.relative_to(ROOT).as_posix(),
        bundle_sha256=sha(archive),source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in paths},
        sequence=['Deenergized prototype; outer service panels removed; support Pi by hand',
                  'Cut two T18I heads from above; remove bands; replace ties during reassembly',
                  'Lid travels8mm normal to split, then80mm vertically to a free hand-held position',
                  'After cable releases are resolved, lift Pi+upper carrier40mm vertically'],
        minimum_pocket_wall_mm=1.,nominal_fit_clearance_mm=.15,split_gap_mm=.25,
        tie_head_tool_budget_mm=[8,25,7],tool_budget_is_project_assumption=True,
        strength_and_fit_qualified=False,selected=False,N01_complete=False,physical_pass=False,
        open=['USB/power releases and parked cables; GPIO mated budget assumption',
              'Actual tool and hand fit; PETG wall/load/creep and tie tightness tests',
              'Remaining F_PI wire-group service sequence and whole N01'],
        extra=extra,worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result);return result
