import unittest
import open_prototype_entry_chambers as E


class EntryChambers(unittest.TestCase):
    def test_whole_twenty_casing_scope(self):
        p=E.build_plan()
        self.assertEqual(len(p['rows']),100)
        self.assertEqual(len({r['native'] for r in p['rows']}),20)
        self.assertEqual(len({r['role'] for r in p['rows']}),100)
        self.assertTrue(all(r['reserved_straight_mm']==9 for r in p['rows']))

    def test_same_bus_permutation_applied_once_to_logical_edges(self):
        p=E.build_plan();rows={r['role']:r for r in p['rows']}
        self.assertIn('F_AUX.in',rows['P_REAR.2']['load_edges'][0]['logical_ends'])
        self.assertIn('F_RL.in',rows['P_REAR.5']['load_edges'][0]['logical_ends'])
        self.assertIn('F_TY.in',rows['P_AUX.5']['load_edges'][0]['logical_ends'])
        self.assertFalse(rows['P_AUX.4']['load_edges'])

    def test_occupancy_is_physical_pairs_not_graph_alias_quantity(self):
        p=E.build_plan()
        self.assertTrue(50 < p['occupied_ports'] <= 100)
        for row in p['rows']:
            pairs=[tuple(r['logical_ends']) for r in row['load_edges']]
            self.assertEqual(len(pairs),len(set(pairs)))

    def test_allowance_does_not_claim_a_wire_or_finished_grip(self):
        p=E.build_plan()
        self.assertTrue(p['budget_intersection_is_not_actual_wire_collision'])
        self.assertFalse(p['complete_route_or_restraint_proof'])
        self.assertFalse(p['selected']);self.assertFalse(p['physical_pass'])
        self.assertFalse(p['stage_completed'])

    def test_joint_inclination_derives_both_input_datums(self):
        p=E.recovery_plan()
        self.assertEqual(sum(r['changed'] for r in p['source_plan']),2)
        for r in p['source_plan']:
            if not r['changed']:continue
            q=r['input_recipe'];u=r['input_departure'];v=q['quarter_arc_direction']
            end=[r['input_exit_mm'][i]+9*u[i]+(6+q['entry_straight_mm'])*v[i] for i in range(3)]
            self.assertLess(E.math.dist(end,r['target_entry_mm']),1e-7)
            self.assertGreaterEqual(q['entry_straight_mm'],9)
            self.assertLess(r['necessary_ZMax_mm']+1,158)
            self.assertTrue(r['native_load_path_not_inherited'])
            self.assertTrue(r['full_output_to_load_route_not_inherited'])

    def test_unchanged_holders_are_not_silently_replaced(self):
        p=E.recovery_plan()
        old={r['holder']:r for r in E.read(E.OUT/'source-layout-plan.json')['source_plan']}
        for r in p['source_plan']:
            if r['changed']:continue
            self.assertEqual(r['input_exit_mm'],old[r['holder']]['input_exit_mm'])
            self.assertEqual(r['output_exit_mm'],old[r['holder']]['output_exit_mm'])
        self.assertTrue(p['retained20_WAGO_positions'])
        self.assertFalse(p['selected'])


if __name__=='__main__':unittest.main()
