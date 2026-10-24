"""Receipt integrity and explicit scope, not a replacement for CAD motion proof."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.r=json.loads((OUT/'n01-USB-lift-bridge-five-poses-20261024.json').read_text())

    def test_length_and_sampled_curvature(self):
        self.assertEqual([r['lift_mm'] for r in self.r['poses']],[0,2.5,5,7.5,10])
        for row in self.r['poses']:
            self.assertAlmostEqual(row['jacket_length_mm'],452,places=5)
            self.assertTrue(row['turn_regular'])
            self.assertGreaterEqual(row['minimum_turn_R_mm'],30)
        self.assertLess(self.r['endpoint_max_deviation_mm'],1e-6)

    def test_no_sample_promoted_to_full_motion(self):
        for key in ['continuous_motion_received','whole_scene_received','N01_complete','physical_pass']:
            self.assertFalse(self.r[key])
        self.assertTrue(self.r['open'])
        self.assertEqual(self.r['errors'],{})
        self.assertTrue(self.r['containment_guard_passed'])
        self.assertTrue(self.r['checks'])
        self.assertTrue(all(v['ok'] for v in self.r['checks'].values()))

    def test_source_pin(self):
        for name,digest in self.r['source_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),digest)


if __name__=='__main__':
    unittest.main()
