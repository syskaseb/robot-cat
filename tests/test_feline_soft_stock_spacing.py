import sys
import unittest
from pathlib import Path
import FreeCAD
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
from feline_fore_power_pair import pair_spacing


class MaterialMargins(unittest.TestCase):
    def test_all_soft_combinations_use_the_documented_point2_reserve(self):
        soft=[('Current:wire:W001',dict(kind='proposal_wire')),
              ('Current:band_budget',dict(kind='project_stock_reservation')),
              ('Current:head_budget',dict(kind='project_stock_reservation'))]
        for a,ar in soft:
            for b,br in soft:self.assertEqual(pair_spacing(a,ar,b,br),.2,(a,b))

    def test_rigid_and_bare_interfaces_keep_point1_25(self):
        for name,kind in [('Current:split_cap_exterior','proposal_material'),('Module','purchased_case'),('Current:bare','bare')]:
            for soft,sk in [('Current:wire:W001','proposal_wire'),('Current:band_budget','project_stock_reservation')]:
                self.assertEqual(pair_spacing(name,dict(kind=kind),soft,dict(kind=sk)),1.25)


if __name__=='__main__':unittest.main()
