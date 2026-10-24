"""N01 candidate: remove the whole straight USB restraint before unplugging.

Reuses the received removable root sleeve and its two ties. The existing
452mm cable is unchanged. Geometry here is a proposal, not an approval.
"""
import FreeCAD as A
import Part


def build(sleeve):
    y, z = 28.85810963471377, 98.7
    axis = A.Vector(1, 0, 0)
    def tube(x, length, ro, ri):
        origin = A.Vector(x, y, z)
        return Part.makeCylinder(ro, length, origin, axis).cut(
            Part.makeCylinder(ri, length, origin, axis))
    upper = Part.makeBox(20, 20, 20, A.Vector(110, y-10, z))
    pad = tube(116, 9, 4.65, 2.65).common(upper)
    # Positive overlap with the roof and the received sleeve, not a floating
    # support. The post is entirely above the unchanged jacket.
    # The beam ends at X118.504. Put the post outside that retained beam,
    # joining the end of the sleeve instead of filling its clearance groove.
    post = Part.makeCylinder(1.5, 7, A.Vector(120.25, y, 102.6))
    body = sleeve.fuse(post).fuse(pad)
    # Same conforming upper-roof/lower-jacket construction as the received
    # curved restraint; a loose full-radius lower ring is not strain relief.
    outer_clip = Part.makeBox(20, 20, 21.2, A.Vector(110, y-10, z-1.2))
    origin = A.Vector(116, y, z)
    cylinder = lambda r: Part.makeCylinder(r, 2.5, origin, axis)
    band = cylinder(5.85).common(outer_clip).fuse(cylinder(3.85)).cut(
        cylinder(4.65).common(upper).fuse(cylinder(2.65)))
    # The negative-Y side is occupied by the BUS front rail/DC region.
    head = Part.makeBox(5, 4.3, 5.3, A.Vector(114.75, y+5.85, z-2.65))
    parts = dict(body=body, pad=pad, post=post, band_budget=band, head=head)
    for shape in parts.values():
        shape.check(True)
        assert shape.isValid() and len(shape.Solids) == 1
    return parts, dict(status='CANDIDATE_NOT_RECEIVED', grip_length_mm=9,
        cable_unchanged=True, jacket_radius_mm=2.5, groove_radius_mm=2.65,
        remove_jacket_and_root_ties_before_lift=True,
        existing_root_sleeve_reused=True, N01_complete=False,
        full_scene_motion_access_and_retention_open=True, physical_pass=False)
