import math,unittest
from w5_source_inlet_joint_r2 import factory_path

class SourceInletSeparationTests(unittest.TestCase):
    def test_same_endpoints_and_factory_limit(self):
        r=factory_path()
        self.assertEqual(r['start'],[-73,-21,115]);self.assertEqual(r['end'],[-76.5,7,135.5])
        self.assertLessEqual(r['exposed_path_mm']+24,80)
        self.assertLessEqual(80,r['factory_minimum_mm'])
        self.assertFalse(r['selected']);self.assertFalse(r['physical_pass'])

    def test_continuous_separated_riser(self):
        r=factory_path()
        self.assertEqual(r['edges'][2]['end'],[-79.5,-21,129.5])
        for a,b in zip(r['edges'],r['edges'][1:]):self.assertLess(math.dist(a['end'],b['start']),1e-7)
        self.assertTrue(all(e.get('radius_mm',6)>=6 for e in r['edges']))

if __name__=='__main__':unittest.main()
