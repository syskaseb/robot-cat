import json
import math
import unittest
from pathlib import Path
from w5_main_ground_low_return_r3 import recipe as main_recipe
from w5_bus_factory900_r4 import recipe as bus_recipe
from w5_front_paired_flights_r2 import recipes as front_recipes
from w5_coupled_corridors_r3 import contract


class RemainingCentralRecipesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root=Path(__file__).resolve().parents[2]
        cls.family=json.loads((root/'hardware/electronics/full-cat/w5-central-bridge-low-arc-r1/received-family.json').read_text(encoding='utf-8'))
        cls.bus_source=json.loads((root/'hardware/electronics/full-cat/w5-bus-pair-r52-r4/intent.json').read_text(encoding='utf-8'))['source_lead_datums']['W003']

    def test_main_preserves_cage_and_tail_with_diagonal_departure(self):
        r=main_recipe(self.family)
        self.assertEqual(r['edges'][0]['start'],self.family['ends']['W060']['edges'][0]['start'])
        self.assertLess(math.dist(r['edges'][-1]['end'],[132.5,0,95]),1e-7)
        self.assertAlmostEqual(r['edges'][0]['length_mm'],6)
        self.assertAlmostEqual(r['edges'][1]['end'][0],60)
        self.assertTrue(all(e['radius_mm']>=10 for e in r['edges'] if e['kind']=='arc'))

    def test_bus_corridor_is_between_actual_material_limits(self):
        r=bus_recipe(self.family,self.bus_source)
        self.assertAlmostEqual(r['edges'][6]['start'][2],148.6)
        self.assertAlmostEqual(r['edges'][6]['end'][2],148.6)
        self.assertAlmostEqual(148.6-1-146.75,.85)
        self.assertAlmostEqual(150.45-148.6-1,.85)

    def test_bus_has_whole_factory_blank_and_no_splice(self):
        r=bus_recipe(self.family,self.bus_source)
        self.assertLessEqual(r['trial_blank_mm'],900)
        self.assertLess(math.dist(r['edges'][-1]['end'],self.bus_source),1e-7)
        self.assertGreaterEqual(r['source_end_straight_mm'],6)
        self.assertTrue(all(e['radius_mm']>=10 for e in r['edges'] if e['kind']=='arc'))

    def test_front_pair_r2_keeps_complete_registered_ports(self):
        for r in front_recipes(self.family,contract()[1]):
            self.assertLess(math.dist(r['edges'][-1]['end'],r['leg_target']),1e-7)
            self.assertAlmostEqual(r['edges'][-1]['length_mm'],6)
            self.assertTrue(all(math.dist(a['end'],b['start'])<1e-7 for a,b in zip(r['edges'],r['edges'][1:])))


if __name__=='__main__':unittest.main()
