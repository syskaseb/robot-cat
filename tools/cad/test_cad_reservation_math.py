import unittest
from cad_reservation_math import triangle_box

class Tests(unittest.TestCase):
    def test_intersecting_face(self):
        self.assertTrue(triangle_box([(-2,-2,0),(2,-2,0),(0,2,0)],(0,0,0),(.5,.5,.5)))
    def test_disjoint_height(self):
        self.assertFalse(triangle_box([(-2,-2,2),(2,-2,2),(0,2,2)],(0,0,0),(.5,.5,.5)))
    def test_bbox_overlap_is_not_triangle_contact(self):
        self.assertFalse(triangle_box([(0,2,0),(2,0,0),(2,2,0)],(0,0,0),(.5,.5,.5)))
    def test_translated_corner_contact(self):
        self.assertTrue(triangle_box([(5.5,6.5,7.5),(6,6.5,7.5),(5.5,7,7.5)],(5,6,7),(.5,.5,.5)))
    def test_reversed_winding(self):
        t=[(-2,-2,0),(2,-2,0),(0,2,0)]
        self.assertEqual(triangle_box(t,(0,0,0),(.5,.5,.5)),triangle_box(t[::-1],(0,0,0),(.5,.5,.5)))

if __name__=='__main__':unittest.main()
