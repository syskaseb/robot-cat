import unittest
from parallel_core_candidates import tangent,shifted


class ParallelGeometryTest(unittest.TestCase):
    def test_exact_circle_tangent_not_sample_chord(self):
        actual=tangent(dict(kind='arc',start=[10,0,0],mid=[2**.5*5,2**.5*5,0],end=[0,10,0]))
        for a,b in zip(actual,[-1,0,0]):self.assertAlmostEqual(a,b,12)
    def test_shift_preserves_shape_and_length(self):
        p=dict(kind='bezier',start=[0,0,0],end=[3,0,0],poles_mm=[[0,0,0],[1,0,0],[2,0,0],[3,0,0]],length_mm=3)
        q=shifted(p,[0,2.25,-1.299]);self.assertEqual(q['length_mm'],3)
        self.assertEqual(q['poles_mm'][0],[0,2.25,-1.299]);self.assertEqual(p['start'],[0,0,0])


if __name__=='__main__':unittest.main()
