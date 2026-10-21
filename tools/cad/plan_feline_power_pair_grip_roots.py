"""Root both unfused input grips together, with their full existing bands.

Their actual pad faces are horizontal; measure AWAY from their own wire,
then go round the whole WAGO back at Y<=-51. No bought case changes.
"""
import FreeCAD as A
import Part


def isolated(shape):
    """Private BRep topology; Booleans must not contaminate pinned parents."""
    assert shape.isValid() and shape.Solids
    result=Part.Shape();result.importBrepFromString(shape.exportBrepToString())
    assert result.isValid() and result.Solids
    return result


def construct(scene):
    actors={};joints={}
    for wire in ('XA01','XP01'):
        pad=isolated(scene['PowerFan:grip:'+wire+':pad'])
        ownwire=isolated(scene['PowerFan:wire:'+wire])
        faces=[f for f in pad.Faces if type(f.Surface).__name__=='Plane'
               and abs(f.normalAt(0,0).z)>.9999]
        distances=[(f.distToShape(ownwire)[0],f.Area,f) for f in faces]
        _,_,chosen=max(distances,key=lambda r:(round(r[0],6),r[1]))
        sign=1 if chosen.CenterOfMass.z>pad.Solids[0].CenterOfMass.z else -1
        assert sign==(1 if wire=='XA01' else -1)
        level=chosen.CenterOfMass.z+(1 if sign>0 else -3)
        face=chosen.copy();face.translate(A.Vector(0,0,-sign*.5))
        foot=face.extrude(A.Vector(0,0,sign*3.5))
        b=scene['PowerFan:grip:'+wire+':band'].BoundBox
        foot=foot.cut(Part.makeBox(b.XLength+.4,b.YLength+.4,b.ZLength+.4,
                                 A.Vector(b.XMin-.2,b.YMin-.2,b.ZMin-.2)))
        return_z=min(level,98.) # overlap the existing rear backer's98.5 roof
        beams=[
            Part.makeBox(4,10,2,A.Vector(134,-53,level)),
            Part.makeBox(31.5,2,2,A.Vector(134,-53,level)),
            Part.makeBox(2,4.281,level+2-return_z,A.Vector(163.5,-53,return_z))]
        extra=foot.multiFuse(beams)
        # Include the whole HEAD as well as the band in the same channel;
        # both selected nylon envelopes remain exactly as received.
        for suffix in ('band','head'):
            b=scene['PowerFan:grip:'+wire+':'+suffix].BoundBox
            extra=extra.cut(Part.makeBox(b.XLength+.4,b.YLength+.4,b.ZLength+.4,
                                        A.Vector(b.XMin-.2,b.YMin-.2,b.ZMin-.2)))
        # A conservative full-band channel can split off an unnecessary
        # sliver of ADDED foot. Keep only the component reaching the frame;
        # the original full9 pad, wire and nylon remain entirely unchanged.
        connected=[s for s in extra.Solids if s.common(beams[-1]).Volume>1]
        assert len(connected)==1
        root=connected[0]
        if wire=='XA01':
            # Preserve the whole AUX escape. A clearance channel in this
            # NEW printed bridge replaces another scalar placement retry.
            core=Part.makeBox(31.5,1.5,1.2,A.Vector(134,-52.75,99.3))
            assert core.cut(root).Volume<1e-6
            cutter=isolated(scene['AuxEscape:XA04']).makeOffsetShape(1.25,1e-6)
            assert cutter.isValid() and len(cutter.Solids)==1
            root=root.cut(cutter)
            assert root.isValid() and len(root.Solids)==1
            assert core.cut(root).Volume<1e-6
        assert root.isValid() and len(root.Solids)==1,wire
        values={n:root.copy().common(isolated(scene[n])).Volume for n in
                ('PowerFan:grip:'+wire+':pad','PowerMount:P_REAR:PETG')}
        assert all(v>0 for v in values.values()),(wire,values)
        actors['PowerGripRoot:'+wire]=root;joints[wire]=values
    return actors,dict(status='TWO_UNFUSED_GRIP_ROOTS_PROPOSAL_NOT_RECEIVED',
        wire_grips_and_factory_boundaries_unchanged=True,
        named_integral_joints_mm3=joints,whole_WAGO_avoided_on_its_back=True,
        adhesive_case_retention_NOT_wire_strain_relief=True,
        other_two_grip_roots_and_whole_N01_OPEN=True,N01_complete=False,physical_pass=False)


def construct_tails(scene):
    """Two printed braces around the WHOLE cases; no wire routing changes."""
    actors={};plans={}
    for wire,caseid in [('XP02','F_PWM'),('XA02','F_AUX')]:
        pad=isolated(scene['PowerFan:grip:'+wire+':pad']);case=isolated(scene['PowerFan:'+caseid+':case'])
        lead=isolated(scene['PowerFan:'+caseid+':out9']);head=isolated(scene['PowerFan:grip:'+wire+':head'])
        candidates=[]
        for v in pad.Vertexes:
            distances=[v.distToShape(s)[0] for s in (case,lead,head)]
            if min(distances)>=1.7:candidates.append((distances[0],distances[1],v.Point))
        assert candidates,wire
        start=max(candidates,key=lambda r:(round(r[0],6),round(r[1],6)))[2]
        if wire=='XP02':
            centre=case.Solids[0].CenterOfMass
            caps=[f for f in case.Faces if type(f.Surface).__name__=='Plane']
            near=min(caps,key=lambda f:f.distToShape(pad)[0])
            into=centre-near.CenterOfMass;into.normalize()
            side=A.Vector(-into.y,into.x,0)
            # Use the other axial side of the whole central band: this also
            # stays south of the complete retained RR cuff and its head.
            frame=centre-into*4+side*6+A.Vector(0,0,-1.5)
            outside=centre-into*4+side*9+A.Vector(0,0,-1.5)
            # Outside the WHOLE output head (XMin96.507), then north of
            # YMax-83.153; remain outside the circular case and its full
            # central band, only returning radially at axis-4.
            points=[start,A.Vector(94,start.y,start.z),A.Vector(94,-81,start.z),outside,frame]
            parent='PowerMount:F_PWM:PETG'
        else:
            # Directly skirt the actual 90deg case corner at its side. The
            # former roof loop intruded into the full Pi USB boot budget.
            frame=A.Vector(92.5,0,94)
            points=[start,frame]
            parent='PowerMount:F_AUX:PETG'
        pieces=[]
        for a,b in zip(points,points[1:]):
            delta=b-a;length=delta.Length;delta.normalize()
            pieces.append(Part.makeCylinder(1.5,length+2,a-delta,delta))
        root=pieces[0].multiFuse(pieces[1:])
        assert root.isValid() and len(root.Solids)==1
        if wire=='XP02':
            # Permanent material must leave the WHOLE retained ATO service
            # tool its1.25 reserve. Keep an entire R1.4 brace core, not a
            # severed/notched-looking ligament declared strong by volume.
            corepieces=[]
            for a,b in zip(points,points[1:]):
                delta=b-a;length=delta.Length;delta.normalize()
                corepieces.append(Part.makeCylinder(1.4,length+2,a-delta,delta))
            core=corepieces[0].multiFuse(corepieces[1:])
            tool=isolated(scene['Service:Ref_Material_F_R6_CP2_ATO_0_0:tool_budget']).makeOffsetShape(1.25,1e-6)
            assert tool.isValid() and tool.Solids
            root=root.cut(tool)
            assert root.isValid() and len(root.Solids)==1 and core.cut(root).Volume<1e-5
        joints={n:root.copy().common(isolated(scene[n])).Volume for n in
                ('PowerFan:grip:'+wire+':pad',parent)}
        assert all(v>0 for v in joints.values()),(wire,joints)
        whole=isolated(root).multiFuse([isolated(pad),isolated(scene[parent])])
        assert whole.isValid() and len(whole.Solids)==1
        actors['PowerGripRoot:'+wire]=root
        plans[wire]=dict(brace_points_mm=[list(p) for p in points],printed_brace_radius_mm=1.5,
                         actual_anchor_vertex_case_lead_head_clearance_mm=1.7,
                         named_integral_joints_mm3=joints)
    return actors,dict(status='TWO_OUTPUT_GRIP_BRACES_PROPOSAL_NOT_RECEIVED',
        recipes=plans,printed_braces_NOT_wire_centrelines=True,
        full_existing_grips_bends_wires_heads_and_cases_unchanged=True,
        whole_N01_OPEN=True,N01_complete=False,physical_pass=False)
