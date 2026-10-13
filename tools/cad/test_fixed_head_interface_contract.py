"""Small exact-curve contracts; no candidate native files or safety claim."""
import unittest
import FreeCAD as A
import Part
from check_fixed_head_feed_interface import nonlocal_edge_pairs
from build_fixed_head_interface import band_boxes
from plan_fixed_head_feed_interface import strap
from fixed_head_land_profile import flat_land,flat_bend_prefix
from plan_current_data_ground_mounts import bearing_area

V=A.Vector

class InterfaceContracts(unittest.TestCase):
    def test_local_arc_profile_keeps_length_and_nominal_volume(self):
        arc=Part.Arc(V(0,0,0),V(31.5-31.5/2**.5,31.5/2**.5,0),V(31.5,31.5,0)).toShape()
        material,rest=flat_bend_prefix(arc)
        self.assertAlmostEqual(material.Volume,8*3.5*1.8,places=4)
        self.assertAlmostEqual(rest.Length+8,arc.Length,places=6)
        self.assertTrue(material.isValid())

    def test_flat_source_bears_on_nominal_bed_not_diagonal_circle(self):
        e=Part.makeLine(V(-176,47.2187454246,153.5),V(-176,56.2187454246,153.5))
        flat=flat_land(e)
        self.assertAlmostEqual(flat.BoundBox.ZMin,152.6)
        self.assertAlmostEqual(flat.BoundBox.ZMax,154.4)
        self.assertAlmostEqual(flat.Volume,56.7)
        bed=Part.makeBox(8,9,3,V(-180,47.2187454246,149.6))
        self.assertAlmostEqual(flat.common(bed).Volume,0)
        self.assertAlmostEqual(bearing_area(flat,bed,152.6),31.5)

    def test_short_connected_middle_does_not_fake_self_contact(self):
        es=[Part.makeLine(V(0,0,0),V(20,0,0)),
            Part.makeLine(V(20,0,0),V(21,0,0)),
            Part.makeLine(V(21,0,0),V(41,0,0))]
        pairs=list(nonlocal_edge_pairs(es,2))
        self.assertEqual(len(pairs),2)
        self.assertGreater(min(e.distToShape(f)[0] for _,e,_,f in pairs),4)

    def test_nonlocal_crossing_is_not_waived(self):
        es=[Part.makeLine(V(0,0,0),V(20,0,0)),
            Part.makeLine(V(20,0,0),V(20,20,0)),
            Part.makeLine(V(20,20,0),V(10,-10,0))]
        pairs=list(nonlocal_edge_pairs(es,2))
        self.assertEqual(len(pairs),1)
        self.assertLess(pairs[0][1].distToShape(pairs[0][3])[0],1e-6)

    def test_changed_native_band_recipe_matches_material(self):
        boxes=band_boxes(-198.6,-8.320513724211025)
        for n,yy,z,sx in [('XB23',68,51,-216),('XB22',78,48,-169),('XS23',88,45,-187)]:
            expected=strap(0,0,40,z+1.25,1.25)
            expected.rotate(V(),V(0,0,1),90);expected.translate(V(sx,yy,0))
            actual=None
            for row in boxes[n+'NorthBand']:
                import plan_current_head_wiring as H
                box=H.T.box(row);actual=box if actual is None else actual.fuse(box)
            self.assertLess(actual.cut(expected).Volume+expected.cut(actual).Volume,1e-6)

if __name__=='__main__':unittest.main()
