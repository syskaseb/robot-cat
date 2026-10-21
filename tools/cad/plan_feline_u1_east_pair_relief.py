"""Same U1 bare-pad seams, two east-directed insulated arcs, full clamp."""
import FreeCAD as A
import Part


def construct(parts):
    names = ['U1Five:XP02.module:jacket', 'U1Five:XP03.module:jacket',
             'U1Relief:RearRoot', 'U1Relief:E2pair:band', 'U1Relief:E2pair:head']
    mirror = A.Matrix()
    mirror.A11, mirror.A14 = -1., 152.7
    changed = {n: parts[n].copy() for n in names}
    for n, shape in changed.items():
        shape.transformShape(mirror, True)
        old = parts[n].BoundBox
        assert shape.isValid() and abs(shape.Volume-parts[n].Volume) < 1e-5
        assert abs(shape.BoundBox.XMin-(152.7-old.XMax)) < 1e-6
    stand = parts['U1Relief:Stand1']
    bores = [f.Surface for f in stand.Faces if isinstance(f.Surface, Part.Cylinder)
             and abs(f.Surface.Radius-1.2) < 1e-7]
    assert len(bores) == 1
    bore = bores[0]
    assert (bore.Center-A.Vector(70, 91.6101, 27.78)).Length < 1e-6
    bridge = Part.makeBox(24.15, 2, 2, A.Vector(67.6, 89.7, 22.74))
    west = Part.makeBox(4.8, 2, 5, A.Vector(67.6, 89.7, 23.74))
    east = Part.makeBox(2, 2, 5, A.Vector(89.75, 89.7, 23.74))
    drill = Part.makeCylinder(bore.Radius, 4, A.Vector(70, 92.7, 27.78), bore.Axis)
    root = changed['U1Relief:RearRoot'].fuse(bridge).fuse(west).fuse(east).cut(drill)
    joint = root.common(stand).Volume
    assert root.isValid() and len(root.Solids) == 1 and joint > 0
    changed['U1Relief:RearRoot'] = root
    return changed, dict(
        same_named_bare_pads_and_other12_interfaces=True,
        reflection_plane_world_X_mm=76.35,
        same_complete_nylon_stock_envelopes=True,
        mirrored_rectangular_stock_envelope_NOT_manufactured_mirrored_ratchet=True,
        existing_Stand1_bore_radius_mm=bore.Radius,
        named_integral_Stand1_root_joint_mm3=joint,
        printed_bridge_and_posts_provisional_not_strength_qualification=True,
        native_master_changed=False, N01_complete=False, physical_pass=False)
