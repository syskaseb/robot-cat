"""Complete PWM owner construction contracts, not global clearance approval."""
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
from feline_pwm_board_shelf import build,source_inputs
from plan_feline_layout import OUT


class PWMShelf(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parts,cls.kinds,cls.s1,cls.contract=build(*source_inputs())

    def test_purchased_parts_and_complete_four_stacks_preserved(self):
        p=self.contract
        self.assertEqual(len(p['purchased_parts']),15)
        self.assertEqual(sorted(map(len,p['reversed_complete_fastener_stacks'])),[3,3,4,4])
        self.assertEqual(sum(k['kind']=='board' for k in self.kinds.values()),1)

    def test_every_bare_end_and_minimum_radius_preserved(self):
        recipes=self.contract['source_endpoints']
        self.assertEqual({r['wire'] for r in recipes},{'XL02','XL05','XL06','XL08','XS11','XS21','XS31'})
        for r in recipes:
            self.assertGreaterEqual(r['R_mm'],r['minimum_inherited_R_mm'])
            self.assertTrue(r['bare_segments_preserved'])
            a,b=r['grip_start_mm'],r['grip_end_mm']
            self.assertAlmostEqual(sum((x-y)**2 for x,y in zip(a,b)),81)
        self.assertEqual(sum(k['kind']=='bare' for k in self.kinds.values()),7)

    def test_connected_carrier_and_separate_full_common_restraints(self):
        self.assertEqual(self.contract['carrier_solid_count'],1)
        self.assertEqual(len([n for n in self.parts if n.endswith(':band_budget')]),2)
        self.assertEqual(len([n for n in self.parts if n.endswith(':head_budget')]),2)
        self.assertTrue(all(s.isValid() and s.Solids for s in self.parts.values()))
        self.assertFalse(self.contract['N01_complete'])
        self.assertFalse(self.contract['selected'])

    def test_received_source_motion_is_not_whole_N01(self):
        r=json.loads((OUT/'n01-source-saddles-whole-joint.json').read_text())['hard_source_motion_receiver']
        self.assertEqual(len(r['completed_sources']),10)
        self.assertEqual(r['motion_samples'],36)
        self.assertIsNone(r['first_failure'])
        self.assertFalse(r['N01_complete'])
        self.assertFalse(r['continuous_sweep_verified'])
        self.assertEqual(len(r['outer_refinement_required']),2)


if __name__=='__main__':unittest.main()
