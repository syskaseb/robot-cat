import sys
import unittest
from pathlib import Path
import FreeCAD
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/cad'))
from feline_remaining_kits import candidates as original_candidates
from feline_bank_selected_t18i import candidates,materialise,dimensions
from feline_bank_zoned_layout import materialise as old_materialise


class SelectedBankHead(unittest.TestCase):
    def test_all24_full_selected_upper_heads_nonheads_unchanged(self):
        groups,_=original_candidates();rows=candidates(groups);self.assertEqual(len(rows),24)
        self.assertEqual(dimensions(),(4.3,5.3,5.0))
        for group,recipes in rows.items():
            r=recipes[0];new,nk=materialise(group,r);old,ok=old_materialise(group,r)
            self.assertEqual(nk,ok)
            for name,s in new.items():
                if name.endswith('head_budget'):
                    self.assertAlmostEqual(s.Volume,113.95,places=5)
                    self.assertLess(s.cut(old[name]).Volume,1e-7)
                else:
                    self.assertEqual(s.exportBrepToString(),old[name].exportBrepToString())


if __name__=='__main__':unittest.main()
