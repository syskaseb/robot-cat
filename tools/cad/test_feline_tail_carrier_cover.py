"""Receipt integrity; explicitly keep the DC margin and whole sequence open."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'


class CoverTests(unittest.TestCase):
    def setUp(self):
        self.r=json.loads((OUT/'n01-USB-unplug-tail-cover-20261024.json').read_text())

    def test_complete_cover_separated(self):
        r=self.r
        self.assertEqual(r['cover_constituents'],len(r['gaps_mm']))
        self.assertGreater(r['minimum_gap_mm'],r['minimum_required_mm'])
        self.assertEqual(r['minimum_gap_mm'],min(r['gaps_mm'].values()))
        self.assertTrue(r['strict_valid_constituents'])
        for name in ['old_tail','anchor','D:uncut_saddle','G:uncut_saddle']:
            self.assertIn(name,r['gaps_mm'])

    def test_no_invalid_repair_or_whole_acceptance(self):
        r=self.r
        self.assertTrue(r['source_union_still_invalid'])
        self.assertTrue(r['DC_project_margin_not_met'])
        self.assertLess(r['DC_conservative_nominal_gap_mm'],.5)
        self.assertFalse(r['dc_original_strict_valid'])
        for flag in ['selected_geometry_changed','N01_complete','physical_pass']:
            self.assertFalse(r[flag])

    def test_source_pins(self):
        self.assertTrue(self.r['source_native_matches_core_pin'])
        for name,digest in self.r['source_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),digest)


if __name__=='__main__':
    unittest.main()
