import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
import FreeCAD as A
import Part
from receive_feline_s1_source_datums import plane_receipts,mouth_receipts


class SourcePlanes(unittest.TestCase):
    def test_transformed_annular_barrel_centres_and_wrong_direction(self):
        tube=Part.makeCylinder(2.1,10).cut(Part.makeCylinder(1.1,10))
        tube.rotate(A.Vector(),A.Vector(0,1,0),90);tube.translate(A.Vector(20,30,40))
        rows=plane_receipts({'source_ring':tube},A.Vector(30,30,40),A.Vector(1,0,0))
        self.assertAlmostEqual(rows[0]['centre_distance_mm'],0,places=7)
        self.assertEqual(plane_receipts({'source_ring':tube},A.Vector(30,30,40),A.Vector(0,1,0)),[])

    def test_split_end_face_centroid_is_not_a_mouth_datum(self):
        tube=Part.makeCylinder(2.1,10).cut(Part.makeCylinder(1.1,10))
        tube=tube.cut(Part.makeBox(5,5,12,A.Vector(0,0,-1)))
        q=A.Vector(0,0,10);d=A.Vector(0,0,1)
        matches,planes=mouth_receipts({'source_ring':tube},q,d)
        self.assertTrue(matches)
        self.assertTrue(all(p['centre_distance_mm']>.1 for p in planes))
        self.assertEqual(mouth_receipts({'source_ring':tube},A.Vector(.5,0,10),d)[0],[])


if __name__=='__main__':unittest.main()
