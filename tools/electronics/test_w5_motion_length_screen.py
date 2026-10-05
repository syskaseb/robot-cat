"""Small mathematical tests; no FreeCAD or repeated whole-robot audit."""
import math, unittest
import w5_motion_length_screen_r2 as M

class ReachBounds(unittest.TestCase):
    def test_coaxial_rotation_leaves_axial_offset(self):
        self.assertAlmostEqual(M.one_axis_maximum([0,0,3],[0,0,-2],[0,0,0],[0,0,4]),5)

    def test_single_axis_radial_extrema(self):
        self.assertAlmostEqual(M.one_axis_maximum([2,0,1],[3,0,5],[0,0,0],[0,0,1]),math.hypot(5,4))

    def test_rotation_around_offset_axis(self):
        p=M.rotate([4,2,3],[2,2,3],[0,0,1],math.pi/2)
        for a,b in zip(p,[2,4,3]):self.assertAlmostEqual(a,b)

    def test_two_axis_continuous_bound(self):
        first=dict(pivot_mm=[1,2,3],axis=[1,0,0])
        second=dict(pivot_mm=[5,6,7],axis=[0,1,0])
        p=[9,8,13];f=[20,-10,4]
        bound,gap=M.two_axis_maximum_upper(p,f,first,second)
        self.assertGreater(gap,0)
        # Samples deliberately lie halfway BETWEEN receiver samples, so the
        # gap bound is exercised rather than only rechecking its360inputs.
        for inner in range(0,360,9):
            q=M.rotate(p,second['pivot_mm'],second['axis'],math.radians(inner+.5))
            for outer in range(0,360,13):
                v=M.rotate(q,first['pivot_mm'],first['axis'],math.radians(outer))
                self.assertLessEqual(math.dist(v,f),bound+1e-9)

if __name__=='__main__':unittest.main()
