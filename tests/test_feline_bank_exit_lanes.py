import json
from pathlib import Path
import sys
import unittest
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/cad'))
from feline_remaining_kits import candidates as old_candidates,materialise as original
from feline_bank_exit_lanes import candidates,materialise
from feline_fore_power_pair import SolidQueries,pair_spacing
from feline_solid_distance import bbox_lower_bound


class WholeBankPlanes(unittest.TestCase):
    def test_all24_preserve_first9_and_full_selected_before_stock(self):
        groups,_=old_candidates();lanes=candidates(groups)
        for group,recipes in lanes.items():
            recipe=recipes[0];r=recipe['base_recipe'];before,kinds=original(group,r);after,_=materialise(group,recipe)
            for n,s in before.items():
                if kinds[n]=='proposal_wire':
                    prefix=Part.makeCylinder(r.get('radius_mm',r.get('radius')),9,A.Vector(*r['point_mm']),A.Vector(*r['departure_axis']))
                    self.assertLess(prefix.cut(after[n]).Volume,1e-7,group)
                else:
                    self.assertLess(s.cut(after[n]).Volume,1e-7,(group,n))
                    self.assertLess(after[n].cut(s).Volume,1e-7,(group,n))

    def test_opposed_W028_W038_actual_wires_separate_in_Z_not_scalar_offset(self):
        groups,_=old_candidates();lanes=candidates(groups);query=SolidQueries()
        aa,ak=materialise('Bank:W028/single/end',lanes['Bank:W028/single/end'][0])
        bb,bk=materialise('Bank:W038/single/end',lanes['Bank:W038/single/end'][0])
        a=next(s for n,s in aa.items() if ak[n]=='proposal_wire');b=next(s for n,s in bb.items() if bk[n]=='proposal_wire')
        self.assertGreaterEqual(query.distance(a,b),.2-1e-6)


if __name__=='__main__':unittest.main()
