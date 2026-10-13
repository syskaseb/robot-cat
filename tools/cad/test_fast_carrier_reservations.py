import unittest
import numpy as np
from cad_reservation_math import triangle_box
from fast_carrier_reservations import TriangleBucket,WireBucket


class FastReservations(unittest.TestCase):
    def test_same_triangle_sat_200_random_boxes(self):
        rng=np.random.default_rng(137)
        triangles=rng.uniform(-10,10,(200,3,3));items=[(tuple(map(tuple,t)),str(i)) for i,t in enumerate(triangles)]
        bucket=TriangleBucket(items)
        for _ in range(200):
            point=rng.uniform(-12,12,3);half=rng.uniform(.1,3,3)
            expected=next((n for tri,n in items if triangle_box(tri,point,half)),None)
            self.assertEqual(bucket.hit(point,half),expected)

    def test_exact_wire_tangency_not_roundoff_contact(self):
        bucket=WireBucket([((0,0,0),3,'same')])
        self.assertIsNone(bucket.hit((6-3e-14,0,0),(2,3,2),.5))
        self.assertEqual(bucket.hit((6-1e-4,0,0),(2,3,2),.5),'same')

    def test_internal_triangle_and_degenerate_cases(self):
        for tri in (((0,0,0),(0,0,0),(0,0,0)),((0,0,0),(1,0,0),(0,1,0)),((5,5,5),(5,6,5),(6,5,5))):
            self.assertEqual(TriangleBucket([(tri,'one')]).hit((0,0,0),(1,1,1)) is not None,triangle_box(tri,(0,0,0),(1,1,1)))


if __name__=='__main__':unittest.main()
