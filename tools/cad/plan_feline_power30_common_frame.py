"""One N01 power frame on the existing real AUX support.

Nominal case-envelope adhesive lands are provisional delivery-fit interfaces,
not new manufacturer holes, lever clamping or verified adhesive load ratings.
All independent grip roots still have to join this same frame.
"""
import FreeCAD as A
import Part


def plane_at(shape,axis,position):
    found=[f for f in shape.Faces if type(f.Surface).__name__=='Plane'
           and abs(f.CenterOfMass[axis]-position)<1e-6
           and abs(f.normalAt(0,0)[axis])>.9999]
    assert len(found)==1,(axis,position,len(found))
    return found[0]


def construct(scene,construction_cells=None):
    actors={};joints={}
    root=scene['AuxGrip:CommonRoot']
    shelf_shapes={}
    for key in ('P_REAR','F_AUX'):
        case=scene['PowerFan:'+key+':case']
        if key=='P_REAR':
            face=plane_at(case,0,case.BoundBox.XMax);normal=A.Vector(1,0,0)
        else:
            sides=[f for f in case.Faces if type(f.Surface).__name__=='Plane'
                   and abs(f.Area-1122)<1e-5]
            assert len(sides)==2
            face=min(sides,key=lambda f:f.CenterOfMass.x)
            normal=face.normalAt(0,0)
        tape=face.extrude(normal*.5)
        lower=face.copy();lower.translate(normal*.5)
        shelf=lower.extrude(normal*2)
        actors['PowerMount:'+key+':4905']=tape
        shelf_shapes[key]=shelf
    # Both the old low AUX-root arm and the ceiling family are REJECTED.
    # Reach the actual carrier UNDER its PCB, preserving the selected M2
    # bore, then stay east of ALL AUX wires/grips (XMax157.439).
    # The old rectangular rear corner escaped the TRUE contour by8.044mm3.
    # Connect the two actual joints diagonally, not by widening the shell
    # or nudging the already-received power modules and all their wires.
    a=A.Vector(151.5,-74.5,49);b=A.Vector(164.5,-48.7196985092769,49)
    tangent=b-a;tangent.normalize();normal=A.Vector(-tangent.y,tangent.x,0)*2
    ring=Part.makePolygon([a+normal,b+normal,b-normal,a-normal,a+normal])
    foot=Part.Face(Part.Wire(ring.Edges)).extrude(A.Vector(0,0,2))
    centre2=scene['Ref_Material_AUX409222TopWasher_0_0'].BoundBox.Center
    foot=foot.cut(Part.makeCylinder(1.1,4,A.Vector(centre2.x,centre2.y,48)))
    rear_bits=[shelf_shapes['P_REAR'],foot,
        Part.makeBox(2,11,14,A.Vector(163.5,-49.7196985092769,49))]
    rear=rear_bits[0].multiFuse(rear_bits[1:])
    if construction_cells is not None:construction_cells['P_REAR']=rear_bits
    # This common corridor is BELOW every power fan, away from the existing
    # AUX bolt heads. Its one XP01-head bypass is derived from that WHOLE
    # head (X135.293..141.240,YMin-47.558), not a clipped reservation.
    # The whole retained FR6 housing is X77.5..92.5/Z55..83. A single
    # bridge goes OVER it, while its upright stays east of XMax+1.25.
    # Actual three-wire intersection with X70..96 has YMax-48.7214;
    # the bridge YMin-46.5 has >=2.22 clearance. The entire W065 head
    # startsX98.1118, hence the upright endsX96, not inside that head.
    low=Part.makeBox(40,4,2,A.Vector(94,-49.8,56.5)).multiFuse([
        Part.makeBox(12,4.7,2,A.Vector(133,-54,56.5)),
        Part.makeBox(22.5,4,2,A.Vector(143,-49.8,56.5)),
        Part.makeBox(2,2,30,A.Vector(94,-46.5,56.5)),
        Part.makeBox(26,2,2,A.Vector(70,-46.5,84.5)),
        Part.makeBox(2.5,5.3,2,A.Vector(70,-49.8,84.5)),
        Part.makeBox(2,2,8,A.Vector(119,-49.8,56.5)),
        Part.makeBox(2,11.3,2,A.Vector(119,-49.8,62.5))])
    # F_PWM is ACTUALLY a cylinder R3.2, not a box with a flat underside.
    # A central open saddle leaves both end caps and integral wires free.
    case=scene['PowerFan:F_PWM:case'];centre=case.Solids[0].CenterOfMass
    caps=[f for f in case.Faces if type(f.Surface).__name__=='Plane']
    assert len(caps)==2
    axis=caps[1].CenterOfMass-caps[0].CenterOfMass;axis.normalize()
    tf=A.Placement(centre,A.Rotation(A.Vector(1,0,0),axis))
    cradle=Part.makeCylinder(5.35,14,A.Vector(-7,0,0),A.Vector(1,0,0)).cut(
        Part.makeCylinder(3.35,16,A.Vector(-8,0,0),A.Vector(1,0,0)))
    cradle=cradle.common(Part.makeBox(20,20,10,A.Vector(-10,-10,-10)))
    band=Part.makeBox(2.5,13.1,11.1,A.Vector(-1.25,-6.55,-6.55)).cut(
        Part.makeBox(4,10.7,8.7,A.Vector(-2,-5.35,-5.35)))
    head=Part.makeBox(5.3,4.3,5,A.Vector(-2.65,-10.85,-1))
    for s in (cradle,band,head):s.Placement=tf*s.Placement
    assert band.fuse(head).isValid() and len(band.fuse(head).Solids)==1
    actors['PowerMount:F_PWM:Band']=band;actors['PowerMount:F_PWM:Head']=head
    foot=Part.makeBox(15.7,6,2,A.Vector(119,-68,61.3))
    b=band.BoundBox
    foot=foot.cut(Part.makeBox(b.XLength+.4,b.YLength+.4,b.ZLength+.4,
                             A.Vector(b.XMin-.2,b.YMin-.2,b.ZMin-.2)))
    # Existing AUX upright begins at63.71 here; the lower saddle alone
    # cannot reach it. This side riser stays beyond the WHOLE fuse XMax.
    fpwm=cradle.multiFuse([foot,Part.makeBox(2,2,4.41,A.Vector(134,-66,61.3))])
    faux=shelf_shapes['F_AUX'].multiFuse([low,
             # Below the case use the east side of the WHOLE RR cuff;
             # above its77.35 roof return toward the actual side plate.
             # YMin-40.5 is north of ALL three complete power fans.
             Part.makeBox(2,2,17,A.Vector(119,-40.5,62.5)),
             Part.makeBox(5,2,2,A.Vector(116,-40.5,79)),
             Part.makeBox(2,2,5,A.Vector(116,-40.5,79))])
    comb=scene['PowerFan:trunk:comb'];b=comb.BoundBox
    # The short tab enters only the already-clear back half of the existing
    # pad. The upright stays WHOLE left of the full fans, not between wires.
    tab=Part.makeBox(b.XMin+1-70,1,1,A.Vector(70,b.YMin,b.ZMax-.5))
    upright=Part.makeBox(2.5,2.479,b.ZMax+.5-56.5,A.Vector(70,-49.8,56.5))
    trunk=tab.multiFuse([upright,low])
    for key,shape in [('P_REAR',rear),('F_PWM',fpwm),('F_AUX',faux),('Trunk',trunk)]:
        assert shape.isValid() and len(shape.Solids)==1,key
        mate=scene['AuxInboard:Carrier'] if key=='P_REAR' else root if key=='F_PWM' else rear
        v=shape.common(mate).Volume
        assert v>0,(key,v)
        actors['PowerMount:'+key+':PETG']=shape
        joints[key]=v
    merged=root.multiFuse([scene['AuxInboard:Carrier'],*[s for n,s in actors.items() if n.endswith(':PETG')],comb])
    assert merged.isValid() and len(merged.Solids)==1
    envelope=[merged.BoundBox.XLength,merged.BoundBox.YLength,merged.BoundBox.ZLength]
    assert max(envelope)<250
    return actors,dict(status='POWER_COMMON_FRAME_PROPOSAL_NOT_RECEIVED',
        existing_frame_roots=['AuxInboard:Carrier','AuxGrip:CommonRoot'],root_joints_mm3=joints,
        whole_print_solids=1,whole_print_envelope_mm=envelope,
        three_trunk_grips_supported_together=True,
        four_other_independent_grip_roots_still_OPEN=True,
        adhesive_stock_4905_nominal_thickness_mm=.5,
        tape_on_nominal_case_back_or_underside_not_levers=True,
        supplier_real_flat_lands_and_adhesive_load_are_delivery_fit_gates=True,
        no_new_bought_parts_or_PCB_holes=True,
        N01_complete=False,physical_pass=False)
