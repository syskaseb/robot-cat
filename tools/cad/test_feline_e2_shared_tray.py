import hashlib
import json
import unittest
import zipfile
import FreeCAD
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_e2_shared_tray import construct


class E2Tray(unittest.TestCase):
    def test_actual_pad_footprints_and_existing_frame_rebuild(self):
        packet=json.loads((OUT/'n01-E2-common-tray.json').read_text())
        archive=ROOT/packet['bundle']
        self.assertEqual(sha(archive),packet['bundle_sha256'])
        inputs={};actors={}
        with zipfile.ZipFile(archive) as z:
            for index,target in [('inputs.json',inputs),('geometry.json',actors)]:
                for row in json.loads(z.read(index)):
                    raw=z.read(row['entry'])
                    self.assertEqual(hashlib.sha256(raw).hexdigest(),row['sha256'])
                    shape=Part.Shape();shape.importBrepFromString(raw.decode())
                    self.assertTrue(shape.isValid());self.assertEqual(len(shape.Solids),1)
                    target[row['name']]=shape
            receipt=json.loads(z.read('received.json'))
        rebuilt,plan=construct(inputs)
        for name,s in rebuilt.items():
            self.assertAlmostEqual(s.Volume,actors[name].Volume,places=6)
            self.assertLess((s.Solids[0].CenterOfMass-actors[name].Solids[0].CenterOfMass).Length,1e-6)
        self.assertEqual(len(plan['joints_mm3']),3)
        self.assertTrue(all(v>0 for v in plan['joints_mm3'].values()))
        self.assertTrue(all(r['ok'] for r in receipt['static']['checks'].values()))
        self.assertEqual(receipt['motion36']['status'],'SOURCE_UNIT_SAMPLE36_MOTION_RECEIVED')
        self.assertTrue(receipt['outer']['ok'])
        self.assertFalse(packet['N01_complete']);self.assertFalse(packet['physical_pass'])


if __name__=='__main__':
    unittest.main()
