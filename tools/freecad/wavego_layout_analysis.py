"""Measurements and study-only display setup for the dedicated WAVEGO layout.

Run through FreeCAD MCP execute_code. components.json is design input;
measurements.json and validation.json are generated geometric evidence.
World placements include the complete imported assembly hierarchy.
"""

import json
import math
from pathlib import Path

import FreeCAD as App
import Part

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "hardware/wavego/layout"


def world_shape(obj):
    shape = obj.Shape.copy()
    shape.Placement = obj.getGlobalPlacement()
    return shape


def bounds(shape):
    b = shape.BoundBox
    return [round(v, 4) for v in
            (b.XMin, b.YMin, b.ZMin, b.XMax, b.YMax, b.ZMax)]


def leaves(doc):
    return [o for o in doc.Objects if o.TypeId == "Part::Feature"
            and o.Name.startswith("Part__Feature") and not o.Shape.isNull()]


def inspect(doc):
    if doc.Name != "WAVEGO_component_layout":
        raise RuntimeError("Select the dedicated component-layout copy")
    items, holes, structural = [], [], []
    for o in leaves(doc):
        s = world_shape(o)
        items.append(dict(name=o.Name, label=o.Label, bbox=bounds(s),
                          volume_mm3=round(s.Volume, 3), solids=len(s.Solids)))
        if not any(t in o.Label for t in ("MainFrame", "SidePanel", "Cover")):
            continue
        structural.append((o.Label, s))
        for i, f in enumerate(s.Faces, 1):
            surf = f.Surface
            if not isinstance(surf, Part.Cylinder):
                continue
            u0, u1, v0, v1 = f.ParameterRange
            u, v = (u0 + u1) / 2, (v0 + v1) / 2
            p = f.valueAt(u, v)
            axis = surf.Axis
            center = surf.Center
            on_axis = center + axis * (p - center).dot(axis)
            inward = f.normalAt(u, v).dot(p - on_axis) < 0
            holes.append(dict(object=o.Name, label=o.Label, face=f"Face{i}",
                              diameter=round(surf.Radius * 2, 4),
                              axis=[round(c, 5) for c in axis],
                              center=[round(c, 4) for c in on_axis],
                              bbox=bounds(f), inward=inward,
                              full_circle=abs(u1-u0-6.28318530718)<0.001))
    sections = []
    for x in (-80, -65, -40, 0, 21, 40, 80, 106, 120):
        for z in (2, 10, 20, 30, 35):
            ray = Part.makeLine(App.Vector(x,-80,z),App.Vector(x,80,z))
            hits=[]
            for label,s in structural:
                for edge in ray.common(s).Edges:
                    b=edge.BoundBox
                    hits.append([label,round(b.YMin,4),round(b.YMax,4)])
            negative=[h[2] for h in hits if h[2]<0]
            positive=[h[1] for h in hits if h[1]>0]
            blocked=any(h[1]<=0<=h[2] for h in hits)
            width=min(positive)-max(negative) if positive and negative and not blocked else None
            sections.append(dict(x=x,z=z,clear_width=width,center_blocked=blocked,hits=hits))
    result=dict(document=doc.Name,coordinate_frame="mm: -X front, -Y left, +Z up; imported center x=21",
                parts=items,cylindrical_faces=holes,width_sections=sections,
                note="Cylindrical faces are geometry candidates, not certified threads or unused attachment points.")
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"measurements.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(dict(parts=len(items),cylinder_faces=len(holes),
                          sections=[{k:v for k,v in r.items() if k!='hits'} for r in sections])))
    return result


def layout_inputs(doc):
    if doc.Name != "WAVEGO_component_layout":
        raise RuntimeError("Select the dedicated component-layout copy")
    data=json.loads((OUT/"components.json").read_text(encoding="utf-8"))
    mapping=json.loads((OUT/"object-map.json").read_text(encoding="utf-8"))
    return data, {c["id"]:doc.getObject(mapping[c["id"]]) for c in data["components"]}


def configure(doc):
    """Attach provenance, style study objects, and draw derived measurement aids."""
    import FreeCADGui as Gui
    data, objects=layout_inputs(doc)
    group=doc.getObject("ComponentStudy") or doc.addObject("App::DocumentObjectGroup","ComponentStudy")
    group.Label="PACKAGING STUDY - envelopes, not print parts"
    colors={"lower":(0.90,0.56,0.16),"upper":(0.16,0.68,0.74),
            "head":(0.36,0.72,0.38),"neck":(0.48,0.34,0.72),"tail":(0.48,0.34,0.72)}
    for c in data["components"]:
        o=objects[c["id"]]
        group.addObject(o)
        for prop,value in (("ComponentID",c["id"]),("Evidence",c["status"]),
                           ("Source",c["source"]),("MountingNotes",c.get("note","")),
                           ("StudyZone",c["zone"]),("EnvelopeSizeMM",str(c["size"]))):
            if prop not in o.PropertiesList:o.addProperty("App::PropertyString",prop,"Layout study")
            setattr(o,prop,value)
        for v in (o.ViewObject,o.Tip.ViewObject):
            v.ShapeColor=colors[c["zone"]]
            v.LineColor=(0.1,0.15,0.18)
            v.Transparency=18
    for name in ("Backpack_envelope___NOT_a_printable_shell","Head_envelope___NOT_a_printable_shell"):
        o=doc.getObject(name)
        group.addObject(o)
        o.ViewObject.DisplayMode="Wireframe"
        o.Tip.ViewObject.DisplayMode="Wireframe"
        o.ViewObject.LineColor=(0.85,0.3,0.2)
        o.Tip.ViewObject.LineColor=(0.85,0.3,0.2)
        o.ViewObject.LineWidth=2.0
    for o in doc.Objects:
        if o.Name.startswith(("X_Axis","Y_Axis","Z_Axis","XY_Plane","XZ_Plane","YZ_Plane","Origin","Axis_")):
            o.ViewObject.Visibility=False
    for label in ("TopCover","Part9","Part001"):
        for o in doc.getObjectsByLabel(label):o.ViewObject.Visibility=False
    # Exact circle geometry derives from imported hole centers; no new holes cut.
    markers=[]
    for x in (-80,-70,112,122):
        for y in (-22.5,22.5):
            markers.append(Part.makeCircle(1.3,App.Vector(x,y,38.52)))
            markers.append(Part.makeLine(App.Vector(x,y,38.52),App.Vector(x,y,43)))
    for x in (1,59):
        for y in (-24.5,24.5):
            markers.append(Part.makeCircle(1.3,App.Vector(x,y,0)))
            markers.append(Part.makeLine(App.Vector(x,y,-1.5),App.Vector(x,y,3)))
    hole=doc.getObject("StudyMountingAxes") or doc.addObject("Part::Feature","StudyMountingAxes")
    hole.Label="Measured lid + bottom Pi-pattern axes - diameter 2.6 mm"
    hole.Shape=Part.makeCompound(markers)
    hole.ViewObject.LineColor=(1.0,0.2,0.1)
    hole.ViewObject.LineWidth=3
    group.addObject(hole)
    origin=App.Vector(*data["camera"]["optical_origin"])
    depth=80
    h=depth*math.tan(math.radians(data["camera"]["horizontal_fov_deg"]/2))
    v=depth*math.tan(math.radians(data["camera"]["vertical_fov_deg"]/2))
    forward=App.Vector(*data["camera"]["optical_direction"])
    right=App.Vector(*data["camera"]["image_right"])
    corners=[origin+forward*depth+right*(sy*h)+App.Vector(0,0,sz*v)
             for sy,sz in ((-1,-1),(1,-1),(1,1),(-1,1))]
    edges=[Part.makeLine(origin,p) for p in corners]
    edges += [Part.makeLine(corners[i],corners[(i+1)%4]) for i in range(4)]
    fov=doc.getObject("CameraFOV") or doc.addObject("Part::Feature","CameraFOV")
    fov.Label="Camera FOV 102 x 67 deg - illustrative optical rays"
    fov.Shape=Part.makeCompound(edges)
    fov.ViewObject.LineColor=(0.95,0.55,0.02)
    fov.ViewObject.LineWidth=2
    group.addObject(fov)
    camera_holes=[]
    # Carrier datum is a proposed plane, not a measured PCB back face.
    # Hole pattern and optical-axis offsets come from the official drawing.
    for center in data["camera"]["mount_hole_centers"]:
        p=App.Vector(*center)
        camera_holes.append(Part.makeCircle(1.1,p,forward))
        camera_holes.append(Part.makeLine(p-forward*4,p+forward*4))
    guide=doc.getObject("CameraMountPattern") or doc.addObject("Part::Feature","CameraMountPattern")
    guide.Label="Camera carrier datum: 4 x diameter 2.2 / 21 x 12.5 pitch"
    guide.Shape=Part.makeCompound(camera_holes)
    guide.ViewObject.LineColor=(1.0,0.2,0.1)
    guide.ViewObject.LineWidth=3
    group.addObject(guide)
    doc.recompute()
    Gui.activeDocument().activeView().viewAxonometric()
    Gui.activeDocument().activeView().fitAll()
    doc.save()


def overlap(a,b):
    aa,bb=a.BoundBox,b.BoundBox
    if any(min(getattr(aa,k+"Max"),getattr(bb,k+"Max"))-
           max(getattr(aa,k+"Min"),getattr(bb,k+"Min"))<=1e-5 for k in "XYZ"):
        return 0.0
    return a.common(b).Volume


def rotation(pivot,axis,angle):
    p=App.Vector(*pivot)
    r=App.Rotation(App.Vector(*axis),angle)
    return App.Placement(p-r.multVec(p),r)


def parents(obj):
    found=set()
    todo=list(obj.InList)
    while todo:
        p=todo.pop()
        if p.Name in found or p.TypeId!="App::Part":continue
        found.add(p.Name)
        todo.extend(p.InList)
    return found


def verify_source(doc):
    """Reject changed source geometry or an animated pose before measuring."""
    baseline=json.loads((OUT/"measurements.json").read_text(encoding="utf-8"))
    changed=[]
    for entry in baseline["parts"]:
        obj=doc.getObject(entry["name"])
        if obj is None:
            changed.append(entry["name"])
            continue
        shape=world_shape(obj)
        if (any(abs(a-b)>0.01 for a,b in zip(bounds(shape),entry["bbox"]))
                or abs(shape.Volume-entry["volume_mm3"])>0.01
                or len(shape.Solids)!=entry["solids"]):
            changed.append(entry["name"])
    if changed:
        raise RuntimeError("Source differs from neutral baseline; stop/reset motion first: "+str(changed))
    return len(baseline["parts"])


def validate(doc):
    data,objects=layout_inputs(doc)
    verify_source(doc)
    source_names={p["name"] for p in json.loads((OUT/"measurements.json").read_text())["parts"]}
    original=[(o,world_shape(o)) for o in doc.Objects if o.Name in source_names]
    omitted={"TopCover","Part9","Part001"}
    comp={k:world_shape(o) for k,o in objects.items()}
    manifest_mismatch=[]
    for c in data["components"]:
        expected=c["min"]+[a+b for a,b in zip(c["min"],c["size"])]
        if any(abs(a-b)>0.01 for a,b in zip(bounds(comp[c["id"]]),expected)):
            manifest_mismatch.append(c["id"])
    if manifest_mismatch:
        raise RuntimeError("Update CAD/manifest disagreement: "+str(manifest_mismatch))
    source_hits=[]
    for cid,shape in comp.items():
        for o,s in original:
            volume=overlap(shape,s)
            if volume>0.001:
                source_hits.append(dict(component=cid,part=o.Label,volume_mm3=round(volume,4),
                                        removed_in_proposal=o.Label in omitted))
    pairs=[]
    for i,a in enumerate(data["components"]):
        for b in data["components"][i+1:]:
            volume=overlap(comp[a["id"]],comp[b["id"]])
            if volume>0.001:pairs.append([a["id"],b["id"],round(volume,4)])
    # Load only definitions; never run the motion macro's saveAs/UI entry point.
    macro=ROOT/"tools/freecad/WAVEGO_Motion.FCMacro"
    definitions=macro.read_text(encoding="utf-8").rsplit("\ndoc = App.ActiveDocument",1)[0]
    ns={}
    exec(compile(definitions,str(macro),"exec"),ns)
    moving=[]
    for o,s in original:
        ancestor=parents(o)
        for leg in ns["LEGS"]:
            chain=[joint for joint in ("Hip","Knee","Ankle") if f"Motion_{leg}_{joint}" in ancestor]
            if chain:moving.append((o.Label,s,leg,chain))
    backpack=world_shape(doc.getObject("Backpack_envelope___NOT_a_printable_shell"))
    head=world_shape(doc.getObject("Head_envelope___NOT_a_printable_shell"))
    gait_keepouts=dict(comp,BackpackEnvelope=backpack,HeadEnvelope=head)
    gait_hits=[]
    for i in range(25):
        phase=i/25
        angles=ns["trot_angles"](phase)
        for label,s,leg,chain in moving:
            t=App.Placement()
            spec=ns["LEGS"][leg]
            for joint in chain:
                j=("Hip","Knee","Ankle").index(joint)
                t=t.multiply(rotation(spec["pivots"][j],spec["axes"][j],angles[leg][j]))
            moved=s.copy()
            moved.Placement=t.multiply(s.Placement)
            for cid,shape in gait_keepouts.items():
                volume=overlap(moved,shape)
                if volume>0.001:gait_hits.append([round(phase,3),label,cid,round(volume,4)])
    head_hits=[]
    head_min_gap=float("inf")
    # Volume envelopes deliberately overestimate rounded shell occupancy.
    for yaw in range(-45,46,5):
        for pitch in range(-25,26,5):
            t=rotation(data["camera"]["pan_pivot"],(0,0,1),yaw).multiply(
                rotation(data["camera"]["tilt_pivot"],data["camera"]["tilt_axis"],pitch))
            moved=head.copy()
            moved.Placement=t.multiply(head.Placement)
            volume=overlap(moved,backpack)
            if volume>0.001:head_hits.append([yaw,pitch,round(volume,4)])
            head_min_gap=min(head_min_gap,moved.distToShape(backpack)[0])
    # Exact free volume inside a generous original central bounding box.
    # This is an UPPER bound: includes assembly access and unused crevices.
    free=Part.makeBox(212,100.4558,37.02,App.Vector(-85,-50.2279,0))
    for o,s in original:
        if overlap(free,s)>0.001:free=free.cut(s)
    onboard=[c for c in data["components"] if c["zone"] in ("lower","upper")]
    result=dict(coordinate_frame=data["coordinate_frame"],
                component_count=len(comp),neutral_hits=source_hits,component_pair_hits=pairs,
                manifest_mismatch=manifest_mismatch,
                gait_phases=25,moving_shapes=len(moving),gait_hits=gait_hits,
                head_samples=19*11,head_hits=head_hits,head_min_gap_mm=round(head_min_gap,4),
                original_central_free_volume_upper_bound_l=round(free.Volume/1e6,5),
                lower_upper_reserved_volume_l=round(sum(math.prod(c["size"]) for c in onboard)/1e6,5),
                study_limits=["Boxes include assumed service/connector margins, not measured bought assemblies.",
                              "25 discrete existing-preview gait phases; not continuous or full servo range certification.",
                              "Head outer envelope vs backpack at 209 samples; neck bracket and internal head mechanism not designed.",
                              "No strength, thermal, current, mass, torque, cable fatigue, or print validation."])
    (OUT/"validation.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result))
    return result


def show_layer(doc,mode="all"):
    data,objects=layout_inputs(doc)
    for c in data["components"]:
        visible=(mode=="all" or c["zone"]==mode or
                 (mode=="head" and c["zone"]=="neck"))
        objects[c["id"]].ViewObject.Visibility=visible
    doc.getObject("CameraFOV").ViewObject.Visibility=mode=="head"
    doc.getObject("CameraMountPattern").ViewObject.Visibility=mode=="head"
    doc.getObject("Backpack_envelope___NOT_a_printable_shell").ViewObject.Visibility=mode in ("all","upper")
    doc.getObject("Head_envelope___NOT_a_printable_shell").ViewObject.Visibility=mode in ("all","head")
    doc.getObject("StudyMountingAxes").ViewObject.Visibility=mode in ("all","lower")


if __name__ == "__main__":
    inspect(App.ActiveDocument)
