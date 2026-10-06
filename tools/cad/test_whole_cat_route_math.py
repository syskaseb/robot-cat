"""Cheap route arithmetic tests; not a geometry/clearance acceptance."""
import itertools
import math
import unittest
import whole_cat_mta_common_plan as m


class RouteMath(unittest.TestCase):
    def test_suffix_endpoints_and_continuity(self):
        accepted=0
        for heading,target_heading,h,v in itertools.product(
                m.AXES,m.AXES,[0,1,20,50,75,100,101,150],[9,20,60,150]):
            target=m.add(m.scale(target_heading,v),[h,0,0])
            segments=m.suffix([0,0,0],heading,target,target_heading)
            if segments is None:continue
            accepted+=1
            self.assertLess(m.length(m.minus(segments[-1]['end_mm'],target)),1e-6)
            previous=[0,0,0]
            for segment in segments:
                self.assertLess(m.length(m.minus(segment['start_mm'],previous)),1e-6)
                self.assertTrue(math.isfinite(segment['length_mm']))
                self.assertGreaterEqual(segment['length_mm'],0)
                samples=m.points(segment)
                self.assertLess(m.length(m.minus(samples[-1],segment['end_mm'])),1e-6)
                previous=segment['end_mm']
        self.assertGreater(accepted,100)


if __name__=='__main__':unittest.main()
