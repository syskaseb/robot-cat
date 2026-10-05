import json
import math
import unittest
from pathlib import Path
from w5_four_low_returns import recipes
from w5_coupled_corridors_r3 import contract


class LowReturnTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root=Path(__file__).resolve().parents[2]
        family=json.loads((root/'hardware/electronics/full-cat/w5-central-bridge-low-arc-r1/received-family.json').read_text(encoding='utf-8'))
        cls.rows=recipes(family,contract()[1])

    def test_all_four_whole_routes_keep_registered_ends(self):
        self.assertEqual({r['wire'] for r in self.rows},{'W025','W036','W062','W063'})
        for r in self.rows:
            self.assertLess(math.dist(r['edges'][0]['start'],r['central_start']),1e-7)
            self.assertLess(math.dist(r['edges'][-1]['end'],r['leg_end']),1e-7)
            self.assertTrue(all(math.dist(a['end'],b['start'])<1e-7 for a,b in zip(r['edges'],r['edges'][1:])))

    def test_exact_radius_and_no_high_vertical_departure(self):
        for r in self.rows:
            self.assertTrue(all(e['radius_mm']>=21 for e in r['edges'] if e['kind']=='arc'))
            self.assertTrue(all(max(e['start'][2],e['end'][2])<=169.5+1e-7 for e in r['edges']))
            self.assertEqual(r['edges'][0]['start'][2],r['edges'][1]['end'][2])


if __name__=='__main__':unittest.main()
