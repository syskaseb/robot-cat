import hashlib,json,unittest,zipfile
import FreeCAD
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_rl_common_arc_bay import construct


class RLArcBay(unittest.TestCase):
    def test_rebuild_full12_and_immutable_parent(self):
        p=json.loads((OUT/'n01-RL9-common-arc-rooted-space.json').read_text());shapes={}
        self.assertEqual(sha(ROOT/p['bundle']),p['bundle_sha256'])
        with zipfile.ZipFile(ROOT/p['bundle']) as z:
            for r in p['geometry']:
                raw=z.read(r['entry']);self.assertEqual(hashlib.sha256(raw).hexdigest(),r['sha256'])
                s=Part.Shape();s.importBrepFromString(raw.decode());shapes[r['name']]=s
        parent=shapes['Input:parent'];before=parent.exportBrepToString()
        actors,plan=construct(p['constructor_rows'],p['constructor_profiles'],parent)
        self.assertEqual(before,parent.exportBrepToString());self.assertEqual(len(actors),12)
        for n,s in actors.items():
            self.assertTrue(s.isValid());self.assertEqual(len(s.Solids),1)
            self.assertAlmostEqual(s.Volume,shapes[n].Volume,places=5)
            self.assertAlmostEqual(s.common(shapes[n]).Volume,shapes[n].Volume,places=5)
        for r in plan['recipes'].values():
            self.assertEqual(r['first9_arclength_mm'],[0,9]);self.assertGreaterEqual(r['parts'][0]['length_mm'],10.5)
            self.assertGreaterEqual(r['parts'][0]['radius_mm'],12.4-1e-6)
        self.assertGreater(plan['parent_joint_mm3'],0)
        self.assertTrue(all(r['ok'] for r in p['checks'].values()))
        self.assertTrue(all(r['ok'] for r in p['outer'].values()))
        self.assertFalse(p['N01_complete']);self.assertFalse(p['physical_pass'])


if __name__=='__main__':unittest.main()
