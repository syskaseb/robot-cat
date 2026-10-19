"""Validity caching must never reuse children at an old rigid location."""
from pathlib import Path
import sys
import unittest
import FreeCAD as A
import Part
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
from feline_fore_power_pair import SolidQueries


class SolidCache(unittest.TestCase):
    def test_changed_parent_placement_invalidates_cached_children(self):
        q=SolidQueries();a=Part.makeBox(2,2,2);b=Part.makeBox(2,2,2,A.Vector(5,0,0))
        self.assertAlmostEqual(q.distance(a,b),3)
        a.translate(A.Vector(5,0,0))
        self.assertEqual(q.distance(a,b),0)
        a.translate(A.Vector(10,0,0))
        self.assertAlmostEqual(q.distance(a,b),8)

    def test_containment_is_not_positive_air_gap_at_compound_level(self):
        a=Part.makeCompound([Part.makeBox(10,10,10)])
        b=Part.makeBox(1,1,1,A.Vector(4,4,4))
        self.assertEqual(SolidQueries().distance(a,b),0)


if __name__=='__main__':unittest.main()
