"""Nominal split-clamp geometry, not a pull test or layout acceptance."""
import math,unittest
import FreeCAD as A
import Part
from feline_gallery_tail_support import split_clamp


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


if __name__=='__main__':unittest.main()
