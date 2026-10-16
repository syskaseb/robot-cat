import unittest
import FreeCAD as A
import Part
from local_bank_cradle_material import families,GROUPS
from loom_land_port import box


class BankCradleTests(unittest.TestCase):
    def test_four_families_preserve_twelve_holder_slots_and_ties(self):
        f=families();self.assertEqual(len(f),4)
        for leg,y,centres,owner in GROUPS:
            for side,q in f[leg].items():
                self.assertEqual(q['owner'],owner)
                self.assertEqual(len(q['ties']),6)
                self.assertIsNone(q['recipe']['root_path'])
                ties=list(q['ties'].values())
                for i,t in enumerate(ties):
                    for j,u in enumerate(ties[i+1:],i+1):
                        if t.BoundBox.intersect(u.BoundBox):self.assertLess(t.common(u).Volume,1e-6,(leg,side,i,j))
                for x in centres:
                    fuse=box([x-9.55,y-2.55,126,x+9.55,y+2.55,179.8])
                    self.assertLess(q['body'].common(fuse).Volume,1e-6)
                    for t in q['ties'].values():self.assertLess(t.common(fuse).Volume,1e-6)

    def test_distinct_frame_combs_do_not_overlap_at_group_boundaries(self):
        f=families()
        for left,right in [('FL','RL'),('FR','RR')]:
            for side_a in (-1,1):
                for side_b in (-1,1):
                    # Alternatives need a joint solution, not every arbitrary
                    # closure pairing. Opposite roots put boundary heads on
                    # their opposite long sides; identical roots stagger them.
                    a=f[left][f'{side_a}/1']
                    pattern_b=1 if side_a==side_b else -1
                    b=f[right][f'{side_b}/{pattern_b}']
                    pa=[a['body'],*a['ties'].values()];pb=[b['body'],*b['ties'].values()]
                    for i,s in enumerate(pa):
                        for j,t in enumerate(pb):
                            if s.BoundBox.intersect(t.BoundBox):self.assertLess(s.common(t).Volume,1e-6,(left,right,side_a,side_b,i,j))


if __name__=='__main__':unittest.main()
