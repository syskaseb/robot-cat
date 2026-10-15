import unittest
import FreeCAD as A
import Part
from bolted_rail_pressure_bridge import build


class BoltedBridgeTest(unittest.TestCase):
    def test_one_feed_leaves_other_outer_position_for_cap_screw(self):
        lands=[dict(centre_world_mm=[x,0,0],axis=[0,0,-1],length_mm=9) for x in (-4.75,0,4.75)]
        for sign in (-1,1):
            for normal in ([0,1,0],[0,-1,0]):
                p=build(lands,normal,[dict(point_world_mm=[sign*9.5,0,-4.5],radius_mm=2.1)])
                self.assertEqual(p['recipe']['T18I_quantity'],0)
                self.assertEqual(p['recipe']['M2x14_quantity'],1)
                self.assertTrue(p['recipe']['hardware_SKU_and_tightening_gate_open'])
                for name in ('body','cap','screw','nut','access_tool'):
                    self.assertTrue(p[name].isValid())
                    self.assertEqual(len(p[name].Solids),1)
                self.assertLess(p['body'].common(p['cap']).Volume,1e-6)
                self.assertLess(p['body'].common(p['screw']).Volume,1e-6)
                self.assertLess(p['cap'].common(p['screw']).Volume,1e-6)
                self.assertGreater(p['recipe']['minimum_nut_trap_to_core_ligament_mm'],1.2)
                for x in (-4.75,0,4.75):
                    wire=Part.makeLine(A.Vector(x,0,4.5),A.Vector(x,0,-4.5))
                    for component in ('body','cap','screw','nut','access_tool'):
                        self.assertGreaterEqual(p[component].distToShape(wire)[0],1.25-1e-6)

    def test_two_feed_rail_cannot_be_used_as_free_bolt_position(self):
        lands=[dict(centre_world_mm=[x,0,0],axis=[0,0,-1],length_mm=9) for x in (-4.75,0,4.75)]
        with self.assertRaises(AssertionError):
            build(lands,[0,1,0],[dict(point_world_mm=[s*9.5,0,-4.5],radius_mm=.65) for s in (-1,1)])


if __name__=='__main__':unittest.main()
