import json,unittest
import FreeCAD
from plan_feline_layout import OUT
from receive_feline_rrp_shared_height import load
from receive_feline_current_factory_lead import current,CAP
from receive_feline_W046_portal_body import current as parent

class CurrentFactoryLead(unittest.TestCase):
    def test_profile_complete_and_scope(self):
        p=json.loads((OUT/'n01-W043-selected-profile-complete-lead.json').read_text())
        self.assertEqual(p['current_profile_radius_mm'],2)
        self.assertLessEqual(p['nominal_cut_including_strip_mm'],50)
        self.assertTrue(all(c['ok'] for c in p['checks'].values()))
        self.assertFalse(p['N01_complete']);self.assertFalse(p['physical_pass'])
        self.assertTrue(p['service_and_root_assembly_OPEN'])
        self.assertGreater(p['cap_subset_removed_mm3'],0)
        shapes=load(p);self.assertEqual(set(shapes),{'W043',CAP})
        self.assertTrue(all(s.isValid() and len(s.Solids)==1 for s in shapes.values()))
        self.assertGreaterEqual(shapes['W043'].distToShape(shapes[CAP])[0],.15-1e-6)

    def test_registry_only_changes_w043(self):
        _,old,_=parent();_,rows,_=current();self.assertEqual(len(rows),246)
        self.assertEqual(len({e['portion_id'] for e in rows if e.get('full_middle_route_accepted')}),31)
        for a,b in zip(old,rows):
            self.assertEqual(a['point_mm'],b['point_mm'])
            if a['portion_id']!='W043/single':self.assertEqual(a,b)
            else:self.assertTrue(b['whole_portion_received'])

if __name__=='__main__':unittest.main()
