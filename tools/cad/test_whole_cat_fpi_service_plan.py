"""Necessary recipe checks; these do not qualify the failed service layouts."""
import unittest
from whole_cat_fpi_service_plan import recipe
from whole_cat_service_zone import allocation


class FPIRecipe(unittest.TestCase):
    def test_shared_lane_allocation_keeps_access_and_bend_budgets(self):
        plan=allocation();gap=plan['derivation']
        self.assertTrue(plan['F_PI_access_unchanged'])
        self.assertGreaterEqual(gap['left_service_gap_mm'],1)
        self.assertGreaterEqual(gap['left_input_elbow_floor_mm']-gap['left_wago_top_mm'],1)
        self.assertGreaterEqual(gap['right_input_elbow_floor_mm']-gap['F0_top_mm'],1)
        self.assertEqual(plan['wire_radius_budget_mm'],12.4)
        self.assertTrue(plan['no_whole_harness_claim'])
        self.assertTrue(plan['exact_supplier_lid_motion_OPEN'])

    def test_factory_output_recipes_fit_nominal_lead(self):
        for side_first, blank in [(False, 45.42477796077), (True, 56.84955592154)]:
            plan = recipe(side_first)
            row = plan['factory_output']
            self.assertAlmostEqual(row['nominal_blank_mm'], blank, places=6)
            self.assertLessEqual(row['nominal_blank_mm'], 84.5)
            self.assertGreaterEqual(row['first_straight_mm'], 9)
            self.assertGreaterEqual(row['last_straight_mm'], 9)
            self.assertTrue(plan['MAIN_extension_route_OPEN'])
            self.assertAlmostEqual(plan['joint_source_port_mm'][0] - plan['joint_extension_port_mm'][0], 35.5)


if __name__ == '__main__':
    unittest.main()
