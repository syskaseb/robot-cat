import sys
import unittest
from pathlib import Path
import FreeCAD as A
import Part
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
from feline_solid_distance import distance


class SolidDistance(unittest.TestCase):
    def test_containment_compound_regression(self):
        outer=Part.makeBox(100,100,100);inner=Part.makeBox(20,20,20,A.Vector(40,40,40));wrapped=Part.makeCompound([outer])
        self.assertGreater(wrapped.distToShape(inner)[0],1.25)
        self.assertEqual(distance(wrapped,inner),0)
        self.assertEqual(distance(inner,wrapped),0)

    def test_all_children_not_only_first(self):
        a=Part.makeBox(10,10,10,A.Vector(100,0,0));b=Part.makeBox(20,20,20);inner=Part.makeBox(2,2,2,A.Vector(5,5,5))
        self.assertEqual(distance(Part.makeCompound([a,b]),inner),0)

    def test_separation_and_transformed_child_frame(self):
        big=Part.makeCompound([Part.makeBox(10,10,10)])
        big.Placement=A.Placement(A.Vector(50,0,0),A.Rotation(A.Vector(0,0,1),90))
        inner=Part.makeBox(2,2,2,A.Vector(43,4,4))
        self.assertEqual(distance(big,inner),0)
        other=Part.makeBox(5,5,5,A.Vector(55,0,0))
        self.assertAlmostEqual(distance(big,other),5)

    def test_shell_is_not_a_material_solid(self):
        shell=Part.makeBox(10,10,10).Shells[0]
        with self.assertRaises(AssertionError):distance(shell,Part.makeBox(1,1,1))


if __name__=='__main__':unittest.main()
