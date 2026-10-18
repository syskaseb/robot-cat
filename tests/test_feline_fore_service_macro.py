import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
import FreeCAD as A
from plan_feline_fore_service_macro import fore_service_datum,rigid_tf


class ServiceMacro(unittest.TestCase):
    def test_continuous_case_and_wire_interval_and_band_height(self):
        centre,interval=fore_service_datum(-141.5,-124.457566,30.842526,14)
        self.assertGreater(interval[1],interval[0])
        self.assertGreaterEqual(centre[0]-10.125-(-141.5),3.25)
        self.assertGreaterEqual(-124.457566-(centre[0]+1.7),1.25)
        self.assertAlmostEqual(centre[2]-25.5-5.75-30.842526,1.75)

    def test_no_interval_is_hold_not_scalar_offset(self):
        with self.assertRaises(AssertionError):fore_service_datum(-140,-124.457566,30.842526,14)

    def test_whole_hardware_and_ports_follow_same_transform(self):
        c=A.Vector(-105,45,65);tf=rigid_tf(c,[15,0,0],180)
        self.assertTrue(tf.multVec(c).isEqual(A.Vector(-90,45,65),1e-8))
        self.assertTrue(tf.Rotation.multVec(A.Vector(0,1,0)).isEqual(A.Vector(0,1,0),1e-8))
        q=A.Vector(-133.123,22.5,53)
        self.assertTrue(tf.multVec(q).isEqual(A.Vector(-61.877,22.5,77),1e-8))


if __name__=='__main__':unittest.main()
