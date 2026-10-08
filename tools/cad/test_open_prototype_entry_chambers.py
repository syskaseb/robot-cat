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


if __name__=='__main__':unittest.main()
