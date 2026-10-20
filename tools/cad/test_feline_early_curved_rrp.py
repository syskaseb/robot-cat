import math, unittest
import numpy as np
from feline_adjudicated_boundaries import current
from feline_selected_material_contract import load as profiles
from receive_feline_early_curved_rrp import construct,source_path


class EarlyRR(unittest.TestCase):
    def test_s_restores_tangent_and_uses_existing_nine_along_arc(self):
        rows,q,d=source_path([6.125,69.5,98])
        self.assertTrue(np.allclose(d,[0,-1,0]))
        self.assertAlmostEqual(sum(r['length_mm'] for r in rows),.25+2*25.2*math.radians(35))
        self.assertAlmostEqual(q[2],98-2*25.2*(1-math.cos(math.radians(35))))
        self.assertGreater(25.2*math.radians(35),9)
        self.assertAlmostEqual(sum(r['length_mm'] for r in source_path([6.125,69.5,98],2.5)[0]),sum(r['length_mm'] for r in rows)-2.5)

    def test_whole_four_circuit_kit_and_full_selected_head(self):
        _,ends,_=current(); contract,_,_=profiles()
        shapes,kinds,recipes,trimmed=construct(ends,contract)
        self.assertEqual(len(shapes),8); self.assertEqual(len(recipes),4)
        self.assertEqual(len(trimmed),4)
        for s in shapes.values():self.assertTrue(s.isValid());self.assertTrue(s.Solids)
        self.assertAlmostEqual(shapes['EarlyRR:head_budget'].Volume,5*4.3*5.3)
        for r in recipes.values():
            self.assertEqual(r['full_grip_arc_length_mm'],9)
            self.assertEqual(r['R_mm'],25.2)
            self.assertTrue(r['total_wire_or_final_cut_NOT_selected'])


if __name__=='__main__':unittest.main()
