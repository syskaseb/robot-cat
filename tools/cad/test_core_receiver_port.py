import json,math,unittest
import FreeCAD as A
import Part
from core_receiver_port import build
from plan_body_receiver_retention import P,land_for


class ReceiverPortTests(unittest.TestCase):
    def test_twenty_lands_are_on_actual_received_routes(self):
        plan=json.loads((P.OUT/'body-fanout-layout.json').read_text())
        rows={r['wire']:r for r in plan['rows']}
        self.assertEqual(len(plan['routes']),20)
        for name,route in plan['routes'].items():
            land=land_for(rows[name],route)
            self.assertAlmostEqual(math.dist(land['start_world_mm'],land['end_world_mm']),9)
            self.assertAlmostEqual(sum(x*x for x in land['axis']),1)

    def test_saddle_and_provisional_band_are_disjoint_valid_single_solids(self):
        for axis,normal in (([0,0,1],[1,0,0]),([1,0,0],[0,1,0]),([0,-1,0],[0,0,-1])):
            land=dict(centre_world_mm=[0,0,0],axis=axis,length_mm=9)
            for offset in (-1.5,0,1.5):
                p=build(land,normal,offset)
                for name in ('body','band'):
                    self.assertTrue(p[name].isValid());self.assertEqual(len(p[name].Solids),1)
                self.assertLess(p['body'].common(p['band']).Volume,1e-6)
                wire=Part.makeLine(A.Vector(*[-4.5*x for x in axis]),A.Vector(*[4.5*x for x in axis]))
                self.assertGreaterEqual(wire.distToShape(p['body'])[0],1.5-1e-6)
                self.assertGreaterEqual(wire.distToShape(p['band'])[0],1.2-1e-6)
                self.assertTrue(p['recipe']['sample_retention_and_tightening_gate_open'])


if __name__=='__main__':unittest.main()
