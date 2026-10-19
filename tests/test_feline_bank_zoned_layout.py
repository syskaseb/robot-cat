from pathlib import Path
import sys
import unittest
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/cad'))
from feline_remaining_kits import candidates as original_candidates,materialise as original_material
from feline_bank_receiving_grips import both_after_candidates,both_after_materialise
from feline_bank_zoned_layout import candidates,profile,materialise
from feline_fore_power_pair import SolidQueries,pair_spacing
from feline_solid_distance import bbox_lower_bound


class FunctionalBankZones(unittest.TestCase):
    def test10_changed14_unchanged_all_full9_stock_and_own_fit(self):
        groups,_=original_candidates();changed=candidates(groups);self.assertEqual(len(changed),10)
        for group,rows in both_after_candidates(groups).items():
            r=changed.get(group,rows)[0];parts,kinds=materialise(group,r);before,_=original_material(group,r['base_recipe'])
            if group in changed:
                p=profile(group,r);self.assertAlmostEqual(A.Vector(*p['start']).distanceToPoint(A.Vector(*p['tip'])),9)
            else:
                old,_=both_after_materialise(group,r)
                for n,s in parts.items():self.assertLess(s.cut(old[n]).Volume,1e-7);self.assertLess(old[n].cut(s).Volume,1e-7)
            for n,s in parts.items():
                if kinds[n]!='proposal_wire':self.assertAlmostEqual(s.Volume,before[n].Volume,places=5)
                else:
                    for other,t in parts.items():
                        if kinds[other]!='proposal_wire':self.assertLess(s.common(t).Volume,1e-7,(group,other))

    def test_complete_cross_bank_receiving_pairs_in_all_functional_zones(self):
        groups,_=original_candidates();allrows=both_after_candidates(groups);allrows.update(candidates(groups));query=SolidQueries()
        pairs=[('W028/single/end','W038/single/end'),('W046/single/end','W040/single/end'),
            ('W020/body/end','W031/body/end'),('W024/body/end','W035/body/end'),('W051/body/end','W058/single/end')]
        for a,b in pairs:
            a='Bank:'+a;b='Bank:'+b;accepted=[];reasons={}
            for ar in allrows[a]:
                aa,ak=materialise(a,ar)
                for br in allrows[b]:
                    bb,bk=materialise(b,br);ok=True
                    for n,s in aa.items():
                        for other,t in bb.items():
                            minimum=pair_spacing(a+':'+n,dict(kind=ak[n]),b+':'+other,dict(kind=bk[other]))
                            if bbox_lower_bound(s.BoundBox,t.BoundBox)<minimum:
                                gap=query.distance(s,t)
                                if gap<minimum-1e-6:
                                    k=(n,other,round(gap,6));reasons[k]=reasons.get(k,0)+1;ok=False;break
                        if not ok:break
                    if ok:accepted.append((ar['base_recipe'].get('complete_band_head_degrees'),br['base_recipe'].get('complete_band_head_degrees')))
            print('Zoned complete pair',a,b,'accepted',accepted,'rejected',reasons)
            with self.subTest(a=a,b=b):self.assertTrue(accepted)


if __name__=='__main__':unittest.main()
