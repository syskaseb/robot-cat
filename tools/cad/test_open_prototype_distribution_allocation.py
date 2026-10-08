import unittest
import open_prototype_distribution_allocation as D


class SharedAllocation(unittest.TestCase):
    def test_all_twenty_stations_are_unique_and_same_roles(self):
        p=D.build_plan()
        old=D.read(D.BASE/'mounting-checkpoint/distribution-mount-plan.json')['distribution']
        self.assertEqual({r['role'] for r in old},{r['role'] for r in p['distribution']})
        self.assertEqual(len({tuple(r['centre_mm']) for r in p['distribution']}),20)
        self.assertTrue(all(r['size_mm']==next(o['size_mm'] for o in old if o['role']==r['role']) for r in p['distribution']))

    def test_original_logical_ports_permuted_once(self):
        p=D.build_plan();loads=p['occupied_ports']
        self.assertIn('F_AUX.in',loads['P_REAR.3'][0]['logical_ends'])
        self.assertIn('F_RL.in',loads['P_REAR.5'][0]['logical_ends'])
        self.assertIn('F_TY.in',loads['P_AUX.4'][0]['logical_ends'])
        self.assertFalse(loads.get('P_AUX.5'))
        roles={r['role'] for r in p['distribution']}
        self.assertTrue(all(len(v)<=1 for k,v in loads.items() if k.rsplit('.',1)[0] in roles))

    def test_five_both_exits_and_independent_grip_allowance(self):
        p=D.build_plan()
        self.assertEqual(len(p['holders']),5)
        for r in p['holders']:
            self.assertAlmostEqual(D.math.dist(r['input_mm'],r['output_mm']),51)
            self.assertEqual(r['new_wire_grip_straight_mm'],21.5)
            self.assertEqual(r['factory_radius_assumption_mm'],6)
        self.assertGreaterEqual(len(p['open_gates']),5)
        self.assertFalse(p['selected']);self.assertFalse(p['stage_completed'])
        self.assertFalse(p['physical_pass'])

    def test_whole_entry_and_exit_corridors_have_derived_margin(self):
        p=D.build_plan()
        self.assertGreaterEqual(p['corridor_basis']['clear_gap_mm'],2)
        self.assertEqual(len(p['mts']),4)
        self.assertTrue(all(r['both_factory_tail_reservations_mm']==100 for r in p['mts']))
        self.assertTrue(all(r['tail_length_not_catalog'] for r in p['mts']))

    def test_exact_three_dimensional_factory_dogleg(self):
        r=D.input_recipe([-40,25.5,125],[-53.5,51.25,120],[0,1,0])
        self.assertGreaterEqual(r['first_straight_mm'],3)
        self.assertEqual(r['grip_straight_mm'],9)
        self.assertLess(r['centreline_mm']+14,50)
        parts=r['segments']
        self.assertEqual(parts[0]['start'],[-40,25.5,125])
        self.assertEqual(parts[-1]['end'],[-53.5,51.25,120])
        for a,b in zip(parts,parts[1:]):self.assertLess(D.math.dist(a['end'],b['start']),1e-7)

    def test_straight_distance_can_pass_while_full_bent_blank_fails(self):
        a=[-15,-25.5,125];b=[37.75,-52.75,120]
        self.assertLess(D.math.dist(a,b)+11,84.5)
        r=D.input_recipe(a,b,[0,-1,0])
        self.assertGreater(r['centreline_mm']+11,84.5)
        self.assertFalse(r['supplier_bend_or_mutual_clearance_qualified'])

    def test_small_shift_uses_shallow_arcs_without_negative_middle(self):
        r=D.input_recipe([35,25.5,125],[33,51.25,120],[0,1,0])
        self.assertLess(r['arc_angle_deg'],90)
        self.assertEqual(len(r['segments']),4)
        with self.assertRaises(ValueError):D.input_recipe([0,0,0],[20,15,0],[0,1,0])


if __name__=='__main__':unittest.main()
