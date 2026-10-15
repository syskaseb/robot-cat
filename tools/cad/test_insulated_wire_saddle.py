import unittest
import FreeCAD as A
import Part
from insulated_wire_saddle import build
from core_receiver_port import build as original


class InsulatedSaddleTest(unittest.TestCase):
    def land(self):return dict(id='Fixture',centre_world_mm=[0,0,0],axis=[0,0,1],length_mm=9)
    def test_radius_one_retains_existing_exact_component(self):
        a=build(self.land(),[1,0,0],1);b=original(self.land(),[1,0,0])
        for n in ('body','band'):
            self.assertLess(a[n].cut(b[n]).Volume,1e-6)
            self.assertLess(b[n].cut(a[n]).Volume,1e-6)
    def test_data_and_power_insulation_clearance(self):
        wire=Part.makeLine(A.Vector(0,0,-4.5),A.Vector(0,0,4.5))
        for r in (.65,1.05,1.55,2.1,2.25):
            p=build(self.land(),[1,0,0],r)
            self.assertGreaterEqual(p['body'].distToShape(wire)[0],r+.49)
            self.assertGreaterEqual(p['band'].distToShape(wire)[0],r+.19)
            self.assertTrue(p['recipe']['sample_retention_tightening_creep_gate_open'])
    def test_no_invented_short_land_or_unknown_radius(self):
        q=self.land();q['length_mm']=3
        with self.assertRaises(AssertionError):build(q,[1,0,0],1)
        with self.assertRaises(AssertionError):build(self.land(),[1,0,0],4)


if __name__=='__main__':unittest.main()
