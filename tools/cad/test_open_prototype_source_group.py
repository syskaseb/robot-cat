import math
import unittest
from open_prototype_source_group import build, check_path, segment_geometry, quarter, line, UP, WEST, EAST

class SourceGroup(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.plan=build()

    def test_complete_binding(self):
        p=self.plan
        self.assertEqual((len(p['stations']),len(p['ports']),len(p['body_ends'])),(20,100,160))
        self.assertEqual((p['occupied_ports'],p['NC_ports']),(86,14))
        for bus in {k.split('.')[0] for k in p['permutation']}:
            old={f'{bus}.{n}' for n in range(1,6)}
            self.assertEqual({p['permutation'].get(k,k) for k in old},old)

    def test_tangency_and_bend_limits_all_paths(self):
        p=self.plan
        for r in p['tails']+p['s1_routes']:check_path(r['segments'],min_radius=r['min_radius_mm'])
        for h in p['holders']:
            check_path(h['input_segments'],h['input_mm'],p['ports'][h['input_target']]['point_mm'],6)
            check_path(h['output_segments'],h['output_mm'],min_radius=6)

    def test_kink_is_rejected_before_cad(self):
        q=quarter([0,0,0],WEST,UP,6)
        with self.assertRaisesRegex(AssertionError,'Kink'):
            check_path([q,line(q['end'],[10,0,6])])

    def test_shallow_arc_length_not_quarter_assumption(self):
        from open_prototype_distribution_allocation import input_recipe
        p=input_recipe([0,0,0],[40,3,0],EAST,6)
        self.assertAlmostEqual(check_path(p['segments']),p['centreline_mm'],places=7)

    def test_both_factory_exits_bound_once(self):
        p=self.plan
        self.assertEqual(len(p['tails']),8)
        for m in p['mta']:
            rows=[r for r in p['tails'] if 'MTA_'+r['leg']==m['role']]
            self.assertEqual({r['side'] for r in rows},{'source','output'})
            for r in rows:
                self.assertEqual(r['segments'][0]['start'],m[r['side']+'_exit_mm'])
                self.assertLessEqual(r['required_blank_mm'],100)
                self.assertTrue(r['factory_limit_not_catalog'])
                self.assertEqual(r['segments'][-1]['end'],p['ports'][r['target']]['point_mm'])
        self.assertLess(100-max(r['required_blank_mm'] for r in p['tails']),1)

    def test_s1_no_guess_cut_or_legacy_920_claim(self):
        self.assertEqual({r['wire'] for r in self.plan['s1_routes']},{'W064','W065','W067','W068'})
        for r in self.plan['s1_routes']:
            self.assertIsNone(r['nominal_cut_length_mm'])
            self.assertEqual(r['min_radius_mm'],25.2)
            self.assertAlmostEqual(math.dist(r['eye_mm'],r['barrel_mm']),22.123,places=6)

    def test_joint_coverage_is_on_straight_factory_insulation(self):
        for h in self.plan['holders']:
            self.assertGreaterEqual(math.dist(h['output_segments'][-1]['start'],h['output_segments'][-1]['end']),17.25)
            self.assertAlmostEqual(math.dist(h['sleeve_start_mm'],h['sleeve_end_mm']),26.5)
            self.assertEqual(h['covered_overlap_mm'],8)
            self.assertIn('OPEN',h['output_status'])

    def test_no_selection_or_native_credit(self):
        for flag in ('selected','stage_completed','W5_complete','physical_pass'):self.assertFalse(self.plan[flag])

if __name__=='__main__':unittest.main()
