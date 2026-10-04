import math,unittest
from w5_s1_source_layout_r3 import layout

class SixLeadTests(unittest.TestCase):
    def test_all_six_complete_and_no_small_radius(self):
        rows=layout();self.assertEqual({r['wire'] for r in rows},{'W043','W064','W065','W066','W067','W068'})
        for r in rows:
            for a,b in zip(r['edges'],r['edges'][1:]):self.assertLess(math.dist(a['end'],b['start']),1e-7)
            for e in r['edges']:
                if e['kind']=='arc':self.assertGreaterEqual(e['radius_mm'],r['minimum_static_radius_mm'])
            self.assertIsNone(r['actual_cut_mm']);self.assertFalse(r['selected'])

    def test_real_factory_minimum_and_separated_ring_tips(self):
        rows={r['wire']:r for r in layout()};f=rows['W043']
        self.assertLessEqual(f['nominal_trial_blank_mm'],84.5)
        self.assertGreaterEqual(f['nominal_trial_blank_mm'],f['exposed_path_mm']+29)
        for w in ('W064','W067'):self.assertEqual(rows[w]['end'][0],94.877)
        for w in ('W065','W068'):self.assertEqual(rows[w]['end'][0],151.123)
        self.assertEqual(rows['W065']['start'],[32,13.6,129])

if __name__=='__main__':unittest.main()
