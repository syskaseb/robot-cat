import math,unittest
from w5_xa05_joint_repair_r1 import layout as r1
from w5_xa05_joint_repair_r2 import layout as r2
from w5_xa05_joint_repair_r3 import layout as r3


class JointXA05Tests(unittest.TestCase):
    def test_endpoints_and_radius_preserved(self):
        for layout in (r1,r2,r3):
            r=layout();self.assertEqual(r['edges'][0]['start'],[123,9.5,113.5])
            self.assertEqual(r['edges'][-1]['end'],[110.5,-57,113.5])
            for a,b in zip(r['edges'],r['edges'][1:]):
                self.assertLess(math.dist(a['end'],b['start']),1e-7)
            for e in r['edges']:
                if e['kind']=='arc':self.assertGreaterEqual(e['radius_mm'],15)

    def test_no_cuts_or_readiness_claims(self):
        for layout in (r1,r2,r3):
            r=layout();self.assertIsNone(r['actual_cut_mm'])
            self.assertFalse(r['selected']);self.assertFalse(r['physical_pass'])
            self.assertGreaterEqual(r['nominal_trial_blank_mm'],r['path_mm']+82)

    def test_whole_high_flight_below_carrier(self):
        r=r2();middle=r['edges'][5]
        self.assertEqual(middle['kind'],'line')
        self.assertEqual(middle['start'][2],135)
        self.assertEqual(middle['end'][2],135)
        self.assertLess(135+r['OD_mm']/2,140)

    def test_rear_bypass_preserves_plane_and_gap(self):
        r=r3();self.assertTrue(all(e['start'][2]==113.5 and e['end'][2]==113.5 for e in r['edges']))
        e=r['edges'][6];self.assertEqual(e['start'][0],93);self.assertEqual(e['end'][0],93)
        self.assertGreater(93-r['OD_mm']/2,90)
        self.assertLess(93+r['OD_mm']/2,96)


if __name__=='__main__':unittest.main()
