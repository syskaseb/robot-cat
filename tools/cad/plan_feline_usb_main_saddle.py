"""N01: retain USB on its straight main run, allowing release downward.

This replaces the removable near-plug arm/pad/sleeve proposal. The received
452mm cable and side-bow family stay unchanged. Native integration is N03;
printed strength, clamp fit and tool budgets are provisional, not hardware PASS.
"""
import math


def build():
    import FreeCAD as A
    import Part

    x, y, z = 56.5, 91.85810963471377, 89.
    origin, axis = A.Vector(x, y, z), A.Vector(1, 0, 0)
    def tube(radius, length=9):
        return Part.makeCylinder(radius, length, origin, axis)
    # Constant2mm roof wall over a60degree sector; not a thinner sidewall.
    # The broad180degree roof's tie failed the3.25mm outer-skin allowance.
    points = [A.Vector(x,y,z), A.Vector(x,y-20,z+20*math.sqrt(3)),
              A.Vector(x,y+20,z+20*math.sqrt(3)), A.Vector(x,y,z)]
    wedge = Part.Face(Part.makePolygon(points)).extrude(A.Vector(9,0,0))
    expanded = wedge.copy()
    expanded.translate(A.Vector(0,0,-2.4))  # 1.2mm normal nylon budget
    pad = tube(4.65).cut(tube(2.65)).common(wedge)
    post = Part.makeCylinder(2,40,A.Vector(61,79,54))
    bridge = Part.makeBox(4,13.5,3,A.Vector(59,79,92.7))
    body = pad.fuse(bridge).fuse(post)
    band = tube(5.85,2.5).common(expanded).fuse(tube(3.85,2.5)).cut(
        tube(4.65,2.5).common(wedge).fuse(tube(2.65,2.5)))
    head = Part.makeBox(5,4.3,5.3,A.Vector(55.25,y-8.15,86.35))
    parts = {'body':body,'band':band,'head':head}
    for shape in parts.values():
        shape.check(True)
        assert shape.isValid() and len(shape.Solids)==1
    # Planning access reservations, NOT a measured manufacturer tool.
    access = {
        'cutting_tip':Part.makeBox(6,5,20,A.Vector(49.75,y-8.15,89)),
        'grip':Part.makeBox(12,19,30,A.Vector(46.75,y-15.15,109)),
    }
    return parts, access, {
        'status':'CONSTRUCTIVE_PLANNING_NOT_NATIVE',
        'grip_length_mm':9, 'groove_radius_mm':2.65, 'wall_mm':2,
        'roof_sector_degrees':60,
        'root_parent':'CurrentFoundation:BankBedCurrent:1',
        'old_near_plug_arm_pad_sleeve_and_ties_retired':True,
        'old_fixed_beam_retained':True,
        'W009_unplug_or_parking_required_by_this_restraint':False,
        'USB_length_and_side_bow_unchanged':True,
        'access_is_project_assumption':True,
        'N01_complete':False, 'physical_pass':False,
    }
