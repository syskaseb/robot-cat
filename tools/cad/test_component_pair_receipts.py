import tempfile,unittest
from pathlib import Path
import FreeCAD as A
import Part
from exact_pair_receipts import PairReceipts
from component_pair_receipts import ComponentPairReceipts
from immutable_bounds import ImmutableBounds

class CompoundTest(unittest.TestCase):
    def test_clear_overlap_containment_wire_and_placement(self):
        source=Part.makeCompound([Part.makeBox(3,4,5),Part.makeBox(3,4,5,A.Vector(30,0,0))])
        targets=[(Part.makeBox(2,2,2,A.Vector(1,1,1)),0),
            (Part.makeBox(2,2,2,A.Vector(2,2,2)),0),
            (Part.makeBox(2,2,2,A.Vector(14,1,1)),0),
            (Part.makeLine(A.Vector(-1,-.4,2),A.Vector(35,-.4,2)),.5),
            (Part.makeLine(A.Vector(-1,-2,2),A.Vector(35,-2,2)),.5)]
        with tempfile.TemporaryDirectory() as td:
            for angle in (0,23):
                s=source.copy();s.rotate(A.Vector(),A.Vector(0,0,1),angle)
                for index,(t,radius) in enumerate(targets):
                    t=t.copy();t.rotate(A.Vector(),A.Vector(0,0,1),angle)
                    old=PairReceipts(Path(td)/'unused.json',ImmutableBounds().near)
                    new=ComponentPairReceipts(Path(td)/(str(angle)+'_'+str(index)+'.json'),ImmutableBounds().near)
                    g,v=old.check(s,t,0,radius);G,V=new.check(s,t,0,radius)
                    self.assertEqual(g<radius-1e-4,G<radius-1e-4)
                    self.assertAlmostEqual(v,V,places=6)
                    self.assertEqual(new.decomposed,1)

    def test_mixed_compound_is_not_decomposed(self):
        s=Part.makeCompound([Part.makeBox(2,2,2),Part.makeLine(A.Vector(4,0,0),A.Vector(8,0,0))])
        with tempfile.TemporaryDirectory() as td:
            c=ComponentPairReceipts(Path(td)/'p.json',ImmutableBounds().near)
            c.fingerprint(s);self.assertEqual(c.decomposed,0)

    def test_reuses_legacy_and_new_saved_negative_results(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'p.json';s=Part.makeBox(3,4,5);t=Part.makeBox(3,4,5,A.Vector(1,0,0))
            old=PairReceipts(p,ImmutableBounds().near);expected=old.check(s,t);old.save()
            new=ComponentPairReceipts(p,ImmutableBounds().near)
            self.assertEqual(new.check(s,t),expected);self.assertEqual(new.reused,1)
            new.save();again=ComponentPairReceipts(p,ImmutableBounds().near)
            self.assertEqual(again.check(s,t),expected);self.assertEqual(again.reused,1)

if __name__=='__main__':unittest.main()
