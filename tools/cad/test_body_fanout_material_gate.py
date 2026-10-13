"""Regression checks for scoped mouths and exact broad-phase margins."""
import tempfile
import unittest
from pathlib import Path
import FreeCAD as A
import Part
from check_body_fanout_material import terminal_trim,mate_names,AtomicPairs
from plan_current_mta_interfaces import line
from immutable_bounds import ImmutableBounds


class GateTest(unittest.TestCase):
    def test_only_last_mouth_is_trimmed(self):
        a=line([0,0,0],[0,0,5]);b=line([0,0,5],[0,0,14])
        result=terminal_trim([a,b])
        self.assertEqual(result[0],a)
        self.assertEqual(result[-1]['end'],[0.,0.,12.5])
        self.assertAlmostEqual(result[-1]['length_mm'],7.5)

    def test_receiver_exceptions_are_named_not_whole_bank(self):
        self.assertEqual(mate_names(dict(core='D',receiver_role='D_FL.2')),{'D_FL'})
        self.assertEqual(mate_names(dict(core='V',receiver_role='F_RR2.out')),
            {'F_R5_CP2_OUT','F_R5_CP2_Housing'})

    def test_project_margin_reaches_exact_component_pairs(self):
        first=Part.makeLine(A.Vector(0,0,0),A.Vector(10,0,0))
        second=Part.makeLine(A.Vector(0,1.1,0),A.Vector(10,1.1,0))
        with tempfile.TemporaryDirectory() as folder:
            bounds=ImmutableBounds();cache=AtomicPairs(Path(folder)/'pairs.json',bounds.near)
            gap,_=cache.check(first,second,1.25,0)
            self.assertAlmostEqual(gap,1.1)
            cache.save()
            reopened=AtomicPairs(Path(folder)/'pairs.json',bounds.near)
            self.assertEqual(reopened.check(first,second,1.25,0),[gap,0])
            self.assertEqual(reopened.reused,1)


if __name__=='__main__':unittest.main()
