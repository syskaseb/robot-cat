import hashlib
import json
import unittest
import zipfile
import FreeCAD
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_power_pair_grip_roots import construct,construct_tails,isolated


class Power42(unittest.TestCase):
    def test_pinned_sources_rebuild_four_roots_without_mutating_inputs(self):
        packet=json.loads((OUT/'n01-power42-rooted-joint-space.json').read_text())
        archive=ROOT/packet['bundle'];self.assertEqual(sha(archive),packet['bundle_sha256'])
        actors={};inputs={}
        with zipfile.ZipFile(archive) as z:
            for index,target in [('geometry.json',actors),('inputs.json',inputs)]:
                for row in json.loads(z.read(index)):
                    raw=z.read(row['entry'])
                    self.assertEqual(hashlib.sha256(raw).hexdigest(),row['sha256'])
                    s=Part.Shape();s.importBrepFromString(raw.decode())
                    self.assertTrue(s.isValid());self.assertEqual(len(s.Solids),1)
                    target[row['name']]=s
            receipt=json.loads(z.read('received.json'))
        self.assertEqual(len(actors),42);self.assertEqual(len(inputs),23)
        before={n:hashlib.sha256(s.exportBrepToString().encode()).hexdigest() for n,s in inputs.items()}
        pair,pplan=construct(inputs);tails,tplan=construct_tails(inputs)
        for n,s in {**pair,**tails}.items():
            self.assertLess(isolated(s).cut(isolated(actors[n])).Volume+
                            isolated(actors[n]).cut(isolated(s)).Volume,1e-5)
        self.assertEqual(before,{n:hashlib.sha256(s.exportBrepToString().encode()).hexdigest() for n,s in inputs.items()})
        shapes=[isolated(actors[n] if n in actors else inputs[n])
                for n in receipt['one_common_print_actors']]
        whole=shapes[0].multiFuse(shapes[1:])
        self.assertTrue(whole.isValid());self.assertEqual(len(whole.Solids),1)
        self.assertLess(max(whole.BoundBox.XLength,whole.BoundBox.YLength,whole.BoundBox.ZLength),250)
        self.assertTrue(all(r['ok'] for r in receipt['new_four_roots_static']['checks'].values()))
        self.assertTrue(receipt['whole_outer']['ok'])
        self.assertTrue(all(v>=1.25 for v in receipt['global_sample36_Z_bounds_mm'].values()))
        self.assertEqual(receipt['canonical_low_rear_sample36']['status'],'UNION_SAMPLE36_RECEIVED')
        self.assertFalse(receipt['quarantined_live_parent']['selected'])
        self.assertFalse(packet['N01_complete']);self.assertFalse(packet['physical_pass'])


if __name__=='__main__':
    unittest.main()
