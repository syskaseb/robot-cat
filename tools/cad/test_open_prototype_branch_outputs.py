"""Focused pure recipe checks, without repeated wire/holder CAD."""
import unittest
import open_prototype_branch_outputs as B
import open_prototype_output_reliefs as R


class BranchOutputRecipe(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.plan=B.build_plan();cls.reliefs=R.build_plan()

    def test_four_not_five_new_outputs(self):
        self.assertEqual({r['holder'] for r in self.plan['output_recipes']}, {'F_AUX','F_HY','F_HP','F_TY'})
        self.assertEqual(len(self.plan['output_recipes']),4)

    def test_factory_minimum_and_joint_straight(self):
        for r in self.plan['output_recipes']:
            self.assertLessEqual(r['guide_length_mm'],r['nominal_factory_blank_mm'])
            self.assertLessEqual(r['nominal_factory_blank_mm'],r['factory_minimum_available_mm'])
            self.assertGreaterEqual(r['insulation_grip_straight_mm'],9)
            self.assertGreaterEqual(r['terminal_straight_mm']-r['bare_lap_allowance_on_terminal_mm'],6)

    def test_physical_landing_joins_same_copper_not_same_coordinate(self):
        pop=B.read(B.POP);terms={r['ref']:r for r in pop['terminals']}
        for r in self.plan['chosen_PWM_landings']:
            a,b=terms[r['logical_role']],terms[r['chosen_physical_landing']]
            self.assertEqual(a['source_copper_group'],b['source_copper_group'])
            self.assertEqual(a['net'],b['net'])
            self.assertNotEqual(a['y'],b['y'])
            self.assertTrue(r['isolated_from_unknown_U1_external_padmap'])

    def test_current_PWM_plane_not_old_156mm(self):
        for r in self.plan['chosen_PWM_landings']:
            self.assertAlmostEqual(r['current_nominal_pad_top_mm'][2],84.3202)

    def test_no_print_part_or_connector_multiplication(self):
        self.assertEqual(self.plan['new_print_parts'],0)
        self.assertEqual(self.reliefs['additional_print_parts'],0)
        self.assertEqual(self.reliefs['additional_screws_connectors'],0)
        self.assertEqual(self.reliefs['additional_ties'],4)
        self.assertEqual({r['native'] for r in self.reliefs['rows']}, {'SourceLeftCarrier','SourceRightCarrier'})

    def test_independent_grips_hold_intact_wire(self):
        for r in self.reliefs['rows']:
            self.assertTrue(r['intact_factory_insulation_only'])
            self.assertEqual(r['straight_insulation_grip_mm'],9)
            self.assertAlmostEqual(r['wire_axis_z_mm']-r['floor_top_z_mm'],2)
            self.assertAlmostEqual(r['floor_top_z_mm']-r['carrier_top_z_mm'],8)
            self.assertEqual(len(r['slot_centres_mm']),2)

    def test_never_accept_whole_stage_from_guides(self):
        self.assertFalse(self.plan['stage_completed'])
        self.assertFalse(self.reliefs['stage_completed'])
        self.assertFalse(self.plan['physical_pass'])
        self.assertTrue(all(r['independent_output_grip_and_load_route_open'] for r in self.plan['output_recipes']))


if __name__=='__main__':unittest.main()
