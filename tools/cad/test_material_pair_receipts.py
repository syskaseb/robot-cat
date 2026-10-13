import tempfile,unittest
from pathlib import Path
import FreeCAD as A
import Part
from exact_pair_receipts import PairReceipts
from material_pair_receipts import MaterialPairReceipts
from immutable_bounds import ImmutableBounds

class MaterialTests(unittest.TestCase):
    def test_overlap_containment_touch_disjoint_and_wire(self):
        s=Part.makeBox(5,5,5)
        targets=[Part.makeBox(2,2,2,A.Vector(1,1,1)),Part.makeBox(2,2,2,A.Vector(4,2,2)),
                 Part.makeBox(2,2,2,A.Vector(5,2,2)),Part.makeBox(2,2,2,A.Vector(8,2,2))]
        with tempfile.TemporaryDirectory() as td:
            for i,t in enumerate(targets):
                old=PairReceipts(Path(td)/'old.json',ImmutableBounds().near)
                expected=old.check(s,t)[1]
                new=MaterialPairReceipts(Path(td)/(str(i)+'.json'),ImmutableBounds().near)
                actual=new.check(s,t);self.assertIsNone(actual[0])
                self.assertAlmostEqual(actual[1],expected,places=6)
                new.save();again=MaterialPairReceipts(Path(td)/(str(i)+'.json'),ImmutableBounds().near)
                self.assertEqual(again.check(s,t),actual);self.assertEqual(again.reused,1)
            wire=Part.makeLine(A.Vector(-1,-.4,2),A.Vector(6,-.4,2))
            self.assertEqual(new.check(s,wire,0,.5),old.check(s,wire,0,.5))
if __name__=='__main__':unittest.main()
