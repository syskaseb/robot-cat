import unittest
import FreeCAD as A
import Part
from low_profile_rail_pressure_bridge import build as common
from short_feed_lacing_saddle import build


class ShortFeedGripTest(unittest.TestCase):
    def test_rooted_to_same_print_and_separate_from_cap(self):
        lands=[dict(id=str(i),centre_world_mm=[0,y,84],axis=[0,0,-1],length_mm=9) for i,y in enumerate((-4.75,0,4.75))]
        for radius in (.65,1,2.1):
            for y in (-9.5,9.5):
                feed=dict(wire='Fixture',point_world_mm=[0,y,79.5],radius_mm=radius)
                old=common(lands,[1,0,0],[feed]);new=build(old['recipe'],feed)
                joined=old['body'].fuse(new['body']).removeSplitter()
                self.assertEqual(len(joined.Solids),1);self.assertFalse(joined.check(True))
                self.assertLess(new['body'].common(old['cap']).Volume,1e-6)
                self.assertLess(new['band'].common(old['cap']).Volume,1e-6)
                self.assertLess(new['band'].common(old['body']).Volume,1e-6)
                wire=Part.makeLine(A.Vector(0,y,79.5),A.Vector(0,y,88.5))
                self.assertGreaterEqual(new['body'].distToShape(wire)[0],radius+.49)
                self.assertGreaterEqual(new['band'].distToShape(wire)[0],radius+.19)
                self.assertTrue(new['recipe']['does_not_claim_nine_mm_pressure_land'])


if __name__=='__main__':unittest.main()
