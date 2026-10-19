"""Nominal split-clamp geometry, not a pull test or layout acceptance."""
import math,unittest
import FreeCAD as A
import Part
from feline_gallery_tail_support import split_clamp,capsule_rail,keyed_foot


class SplitClampGeometry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.body,cls.kit,cls.slot=split_clamp([0,0,0],[1,0,0])

    def test_each_complete_print_and_full_selected_head(self):
        for s in [self.body,*self.kit.values()]:
            self.assertTrue(s.isValid());self.assertEqual(len(s.Solids),1)
        self.assertAlmostEqual(self.kit['head'].Volume,5*4.3*5.3,places=6)
        self.assertAlmostEqual(self.body.BoundBox.XLength,9,places=6)

    def test_preserves_jacket_and_nominal_insertion_clearance(self):
        jacket=Part.makeCylinder(1.55,9,A.Vector(),A.Vector(1,0,0))
        for s in (self.body,self.kit['cap'],self.kit['band'],self.kit['head']):
            self.assertLess(s.common(jacket).Volume,1e-5)
        self.assertGreaterEqual(4-1.85,2)
        self.assertGreaterEqual(4-1.7,2)
        self.assertGreaterEqual(4.2-1.7,2)

    def test_rounded_rail_preserves_real_holes(self):
        rail=Part.makeBox(34,6,3,A.Vector(-3,-3,2))
        for x in (0,28):rail=rail.cut(Part.makeCylinder(1.2,5,A.Vector(x,0,1)))
        s=capsule_rail(rail,[0,28])
        self.assertLess(s.Volume,rail.Volume)
        for x in (0,28):self.assertLess(s.common(Part.makeCylinder(1.2,5,A.Vector(x,0,1))).Volume,1e-5)

    def test_keyed_foot_retains_bearing_area_and_clearance(self):
        foot=Part.makeCylinder(3,2).cut(Part.makeCylinder(1.2,2))
        obstacle=Part.makeBox(4,2,2,A.Vector(-2,-4.5,-1))
        result,proof=keyed_foot(foot,obstacle)
        self.assertGreaterEqual(proof['contact_area_mm2'],12)
        self.assertGreaterEqual(result.distToShape(obstacle)[0],1.25-1e-6)


if __name__=='__main__':unittest.main()
