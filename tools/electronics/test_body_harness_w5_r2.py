import unittest,json,hashlib
from pathlib import Path
from body_harness_w5_r2 import build,ROOT
class CurrentLedger(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data,cls.stock=build();cls.rows={r['id']:r for r in cls.data['conductors']}
    def test_exact_80_160(self):
        self.assertEqual(len(self.rows),80);self.assertEqual(sum(len(r['ends']) for r in self.rows.values()),160)
    def test_source_binding(self):
        for p,h in self.data['source_bindings'].items():self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),h,p)
    def test_current_main_supersedes_old_blank(self):
        self.assertEqual(self.rows['W078']['nominal_selected_blank_mm'],210)
        self.assertIsNone(self.rows['W078']['limit_mm'])
        self.assertEqual(self.rows['W060']['nominal_selected_blank_mm'],220)
        self.assertEqual(self.rows['W043']['nominal_selected_blank_mm'],40)
        self.assertEqual(self.rows['W077']['nominal_selected_blank_mm'],80)
    def test_no_rejected_route_selected(self):
        rows=[r for r in self.rows.values() if r['group']=='SERVO_FUSE_INPUTS'];self.assertEqual(len(rows),12)
        for r in rows:self.assertFalse(r['current_selected_route_checked']);self.assertIsNone(r['nominal_selected_blank_mm'])
    def test_shared_colour_stock(self):
        r=self.stock['stock'][0];self.assertEqual(r['purchase_quantity'],1)
        for colour,v in r['allocation_per_colour_mm'].items():self.assertAlmostEqual(1000-sum(v.values()),r['remaining_per_colour_mm'][colour])
    def test_one_ground_bridge_and_not_graph_duplicates(self):
        self.assertEqual(self.rows['W061']['nominal_selected_blank_mm'],240)
        self.assertEqual(sum(r['id']=='W061' for r in self.data['conductors']),1)
    def test_actual_cuts_and_phase_are_not_fabricated(self):
        self.assertTrue(all(r['actual_cut_mm'] is None for r in self.rows.values()))
        for k in ('W5_complete','K3_complete','physical_pass'):self.assertFalse(self.data[k])
        self.assertEqual(self.data['coverage']['selected_nominal_cuts'],10)
        self.assertEqual(self.data['coverage']['remaining_body_ledger_cuts'],70)
if __name__=='__main__':unittest.main()
