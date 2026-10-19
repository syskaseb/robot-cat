import json
from pathlib import Path
import sys
import unittest
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/cad'))
from plan_feline_layout import OUT
from feline_above_hardware_grip import unit
from feline_compact_after_land import unit as original
from feline_remaining_kits import candidates,materialise
from feline_bank_exit_lanes import under_key_candidates,under_key_materialise
from feline_fore_power_pair import SolidQueries,pair_spacing
from feline_solid_distance import bbox_lower_bound


class AboveFullHardware(unittest.TestCase):
    def test_whole_stock_and5wires_clear_all12_rear_hardware_and_W051(self):
        st=next(s for s in json.loads((OUT/'n01-flat-station-architecture.json').read_text())['stations'] if s['ref']=='D_FL')
        c=json.loads((OUT/'n01-two-lane-comb-joint.json').read_text())['chosen']['D_FL'];choice=dict(slot=c['slot'],base_recipe=c['recipe'])
        old=original(st,choice);model=unit(st,choice);groups,_=candidates()
        hardware,hk=materialise('Anchor:Rear',next(r for r in groups['Anchor:Rear'] if r['axis_X_mm']==72))
        recipe=under_key_candidates(groups)['Bank:W051/body/end'][0];bank,bk=under_key_materialise('Bank:W051/body/end',recipe);query=SolidQueries()
        self.assertLess(model['full_stock_guard_mm'],model['previous_axial_guard_mm'])
        for name,s in model['parts'].items():
            if not name.startswith('wire:'):self.assertAlmostEqual(s.Volume,old['parts'][name].Volume,places=5)
            else:self.assertLess(s.cut(old['parts'][name]).Volume,1e-7,'Shorter wire is a subset of received own wire spacing')
            for other,t in hardware.items():
                if bbox_lower_bound(s.BoundBox,t.BoundBox)<1.25:self.assertGreaterEqual(query.distance(s,t),1.25-1e-6,(name,other))
            for other,t in bank.items():
                required=pair_spacing('Current:'+name,dict(kind=model['kinds'][name]),'Bank:'+other,dict(kind=bk[other]))
                if bbox_lower_bound(s.BoundBox,t.BoundBox)<required:self.assertGreaterEqual(query.distance(s,t),required-1e-6,(name,other))
        for w in model['wires']:
            self.assertGreaterEqual(w['R_mm'],w['minimum_R_mm']);self.assertEqual(w['grip_length_mm'],9)
            for n,s in model['parts'].items():
                if not n.startswith('wire:'):self.assertLess(model['parts']['wire:'+w['endpoint']].common(s).Volume,1e-7,n)
        print('Guard',model['previous_axial_guard_mm'],'to',model['full_stock_guard_mm'],'whole stock minZ',model['clearance_basis']['lowest_full_stock_mm'])


if __name__=='__main__':unittest.main()
