import math,unittest
from w5_source_inlet_joint_r1 import factory_path

class SourceFactoryLeadTests(unittest.TestCase):
    def test_factory_lead_not_extended(self):
        r=factory_path()
        self.assertLessEqual(r['nominal_trial_blank_mm'],r['factory_minimum_mm'])
        self.assertGreaterEqual(80,r['exposed_path_mm']+24)
        self.assertEqual(r['start'],[-73,-21,115]);self.assertEqual(r['end'],[-76.5,7,135.5])

    def test_outward_end_face_then_complete_tangent_path(self):
        r=factory_path();self.assertLess(r['edges'][0]['end'][0],r['start'][0])
        for a,b in zip(r['edges'],r['edges'][1:]):self.assertLess(math.dist(a['end'],b['start']),1e-7)
        for e in r['edges']:
            if e['kind']=='arc':self.assertGreaterEqual(e['radius_mm'],6)
        self.assertIsNone(r['actual_cut_mm']);self.assertFalse(r['physical_pass'])

if __name__=='__main__':unittest.main()
