import sys
import unittest
from pathlib import Path
import FreeCAD
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/cad'))
from feline_remaining_kits import candidates as original_candidates
from feline_bank_selected_t18i import candidates,materialise,dimensions,current_profile
from feline_bank_zoned_layout import materialise as old_materialise
from feline_remaining_kits import materialise as original_materialise


class SelectedBankHead(unittest.TestCase):
    def test_all24_full_selected_upper_heads_nonheads_unchanged(self):
        groups,_=original_candidates();rows=candidates(groups);self.assertEqual(len(rows),24)
        self.assertEqual(dimensions(),(4.3,5.3,5.0))
        for group,recipes in rows.items():
            r=next(r for r in recipes if not r.get('joint_current_bank_plane'));new,nk=materialise(group,r);old,ok=old_materialise(group,r)
            self.assertEqual(nk,ok)
            for name,s in new.items():
                if name.endswith('head_budget'):
                    self.assertAlmostEqual(s.Volume,113.95,places=5)
                    self.assertLess(s.cut(old[name]).Volume,1e-7)
                else:
                    self.assertEqual(s.exportBrepToString(),old[name].exportBrepToString())

    def test_current_shared_planes_keep_full_caps_bands_and_clear_own_wires(self):
        groups,_=original_candidates();rows=candidates(groups)
        for group,recipes in rows.items():
            r=recipes[0];self.assertTrue(r['joint_current_bank_plane'])
            p=current_profile(group,r);self.assertAlmostEqual(FreeCAD.Vector(*p['start']).distanceToPoint(FreeCAD.Vector(*p['tip'])),9)
            parts,kinds=materialise(group,r);old,_=original_materialise(group,r['base_recipe'])
            for name,s in parts.items():
                if kinds[name]=='proposal_wire':
                    for other,t in parts.items():
                        if kinds[other]!='proposal_wire':self.assertLess(s.common(t).Volume,1e-7,(group,other))
                elif not name.endswith('head_budget'):self.assertAlmostEqual(s.Volume,old[name].Volume,places=5)


if __name__=='__main__':unittest.main()
