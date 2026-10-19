"""Both complete retained FHAC interfaces in the current shared scene."""
import hashlib,json,math,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'


class RemainingInline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=json.loads((OUT/'n01-remaining-inline-body-closure.json').read_text())
    def test_whole36_and_four_both_side_recipes(self):
        self.assertEqual(self.r['status'],'TWO_WHOLE_INLINE_KITS_RECEIVED_ROOTS_CORRIDORS_OPEN')
        self.assertEqual(len(self.r['parts']),36);self.assertFalse(self.r['errors'])
        self.assertTrue(all(r['failure'] is None for r in self.r['parts'].values()))
        self.assertEqual({r['endpoint'] for r in self.r['recipes']},{'F_HP.in','F_HP.out','F_TY.in','F_TY.out'})
        for r in self.r['recipes']:
            self.assertAlmostEqual(math.dist(*r['factory_grip9_mm']),9)
            self.assertAlmostEqual(math.dist(*r['custom_grip9_mm']),9)
            self.assertEqual(r['solder_overlap_mm'],8)
            self.assertLess(r['nominal_external_factory_cut_mm'],r['available_factory_min_reference_mm'])
    def test_reuse_not_promoting_negatives(self):
        p=self.r['geometry_reuse'];self.assertEqual(p['unchanged'],32)
        self.assertEqual(p['complete_changed_heads_recheck'],4)
        self.assertTrue(p['negative_receipts_never_promoted'])
        for n,r in self.r['parts'].items():
            if ':custom:head_budget' in n:
                self.assertTrue(r['pairs']);self.assertTrue(all(v['ok'] for v in r['pairs'].values()))
        self.assertFalse(self.r['N01_complete']);self.assertFalse(self.r['physical_pass']);self.assertFalse(self.r['native_changed'])
    def test_pinned_actual_packet(self):
        for n,h in self.r['source_sha256'].items():self.assertEqual(hashlib.sha256((ROOT/n).read_bytes()).hexdigest(),h,n)
        self.assertEqual(hashlib.sha256((ROOT/self.r['bundle']).read_bytes()).hexdigest(),self.r['bundle_sha256'])


if __name__=='__main__':unittest.main()
