import math
import unittest
from w5_battery_parallel_s import route


class BatteryS(unittest.TestCase):
    def test_fixed_source_and_budget(self):
        r=route([87,16.5,113.5],[55.5,75,70])
        self.assertLess(r['body_mm']+19,150)
        self.assertLess(math.dist(r['edges'][-1]['end'],[55.5,75,70]),1e-7)
        self.assertTrue(all(e.get('radius_mm',12.4)>=12.4 for e in r['edges']))
        self.assertAlmostEqual(r['edges'][0]['length_mm'],6)
        self.assertAlmostEqual(r['edges'][-1]['length_mm'],6)

    def test_rotated_offset_same_length(self):
        a=route([0,0,0],[30,80,40])
        b=route([0,0,0],[0,80,50])
        self.assertAlmostEqual(a['body_mm'],b['body_mm'])

    def test_reject_negative_advance(self):
        with self.assertRaises(AssertionError):route([0,0,0],[20,5,20])


if __name__=='__main__':unittest.main()
