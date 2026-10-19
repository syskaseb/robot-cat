"""Validity caching must never reuse children at an old rigid location."""
from pathlib import Path
import sys
import unittest
import FreeCAD as A
import Part
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
from feline_fore_power_pair import SolidQueries,pair_spacing


class SolidCache(unittest.TestCase):
    def test_soft_insulated_interfaces_do_not_relax_rigid_or_bare_interfaces(self):
        wire={'kind':'proposal_wire'};tie={'kind':'tie_reservation'}
        self.assertEqual(pair_spacing('sleeve20',wire,'BundleTie:FL',tie),.2)
        self.assertEqual(pair_spacing('sleeve20',wire,'BundleCuff:FL',{'kind':'frame_reservation'}),1.25)
        self.assertEqual(pair_spacing('PCA:bare0',{'kind':'bare'},'BundleTie:FL',tie),1.25)
        self.assertEqual(pair_spacing('BundleTie:FR',tie,'P0_Mount',{'kind':'actual_source'}),1.25)

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
