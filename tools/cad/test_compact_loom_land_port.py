import unittest
import FreeCAD as A
import Part
from compact_loom_land_port import build


class CompactPort(unittest.TestCase):
    def test_whole_arrival_and_band_with_stagger_and_oblique_splice(self):
        axes=[([0,0,1],[1,0,0]),([1,0,0],[0,0,1]),([0,.9902680687,-.139173101],[1,0,0])]
        for axis,normal in axes:
            for offset in (-1.5,0,1.5):
                for far in (False,True):
                    land=dict(id='FL3/Splice/1' if far else 'test',centre_world_mm=[0,0,0],axis=axis)
                    p=build(land,normal,offset);body=p['body'];x,y,z=p['arrival_world_mm']
                    seed=Part.makeBox(4,6,4,A.Vector(x-2,y-3,z-2))
                    self.assertLess(seed.common(p['band']).Volume,1e-6)
                    self.assertGreater(seed.common(body).Volume,1)
                    self.assertEqual(len(body.Solids),1)
                    wire=Part.makeLine(A.Vector(*axis)*-4.5,A.Vector(*axis)*4.5)
                    self.assertGreaterEqual(body.distToShape(wire)[0],3-1e-6)
                    self.assertLess(body.Volume,300)


if __name__=='__main__':unittest.main()
