"""Keep partial access evidence distinct from whole-layout acceptance."""
import hashlib,json,unittest,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'

class AccessReceipt(unittest.TestCase):
    def test_partial_and_length_gate(self):
        r=json.loads((OUT/'n01-D_FR-side-access-20261024.json').read_text())
        self.assertFalse(r['N01_complete']);self.assertFalse(r['selected'])
        self.assertFalse(r['physical_pass'])
        self.assertFalse(r['recipe']['factory900_whole_length_allocation_received'])
        self.assertEqual(r['recipe']['extra_per_lead_mm'],15)
        self.assertEqual(r['recipe']['prefix_length_mm'],39.25)
        self.assertGreater(r['evidence']['actual_lead3_flange_common_mm3'],2.9)
        self.assertEqual(r['evidence']['lever_hand_subset']['holds'],[])
        self.assertEqual(r['evidence']['lever_hand_subset']['errors'],{})
        self.assertGreater(r['evidence']['missing_actor_count'],0)
        self.assertEqual(len(r['geometry']),8)
        self.assertEqual(hashlib.sha256((ROOT/'tools/cad/plan_feline_dfr_joint_access.py').read_bytes()).hexdigest(),r['constructor_sha256'])
        archive=OUT/r['bundle']
        self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(),r['bundle_sha256'])
        with zipfile.ZipFile(archive) as z:
            for row in r['geometry']:
                self.assertTrue(row['strict_reopen'])
                self.assertEqual(hashlib.sha256(z.read(row['entry'])).hexdigest(),row['sha256'])

if __name__=='__main__':unittest.main()
