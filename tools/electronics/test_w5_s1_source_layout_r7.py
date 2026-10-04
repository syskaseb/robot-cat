import math,unittest
from w5_s1_source_layout_r7 import layout
from w5_s1_source_layout_r6 import layout as previous

class SharedApproaches(unittest.TestCase):
    def test_preserved_mouths_and_ring_entries(self):
        for row,old in zip(layout(),previous()):
            self.assertEqual(row['wire'],old['wire']);self.assertEqual(row['start'],old['start'])
            self.assertEqual(row['end'],old['end']);self.assertEqual(row['a'],old['a']);self.assertEqual(row['b'],old['b'])
            if row['wire'] in ('W064','W065','XA01'):self.assertEqual(row,old)

    def test_continuous_bend_and_stock_intent(self):
        for row in layout():
            for a,b in zip(row['edges'],row['edges'][1:]):self.assertLess(math.dist(a['end'],b['start']),1e-7)
            for e in row['edges']:
                self.assertGreater(e['length_mm'],0)
                if e['kind']=='arc':self.assertGreaterEqual(e['radius_mm'],row['minimum_static_radius_mm'])
            self.assertGreaterEqual(row['nominal_trial_blank_mm'],row['exposed_path_mm']+row['strip_allowance_mm']+row['trial_reserve_mm'])
            self.assertFalse(row['selected']);self.assertFalse(row['physical_pass'])

if __name__=='__main__':unittest.main()
