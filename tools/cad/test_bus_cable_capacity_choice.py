import unittest
from prepare_bus_cable_capacity_choice import choice

class BUSCableCapacityTests(unittest.TestCase):
    def data(self):
        routes={n:dict(minimum_factory_blank_project_mm=m,guide_mm=m-35.05,three_hundred_mm_recipe_fits=False,
                       radius_mm=1,project_R_mm=10) for n,m in [('W002',394.58421135755106),('W003',393.98061667487184)]}
        facts=dict(part_number='SR-Cable-5264-3PIN-900mm-6PCS',advertised_length_mm=900,cables_per_pack=6)
        binding=dict(installed_candidate_header='H5',V_contact_and_wire_removed_before_installation=True)
        return routes,facts,binding

    def test_one_cable_not_two_and_no_double_terminal_allowance(self):
        r=choice(*self.data())
        self.assertEqual(r['physical_cables_installed'],1)
        self.assertEqual(r['project_round_up_for_fit_blank_mm'],395)
        self.assertEqual(r['new_splices'],0)
        self.assertFalse(r['selected']);self.assertFalse(r['W5_complete'])
        self.assertTrue(all(w['actual_cut_mm'] is None for w in r['wires']))

    def test_insufficient_or_energized_pin_candidate_is_rejected(self):
        routes,facts,binding=self.data();facts['advertised_length_mm']=300
        with self.assertRaises(AssertionError):choice(routes,facts,binding)
        routes,facts,binding=self.data();binding['V_contact_and_wire_removed_before_installation']=False
        with self.assertRaises(AssertionError):choice(routes,facts,binding)

if __name__=='__main__':unittest.main()
