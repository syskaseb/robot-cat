import unittest
import FreeCAD as A
import Part
from mapped_rail_pressure_bridge import build
from csg_bore_clearance import prove


class MappedRail(unittest.TestCase):
    def test_one_two_and_thick_feed_cases_without_invented_NC(self):
        lands=[dict(id=str(x),centre_world_mm=[x,0,0],axis=[0,0,1],length_mm=9) for x in (-4.75,0,4.75)]
        for normal in ([0,1,0],[0,-1,0]):
            for values in (((-9.5,.65),),((9.5,2.1),),((-9.5,.65),(9.5,.65))):
                feeds=[dict(point_world_mm=[x,0,-4.5],radius_mm=r) for x,r in values];q=build(lands,normal,feeds)
                for x,r in [(-4.75,1),(0,1),(4.75,1),*values]:
                    wire=Part.makeLine(A.Vector(x,0,-4.5),A.Vector(x,0,4.5));required=r+.25
                    for s in (q['body'],q['cap'],*q['bands']):self.assertGreaterEqual(s.distToShape(wire)[0],required-1e-6)
                    for kind in ('body','cap'):self.assertTrue(prove(q['recipe'],kind,wire,required))
                self.assertEqual(len(q['recipe']['feed_slots']),len(values))


if __name__=='__main__':unittest.main()
