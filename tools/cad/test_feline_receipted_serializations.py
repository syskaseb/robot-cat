import json
import unittest
from recover_feline_receipted_serializations import eligible, OUT, ROOT, sha


class RecoveryTests(unittest.TestCase):
    def test_requires_both_exact_hash_links_and_missing_membership(self):
        receipt = dict(previous_bridge=dict(source_geometry_sha256={'x': 'old'}),
                       current_source_geometry_sha256={'x': 'new'})
        self.assertTrue(eligible('x', 'old', {'x'}, {'x': 'new'}, receipt))
        self.assertFalse(eligible('x', 'other', {'x'}, {'x': 'new'}, receipt))
        self.assertFalse(eligible('x', 'old', {'x'}, {'x': 'other'}, receipt))
        self.assertFalse(eligible('x', 'old', set(), {'x': 'new'}, receipt))

    def test_saved_scope_and_provenance(self):
        p = json.loads((OUT/'W009-W069-harness-corridor/receipted-serialization-recovery.json').read_text())
        self.assertEqual(len(p['geometry']), 101)
        self.assertEqual(len(p['unrecovered']), 175)
        self.assertFalse(p['N01_complete'])
        self.assertFalse(p['whole_scene_received'])
        self.assertEqual(sha(ROOT/p['bundle']), p['bundle_sha256'])
        for path, digest in p['source_sha256'].items():
            self.assertEqual(sha(ROOT/path), digest, path)


if __name__ == '__main__':
    unittest.main()
