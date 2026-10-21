import hashlib,json,unittest,zipfile
import FreeCAD
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_rr_outer_spine import construct


class RRServiceSpine(unittest.TestCase):
    def test_rebuild_whole21_source_resource_and_immutable_parent(self):
        p=json.loads((OUT/'n01-RR9-service-spine-rooted-space.json').read_text())
        self.assertEqual(sha(ROOT/p['bundle']),p['bundle_sha256']);shapes={}
        with zipfile.ZipFile(ROOT/p['bundle']) as z:
            for r in p['geometry']:
                raw=z.read(r['entry']);self.assertEqual(hashlib.sha256(raw).hexdigest(),r['sha256'])
                s=Part.Shape();s.importBrepFromString(raw.decode());shapes[r['name']]=s
        parent=shapes['Input:AuxGrip:CommonRoot'];before=parent.exportBrepToString()
        actors,resources,plan=construct(p['constructor_rows'],p['constructor_profiles'],parent)
        self.assertEqual(before,parent.exportBrepToString());self.assertEqual(len(actors)+len(resources),21)
        for n,s in {**actors,**resources}.items():
            self.assertTrue(s.isValid());self.assertEqual(len(s.Solids),1)
            self.assertAlmostEqual(s.Volume,shapes[n].Volume,places=5)
            self.assertAlmostEqual(s.common(shapes[n]).Volume,shapes[n].Volume,places=5)
        for r in plan['recipes'].values():
            self.assertEqual(r['parts'][0]['length_mm'],9)
            self.assertEqual(r['resource_end_mm'][0],r['actual_target_exit_mm'][0])
            self.assertEqual(r['common_section_translation_mm'],[0.,2.,4.549999999999997])
            self.assertTrue(r['resource_is_capacity_NOT_wire_cut'])
            self.assertTrue(all(e['kind']=='line' or e['radius_mm']>=12.4-1e-6 for e in r['resource_parts']))
        self.assertTrue(all(r['ok'] for r in p['checks'].values()))
        self.assertTrue(all(r['ok'] for r in p['outer'].values()))
        self.assertTrue(all(r['common_mm3']>0 for r in p['positive_shared_print_graph']))
        self.assertFalse(p['N01_complete']);self.assertFalse(p['physical_pass'])


if __name__=='__main__':unittest.main()
