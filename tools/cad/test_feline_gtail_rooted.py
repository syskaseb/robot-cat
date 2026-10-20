"""The source transformation is not a whole-route or N01 qualification."""
import json,unittest
import FreeCAD as A
import Part
from plan_feline_layout import OUT
from receive_feline_rrp_shared_height import load


class GtailRootedTests(unittest.TestCase):
    def test_complete_station_and_positive_independent_root_joints(self):
        p=json.loads((OUT/'n01-GTAIL-whole10-rooted.json').read_text())
        self.assertFalse(p['failures']);self.assertFalse(p['N01_complete'])
        self.assertTrue(p['whole123_routes_common_assembly_and_lever_access_OPEN'])
        shapes=load(p);self.assertEqual(len(shapes),10)
        self.assertTrue(all(s.isValid() and s.Solids for s in shapes.values()))
        for row in p['recipe']['joints'].values():
            self.assertGreater(row['common_mm3'],1)
            self.assertTrue(row['fuse_valid']);self.assertEqual(row['solids'],1)
        self.assertEqual(p['recipe']['joints']['rail']['source_solid_count'],2)
        self.assertAlmostEqual(p['recipe']['case_only_adhesive_mm'],.5)
        self.assertEqual(len(p['updates']),4)
        for row in p['updates'].values():
            self.assertFalse(row['full_middle_route_accepted'])
            self.assertAlmostEqual(row['routing_exit_mm'][0],128)
            self.assertAlmostEqual(row['routing_exit_mm'][2],80.595)
            self.assertAlmostEqual(row['routing_exit_axis'][2],1)
            a,b=map(lambda q:A.Vector(*q),row['jacket_grip9_mm'])
            self.assertAlmostEqual((b-a).Length,9)
        for name in ('n01-GTAIL-above-legs-motion.json','n01-GTAIL-shared-rail-root-motion.json'):
            motion=json.loads((OUT/name).read_text())
            self.assertEqual(motion['status'],'SOURCE_UNIT_SAMPLE36_MOTION_RECEIVED')


if __name__=='__main__':unittest.main()
