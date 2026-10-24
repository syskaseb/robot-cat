"""Current routes must not disappear behind a historical recovery cache."""
import hashlib,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'

class ServiceContext(unittest.TestCase):
    def test_received_deltas_and_no_false_acceptance(self):
        r=json.loads((OUT/'n01-current-service-context-20261024.json').read_text())
        self.assertEqual(r['count_after']-r['count_before'],7)
        self.assertEqual(len(r['owners']),32)
        self.assertEqual(set(r['excluded_proof_shapes']),{'MotionProof:Trunk','MotionProof:Branch'})
        for wire in ('W009','W031','W033','W035','W046','W047','W069'):
            self.assertIn('CurrentMiddle:'+wire,r['added_names'])
        for p,h in r['source_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),h)
        self.assertFalse(r['N01_complete'])
        self.assertFalse(r['stationary_GPIO_proposal_current_clearance_received'])
        self.assertTrue(r['strict_common_failed'])
        self.assertEqual(r['lower_W035_fresh_distance_mm'],0)

    def test_motor_end_is_one_three_core_connector(self):
        r=json.loads((OUT/'n01-FR2-motor-end-service-20261024.json').read_text())
        self.assertEqual({v['wire'] for v in r['cores'].values()},{'W009','W032','W033'})
        self.assertEqual(r['received']['holds'],[])
        self.assertEqual(r['received']['errors'],{})
        self.assertFalse(r['N01_complete']);self.assertFalse(r['selected'])
        self.assertFalse(r['project_only']['supplier_fit_and_latch_geometry_verified'])
        self.assertTrue(r['open'])

if __name__=='__main__':unittest.main()
