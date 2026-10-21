import hashlib,json,unittest,zipfile
import FreeCAD
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_fl_common_arc_bay import construct,power_band_above_feeder,continue_inner_gallery


class FLArcBay(unittest.TestCase):
    def test_fresh_rebuild_all12_full9_and_immutable_parent(self):
        p=json.loads((OUT/'n01-FL9-common-arc-rooted-space.json').read_text());self.assertEqual(sha(ROOT/p['bundle']),p['bundle_sha256'])
        shapes={}
        with zipfile.ZipFile(ROOT/p['bundle']) as z:
            for row in p['geometry']:
                raw=z.read(row['entry']);self.assertEqual(hashlib.sha256(raw).hexdigest(),row['sha256'])
                s=Part.Shape();s.importBrepFromString(raw.decode());shapes[row['name']]=s
        parent=shapes['Input:parent'];before=parent.exportBrepToString()
        a,r=construct(p['constructor_rows'],p['constructor_profiles'],parent)
        a,r=power_band_above_feeder(a,r);a,r=continue_inner_gallery(a,r)
        self.assertEqual(before,parent.exportBrepToString());self.assertEqual(len(a),12)
        for name,s in a.items():
            self.assertTrue(s.isValid());self.assertEqual(len(s.Solids),1)
            old=shapes[name];self.assertAlmostEqual(s.Volume,old.Volume,places=5)
            self.assertAlmostEqual(s.common(old).Volume,old.Volume,places=5)
        for name,row in r['recipes'].items():
            self.assertEqual(row['first9_arclength_mm'],[0,9])
            self.assertGreaterEqual(row['parts'][0]['length_mm'],10.5)
            self.assertTrue(all(e['kind']=='line' or e['radius_mm']>=12.4-1e-6 for e in row['parts']))
        self.assertTrue(all(v['ok'] for v in p['checks'].values()))
        self.assertTrue(all(v['ok'] for v in p['outer'].values()))
        self.assertFalse(p['N01_complete']);self.assertFalse(p['physical_pass'])
        self.assertGreater(p['parent_joint_mm3'],0);self.assertLess(max(p['shared_print_envelope_mm']),250)


if __name__=='__main__':unittest.main()
