"""Acceptance gates for a rejected or unfinished twelve-input candidate."""
import unittest,json,hashlib,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-inputs-r1'
class InputCandidate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((OUT/'checks.json').read_text(encoding='utf-8'))
        cls.intent=json.loads((OUT/'intent.json').read_text(encoding='utf-8'))
    def test_exact_conductor_coverage(self):
        source=json.loads((ROOT/'hardware/electronics/full-cat/body-harness-w5-r1/interface.json').read_text(encoding='utf-8'))
        expected={r['id']:(r['a'],r['b']) for r in source['conductors'] if r['group']=='SERVO_FUSE_INPUTS'}
        actual={r['id']:(r['a'],r['b']) for r in self.data['lengths']}
        self.assertEqual(actual,expected);self.assertEqual(len(actual),12)
        self.assertEqual(self.data['terminals_checked'],24)
    def test_source_bindings(self):
        for bindings in (self.intent['source_sha256'],self.data['source_sha256']):
            for p,h in bindings.items():self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),h,p)
    def test_blank_is_not_path_or_delivered_cut(self):
        for r in self.data['lengths']:
            self.assertIsNone(r['actual_cut_mm'])
            self.assertEqual(r['nominal_blank_mm'],math.ceil((r['path_mm']+32.30)/10)*10)
            self.assertEqual(r['old_100mm_limit_met'],r['nominal_blank_mm']<=100)
    def test_shared_stock_once(self):
        stock=self.data['stock'];self.assertEqual(stock['legacy_LAPP_purchase_mm'],2000)
        self.assertEqual(stock['inputs_candidate_mm'],sum(r['nominal_blank_mm'] for r in self.data['lengths']))
        self.assertEqual(stock['remaining_mm'],2000-150-stock['inputs_candidate_mm'])
    def test_no_false_selection_or_phase_completion(self):
        for field in ('selected','physical_pass','W5_complete'):self.assertFalse(self.data[field])
        if self.data['hits'] or not all(r['old_100mm_limit_met'] for r in self.data['lengths']):self.assertEqual(self.data['status'],'REJECTED')
    def test_provisional_interface_is_not_measurement(self):
        p=self.intent['prototype'];self.assertEqual(p['MTA_terminal_seating_e_mm'],0)
        self.assertEqual(p['terminal_axis_offset_y_mm'],7)
        self.assertEqual(p['minimum_fixed_radius_mm'],12.4)
        self.assertIn('prototype assumptions',self.intent['distinction'])
if __name__=='__main__':unittest.main()
