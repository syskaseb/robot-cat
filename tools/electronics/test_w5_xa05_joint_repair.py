import math,unittest
from w5_xa05_joint_repair_r1 import layout as r1
from w5_xa05_joint_repair_r2 import layout as r2
from w5_xa05_joint_repair_r3 import layout as r3
from w5_xa05_outer_support_r4 import layout as r4
from w5_xa05_outer_support_r5 import layout as r5


class JointXA05Tests(unittest.TestCase):
    def test_endpoints_and_radius_preserved(self):
        for layout in (r1,r2,r3,r4,r5):
            r=layout();self.assertEqual(r['edges'][0]['start'],[123,9.5,113.5])
            self.assertEqual(r['edges'][-1]['end'],[110.5,-57,113.5])
            for a,b in zip(r['edges'],r['edges'][1:]):
                self.assertLess(math.dist(a['end'],b['start']),1e-7)
            for e in r['edges']:
                if e['kind']=='arc':self.assertGreaterEqual(e['radius_mm'],15)

    def test_no_cuts_or_readiness_claims(self):
        for layout in (r1,r2,r3,r4,r5):
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

    def test_outer_flight_does_not_enter_centre_equipment(self):
        r=r4();self.assertEqual(r['changed_bought_blocks'],0)
        self.assertEqual(r['new_electrical_SKUs'],0)
        self.assertEqual(r['edges'][1]['angle_rad'],math.pi)
        self.assertGreater(r['edges'][-1]['length_mm'],0)

    def test_r5_blank_and_unchanged_cages(self):
        r=r5();self.assertEqual((r['a'],r['b']),('P0G2.5','G_AUX.1'))
        self.assertAlmostEqual(r['path_mm'],227.345310129943)
        self.assertEqual(r['nominal_trial_blank_mm'],310)
        self.assertEqual(r['changed_bought_blocks'],0)

    def test_native_slot_keeps_two_rail_cheeks(self):
        from w5_xa05_native_r1 import RISE_SLOT
        self.assertAlmostEqual(RISE_SLOT[3]-RISE_SLOT[0],3.2)
        self.assertAlmostEqual(RISE_SLOT[0]-149.7,1.7)
        self.assertAlmostEqual(156.3-RISE_SLOT[3],1.7)
        self.assertLess(RISE_SLOT[1],-5.235685689754676)
        self.assertGreater(RISE_SLOT[4],6.271840925594386)


if __name__=='__main__':unittest.main()
