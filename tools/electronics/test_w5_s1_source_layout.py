import math
import unittest
from w5_s1_source_layout_r1 import layout,R


class S1LayoutTests(unittest.TestCase):
    def test_four_continuous_unspliced_paths_and_correct_contacts(self):
        rows=layout()
        self.assertEqual({r['b'] for r in rows},{'S1.2','S1.3','S1.5','S1.6'})
        self.assertEqual(len(rows),4)
        for r in rows:
            for a,b in zip(r['edges'],r['edges'][1:]):
                self.assertLess(math.dist(a['end'],b['start']),1e-7)
            self.assertGreater(r['nominal_trial_blank_mm'],r['exposed_path_mm']+22.73)
            self.assertIsNone(r['actual_cut_mm'])

    def test_no_radius_reduction_or_negative_straight(self):
        for r in layout():
            for e in r['edges']:
                self.assertGreater(e['length_mm'],0)
                if e['kind']=='arc':self.assertEqual(e['radius_mm'],R)


if __name__=='__main__':unittest.main()
