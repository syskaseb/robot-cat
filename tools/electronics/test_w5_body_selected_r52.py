"""Bounded invariants for the selected body/TE merge, without CAD or ROS."""
import unittest
from w5_body_selected_r52 import compile_ledger


class SelectedBodyLedger(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = compile_ledger()
        cls.rows = {r['id']: r for r in cls.receipt['conductors']}

    def test_graph_preserved(self):
        self.assertEqual(set(self.rows), {f'W{i:03}' for i in range(1, 81)})
        self.assertEqual(self.receipt['physical_P0_ends'], 160)

    def test_twelve_selected_input_cuts(self):
        inputs = [r for r in self.rows.values() if 'selected_end_overlay' in r
                  and r['selected_end_overlay']['id'].endswith('.in')]
        self.assertEqual(len(inputs), 12)
        self.assertEqual(sum(r['nominal_blank_mm'] for r in inputs), 2880)
        self.assertTrue(all(r['full_route_prepared'] for r in inputs))
        self.assertTrue(all(r['stock_identity'] == 'p0:WIRE-INLET-BLACK12-P0' for r in inputs))

    def test_local_output_does_not_close_servo_loom(self):
        moving = [r for r in self.rows.values() if r['group'] == 'MOVING_SERVO_LOOMS']
        self.assertEqual(len(moving), 36)
        self.assertTrue(all(not r['full_route_prepared'] for r in moving))
        self.assertEqual(sum('selected_end_overlay' in r for r in moving), 12)

    def test_eight_mta_routes_not_duplicate_factory_stock(self):
        ids = {'W026', 'W037', 'W041', 'W042', 'W044', 'W045', 'W052', 'W053'}
        self.assertTrue(all(self.rows[k]['full_route_prepared'] for k in ids))
        self.assertTrue(all(self.rows[k]['nominal_blank_mm'] is None for k in ids))
        self.assertNotIn('extension_blank_mm', self.rows['W041'])
        self.assertEqual(sum(self.rows[k].get('extension_blank_mm', 0) for k in ids), 1190)

    def test_physical_results_not_fabricated(self):
        self.assertTrue(all(r['actual_cut_mm'] is None and not r['phase2_physical_continuity_checked']
                            for r in self.rows.values()))
        self.assertFalse(self.receipt['physical_pass'])
        self.assertFalse(self.receipt['W5_complete'])
        self.assertEqual(self.receipt['phase1_percent'], 75)

    def test_remaining_work_explicit(self):
        self.assertEqual(self.receipt['current_body_route_rows_prepared'], 34)
        self.assertEqual(len(self.receipt['route_rows_pending']), 46)
        self.assertTrue({'W064', 'W065', 'W067', 'W068'}.issubset(self.receipt['route_rows_pending']))


if __name__ == '__main__':
    unittest.main()
