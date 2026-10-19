from pathlib import Path
import sys
import unittest
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/cad'))
from feline_remaining_kits import candidates as source_candidates
from feline_bank_exit_lanes import under_key_candidates,under_key_materialise
from feline_bank_receiving_grips import candidates,materialise,grip_line,both_after_candidates,both_after_materialise,both_after_line
from feline_fore_power_pair import SolidQueries,pair_spacing
from feline_solid_distance import bbox_lower_bound


class CompleteReceivingPairs(unittest.TestCase):
    def test_all11_whole_grips_move_rigidly_but_no_wire_changes(self):
        groups,_=source_candidates()
        for group,recipes in candidates(groups).items():
            recipe=recipes[0];before,kinds=under_key_materialise(group,recipe);after,_=materialise(group,recipe)
            for n,s in before.items():
                self.assertAlmostEqual(after[n].Volume,s.Volume,places=5,msg=(group,n))
                if kinds[n]=='proposal_wire':
                    self.assertLess(after[n].cut(s).Volume,1e-7);self.assertLess(s.cut(after[n]).Volume,1e-7)
                else:
                    for wn,w in after.items():
                        if kinds[wn]=='proposal_wire':self.assertLess(w.common(after[n]).Volume,1e-7,(group,n))
            start,axis,tip=grip_line(recipe);self.assertAlmostEqual(A.Vector(*start).distanceToPoint(A.Vector(*tip)),9)

    def test_old_one_sided_after_receivers_REJECTED_not_just_wire_pass(self):
        groups,_=source_candidates();left=under_key_candidates(groups);right=candidates(groups);query=SolidQueries()
        for a,b in (('Bank:W028/single/end','Bank:W038/single/end'),('Bank:W020/body/end','Bank:W031/body/end')):
            accepted=[];reasons={}
            for ar in left[a]:
                aa,ak=under_key_materialise(a,ar)
                for br in right[b]:
                    bb,bk=materialise(b,br);ok=True
                    for n,s in aa.items():
                        for other,t in bb.items():
                            minimum=pair_spacing(a+':'+n,dict(kind=ak[n]),b+':'+other,dict(kind=bk[other]))
                            if bbox_lower_bound(s.BoundBox,t.BoundBox)<minimum:
                                gap=query.distance(s,t)
                                if gap<minimum-1e-6:
                                    reason=(n,other,round(gap,6),minimum);reasons[reason]=reasons.get(reason,0)+1;ok=False;break
                        if not ok:break
                    if ok:accepted.append((ar['base_recipe'].get('complete_band_head_degrees'),br['base_recipe'].get('complete_band_head_degrees')))
            print('Whole receiving pair',a,b,'complete stock choices',accepted,'rejections',reasons)
            with self.subTest(a=a,b=b):self.assertFalse(accepted,'Known rejected one-sided family must not be called accepted')

    def test_all24_both_after_full9_stock_and_own_fit(self):
        groups,_=source_candidates()
        from feline_remaining_kits import materialise as original
        for group,recipes in both_after_candidates(groups).items():
            recipe=recipes[0];before,kinds=original(group,recipe['base_recipe']);after,_=both_after_materialise(group,recipe)
            for n,s in before.items():
                if kinds[n]!='proposal_wire':self.assertAlmostEqual(after[n].Volume,s.Volume,places=5,msg=(group,n))
            start,axis,tip,b=both_after_line(group,recipe);self.assertAlmostEqual(A.Vector(*start).distanceToPoint(A.Vector(*tip)),9)
            for wn,w in after.items():
                if kinds[wn]!='proposal_wire':continue
                for n,s in after.items():
                    if kinds[n]!='proposal_wire':self.assertLess(w.common(s).Volume,1e-7,(group,n))

    def test_both_after_complete_IN_OUT_material_pair_choices(self):
        groups,_=source_candidates();rows=both_after_candidates(groups);query=SolidQueries()
        for a,b in (('Bank:W028/single/end','Bank:W038/single/end'),('Bank:W020/body/end','Bank:W031/body/end')):
            accepted=[];reasons={}
            for ar in rows[a]:
                aa,ak=both_after_materialise(a,ar)
                for br in rows[b]:
                    bb,bk=both_after_materialise(b,br);ok=True
                    for n,s in aa.items():
                        for other,t in bb.items():
                            minimum=pair_spacing(a+':'+n,dict(kind=ak[n]),b+':'+other,dict(kind=bk[other]))
                            if bbox_lower_bound(s.BoundBox,t.BoundBox)<minimum:
                                gap=query.distance(s,t)
                                if gap<minimum-1e-6:
                                    reason=(n,other,round(gap,6),minimum);reasons[reason]=reasons.get(reason,0)+1;ok=False;break
                        if not ok:break
                    if ok:accepted.append((ar['base_recipe'].get('complete_band_head_degrees'),br['base_recipe'].get('complete_band_head_degrees')))
            print('Both AFTER whole pair',a,b,'accepted',accepted,'rejections',reasons)
            with self.subTest(a=a,b=b):self.assertTrue(accepted,'Complete two-sided material fit, not wire-only pass')


if __name__=='__main__':unittest.main()
