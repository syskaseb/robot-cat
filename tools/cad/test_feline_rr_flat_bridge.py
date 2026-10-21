import hashlib,json,unittest,zipfile
import FreeCAD
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_rr_flat_bank_bridge import construct


class RRFlatBridge(unittest.TestCase):
    def test_full21_rebuild_width_bends_and_immutable_parent(self):
        p=json.loads((OUT/'n01-RR9-flat-common-bank-bridge.json').read_text());shapes={}
        self.assertEqual(sha(ROOT/p['bundle']),p['bundle_sha256'])
        with zipfile.ZipFile(ROOT/p['bundle']) as z:
            for r in p['geometry']:
                raw=z.read(r['entry']);self.assertEqual(hashlib.sha256(raw).hexdigest(),r['sha256'])
                s=Part.Shape();s.importBrepFromString(raw.decode());shapes[r['name']]=s
        parent=shapes['Input:parent'];before=parent.exportBrepToString()
        a,b,plan=construct(p['constructor_rows'],p['constructor_profiles'],parent)
        self.assertEqual(before,parent.exportBrepToString());self.assertEqual(len(a)+len(b),21)
        self.assertAlmostEqual(plan['full_section_width_mm'],26.2)
        self.assertAlmostEqual(plan['section_centre_Z_mm'],85.8)
        for n,s in {**a,**b}.items():
            self.assertTrue(s.isValid());self.assertEqual(len(s.Solids),1)
            self.assertAlmostEqual(s.Volume,shapes[n].Volume,places=5)
            self.assertAlmostEqual(s.common(shapes[n]).Volume,shapes[n].Volume,places=5)
        for r in plan['recipes'].values():
            self.assertEqual(r['parts'][0]['length_mm'],9)
            self.assertGreaterEqual(r['resource_parts'][1]['radius_mm'],12.4-1e-6)
            self.assertEqual(r['resource_end_axis'],[0.,1.,0.]);self.assertEqual(r['resource_end_mm'][1],-28)
        self.assertTrue(all(r['ok'] for r in p['checks'].values()));self.assertTrue(all(r['ok'] for r in p['outer'].values()))
        self.assertFalse(p['N01_complete']);self.assertFalse(p['physical_pass'])


if __name__=='__main__':unittest.main()
