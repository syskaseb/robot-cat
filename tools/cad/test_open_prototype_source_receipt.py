"""Current source evidence and cut-ledger contracts; no duplicate CAD gate."""
import math
import unittest
import open_prototype_source_receipt as R
import open_prototype_current_cut_ledger as L


class CurrentSourceReceiptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = R.build()
        cls.ledger = L.build()

    def test_seven_profiles_have_scoped_receipts(self):
        proofs = self.receipt['radius_receipts']
        names = [n for p in proofs for n in p['profiles']]
        self.assertEqual(len(names), 7)
        self.assertEqual(len(set(names)), 7)
        self.assertEqual(proofs[1]['profiles'], ['W068'])
        self.assertTrue(proofs[0]['previous_W068_failure_explicitly_not_accepted'])

    def test_source_lengths_replace_old_stock_without_selecting_it(self):
        rows = self.receipt['source_recipes']
        self.assertEqual({r['id']: r['nominal_fit_blank_mm'] for r in rows},
                         {'W064': 211, 'W065': 183, 'W067': 349, 'W068': 433})
        self.assertEqual(self.receipt['source_nominal_total_mm'], 1176)
        self.assertIsNone(self.receipt['whole_stock_total_mm'])
        self.assertTrue(self.receipt['old920mm_is_replaced_not_extra_stock'])

    def test_two_nine_mm_insulation_stations_per_profile(self):
        seats = self.receipt['restraint_stations']
        self.assertEqual(len(seats), 14)
        self.assertEqual(len({s['id'] for s in seats}), 14)
        for s in seats:
            self.assertAlmostEqual(math.dist(s['straight_seat_start_mm'],
                                            s['straight_seat_end_mm']), 9)
            self.assertTrue(s['native_carrier_and_tie_sweep_and_tool_access_open'])
        for wire in {s['wire'] for s in seats}:
            self.assertEqual({s['id'].rsplit('/', 1)[-1] for s in seats if s['wire'] == wire},
                             {'source', 'receiver'})

    def test_current_ledger_has_eighty_edges_not_a_complete_cutlist(self):
        q = self.ledger
        self.assertEqual(len(q['body_conductors']), 80)
        self.assertEqual(len({r['id'] for r in q['body_conductors']}), 80)
        self.assertEqual(q['current_body_nominal_count'], 14)
        self.assertTrue(all(len(r['current_roles']) == 2 for r in q['body_conductors']))
        self.assertEqual(q['extra_factory_wire_purchase_mm'], 0)
        self.assertIsNone(q['whole_stock_total_mm'])

    def test_neither_receipt_nor_ledger_claims_completion(self):
        for q in (self.receipt, self.ledger):
            for flag in ('selected', 'stage_completed', 'ready_to_cut', 'physical_pass'):
                self.assertFalse(q[flag])


if __name__ == '__main__':
    unittest.main()
