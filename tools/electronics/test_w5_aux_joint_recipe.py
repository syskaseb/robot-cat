import json
import math
import unittest
from pathlib import Path
from w5_aux_diagonal_loop_r3 import recipe


class AuxJointRecipeTests(unittest.TestCase):
    def test_registered_ports_and_cage_straights(self):
        root=Path(__file__).resolve().parents[2]
        family=json.loads((root/'hardware/electronics/full-cat/w5-central-bridge-low-arc-r1/received-family.json').read_text(encoding='utf-8'))
        r=recipe(family,[110.5,-57,113.5])
        self.assertLess(math.dist(r['edges'][0]['start'],family['ends']['XA05']['edges'][0]['start']),1e-7)
        self.assertEqual(r['edges'][-1]['end'],[110.5,-57,113.5])
        self.assertAlmostEqual(r['edges'][-1]['length_mm'],6)
        self.assertTrue(all(math.dist(a['end'],b['start'])<1e-7 for a,b in zip(r['edges'],r['edges'][1:])))
        self.assertTrue(all(e['radius_mm']>=15 for e in r['edges'] if e['kind']=='arc'))


if __name__=='__main__':unittest.main()
