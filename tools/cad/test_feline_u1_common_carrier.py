import hashlib
import json
import unittest
import zipfile
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_u1_common_carrier import construct


class U1CommonCarrier(unittest.TestCase):
    def test_reopen_rebuild_full_clamps_and_constructive_frame_joints(self):
        packet=json.loads((OUT/'n01-U1-common-carrier.json').read_text())
        archive=ROOT/packet['bundle']
        self.assertEqual(sha(archive),packet['bundle_sha256'])
        inputs={};actors={}
        with zipfile.ZipFile(archive) as z:
            for index,target in [('geometry.json',actors),('inputs.json',inputs)]:
                for row in json.loads(z.read(index)):
                    raw=z.read(row['entry'])
                    self.assertEqual(hashlib.sha256(raw).hexdigest(),row['sha256'])
                    shape=Part.Shape();shape.importBrepFromString(raw.decode())
                    self.assertTrue(shape.isValid());self.assertEqual(len(shape.Solids),1)
                    target[row['name']]=shape
            receipt=json.loads(z.read('received.json'))
        cells={}
        rebuilt,_,_,prints,joints,_=construct(inputs,cells)
        self.assertEqual(len(rebuilt),12)
        for name,shape in rebuilt.items():
            self.assertAlmostEqual(shape.Volume,actors[name].Volume,places=6)
            self.assertLess((shape.Solids[0].CenterOfMass-actors[name].Solids[0].CenterOfMass).Length,1e-6)
        for side in ('Fore','Rear'):
            whole=prints[joints[side]['named_integral_root']]
            self.assertEqual(len(whole.Solids),1)
            self.assertGreater(joints[side]['common_mm3'],0)
            self.assertLess(max(whole.BoundBox.XLength,whole.BoundBox.YLength,whole.BoundBox.ZLength),250)
            base=rebuilt['U1Carrier:'+side+':Base']
            screw=rebuilt['U1Carrier:'+side+':RailClamp4Screw']
            self.assertGreaterEqual(base.distToShape(screw)[0],.2-1e-6)
            washer=rebuilt['U1Carrier:'+side+':RailClamp4TopWasher'].copy()
            self.assertLess(base.common(washer).Volume,1e-6)
            washer.translate(A.Vector(0,0,-.001))
            self.assertGreater(base.common(washer).Volume/.001,29)
        self.assertTrue(all(r['ok'] for r in receipt['static_checks'].values()))
        self.assertEqual(receipt['motion36']['status'],'UNION_SAMPLE36_RECEIVED')
        self.assertTrue(receipt['outer']['ok'])
        self.assertEqual(receipt['assembly_driver']['failures'],[])
        self.assertFalse(packet['N01_complete']);self.assertFalse(packet['physical_pass'])


if __name__=='__main__':
    unittest.main()
