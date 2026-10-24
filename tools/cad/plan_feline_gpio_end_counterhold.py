"""Reserve the unused distal casing end, retaining the received root corridor.

The central casing region is occupied by five GPIO departures; the previous
X36..48 feet touch current W035. This single plan uses the last6mm of casing
and extends the existing root, without moving a wire, Pi or purchased housing.
Friction, PETG stiffness and delivered housing fit remain physical gates.
"""
import FreeCAD as A
import Part


def construct():
    x=48.; width=6.
    back=Part.makeBox(width,2.5,8,A.Vector(x,-12.4818903653,84)).fuse(
        Part.makeBox(width,5,3,A.Vector(x,-12.4818903653,83)))
    front=Part.makeBox(width,2.5,8,A.Vector(x,-20.0818903653,84)).fuse(
        Part.makeBox(width,5,3,A.Vector(x,-22.5818903653,83)))
    p=A.Vector(28,3,87.3);q=A.Vector(42,-10,87.3)
    root=Part.makeCylinder(1.5,(q-p).Length,p,q-p)
    extension=Part.makeCylinder(1.5,10.5,A.Vector(40.5,-10,87.3),A.Vector(1,0,0))
    back_root=root.fuse(extension).fuse(back).removeSplitter()
    parts=dict(back_root=back_root,front_jaw=front.removeSplitter(),
        tie_band_budget=Part.makeBox(8.4,17.5,2.5,A.Vector(46.8,-23.7818903653,83.25)),
        tie_head_budget=Part.makeBox(5.3,5,4.3,A.Vector(55.2,-17.5318903653,82.35)))
    for s in parts.values():
        s.check(True);assert s.isValid() and len(s.Solids)==1
    return parts,dict(grip_casing_X_interval_mm=[48,54],grip_width_mm=6,
        retained_original_root_from_mm=list(p),retained_original_root_to_mm=list(q),
        extension_axis_start_mm=[40.5,-10,87.3],extension_length_mm=10.5,
        wire_paths_and_bought_parts_unchanged=True,
        replaces_previous_whole_GPIO_clip_not_added_alongside_it=True,
        printed_fit_friction_stiffness_and_tie_tension_not_qualified=True,
        selected=False,N01_complete=False,physical_pass=False)


def screw_closure():
    """Bench-assembled M2x12 jaw; no zip head and no in-situ driver claim.

    Screw dimensions are project budgets consistent with existing M2 family,
    not a measured supplied screw. The short PETG pilot is a phase2 fit gate.
    """
    parts, plan = construct()
    base = A.Vector(51, -20.0818903653, 84.5)
    direction = A.Vector(0, 1, 0)
    shaft = Part.makeCylinder(1, 12, base, direction)
    head = Part.makeCylinder(2.2, 2.5, base, -direction)
    clearance = Part.makeCylinder(1.1, 8, base - direction*3, direction)
    counterbore = Part.makeCylinder(2.3, 2.6, base + direction*.1, -direction)
    pilot = Part.makeCylinder(.8, 5.2, A.Vector(51,-12.5818903653,84.5), direction)
    result = dict(back_root=parts['back_root'].cut(pilot),
                  front_jaw=parts['front_jaw'].cut(clearance).cut(counterbore),
                  screw_budget=shaft.fuse(head))
    for shape in result.values():
        shape.check(True)
        assert shape.isValid() and len(shape.Solids)==1
    plan.update(closure='M2x12 bench assembled, replaces entire nylon closure',
        screw_underhead_mm=12, screw_axis_world=list(base),
        screw_axis_direction=list(direction), pilot_diameter_mm=1.6,
        nominal_pilot_engagement_mm=4.4, head_budget_diameter_mm=4.4,
        head_budget_height_mm=2.5, existing_family_not_inventory_allocation=True,
        assembly_order=['GPIO housing and five wires seated on bench',
            'Tighten casing jaw before neighboring RR/AUX harness is installed',
            'Install surrounding harness with this clamp already closed',
            'Upper Pi frame mates last; clamp remains closed during Pi release'],
        open=['joint fit/friction and PETG thread strength',
              'head recess wall strength', 'full assembly sequence and missing scene',
              'whole Pi motion with new clip', 'stock allocation in N10'])
    return result, plan


def save(path, parts, plan, evidence):
    """Save only this bounded proposal with exact source pins and reopen check."""
    import hashlib, json, zipfile
    from pathlib import Path
    path=Path(path); archive=path.with_suffix('.breps.zip'); geometry=[]
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for i,(name,shape) in enumerate(parts.items()):
            shape.check(True)
            raw=shape.exportBrepToString().encode()
            reopened=Part.Shape(); reopened.importBrepFromString(raw.decode())
            reopened.check(True)
            assert reopened.isValid() and len(reopened.Solids)==1
            entry=f'{i}.brep';z.writestr(entry,raw)
            geometry.append(dict(name=name,entry=entry,
                sha256=hashlib.sha256(raw).hexdigest(),strict_reopen=True))
    report=dict(status='PARTIAL_GPIO_CASING_COUNTERHOLD_NOT_SELECTED',
        selected=False,N01_complete=False,physical_pass=False,
        recipe=plan,evidence=evidence,geometry=geometry,bundle=archive.name,
        bundle_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
        constructor_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report


def lower_with_clip(source, clip):
    """Reapply the received split/boss recipe; replace only the complete clip.

    Upper frame is reused from its immutable receipt, not regenerated.
    Historical constructor and its pins remain untouched.
    """
    below=source.common(Part.makeBox(600,600,404,A.Vector(-300,-300,-300)))
    lower=next(s for s in below.Solids if s.BoundBox.XMin<0)
    boss=Part.makeCylinder(2.5,6,A.Vector(-8,-11,98)).fuse(
        Part.makeCylinder(2.5,6,A.Vector(-8,-6,98))).fuse(
        Part.makeBox(5,5,6,A.Vector(-10.5,-11,98))).removeSplitter()
    lower=lower.fuse(boss)
    for y in [-11,-6]:
        lower=lower.cut(Part.makeCylinder(.8,6.1,A.Vector(-8,y,98)))
    lower=lower.fuse(clip['back_root']).removeSplitter()
    lower.check(True)
    assert lower.isValid() and len(lower.Solids)==1
    return lower
