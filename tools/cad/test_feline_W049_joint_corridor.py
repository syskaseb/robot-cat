import json,math,unittest
import FreeCAD
from receive_feline_W049_joint_corridor import current,DEST,END,MIDDLE
from receive_feline_current_factory_lead import current as parent
from receive_feline_rrp_shared_height import load
from receive_feline_W024_shared_body import solid
from receive_feline_W046_portal_body import equivalent_solid
import feline_tangent_routes as ft

class JointCorridor(unittest.TestCase):
    def test_saved_geometry_matches_complete_recipe(self):
        r=json.loads(DEST.read_text());shapes=load(r)
        self.assertEqual(set(shapes),{END,MIDDLE})
        self.assertTrue(equivalent_solid(shapes[END],solid(r['bank_recipe'],1)))
        self.assertTrue(equivalent_solid(shapes[MIDDLE],solid(r['middle_recipe'],1)))
        whole=solid(r['whole_recipe'],1)
        self.assertTrue(whole.isValid());self.assertEqual(len(whole.Solids),1)
        self.assertAlmostEqual(whole.Volume,math.pi*ft.length(r['whole_recipe']),places=4)
        self.assertGreaterEqual(r['minimum_R_mm'],12.4-1e-7)
        self.assertTrue(all(c['ok'] for c in r['checks'].values()))
        self.assertTrue(r['factory_moving_native_stock_OPEN']);self.assertFalse(r['N01_complete'])
        self.assertFalse(r['physical_pass'])

    def test_registry_only_w049_and_no_mouth_moves(self):
        _,old,_=parent();_,rows,_=current()
        self.assertEqual(len(rows),246)
        self.assertEqual(len({r['portion_id'] for r in rows if r.get('full_middle_route_accepted')}),32)
        for a,b in zip(old,rows):
            self.assertEqual(a['point_mm'],b['point_mm'])
            if a['portion_id']!='W049/body':self.assertEqual(a,b)
            else:self.assertTrue(b['whole_portion_received'])

if __name__=='__main__':unittest.main()
