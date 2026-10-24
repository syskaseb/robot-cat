"""Bounded receipt checks; no whole-scene or physical qualification implied."""
import hashlib
import json
from pathlib import Path
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'


class CounterholdTests(unittest.TestCase):
    def setUp(self):
        self.r=json.loads((OUT/'n01-GPIO-distal-counterhold-20261024.json').read_text())

    def test_partial_and_both_rejections_preserved(self):
        r=self.r;e=r['evidence']
        for flag in ['selected','N01_complete','physical_pass']:
            self.assertFalse(r[flag])
        self.assertTrue(e['rejected_nylon_side']['holds'])
        self.assertTrue(e['rejected_nylon_front']['holds'])
        self.assertTrue(r['recipe']['open'])

    def test_changed_clip_not_old_w035_hold(self):
        e=self.r['evidence']
        self.assertEqual(e['space']['holds'],[])
        self.assertEqual(e['space']['errors'],{})
        self.assertTrue(e['Pi_lift_0_to_10']['accepted'])
        self.assertEqual(e['bench_driver']['holds'],[])
        self.assertGreater(e['whole_lower_W035_gap_mm'],1.25)
        self.assertGreater(e['root_overlap_mm3'],0)

    def test_saved_geometry_and_constructor_pinned(self):
        r=self.r;p=OUT/r['bundle']
        self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),r['bundle_sha256'])
        self.assertEqual({row['name'] for row in r['geometry']},
                         {'lower','upper','front_jaw','screw_budget'})
        with zipfile.ZipFile(p) as z:
            for row in r['geometry']:
                self.assertTrue(row['strict_reopen'])
                self.assertEqual(hashlib.sha256(z.read(row['entry'])).hexdigest(),row['sha256'])
        source=ROOT/'tools/cad/plan_feline_gpio_end_counterhold.py'
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),r['constructor_sha256'])

    def test_recovered_neighbors_do_not_claim_complete_scene(self):
        r=json.loads((OUT/'n01-service-bound-actors-restored-20261024.json').read_text())
        self.assertEqual(len(r['restored']),174)
        self.assertEqual(len(r['unbound']),102)
        self.assertFalse(r['whole_scene_received'])
        self.assertFalse(r['N01_complete'])
        self.assertEqual(r['clip_delta']['holds'],[])
        self.assertEqual(r['clip_delta']['errors'],{})
        for name,digest in r['source_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),digest)
        bad=r['invalid_TypeC_separation_only']
        self.assertFalse(bad['raw_and_native25_strict_valid'])
        self.assertTrue(bad['not_an_acceptance_of_invalid_BRep'])
        self.assertGreater(bad['minimum_new_clip_gap_to_full_catalog_envelope_mm'],1.25)


if __name__=='__main__':
    unittest.main()
