"""Validate recorded whole-amplitude bound and narrow service exceptions."""
import hashlib
import json
from pathlib import Path
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'


class SideBowTests(unittest.TestCase):
    def setUp(self):
        self.r=json.loads((OUT/'n01-USB-side-bow-20261024.json').read_text())

    def test_length_radius_and_outline(self):
        r=self.r
        self.assertAlmostEqual(r['recipe']['jacket_length_mm'],452,places=5)
        self.assertGreaterEqual(r['family_curvature_bound']['minimum_R_lower_bound_mm'],30)
        self.assertTrue(r['family_curvature_bound']['covers_all_amplitudes_from_zero'])
        self.assertTrue(r['point_inside_true_outer'])
        self.assertGreater(r['jacket_gap_to_true_outer_boundary_mm'],1.25)

    def test_only_mutually_exclusive_access_not_parts(self):
        r=self.r;exceptions=r['mutually_exclusive_ATO_access']
        self.assertEqual(len(exceptions),7)
        for name,row in exceptions.items():
            self.assertTrue(name.startswith('Service:'))
            self.assertEqual(row['kind'],'project_access_reservation')
            self.assertEqual(row['group'],'ATO_service')
        self.assertEqual(r['errors'],{})
        self.assertTrue(all(v['ok'] for n,v in r['checks'].items() if n not in exceptions))
        for flag in ['whole_USB_service_received','selected_geometry_changed','N01_complete','physical_pass']:
            self.assertFalse(r[flag])

    def test_reopen_and_sources(self):
        r=self.r
        for name,digest in r['source_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),digest)
        self.assertEqual(hashlib.sha256((ROOT/r['bundle']).read_bytes()).hexdigest(),r['bundle_sha256'])
        with zipfile.ZipFile(ROOT/r['bundle']) as z:
            for row in r['geometry']:
                self.assertTrue(row['strict_reopen'])
                self.assertEqual(hashlib.sha256(z.read(row['entry'])).hexdigest(),row['sha256'])


if __name__=='__main__':
    unittest.main()
