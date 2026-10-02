import copy,json,unittest
from main_positive_wiring_card_r1 import payload,ROOT

class MainPositiveCard(unittest.TestCase):
    def setUp(self):
        self.screen=json.loads((ROOT/'hardware/electronics/full-cat/main-positive-complete-r8/checks.json').read_text(encoding='utf-8'))
        self.native=dict(status='NATIVE_COMPLETE_WITH_SOFT_FIT_CONDITION')
    def card(self):return payload(self.screen,self.native)
    def test_routes_and_factory_budget(self):
        c=self.card();self.assertEqual([r['wire'] for r in c['rows']],['W043','W077','W078'])
        self.assertEqual([r['nominal_blank_mm'] for r in c['rows']],[40,80,210])
        self.assertTrue(all(r['required_bound_mm']<=r['nominal_blank_mm'] for r in c['rows']))
        self.assertGreaterEqual(c['confirmed_factory_lead_minimum_mm'],80)
    def test_splice_overlap(self):
        s=self.card()['splice'];self.assertEqual(s['bare_overlap_mm'],8)
        self.assertEqual(s['sleeve_X_mm'][1]-s['sleeve_X_mm'][0],8+2*6)
    def test_shared_stock_not_second_cable(self):
        c=self.card()['stock'];self.assertTrue(c['parallel_conductors_not_summed'])
        self.assertTrue(c['no_second_K1474']);self.assertGreater(c['red_remaining_mm'],490)
        self.assertGreater(c['black_remaining_mm'],480)
    def test_restraints_replacement_not_double_count(self):
        r=self.card()['retention'];self.assertEqual(r['small_working_after'],93-2+4)
        self.assertLessEqual(r['small_working_after'],r['shared_small_bag'])
        self.assertLess(r['large_loop_bound_mm'],r['large_minimum_length_mm'])
        self.assertTrue(r['retained_W060_MAIN_strap'])
        self.assertEqual(r['large_working_after'],r['prior_large_working_allowance']+1)
        self.assertLessEqual(r['large_working_after'],r['shared_large_bag'])
    def test_rigid_failure_rejected(self):
        self.screen['blocking_hits']=[{'part':'wire','owner':'P0Support0'}]
        with self.assertRaises(AssertionError):self.card()
    def test_no_false_whole_phase_or_physical_pass(self):
        c=self.card();self.assertFalse(c['physical_pass']);self.assertFalse(c['W5_complete'])
        self.assertFalse(c['collision_free']);self.assertTrue(c['soft_contacts'])
        self.assertEqual(c['MAIN_input_insulation']['intact_overlap_each_wire_minimum_mm'],6)
    def test_native_not_complete_rejected(self):
        self.native['status']='OPEN'
        with self.assertRaises(AssertionError):self.card()

if __name__=='__main__':unittest.main()
