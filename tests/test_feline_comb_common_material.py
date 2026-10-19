import json
from pathlib import Path
import sys
import unittest
import FreeCAD as A
import Part
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/cad'))
from feline_shared_straight_combs import slots
from feline_comb_common_material import common_bottom_wall


class SharedActualWall(unittest.TestCase):
    def test_full_family_subset_not_bbox_collision(self):
        source = ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/n01-flat-station-architecture.json'
        stations = [s for s in json.loads(source.read_text())['stations']
                    if s['flat_dimensions_pitch_departure_thickness_mm'][2] < 10]
        self.assertEqual(len(stations), 16)
        for side in (-1, 1):
            slot = next(s for s in slots() if s['profile']=='standard'
                        and s['side']==side and s['tier']=='interdeck')
            wall, proof = common_bottom_wall(stations, slot, 1)
            self.assertGreater(wall.Volume, 1)
            self.assertEqual(len(proof), 16)
            self.assertTrue(all(p['outside_mm3'] < 1e-7 for p in proof))


if __name__ == '__main__':
    unittest.main()
