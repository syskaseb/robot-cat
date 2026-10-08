import math
import unittest
import open_prototype_legacy_source as L


class LegacySource(unittest.TestCase):
    def test_current_bay_is_one_electrical_interface(self):
        p=L.build_plan()
        self.assertEqual([r['id'] for r in p['rows']],['W075','W076_FACTORY','W076_EXTENSION','W001'])
        self.assertTrue(p['W076_factory_and_extension_are_one_logical_conductor'])
        self.assertEqual(p['retained_distribution_casings'],20)
        self.assertEqual(p['extra_electrical_connections'],0)
        self.assertFalse(p['selected'])
        self.assertFalse(p['physical_pass'])
        self.assertTrue(p['old920mm_not_a_current_stock_total'])
        plus=p['rows'][0]
        self.assertLessEqual(plus['nominal_fit_blank_mm'],50)
        factory=p['rows'][1]
        self.assertLessEqual(factory['nominal_fit_blank_mm'],factory['limit_mm'])

    def test_ground_rebound_direction_and_grip_lengths(self):
        row=L.build_plan()['rows'][-1];parts=row['segments']
        self.assertLess(math.dist(parts[0]['start'],[-73,-58.8,57]),1e-7)
        self.assertLess(math.dist(parts[-1]['end'],[-89,-73.75,100.99]),1e-7)
        self.assertEqual(parts[0]['t0'],[1.,0.,0.])
        self.assertEqual(parts[-1]['t1'],[0.,-1.,0.])
        self.assertGreaterEqual(math.dist(parts[0]['start'],parts[0]['end']),9)
        self.assertGreaterEqual(math.dist(parts[-1]['start'],parts[-1]['end']),9)
        for a,b in zip(parts,parts[1:]):
            self.assertLess(math.dist(a['end'],b['start']),1e-7)
            self.assertLess(math.dist(a['t1'],b['t0']),1e-7)
        self.assertEqual(sum(s['kind']=='arc' for s in parts),4)
        self.assertTrue(row['old150mm_limit_exceeded'])
        self.assertGreaterEqual(row['nominal_fit_blank_mm'],row['required_blank_mm'])


if __name__=='__main__':unittest.main()
