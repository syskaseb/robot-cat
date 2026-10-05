"""Pure geometry checks before FreeCAD sweeps."""
import json
import math
import unittest
from w5_central_south_bridge import recipe
from w5_central_shared_routes import FAMILY


class SouthBridge(unittest.TestCase):
    def setUp(self):
        self.family=json.loads(FAMILY.read_text(encoding='utf-8'))
        self.row=recipe(self.family)

    def test_exact_tip_and_tangent(self):
        edges=self.row['bridge_edges']
        self.assertLess(math.dist(edges[0]['start'],self.family['ends']['W061_A']['tip']),1e-7)
        self.assertLess(math.dist(edges[-1]['end'],self.family['ends']['W061_B']['tip']),1e-7)

    def test_radii_and_low_plane(self):
        for edge in self.row['bridge_edges']:
            if edge['kind']=='arc':
                self.assertEqual(edge['radius_mm'],21)
            self.assertGreater(edge['length_mm'],0)
            self.assertLessEqual(max(edge['start'][2],edge['end'][2]),161.500001)

    def test_south_departure_not_old_vertical_crossing(self):
        e=self.row['bridge_edges'][0]
        self.assertEqual(e['kind'],'arc')
        self.assertLess(e['end'][1],e['start'][1])
        self.assertEqual(len(self.row['bridge_edges']),6)


if __name__=='__main__':
    unittest.main()
