import hashlib
import json
import unittest
import zipfile
import FreeCAD
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_power30_common_frame import construct


class PowerFrame(unittest.TestCase):
    def test_reopen_rebuild_actual_cylinder_and_rooted_common_frame(self):
        packet=json.loads((OUT/'n01-power-common-frame.json').read_text())
        archive=ROOT/packet['bundle']
        self.assertEqual(sha(archive),packet['bundle_sha256'])
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
        cells={};rebuilt,plan=construct(inputs,cells)
        self.assertEqual(len(rebuilt),8)
        for n,s in rebuilt.items():
            self.assertAlmostEqual(s.Volume,actors[n].Volume,places=5)
            self.assertLess((s.Solids[0].CenterOfMass-actors[n].Solids[0].CenterOfMass).Length,1e-6)
        self.assertEqual(plan['whole_print_solids'],1)
        self.assertLess(max(plan['whole_print_envelope_mm']),250)
        self.assertTrue(all(v>0 for v in plan['root_joints_mm3'].values()))
        self.assertTrue(any(type(f.Surface).__name__=='Cylinder' for f in inputs['PowerFan:F_PWM:case'].Faces))
        self.assertNotIn('PowerMount:F_PWM:4905',rebuilt)
        self.assertAlmostEqual(rebuilt['PowerMount:F_PWM:Head'].Volume,5.3*4.3*5,places=6)
        self.assertTrue(all(r['ok'] for r in receipt['static_checks'].values()))
        self.assertEqual(receipt['motion_lower']['status'],'UNION_SAMPLE36_RECEIVED')
        self.assertTrue(all(v>=1.25 for v in receipt['other_seven_sample36_global_Z_lower_bounds_mm'].values()))
        self.assertTrue(receipt['outer']['ok'])
        self.assertTrue(all(r['ok'] for r in receipt['intrinsic_new_stock']))
        self.assertTrue(packet['four_independent_grip_roots_OPEN'])
        self.assertFalse(packet['N01_complete']);self.assertFalse(packet['physical_pass'])


if __name__=='__main__':
    unittest.main()
