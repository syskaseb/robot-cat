import math
import unittest
import FreeCAD as A
import Part
from loom_land_port import build


class LandPort(unittest.TestCase):
    def test_staggered_bands_fit_unchanged_nine_mm_lands(self):
        for offset in (-1.5,1.5):
            result=build(dict(centre_world_mm=[0,0,0],axis=[0,0,1]),[1,0,0],offset)
            self.assertTrue(result['body'].isValid())
            self.assertEqual(len(result['body'].Solids),1)
            self.assertFalse(result['body'].check(True))
            self.assertLess(result['body'].common(result['band']).Volume,1e-6)
            self.assertGreaterEqual(4.5-abs(offset)-1.25,1.75)
            seat=result['recipe']['pads'][0]['bounds_mm']
            self.assertEqual(seat,[4,-3,-4.5,8,3,4.5])

    def test_far_splice_bridge_faces_away_without_moving_land(self):
        centre=[0,0,38.5]
        result=build(dict(id='FL3/Splice/1',centre_world_mm=centre,axis=[0,0,1]),[1,0,0])
        self.assertTrue(result['recipe']['reverse_axis_for_outer_splice_bridge'])
        self.assertGreaterEqual(result['body'].BoundBox.ZMin,34-1e-6)
        self.assertAlmostEqual(result['body'].BoundBox.ZMax,46)

    def test_oriented_same_material_and_jacket_gap(self):
        reference=None
        cases=[([0,0,1],[1,0,0]),([1,0,0],[0,0,-1]),
               ([0,.990268068741567,-.139173100960089],[1,0,0])]
        for axis,normal in cases:
            row=dict(centre_world_mm=[25,-42,63],axis=axis)
            result=build(row,normal);body,band=result['body'],result['band']
            self.assertTrue(body.isValid());self.assertEqual(len(body.Solids),1)
            self.assertFalse(body.check(True));self.assertLess(body.common(band).Volume,1e-6)
            centre=A.Vector(*row['centre_world_mm']);direction=A.Vector(*axis)
            wire=Part.makeLine(centre-direction*4.5,centre+direction*4.5)
            self.assertGreaterEqual(body.distToShape(wire)[0],3-1e-6)
            self.assertGreaterEqual(band.distToShape(wire)[0],3-1e-6)
            if reference is None:reference=body.Volume
            self.assertAlmostEqual(reference,body.Volume,places=6)
            self.assertAlmostEqual(math.dist(result['arrival_world_mm'],row['centre_world_mm']),16.9)


if __name__=='__main__':unittest.main()
