import unittest
import FreeCAD as A
import Part
from three_core_pressure_bridge import build


class PressureBridge(unittest.TestCase):
    def test_ties_retain_separate_cap_and_clear_all_three_nominal_cores(self):
        lands=[dict(id=str(x),centre_world_mm=[x,0,0],axis=[0,0,1],length_mm=9) for x in (-4.75,0,4.75)]
        for normal in ([0,1,0],[0,-1,0]):
            q=build(lands,normal)
            for x in (-4.75,0,4.75):
                wire=Part.makeLine(A.Vector(x,0,-4.5),A.Vector(x,0,4.5))
                for s in (q['body'],q['cap'],*q['bands']):self.assertGreaterEqual(s.distToShape(wire)[0],1.25-1e-6)
            self.assertEqual(q['recipe']['T18I_quantity'],2)
            self.assertTrue(q['recipe']['physical_fit_tightening_creep_gate_open'])


if __name__=='__main__':unittest.main()
