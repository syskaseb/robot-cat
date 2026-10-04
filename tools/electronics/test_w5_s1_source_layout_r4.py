import math
import unittest
from w5_s1_source_layout_r4 import layout, ENTRY_Z, ENTRY_LEFT, ENTRY_RIGHT

class SourceLayout(unittest.TestCase):
    def test_nets_and_exact_entry_height(self):
        rows=layout()
        self.assertEqual([r['wire'] for r in rows],['W064','W065','W067','W068'])
        for row in rows:
            self.assertAlmostEqual(row['end'][2],64.8067)
            self.assertEqual(row['selected'],False)
            self.assertEqual(row['physical_pass'],False)
            self.assertGreaterEqual(row['nominal_trial_blank_mm'],row['exposed_path_mm']+52.73)

    def test_continuity_and_curvature(self):
        for row in layout():
            for edge in row['edges']:
                self.assertGreater(edge['length_mm'],0)
                if edge['kind']=='arc':
                    self.assertGreaterEqual(edge['radius_mm'],25.2)
                    self.assertAlmostEqual(edge['length_mm'],edge['radius_mm']*edge['angle_rad'])
            for a,b in zip(row['edges'],row['edges'][1:]):
                self.assertLess(math.dist(a['end'],b['start']),1e-7)

    def test_preserved_terminal_clocking(self):
        rows=layout()
        for row in rows:
            left=row['wire'] in ('W064','W067')
            self.assertAlmostEqual(row['end'][0],ENTRY_LEFT if left else ENTRY_RIGHT)
            self.assertAlmostEqual(row['end'][1],70 if row['wire'] in ('W064','W065') else 82)
        self.assertGreater(sum(r['nominal_trial_blank_mm'] for r in rows),920)

if __name__=='__main__':unittest.main()
