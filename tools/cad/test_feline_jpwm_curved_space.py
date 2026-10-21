import hashlib
import json
import unittest
import zipfile
import FreeCAD
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_n01_shared import pipe
from plan_feline_jpwm_curved_land import construct,module_routes
from plan_feline_pier4_factory_portal import construct as portal


class ReceivedCurvedSpace(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet=json.loads((OUT/'n01-E2-four-factory-critical-space.json').read_text())
        archive=ROOT/cls.packet['bundle']
        assert sha(archive)==cls.packet['bundle_sha256']
        cls.shapes={};cls.mates={}
        with zipfile.ZipFile(archive) as z:
            for index,target in (('geometry.json',cls.shapes),('verification-joints.json',cls.mates)):
                for rec in json.loads(z.read(index)):
                    raw=z.read(rec['entry'])
                    assert hashlib.sha256(raw).hexdigest()==rec['sha256']
                    shape=Part.Shape();shape.importBrepFromString(raw.decode())
                    assert shape.isValid() and len(shape.Solids)==1
                    target[rec['name']]=shape
            cls.plan=json.loads(z.read('plan.json'))
            cls.receipt=json.loads(z.read('received.json'))
            cls.old_pier=Part.Shape();cls.old_pier.importBrepFromString(z.read('parent-BankPier4.brep').decode())

    def test_actual_curved9_full_stock_and_all_four_recipe_rebuild(self):
        actors,plan=construct(None)
        self.assertEqual(plan['full_curved_land_mm'],9)
        self.assertEqual(plan['full_T18I_head_mm'],[5,4.3,5.3])
        for n,s in actors.items():
            t=self.shapes[n]
            self.assertAlmostEqual(s.Volume,t.Volume,places=6)
            self.assertLess((s.Solids[0].CenterOfMass-t.Solids[0].CenterOfMass).Length,1e-6)
        regenerated=module_routes(self.plan['routes'],plan['caps'])
        for w,row in self.plan['routes'].items():
            solid=pipe(row['parts'],.925)
            target=self.shapes['FactoryFour:'+w]
            self.assertAlmostEqual(solid.Volume,target.Volume,places=6)
            self.assertLessEqual(row['required_factory_mm'],220)
            if w in regenerated:
                self.assertAlmostEqual(regenerated[w]['required_factory_mm'],row['required_factory_mm'],places=6)

    def test_actual_portal_preserves_load_path_and_unweakened_clearances(self):
        new,plan=portal(self.old_pier,self.plan['routes'],self.mates)
        target=self.shapes['CurrentFoundation:BankPier:4']
        self.assertLess(new.cut(target).Volume+target.cut(new).Volume,1e-5)
        self.assertEqual(len(plan['preserved_structural_joints']),3)
        for w in ('XP02.module','XP03.module'):
            self.assertGreaterEqual(target.distToShape(self.shapes['FactoryFour:'+w])[0],1.25-1e-6)
        self.assertTrue(all(row['ok'] for row in self.receipt['static_checks'].values()))
        self.assertEqual(len(self.receipt['motion36']['completed']),9)
        self.assertTrue(self.receipt['outer']['ok'])
        self.assertFalse(self.packet['N01_complete'])
        self.assertFalse(self.packet['physical_pass'])


if __name__=='__main__':
    unittest.main()
