import math
import unittest
from w5_s1_source_layout_r5 import layout

class SourceApproaches(unittest.TestCase):
    def test_four_nets_continuity_and_blanks(self):
        rows=layout()
        self.assertEqual(len(rows),4)
        for row in rows:
            self.assertFalse(row['selected']);self.assertFalse(row['physical_pass'])
            self.assertAlmostEqual(row['end'][2],64.8067)
            self.assertGreaterEqual(row['nominal_trial_blank_mm'],row['exposed_path_mm']+52.73)
            for a,b in zip(row['edges'],row['edges'][1:]):
                self.assertLess(math.dist(a['end'],b['start']),1e-7)
            for edge in row['edges']:
                self.assertGreater(edge['length_mm'],0)
                if edge['kind']=='arc':self.assertGreaterEqual(edge['radius_mm'],25.2)

    def test_real_three_dimensional_rear_approach(self):
        row=next(r for r in layout() if r['wire']=='W065')
        first=row['edges'][0]
        self.assertEqual(first['kind'],'arc')
        self.assertLess(first['end'][1],first['start'][1])
        self.assertLess(first['end'][2],first['start'][2])
        self.assertAlmostEqual(row['edges'][1]['angle_rad'],math.pi/6)

    def test_disclosed_upper_envelope(self):
        rows=layout()
        self.assertEqual(sum(r['nominal_trial_blank_mm'] for r in rows),2530)
        upper=max(p[2] for r in rows for e in r['edges'] for p in (e['start'],e['end']))
        self.assertAlmostEqual(upper,199.2)
        self.assertGreater(upper,185)

if __name__=='__main__':unittest.main()
