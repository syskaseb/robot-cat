import json,math,unittest
from plan_feline_layout import OUT
from check_main_p0_placement import ROOT,sha


class PhysicalCables(unittest.TestCase):
    def setUp(self):
        self.doc=json.loads((OUT/'n01-physical-cable-contract.json').read_text())
    def test_usb_is_complete_selected_cable_not_a_new_shorter_sku(self):
        u=self.doc['usb']
        self.assertEqual(u['catalogue_total_mm'],500)
        self.assertEqual(u['quantity'],1)
        self.assertEqual(u['selected_part'],'LanbergCA-USBO-10CU-0005-BK')
        self.assertAlmostEqual(u['remaining_middle_budget_mm']+u['pi_prefix_length_mm']+u['bus_prefix_length_mm']+sum(u['project_overmould_allowances_mm']),500)
        self.assertTrue(u['not_a_proven_joined_curve_or_actual_slack'])
        self.assertAlmostEqual(math.sqrt(sum(v*v for v in u['pi_prefix_exit_axis'])),1)
    def test_balance_never_invents_gtech_cavities(self):
        b=self.doc['balance'];self.assertEqual(len(b['branches']),4)
        self.assertFalse(b['physical_GTech_pinout_assigned'])
        self.assertTrue(all(r['physical_GTech_cavity'] is None for r in b['branches']))
        self.assertFalse(self.doc['N01_complete'])
        self.assertEqual(self.doc['existing_register_unchanged'],dict(portions=123,ends=246))
    def test_sources_are_pinned(self):
        for p,h in self.doc['source_sha256'].items():self.assertEqual(sha(ROOT/p),h,p)


if __name__=='__main__':unittest.main()
