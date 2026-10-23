import json,unittest
import FreeCAD
from plan_feline_layout import OUT
from receive_feline_rrp_shared_height import load
from receive_feline_W046_portal_body import current,PORTAL,MATES
from receive_feline_W024_shared_body import solid

class PortalBody(unittest.TestCase):
    def test_full_portion_and_no_stage_credit(self):
        r=json.loads((OUT/'n01-W046-original-prefix-portal-body.json').read_text())
        self.assertFalse(r['N01_complete']);self.assertFalse(r['physical_pass'])
        self.assertTrue(r['original_ends_and_W045_unchanged'])
        self.assertGreaterEqual(r['minimum_R_mm'],12.4-1e-7)
        self.assertGreaterEqual(r['self_gap_lower_mm'],.2)
        self.assertTrue(all(c['ok'] for c in r['checks'].values()))
        for name,margin in MATES.items():
            c=r['checks']['CurrentWhole:W046|'+name]
            self.assertEqual(c['minimum_mm'],margin);self.assertLess(c['common_mm3'],1e-7)
        shapes=load(r)
        self.assertEqual(len(shapes),3)
        self.assertTrue(all(s.isValid() and len(s.Solids)==1 for s in shapes.values()))
        root=shapes[PORTAL[0]].fuse(shapes[PORTAL[1]])
        self.assertEqual(len(root.Solids),1);self.assertGreater(r['portal_joint_mm3'],300)
        for bearing in r['bearings'].values():
            self.assertAlmostEqual(bearing['before_mm2'],bearing['after_mm2'])
        self.assertEqual(len(solid(r['whole_recipe'],1.55).Solids),1)

    def test_current_registry_has_thirty_whole_portions(self):
        _,rows,_=current()
        self.assertEqual(len(rows),246)
        portions={e['portion_id'] for e in rows if e.get('full_middle_route_accepted')}
        self.assertIn('W046/single',portions)
        self.assertEqual(len(portions),30)
        for e in rows:
            if e['portion_id']=='W046/single':
                self.assertTrue(e['full_middle_route_accepted'])
                self.assertTrue(e['stock_cutting_and_native_mounts_OPEN'])

if __name__=='__main__':unittest.main()
