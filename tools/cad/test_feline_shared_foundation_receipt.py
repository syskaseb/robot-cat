"""Current planning evidence, never native/strength/physical qualification."""
import hashlib,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'


class FoundationReceipt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=json.loads((OUT/'n01-channelled-foundation-static.json').read_text())
    def test_complete_actual_pieces_not_n01(self):
        r=self.r;self.assertEqual(r['status'],'COMMON_FOUNDATION_CLEAR_NOT_ALL_ROOTS')
        self.assertEqual(len(r['parts']),35);self.assertFalse(r['errors'])
        self.assertTrue(all('failure' in q and q['failure'] is None for q in r['parts'].values()))
        self.assertFalse(r['N01_complete']);self.assertFalse(r['native_changed']);self.assertFalse(r['physical_pass'])
    def test_all_real_clamp_and_housing_bearings(self):
        self.assertEqual({r['clamp'] for r in self.r['mates']},{1,2,3,4})
        for r in self.r['mates']:
            self.assertGreaterEqual(r['pad_bearing_area_after_channels_mm2'],60)
            self.assertGreater(r['washer_bearing_after_channels_mm2'],10)
        pads=self.r['construction']['actual_bank_bearing'];self.assertEqual(len(pads),12)
        self.assertEqual(len({p['owner'] for p in pads}),12)
        for p in pads:
            self.assertGreater(p['actual_after_channels_bearing_mm2'],5)
            self.assertLess(p['positive_common_mm3'],1e-7)
    def test_inputs_and_new_material_only(self):
        for n,h in self.r['source_sha256'].items():self.assertEqual(hashlib.sha256((ROOT/n).read_bytes()).hexdigest(),h,n)
        archive=ROOT/self.r['bundle'];self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(),self.r['bundle_sha256'])
        change=self.r['kernel_topology_cause_change'];self.assertEqual(change['part'],'BankLedge:2')
        self.assertEqual(change['source_outside_original_mm3'],0)
        self.assertEqual(change['common_with_expanded_target_box_mm3'],0)
        self.assertGreaterEqual(change['gap_mm'],1.25)
        self.assertGreater(change['actual_positive_connection_count'],0)
        self.assertFalse(self.r['construction']['purchased_material_edited'])


if __name__=='__main__':unittest.main()
