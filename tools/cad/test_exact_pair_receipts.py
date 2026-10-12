"""Checks for strict pair reuse and exact, componentwise broad phase."""
import tempfile,unittest
from pathlib import Path
import FreeCAD as A
import Part
from exact_pair_receipts import PairReceipts

def near(a,b,r):
    bb=a.BoundBox;bb.enlarge(r);return bb.intersect(b.BoundBox)

class Tests(unittest.TestCase):
    def test_valid_collision_is_not_waived_by_cache(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'pairs.json';g=PairReceipts(p,near)
            a=Part.makeBox(2,2,2);b=Part.makeBox(2,2,2,A.Vector(1,0,0))
            self.assertAlmostEqual(g.check(a,b)[1],4);g.save()
            h=PairReceipts(p,near);self.assertAlmostEqual(h.check(a.copy(),b.copy())[1],4)
            self.assertEqual(h.reused,1)

    def test_world_placement_changes_the_key(self):
        with tempfile.TemporaryDirectory() as td:
            g=PairReceipts(Path(td)/'pairs.json',near)
            a=Part.makeBox(2,2,2);b=a.copy();g.check(a,b)
            c=b.copy();c.translate(A.Vector(10,0,0));self.assertEqual(g.check(a,c)[1],0)
            self.assertEqual(g.computed,2)

    def test_radii_change_the_decision_key(self):
        with tempfile.TemporaryDirectory() as td:
            g=PairReceipts(Path(td)/'pairs.json',near)
            a=Part.makeLine(A.Vector(0,0,0),A.Vector(10,0,0))
            b=Part.makeLine(A.Vector(0,2,0),A.Vector(10,2,0))
            self.assertGreater(g.check(a,b,.5,.5)[0],1)
            self.assertAlmostEqual(g.check(a,b,1.1,1.1)[0],2)
            self.assertEqual(g.computed,2)

    def test_component_filter_matches_exact_near_distance(self):
        with tempfile.TemporaryDirectory() as td:
            g=PairReceipts(Path(td)/'pairs.json',near)
            a=Part.makeCompound([Part.makeLine(A.Vector(0,0,0),A.Vector(10,0,0)),Part.makeLine(A.Vector(100,100,0),A.Vector(110,100,0))])
            b=Part.makeBox(1,1,1,A.Vector(5,.2,-.5))
            self.assertAlmostEqual(g.check(a,b,.5,0)[0],a.distToShape(b)[0])

if __name__=='__main__':unittest.main()
