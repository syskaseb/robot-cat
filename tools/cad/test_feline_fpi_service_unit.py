"""Keep necessary rejection and dependency evidence separate from service PASS."""
import json
import unittest
from plan_feline_layout import OUT


class ServiceUnit(unittest.TestCase):
    def test_negative_x_is_margin_not_penetration(self):
        p=json.loads((OUT/'n01-FPI-removable-unit-negative-X-samples.json').read_text())
        self.assertEqual(p['visited_offsets_mm'],[[-5,0,0]])
        q=p['checks']['0|Ref_Material_P0_FrameFront20_0_0']
        self.assertGreater(q['gap_mm'],0)
        self.assertLess(q['gap_mm'],q['minimum_mm'])
        self.assertFalse(p['errors'])
        self.assertIn('P_SYS.5',p['sequence'][1])
        self.assertIn('G1.1',p['sequence'][1])
        self.assertFalse(p['whole_harness_extraction_received'])

    def test_vertical_cell_does_not_inherit_missing_wires(self):
        p=json.loads((OUT/'n01-FPI-vertical-cell-necessary.json').read_text())
        self.assertIn('case|Ref_Material_F_L2_CP2_OUT_0_0',p['failures'])
        self.assertFalse(p['errors'])
        self.assertIn('W043',p['excluded_changed_cell_parts'])
        self.assertFalse(p['selected'])

    def test_top_access_requires_explicit_release(self):
        p=json.loads((OUT/'n01-FPI-top-service-dependencies.json').read_text())
        self.assertEqual(set(p['wire_ids']),{'W027','W020','W031','W033','W035'})
        self.assertIn('Ref_Material_S0_key_CP2_0_0',p['blockers'])
        self.assertFalse(p['errors'])
        self.assertFalse(p['selected'])
        self.assertFalse(p['N01_complete'])
        self.assertFalse(p['physical_pass'])


if __name__=='__main__': unittest.main()
