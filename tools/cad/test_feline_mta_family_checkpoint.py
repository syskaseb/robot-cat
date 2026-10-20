"""Static acceptance must not hide sampled-motion failures or award N01."""
import gzip,json,unittest
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT


class FamilyCheckpoint(unittest.TestCase):
    def test_static_does_not_qualify_motion(self):
        r=json.loads((OUT/'n01-MTA-four-fans-received.json').read_text())
        for p,h in r['source_sha256'].items():self.assertEqual(sha(ROOT/p),h,p)
        self.assertEqual(sha(ROOT/r['pair_rows']),r['pair_rows_sha256'])
        rows=json.loads(gzip.decompress((ROOT/r['pair_rows']).read_bytes()))
        static={k:v for k,v in rows.items() if '|motion:' not in k}
        self.assertEqual(len(static),129);self.assertTrue(all(v['ok'] for v in static.values()))
        self.assertEqual(len(r['inherited_own_grip_pairs']),2)
        for row in r['inherited_own_grip_pairs'].values():
            self.assertTrue(row['old_gap_NOT_inherited'])
            self.assertAlmostEqual(row['actual_current_gap_mm'],1.2)
            self.assertAlmostEqual(row['original_own_grip_gap_mm'],1.45)
            self.assertLess(row['actual_current_common_mm3'],1e-5)
            self.assertEqual(row['foreign_margin_unchanged_mm'],1.25)
        self.assertGreater(len(r['failures']),0)
        self.assertTrue(all('|motion:' in k for k in r['failures']))
        self.assertFalse(r['N01_complete']);self.assertFalse(r['native_changed'])
        self.assertTrue(r['whole_custom_grips_roots_moved_case_kits_tools_and_common123_still_OPEN'])


if __name__=='__main__':unittest.main()
