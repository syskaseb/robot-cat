import math
import json
import unittest
from pathlib import Path
from w5_front_paired_flights import recipes
from w5_coupled_corridors_r3 import contract


class FrontPairedFlightsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root=Path(__file__).resolve().parents[2]
        family=json.loads((root/'hardware/electronics/full-cat/w5-central-bridge-low-arc-r1/received-family.json').read_text(encoding='utf-8'))
        cls.rows=recipes(family,contract()[1])

    def test_full_endpoints_necks_and_joins(self):
        for row in self.rows:
            self.assertLess(math.dist(row['edges'][0]['start'],row['central_start']),1e-7)
            self.assertLess(math.dist(row['edges'][-1]['end'],row['leg_target']),1e-7)
            self.assertAlmostEqual(row['edges'][-1]['length_mm'],6)
            self.assertTrue(all(math.dist(a['end'],b['start'])<1e-7 for a,b in zip(row['edges'],row['edges'][1:])))

    def test_dimensioned_flights_do_not_repeat_blocked_risers(self):
        for row in self.rows:
            self.assertTrue(all(e['radius_mm']>=21 for e in row['edges'] if e['kind']=='arc'))
            self.assertEqual(row['edges'][3]['kind'],'arc')
            self.assertLess(row['edges'][3]['end'][1],row['edges'][3]['start'][1])
            self.assertTrue(all(max(e['start'][2],e['end'][2])<=169.5+1e-7 for e in row['edges']))


if __name__=='__main__':unittest.main()
