import unittest
import FreeCAD as A
import Part
from receive_feline_rooted_end_bays import shoe


class ShoeTests(unittest.TestCase):
    def test_outboard_fasteners_preserve_shoe_thickness_and_nut_stack(self):
        for side in (-1,1):
            case=Part.makeBox(35.5,8.1,8.9,A.Vector(114.25,side*15-4.05,-38.45))
            base,cap,hw=shoe(case)
            for s in (base,cap,*hw.values()):
                self.assertTrue(s.isValid());self.assertEqual(len(s.Solids),1)
            self.assertAlmostEqual(cap.BoundBox.ZMax-cap.BoundBox.ZMin,3.25)
            for i in (0,1):
                screw=hw['CapScrew',i]
                self.assertAlmostEqual(screw.BoundBox.Center.y,side*30.5)
                self.assertAlmostEqual(screw.BoundBox.ZMax-screw.BoundBox.ZMin,13.5)
                self.assertLess(case.common(screw).Volume,1e-6)
            self.assertLess(case.common(cap).Volume,1e-6)


if __name__=='__main__':unittest.main()
