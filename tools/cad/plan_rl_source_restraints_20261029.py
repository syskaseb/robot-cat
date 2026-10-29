"""Source-owned replaceable RL saddles in the current N01 planning assembly.

Standard editable Part primitives/cuts/extrusions/sweeps; no purchased part
changes. Source surfaces are pinned copies from the current neutral geometry.
Project nominal jacket dimensions require delivered-cable fit/pull checks.
"""
import math
import FreeCAD as A
import Part
import Sketcher
import numpy as np


def save_tip_visibility(path, visible_names):
    """Headless-save display metadata: show the six tips, not cutting tools.

    Only GuiDocument.xml is supplied. Native feature data and BReps stay byte
    identical; no external display-data files or fabricated geometry are used.
    Call after the final native save (a later headless save drops GUI metadata).
    """
    import zipfile
    import xml.etree.ElementTree as ET
    from pathlib import Path
    path = Path(path)
    with zipfile.ZipFile(path) as source:
        entries = {n: source.read(n) for n in source.namelist()}
    objects = ET.fromstring(entries['Document.xml']).find('ObjectData')
    names = [o.attrib['name'] for o in objects]
    assert set(visible_names) <= set(names)
    root = ET.Element('Document', SchemaVersion='1', HasExpansion='1')
    ET.SubElement(root, 'Expand')
    providers = ET.SubElement(root, 'ViewProviderData', Count=str(len(names)))
    for name in names:
        view = ET.SubElement(providers, 'ViewProvider', name=name, expanded='0', treeRank='-1')
        props = ET.SubElement(view, 'Properties', Count='1', TransientCount='0')
        prop = ET.SubElement(props, 'Property', name='Visibility', type='App::PropertyBool', status='1')
        ET.SubElement(prop, 'Bool', value='true' if name in visible_names else 'false')
    entries['GuiDocument.xml'] = ET.tostring(root, encoding='utf-8', xml_declaration=True)
    temporary = path.with_suffix('.display.FCStd')
    with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_DEFLATED) as target:
        for name, data in entries.items():
            target.writestr(name, data)
    temporary.replace(path)
    return len(names)


def pose(E, F, U, point):
    m = A.Matrix()
    q = np.column_stack([E, F, U])
    for i in range(3):
        for j in range(3):
            setattr(m, 'A%d%d' % (i+1, j+1), float(q[i, j]))
        setattr(m, 'A%d4' % (i+1), float(point[i]))
    return A.Placement(m)


def build_forked_roots(doc, outputs, clamps):
    """Open belt passages by structural forks, not tiny cut grooves.

    Two feet straddle each case belt; terminal pairs straddle the cap bands.
    Wire lands, source orientation, curved guide and purchased cases stay put.
    New material requires changed-neighbour checks; old cylindrical clearance
    is not silently inherited for the changed supports.
    """
    made = []
    def rod(name, a, b, factor=1.):
        a, b = np.array(a), np.array(b)
        obj = doc.addObject('Part::Cylinder', 'RL29Fork'+name)
        obj.setExpression('Radius', 'RL29Parameters.RodRadius*'+str(factor))
        obj.Height = float(np.linalg.norm(b-a))
        obj.Placement = A.Placement(A.Vector(*a), A.Rotation(A.Vector(0,0,1), A.Vector(*(b-a))))
        made.append(obj)
        return obj
    def terminal_pair(name, start, c, target_f):
        centre = (np.array(c['start'])+c['end'])/2
        E,F,U = map(np.array, [c['E'],c['F'],c['U']])
        junction=centre+(18. if target_f>0 else -18.)*F
        rod(name+'Stem',start,junction)
        for i, sign in enumerate((-1,1)):
            rod(name+str(i), junction, centre+target_f*F+sign*4.*U, .5)
    result = dict(outputs)
    for owner, actor, axis in [('Hip','RL29HipLeg0',[1.,0,0]),('Knee','RL29Knee2Leg0',[0,.9902680687415703,-.13917310096006663])]:
        made.clear()
        base = np.array(list(doc.getObject(actor).Placement.Base))
        normal = np.array(list(doc.getObject('RL29'+owner+'Seat').Dir))
        axis = np.array(axis)
        pads=[]
        if owner=='Knee':
            # The belt and symmetric feet share the actual pad datum. Source-face lobes support both complete footprints.
            for i,sign in enumerate((-1,1)):
                point=base+sign*4*axis-1.5*normal
                window=doc.addObject('Part::Cylinder','RL29ForkKneePadWindow'+str(i))
                window.Radius,window.Height=2.2,6.
                window.Placement=A.Placement(A.Vector(*(point-3*normal)),A.Rotation(A.Vector(0,0,1),A.Vector(*normal)))
                patch=doc.addObject('Part::Common','RL29ForkKneePadPatch'+str(i))
                patch.Base,patch.Tool=doc.getObject('RL29KneeSourceFace'),window
                pad=doc.addObject('Part::Extrusion','RL29ForkKneePad'+str(i))
                pad.Base,pad.Dir,pad.Solid,pad.LengthFwd=patch,A.Vector(*normal),True,3.
                doc.recompute()
                assert patch.Shape.Area>12.,patch.Shape.Area
                pads.append(pad)
        top = base+12*normal
        for i,sign in enumerate((-1,1)):
            foot = base+sign*4*axis
            rod(owner+'Foot'+str(i),foot,foot+12*normal,.5)
        node = doc.addObject('Part::Box','RL29Fork'+owner+'Crossbar')
        e=normal/np.linalg.norm(normal);f=np.cross(axis,e)
        node.setExpression('Length','2*RL29Parameters.RodRadius')
        node.setExpression('Width','2*RL29Parameters.RodRadius')
        node.Height=8.
        node.Placement=pose(e,f,axis,top-3*e-3*f-4*axis)
        for i,k in enumerate('xyz'):
            node.setExpression('Placement.Base.'+k,str(float(top[i]-4*axis[i]))+' mm - '+str(float(e[i]+f[i]))+'*RL29Parameters.RodRadius')
        made.append(node)
        if owner=='Hip':
            rod('HipUpperMain',top,[160,60,45])
            terminal_pair('HipCapArm',[160,60,45],clamps['RL1'],4.)
            rod('HipGuideMain',top,[144,62,45])
            rod('HipGuideUpright',[144,62,45],[144,62,64])
            u=np.array([-2**-.5,2**-.5,0]);f=np.array([-.5,-.5,-2**-.5]);centre=np.array([151.24385796,84.6862915,71.])
            rod('HipGuideStem',[144,62,64],centre+18*f)
            for i,sign in enumerate((-1,1)):
                rod('HipGuideArm'+str(i),centre+18*f,centre+3.3*f+sign*4.*u,.5)
            fixed=[doc.getObject(n) for n in ['RL29HipSeat','RL29HipSourceBed','RL29GuideBed']]
        else:
            rod('Knee2Main',top,[163,100,28]);terminal_pair('Knee2CapArm',[163,100,28],clamps['RL2'],-4.)
            rod('Knee3Main',top,[180,112,28]);terminal_pair('Knee3CapArm',[180,112,28],clamps['RL3'],-4.)
            fixed=[doc.getObject(n) for n in ['RL29KneeSeat','RL29Knee2SourceBed','RL29Knee3SourceBed']]
        fuse = doc.addObject('Part::MultiFuse','RL29'+owner+'ForkedMembers')
        fuse.Shapes, fuse.Refine = fixed[:1]+list(made)+fixed[1:]+pads, False
        doc.recompute()
        fuse.Shape.check(True)
        assert fuse.Shape.isValid() and len(fuse.Shape.Solids)==1,owner
        assert fuse.Shape.Volume>=max(o.Shape.Volume for o in fuse.Shapes)-1e-6,owner
        for member in fuse.Shapes:
            assert member.Shape.cut(fuse.Shape).Volume<1e-5,(owner,member.Name,'union omitted member')
        # Normal feet remove the former slanted-strut/case penetration.
        # Do not Boolean-cut an already disjoint case; require a real zero-
        # volume intersection instead of accepting a failed/null Cut result.
        case = doc.getObject('RL29'+owner+'CaseFitTool').Shape
        assert fuse.Shape.common(case).Volume < 1e-6,owner
        fuse.addProperty('App::PropertyString','MotionOwner').MotionOwner=owner
        fuse.addProperty('App::PropertyString','Scope').Scope='Open belt-pass structural fork; native candidate, delivered fit/pull gate'
        result[owner+'Root']=fuse
    return result


def build(doc, rest, knee_parts, source1_parts):
    made = []
    params = doc.addObject('App::FeaturePython', 'RL29Parameters')
    for name, value in [('RodRadius', 3.), ('SeatThickness', 3.),
                        ('NominalJacketRadius', 1.55), ('NominalVJacketRadius', 1.), ('CorePitch', 3.6),
                        ('GuideRadius', 16.)]:
        params.addProperty('App::PropertyLength', name, 'N01 dimensions')
        setattr(params, name, value)
    params.addProperty('App::PropertyString', 'Status').Status = (
        'N01 constructive study; delivered cable OD/connector/fit/pull unverified')

    def add(kind, name):
        obj = doc.addObject(kind, 'RL29'+name)
        made.append(obj)
        return obj

    def box(name, size, point, E=(1, 0, 0), F=(0, 1, 0), U=(0, 0, 1)):
        obj = add('Part::Box', name)
        obj.Length, obj.Width, obj.Height = map(float, size)
        obj.Placement = pose(E, F, U, point)
        return obj

    def fuse(name, items):
        obj = add('Part::MultiFuse', name)
        obj.Shapes = items
        obj.Refine = True
        return obj

    def cut(name, base, tool):
        obj = add('Part::Cut', name)
        obj.Base, obj.Tool = base, tool
        obj.Refine = True
        return obj

    def rod(name, a, b):
        a, b = np.array(a), np.array(b)
        obj = add('Part::Cylinder', name)
        obj.setExpression('Radius', 'RL29Parameters.RodRadius')
        obj.Height = float(np.linalg.norm(b-a))
        obj.Placement = A.Placement(A.Vector(*a), A.Rotation(A.Vector(0, 0, 1), A.Vector(*(b-a))))
        return obj

    def seat(name, actor, face_index, crop):
        face = rest[actor].Faces[face_index].copy()
        source = add('Part::Feature', name+'SourceFace')
        source.Shape = face
        source.addProperty('App::PropertyString', 'SourceActor').SourceActor = actor
        source.addProperty('App::PropertyInteger', 'SourceFaceIndex').SourceFaceIndex = face_index+1
        lo, hi = map(np.array, crop)
        window = box(name+'Crop', hi-lo, lo)
        patch = add('Part::Common', name+'Patch')
        patch.Base, patch.Tool = source, window
        doc.recompute()
        assert patch.Shape.Area > 20, (name, patch.Shape.Area)
        f = face
        normal = np.array(list(f.normalAt(sum(f.ParameterRange[:2])/2, sum(f.ParameterRange[2:])/2)))
        extr = add('Part::Extrusion', name+'Seat')
        extr.Base, extr.Dir, extr.Solid = patch, A.Vector(*normal), True
        extr.LengthFwd = 3.
        extr.setExpression('LengthFwd', 'RL29Parameters.SeatThickness')
        doc.recompute()
        assert extr.Shape.Volume > 20, (name, extr.Shape.Volume)
        centre = sum((np.array(list(f.CenterOfMass))*f.Area for f in patch.Shape.Faces),
                     np.zeros(3))/patch.Shape.Area
        return extr, centre+normal*1.5

    def clamp(name, part, major):
        p, end = np.array(part['start']), np.array(part['end'])
        U = end-p
        U /= np.linalg.norm(U)
        E = np.array(major)
        E -= np.dot(E, U)*U
        E /= np.linalg.norm(E)
        F = np.cross(U, E)
        case_facing = 1. if name=='HipSource' else -1.
        bed = box(name+'BedBlank', (15.3, 5.5, 9), p-7.65*E+(0. if case_facing>0 else -5.5)*F, E, F, U)
        cap = box(name+'CapBlank', (15.3, 4.05, 9), p-7.65*E+(-4.05 if case_facing>0 else 0.)*F, E, F, U)
        grooves = []
        for i, offset in enumerate([-3.6, 0., 3.6]):
            cyl = add('Part::Cylinder', name+'Jacket%d' % i)
            cyl.setExpression('Radius', 'RL29Parameters.'+('NominalVJacketRadius' if i == 1 else 'NominalJacketRadius'))
            cyl.Height = 9.2
            cyl.Placement = A.Placement(A.Vector(*(p+offset*E-.1*U)), A.Rotation(A.Vector(0, 0, 1), A.Vector(*U)))
            grooves.append(cyl)
        holes = fuse(name+'NominalJackets', grooves)
        bed, cap = cut(name+'Bed', bed, holes), cut(name+'Cap', cap, holes)
        return bed, cap, (p+end)/2+case_facing*7*F, dict(start=p.tolist(), end=end.tolist(), E=E.tolist(), F=F.tolist(), U=U.tolist(),
            nominal_project_radii_mm=[1.55,1.,1.55], delivered_OD_unknown=True, replaceable_insert_and_pull_gate=True,
            actual_source_strain_relief=True, independent_three_jacket_contact_not_three_separate_grips=True)

    # Actual external case panels, not electronic pads or purchased holes.
    hip_actor = 'Ref_Material_P0_Part__Feature022_0_0'
    knee_actor = 'Ref_Material_P0_Part__Feature064_0_0'
    hip_seat, hp = seat('Hip', hip_actor, 2, ([140, 16, 25], [151, 35, 36]))
    ks = rest[knee_actor]
    kface = max((i for i, f in enumerate(ks.Faces) if isinstance(f.Surface, Part.Plane)
                 and f.normalAt(0, 0).x > .7 and f.normalAt(0, 0).z > .6), key=lambda i: ks.Faces[i].Area)
    knee_seat, kp = seat('Knee', knee_actor, kface, ([150, 70, 5], [180, 80, 18]))

    hip_bed, hip_cap, ht, hmeta = clamp('HipSource', source1_parts[-1], [0, 2**-.5, -2**-.5])
    k2bed, k2cap, k2t, k2meta = clamp('Knee2Source', knee_parts['RL2'][-1], [1., 0, 0])
    k3bed, k3cap, k3t, k3meta = clamp('Knee3Source', knee_parts['RL3'][-1], [1., 0, 0])

    # Source1 S guide: two opposite45degree turns. Both native circles and
    # sweep profiles remain editable. It constrains the flat transverse order,
    # not an additional axially fixed cable seam.
    start = np.array(source1_parts[-1]['end'])
    c1 = start+np.array([0, 16, 0])
    c2 = start+np.array([-16*2**.5, 16*(1-2**.5), 0])
    arcs = []
    for i, (centre, radial, tangent) in enumerate([
            (c1, [0, -1, 0], [-1, 0, 0]),
            (c2, [2**-.5, 2**-.5, 0], [-2**-.5, 2**-.5, 0])]):
        circ = add('Part::Circle', 'GuideArc%d' % i)
        circ.setExpression('Radius', 'RL29Parameters.GuideRadius')
        circ.Angle1, circ.Angle2 = 0., 45.
        circ.Placement = pose(radial, tangent, np.cross(radial, tangent), centre)
        if i == 0:
            circ.setExpression('Placement.Base.y', str(float(start[1]))+' mm + RL29Parameters.GuideRadius')
        else:
            circ.setExpression('Placement.Base.x', str(float(start[0]))+' mm - sqrt(2)*RL29Parameters.GuideRadius')
            circ.setExpression('Placement.Base.y', str(float(start[1]))+' mm + (1-sqrt(2))*RL29Parameters.GuideRadius')
        arcs.append(circ)
    spine = add('Part::Compound', 'GuideSpine')
    spine.Links = arcs

    def sweep(name, radius):
        sketch = add('Sketcher::SketchObject', name+'Profile')
        d, r = 3.6, radius
        V = lambda x, y: A.Vector(x, y, 0)
        sketch.addGeometry([Part.LineSegment(V(-d, r), V(d, r)),
            Part.Arc(V(d, r), V(d+r, 0), V(d, -r)),
            Part.LineSegment(V(d, -r), V(-d, -r)),
            Part.Arc(V(-d, -r), V(-d-r, 0), V(-d, r))], False)
        sketch.Placement = pose([0, 2**-.5, -2**-.5], [0, 2**-.5, 2**-.5], [-1, 0, 0], start)
        obj = add('Part::Sweep', name)
        obj.Sections, obj.Spine, obj.Solid, obj.Frenet = [sketch], (spine, ['Edge1', 'Edge2']), True, False
        return obj

    outer, inner = sweep('GuideOuter', 4.05), sweep('GuideChannel', 1.9)
    tube = cut('GuideSplitTube', outer, inner)
    lower = box('GuideLowerHalf', (90, 80, 31), [110, 45, 40])
    upper = box('GuideUpperHalf', (90, 80, 40), [110, 45, 71])
    guide_bed, guide_cap = add('Part::Common', 'GuideBed'), add('Part::Common', 'GuideCap')
    guide_bed.Base, guide_bed.Tool = tube, lower
    guide_cap.Base, guide_cap.Tool = tube, upper

    hip_rods = [rod('HipLeg0', hp, [160, 60, 45]), rod('HipLeg1', [160, 60, 45], ht),
                rod('HipBranch0', hp, [144, 62, 45]), rod('HipBranch1', [144, 62, 45], [144, 62, 64]),
                rod('HipBranch2', [144, 62, 64], [148, 85, 65])]
    knee_rods = [rod('Knee2Leg0', kp, [163, 100, 28]), rod('Knee2Leg1', [163, 100, 28], k2t),
                 rod('Knee3Leg0', kp, [180, 112, 28]), rod('Knee3Leg1', [180, 112, 28], k3t)]
    hip_root = fuse('HipRootAndBed', [hip_seat, hip_bed, guide_bed]+hip_rods)
    knee_root = fuse('KneeRootAndBeds', [knee_seat, k2bed, k3bed]+knee_rods)
    # Form-fit relief is cut ONLY in our printed foot, never in the servo.
    # It removes the tiny round-strut penetration below the bearing plane;
    # the broad source-derived seating face and the structural pad remain.
    def case_relief(name, root, actor):
        tool = add('Part::Feature', name+'CaseFitTool')
        tool.Shape = rest[actor].copy()
        tool.addProperty('App::PropertyString', 'SourceActor').SourceActor = actor
        return cut(name+'CaseRelievedRoot', root, tool)
    hip_root = case_relief('Hip', hip_root, hip_actor)
    knee_root = case_relief('Knee', knee_root, knee_actor)
    doc.recompute()
    outputs = {'HipRoot': hip_root, 'HipSourceCap': hip_cap, 'HipGuideCap': guide_cap,
               'KneeRoot': knee_root, 'Knee2Cap': k2cap, 'Knee3Cap': k3cap}
    for name, obj in outputs.items():
        obj.addProperty('App::PropertyString', 'MotionOwner').MotionOwner = 'Hip' if name.startswith('Hip') else 'Knee'
        obj.addProperty('App::PropertyString', 'Scope').Scope = 'N01 source restraint candidate; not selected master or physicalPASS'
    return outputs, dict(parameters=params.Name, features=[o.Name for o in made],
        source_panels={'Hip': hip_actor+'/Face3', 'Knee': knee_actor+'/Face'+str(kface+1)},
        clamps={'RL1': hmeta, 'RL2': k2meta, 'RL3': k3meta},
        attachment='Broad external mechanical case saddles + one double-T18I145 belt per parent; no electronics-pad pressure or purchased-hole change.',
        stock=dict(sku='111-02370 T18I145', parent_belt_chains=2, ties_per_chain=2,
                   source_cap_ties=3, guide_cap_ties=1, installed_ties=8,
                   two_complete_heads_and_two25mm_lock_tails_per_parent_chain=True),
        full_band_and_head_geometry_received=False, physical_pass=False)
