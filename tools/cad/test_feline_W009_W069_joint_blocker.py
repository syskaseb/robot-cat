"""Fresh-process proof of all five saved actual intersections."""
import json
import unittest
from plan_feline_layout import OUT
from check_main_p0_placement import ROOT,sha
from receive_feline_rrp_shared_height import load


class JointBlocker(unittest.TestCase):
    def test_saved_actual_solids_reproduce_each_intersection(self):
        p=json.loads((OUT/'n01-W009-W069-joint-blocker.json').read_text())
        for name,h in p['source_sha256'].items():self.assertEqual(sha(ROOT/name),h,name)
        shapes=load(p)
        self.assertEqual(len(shapes),7)
        self.assertEqual(len(p['witnesses']),5)
        for witness in p['witnesses']:
            a,b=witness['pair'].split('|')
            self.assertTrue(shapes[a].isValid() and shapes[b].isValid())
            volume=shapes[a].copy().common(shapes[b].copy()).Volume
            self.assertGreater(volume,1e-5)
            self.assertAlmostEqual(volume,witness['common_mm3'],places=5)
        self.assertFalse(p['whole_scene_received'])
        self.assertFalse(p['N01_complete'])
        self.assertFalse(p['physical_pass'])
        self.assertTrue(p['unrecovered_scene_actors'])


if __name__=='__main__':unittest.main()
