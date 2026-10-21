import hashlib
import json
import unittest
import zipfile
import FreeCAD
import Part
from check_main_p0_placement import ROOT, sha
from plan_feline_layout import OUT
from plan_feline_u1_east_pair_relief import construct


class U1EastRelief(unittest.TestCase):
    def test_archived_real_seams_full_stock_existing_bore_and_joint(self):
        packet = json.loads((OUT/'n01-coherent-U1-F0-space-fit.json').read_text())
        archive = ROOT/packet['bundle']
        self.assertEqual(sha(archive), packet['bundle_sha256'])
        wanted = {'U1Five:'+w+':'+s for w in ('XP02.module','XP03.module')
                  for s in ('bare','jacket')}
        wanted |= {'U1Relief:RearRoot','U1Relief:E2pair:band','U1Relief:E2pair:head',
                   'U1Relief:Stand1','Ref_Material_PWM160825Screw_0_0'}
        source = {}
        with zipfile.ZipFile(archive) as z:
            for rec in json.loads(z.read('geometry.json')):
                if rec['name'] in wanted:
                    raw = z.read(rec['entry'])
                    self.assertEqual(hashlib.sha256(raw).hexdigest(),rec['sha256'])
                    shape = Part.Shape()
                    shape.importBrepFromString(raw.decode())
                    source[rec['name']] = shape
        self.assertEqual(set(source),wanted)
        changed,plan = construct(source)
        root = changed['U1Relief:RearRoot']
        self.assertEqual(len(root.Solids),1)
        self.assertGreater(plan['named_integral_Stand1_root_joint_mm3'],17)
        self.assertGreaterEqual(root.distToShape(source['Ref_Material_PWM160825Screw_0_0'])[0],.2-1e-6)
        for w in ('XP02.module','XP03.module'):
            a,b = changed['U1Five:'+w+':jacket'],source['U1Five:'+w+':bare']
            self.assertLess(a.distToShape(b)[0],1e-6)
            self.assertLess(a.common(b).Volume,1e-5)
            self.assertAlmostEqual(a.BoundBox.XMax,88.75,places=6)
        for suffix in ('band','head'):
            n = 'U1Relief:E2pair:'+suffix
            self.assertAlmostEqual(changed[n].Volume,source[n].Volume,places=6)


if __name__ == '__main__':
    unittest.main()
