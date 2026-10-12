import unittest,math
import plan_u1_common_departures as P


class CommonDepartureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.p=P.build()

    def test_actual_j8_xy_and_explicit_current_z(self):
        d=self.p['GPIO_source_datum']
        self.assertTrue(d['XY_verified_against_current5ends'])
        self.assertEqual(d['current_board_to_world_translation_mm'],[-19,-28,47.72])
        self.assertEqual(d['wire_exit_assumed_z_mm'],65.32)
        self.assertFalse(d['source_historical_datums']['physical_pass'])

    def test_rebound_same_net_source_holes_not_invented_pitch(self):
        r=self.p['routes']
        self.assertEqual(r['XL02']['source']['a']['world_mm'][:2],[76.35,-13.97])
        self.assertEqual(r['XL07']['source']['b']['world_mm'][:2],[78.89,6.35])
        self.assertEqual(r['XL02']['source']['a']['net'],'LOGIC3V3')

    def test_portal_covers_whole_assumed_plug_withdrawal(self):
        b=self.p['GPIO_source_datum']['current_housing_bounds_mm'];p=P.PORTAL
        self.assertLess(p[0],b[0]);self.assertGreater(p[3],b[3])
        self.assertLess(p[1],b[1]);self.assertGreater(p[4],b[4])
        self.assertGreater(p[5],b[5]+12)
        self.assertFalse(self.p['selected'])

    def test_pair_is_rebound_together_with_explicit_adapter_stock(self):
        pair=self.p['changed_MAIN_pair'];self.assertEqual(set(pair),{'W079','W080'})
        for r in pair.values():self.assertLessEqual(r['guide_mm']+3,450)
        a=pair['W079']['parts'][-1]['end'];b=pair['W080']['parts'][-1]['end']
        self.assertAlmostEqual(math.dist(a,b),3.5)
        self.assertEqual(a,[32.7,-37.15,50.92]);self.assertEqual(b,[32.7,-40.65,50.92])
        receiver=self.p['USB_receiver']
        self.assertEqual(receiver['quantity'],1)
        self.assertEqual(receiver['mating_front_world_mm'],[-7.8,-29.25,50.92])
        self.assertEqual(receiver['official_Pi_USB_C_shell_board_xy_mm'],[6.875,-1.25,15.525,6.15])
        self.assertFalse(receiver['selected'])
        budget=self.p['PI_CABLE_P0_proposed_routing_cap_supersession']
        self.assertGreater(budget['remaining_single1m_cut_after_output_and_INPUT_offcut_mm'],0)
        self.assertGreater(budget['conditional_remaining_total_loop_budget_ohm'],0)
        self.assertFalse(budget['selected'])

    def test_fine_fan_lands_are_outside_retainer_tie(self):
        lands=[l for l in self.p['grip_lands'] if l['wire'].startswith('XS') and l['side']=='b']
        self.assertEqual(len(lands),3)
        for l in lands:
            self.assertLess(l['line_mm'][0][1]+.4,-5.45)
            self.assertAlmostEqual(math.dist(*l['line_mm']),9)

    def test_ground_reference_new_topology_and_fixed_profile(self):
        r=self.p['routes']['XL09'];e=r['ends']['b']
        self.assertEqual(e['end_mm'],[52.5,-39.75,126.])
        self.assertEqual(e['end_axis'],[0,0,-1])
        self.assertEqual(r['source']['project_radius_mm'],6)
        self.assertEqual(r['source']['nominal_area_mm2'],.25)


if __name__=='__main__':unittest.main()
