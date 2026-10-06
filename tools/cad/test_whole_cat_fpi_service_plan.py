"""Necessary recipe checks; these do not qualify the failed service layouts."""
import unittest
from whole_cat_fpi_service_plan import recipe


class FPIRecipe(unittest.TestCase):
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
