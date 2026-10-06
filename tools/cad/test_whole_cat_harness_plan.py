"""Regression gates for circuit identity and necessary endpoint lengths."""
import unittest
from whole_cat_interior import splice_inventory
from whole_cat_harness_plan import runout_lower_bound
from whole_cat_branch_source import recipe
from whole_cat_board_datums import footprint_coordinates, OLD_PADS, OLD_ORIGIN


class HarnessPlan(unittest.TestCase):
    def test_xb11_is_not_pi_solder_joint(self):
        inventory = splice_inventory()
        xb11 = next(row for row in inventory['baseline'] if row['electrical_role']=='XB11')
        self.assertEqual(xb11['wires'], [dict(id='XB11', a='P_AUX.2', b='F_HY.in')])
        self.assertFalse(any(w['id'] in ['W077','W078'] for row in inventory['baseline'] for w in row['wires']))
        self.assertEqual(inventory['R53_installed'], 5)
        self.assertEqual(inventory['R53_spare'], 1)

    def test_fpi_shortest_factory_lead_fails_declared_runouts(self):
        bound=runout_lower_bound([-4.5,87,90], [1,0,0], [-24,23.5,119], [0,1,0], 12)
        self.assertGreater(bound,84.5)
        self.assertGreater(bound,50)

    def test_coupled_short_input_recipe(self):
        plan=recipe()
        self.assertEqual([r['id'] for r in plan['routes']], ['W043','XA01'])
        for row in plan['routes']:
            self.assertLessEqual(row['nominal_blank_mm'],50)
            self.assertGreaterEqual(row['first_straight_mm'],9)
            self.assertGreaterEqual(row['last_straight_mm'],9)

    def test_layer_change_keeps_short_inputs_and_ground_receiver(self):
        plan=recipe(True)
        self.assertIsNone(plan['G2'])
        self.assertEqual(plan['P_REAR']['origin_mm'][2],132)
        self.assertAlmostEqual(plan['routes'][1]['nominal_blank_mm'],29)
        self.assertLess(plan['routes'][0]['nominal_blank_mm'],50)

    def test_main_pad_frame_uses_named_footprint_not_centre(self):
        low=[-17.24,-9.43,9]
        local=footprint_coordinates(OLD_PADS['MAIN.VIN'], low)
        for actual,expected in zip(local,[26.289,6.18,1.5748]):
            self.assertAlmostEqual(actual,expected)
        for world in OLD_PADS.values():
            p=footprint_coordinates(world,low)
            rebuilt=[x+y+z for x,y,z in zip(p,OLD_ORIGIN,low)]
            for actual,expected in zip(rebuilt,world):
                self.assertAlmostEqual(actual,expected)


if __name__=='__main__':
    unittest.main()
