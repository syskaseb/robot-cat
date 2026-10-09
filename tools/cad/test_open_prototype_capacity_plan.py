import math
import unittest
import open_prototype_source_capacity_plan as C
import open_prototype_source_group as B
from open_prototype_path_preflight import screen

class CapacityPlan(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.p=C.build()

    def test_all_rear_bindings_and_both_mta_exits(self):
        p=self.p;z=C.read(C.CAPACITY)['proposed_entry_z_mm']
        self.assertEqual((len(p['stations']),len(p['ports']),len(p['body_ends'])),(20,100,160))
        for e in p['body_ends']:
            self.assertEqual(e['datum'],p['ports'].get(e['current_role']))
        for r in p['tails']+p['s1_routes']:
            end=p['ports'][r['target']]['point_mm']
            B.check_path(r['segments'],end=end,min_radius=r['min_radius_mm'])
            self.assertLess(B.dot(B.segment_geometry(r['segments'][-1])[2],p['ports'][r['target']]['departure']),-1+1e-7)
            if r['target'].startswith('P_REAR.'):self.assertEqual(end[2],z)
        for m in p['mta']:
            rows=[r for r in p['tails'] if 'MTA_'+r['leg']==m['role']]
            self.assertEqual({r['side'] for r in rows},{'source','output'})
            for r in rows:self.assertEqual(r['segments'][0]['start'],m[r['side']+'_exit_mm'])

    def test_source_length_assumptions_and_early_approach(self):
        p=self.p
        for r in p['tails']:
            self.assertLessEqual(r['required_blank_mm'],100)
            self.assertTrue(r['factory_limit_not_catalog'])
        for h in p['holders']:
            B.check_path(h['input_segments'],h['input_mm'],p['ports'][h['input_target']]['point_mm'],6)
            self.assertLessEqual(h['input_blank_mm'],50 if h['role'] in ('F_PI','F_AUX') else 84.5)
        r=next(r for r in p['s1_routes'] if r['wire']=='W064')
        self.assertEqual(r['terminal_straight_mm'],18)
        self.assertGreaterEqual(math.dist(r['segments'][-1]['start'],r['segments'][-1]['end']),9)
        for r in p['s1_routes']:self.assertIsNone(r['nominal_cut_length_mm'])

    def test_no_known_mutual_crossing_but_no_acceptance(self):
        self.assertFalse([r for r in screen(self.p)['near_pairs'] if r['status']=='REJECT_PLANNING_PROXIMITY'])
        for k in ('selected','stage_completed','W5_complete','physical_pass'):self.assertFalse(self.p[k])

    def test_trial_lengths_do_not_select_or_deduct_legacy_stock(self):
        from open_prototype_source_trial_lengths import build
        result=build()
        self.assertTrue(result['legacy920mm_source_not_closed_or_deducted'])
        self.assertFalse(result['stock_selection'])
        self.assertEqual(result['candidate_nominal_total_mm'],sum(r['nominal_unpowered_trial_blank_mm'] for r in result['rows']))
        for r in result['rows']:
            self.assertGreaterEqual(r['nominal_unpowered_trial_blank_mm'],r['unrounded_trial_blank_mm'])
            self.assertLess(r['nominal_unpowered_trial_blank_mm']-r['unrounded_trial_blank_mm'],10)
            self.assertIsNone(r['actual_cut_mm'])

class FrameCorridor(unittest.TestCase):
    def test_complete_new_corridors_and_independent_rr_grip(self):
        from open_prototype_source_frame_corridor import build
        p=build()
        self.assertEqual(len(p['changed_path_names']),6)
        for r in p['tails']+p['s1_routes']:
            B.check_path(r['segments'],end=p['ports'][r['target']]['point_mm'],min_radius=r['min_radius_mm'])
        rr=next(r for r in p['tails'] if r['wire']=='W053')
        self.assertEqual(rr['terminal_straight_mm'],3)
        self.assertTrue(any(s['kind']=='line' and math.dist(s['start'],s['end'])>=9 for s in rr['segments'][1:-1]))
        pi=next(r for r in p['holders'] if r['role']=='F_PI')
        B.check_path(pi['output_segments'],pi['output_mm'],min_radius=6)
        self.assertGreaterEqual(math.dist(pi['output_segments'][-1]['start'],pi['output_segments'][-1]['end']),17.25)
        self.assertFalse([r for r in screen(p)['near_pairs'] if r['status']=='REJECT_PLANNING_PROXIMITY'])
        for k in ('selected','stage_completed','W5_complete','physical_pass'):self.assertFalse(p[k])

    def test_rr_receiving_branch_rebinds_all_ports_without_credit(self):
        from open_prototype_rr_receiving_branch import build,geometry_digest
        p=build();r=next(r for r in p['tails'] if r['wire']=='W053')
        self.assertLessEqual(r['required_blank_mm'],100)
        self.assertEqual(r['terminal_straight_mm'],9)
        B.check_path(r['segments'],end=p['ports'][r['target']]['point_mm'],min_radius=7.5)
        for e in p['body_ends']:
            if e['current_role'].startswith('RR_P.'):
                self.assertEqual(e['datum'],p['ports'][e['current_role']])
                self.assertEqual(e['datum']['departure'],B.EAST)
        self.assertEqual(geometry_digest(p),geometry_digest(build()))
        self.assertFalse([r for r in screen(p)['near_pairs'] if r['status']=='REJECT_PLANNING_PROXIMITY'])
        self.assertEqual(p['changed_path_names'],['W053'])
        self.assertIn('rejected',p['open_blocker'])

if __name__=='__main__':unittest.main()
