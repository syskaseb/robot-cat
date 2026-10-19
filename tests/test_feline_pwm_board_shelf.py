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

    def test_current_own_and_affected_fixed_receipts_are_complete_not_N01(self):
        r=json.loads((OUT/'n01-pwm-board-shelf.json').read_text())
        self.assertEqual(r['status'],'OWNER_OWN_AND_FIXED_CLEAR_SHARED47_OUTER_PENDING')
        self.assertEqual(r['errors'],[]);self.assertEqual(r['failures'],[])
        self.assertEqual(len(r['completed_parts']),38)
        self.assertEqual(len(r['unchanged_fixed_parts_reused']),22)
        self.assertEqual(len(r['affected_parts_rechecked']),16)
        self.assertEqual(r['internal_assembly']['failures'],[])
        self.assertEqual(r['internal_assembly']['errors'],[])
        self.assertFalse(r['N01_complete']);self.assertFalse(r['physical_pass'])
        self.assertTrue(all(x['symmetric_difference_mm3']<1e-5 for x in r['canonical_source_to_current_actual_equivalence']))

    def test_cumulative_invalidation_is_against_external_baseline_not_last_revision(self):
        r=json.loads((OUT/'n01-pwm-board-shelf.json').read_text())
        baseline=r['previous_internal_assemblies'][0]['geometry_sha256']
        expected={n for n,h in r['geometry_sha256'].items() if h!=baseline[n]}
        self.assertEqual(expected,set(r['affected_parts_rechecked']))
        self.assertEqual(set(r['unchanged_fixed_parts_reused'])|expected,set(r['geometry_sha256']))
        self.assertEqual(set(r['unchanged_fixed_parts_reused'])&expected,set())


if __name__=='__main__':unittest.main()
