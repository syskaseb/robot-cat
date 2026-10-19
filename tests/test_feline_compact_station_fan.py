import json
from pathlib import Path
import sys
import unittest
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/cad'))
from feline_compact_station_fan import unit
from feline_station_zone_domains import materialise
from feline_remaining_kits import candidates,materialise as remaining_material
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from feline_compact_after_land import unit as after_unit
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'


class CompactFan(unittest.TestCase):
    def test_fixed_first9_rejection_preserved_and_after_grip_clears_rear72(self):
        st=next(s for s in json.loads((OUT/'n01-flat-station-architecture.json').read_text())['stations'] if s['ref']=='D_FL')
        choice=json.loads((OUT/'n01-two-lane-comb-joint.json').read_text())['chosen']['D_FL']
        new=unit(st,dict(slot=choice['slot'],base_recipe=choice['recipe']))
        old,_=materialise(st,choice['slot'],choice['recipe'])
        groups,_=candidates();r=next(r for r in groups['Anchor:Rear'] if r['axis_X_mm']==72)
        hardware,_=remaining_material('Anchor:Rear',r);query=SolidQueries()
        self.assertLess(query.distance(old['wire:D_FL.1'],hardware['RailClamp3Screw']),1.25)
        self.assertLess(query.distance(new['parts']['wire:D_FL.1'],hardware['RailClamp3Screw']),1.25)
        after=after_unit(st,dict(slot=choice['slot'],base_recipe=choice['recipe']))
        for name,s in after['parts'].items():
            for other,t in hardware.items():
                if bbox_lower_bound(s.BoundBox,t.BoundBox)>=1.25:continue
                self.assertGreaterEqual(query.distance(s,t),1.25-1e-6,(name,other))
        self.assertLessEqual(after['new_prefix_mm'],after['old_shortest_prefix_mm'])
        for r in after['wires']:
            self.assertGreaterEqual(r['R_mm'],r['minimum_R_mm'])
            self.assertEqual(r['grip_length_mm'],9)
            self.assertAlmostEqual(A.Vector(*r['grip_start_mm']).distanceToPoint(A.Vector(*r['grip_end_mm'])),9)
            for n,s in after['parts'].items():
                if not n.startswith('wire:'):self.assertLess(after['parts']['wire:'+r['endpoint']].common(s).Volume,1e-7,n)

    def test_fixed_all5_mouths_9grips_case_stock_and_minimumR(self):
        st=next(s for s in json.loads((OUT/'n01-flat-station-architecture.json').read_text())['stations'] if s['ref']=='D_FL')
        choice=json.loads((OUT/'n01-two-lane-comb-joint.json').read_text())['chosen']['D_FL']
        new=unit(st,dict(slot=choice['slot'],base_recipe=choice['recipe']))
        old,_=materialise(st,choice['slot'],choice['recipe'])
        self.assertEqual(len(new['wires']),5)
        for n,s in old.items():
            if not n.startswith('wire:'):
                self.assertLess(s.cut(new['parts'][n]).Volume,1e-7)
                self.assertLess(new['parts'][n].cut(s).Volume,1e-7)
        for r in new['wires']:
            self.assertGreaterEqual(r['R_mm'],r['minimum_R_mm'])
            prefix=Part.makeCylinder(r['radius'],9,A.Vector(*r['point_mm']),A.Vector(*r['departure_axis']))
            self.assertLess(prefix.cut(new['parts']['wire:'+r['endpoint']]).Volume,1e-7)
            for n,s in new['parts'].items():
                if not n.startswith('wire:'):self.assertLess(new['parts']['wire:'+r['endpoint']].common(s).Volume,1e-7,n)


if __name__=='__main__':unittest.main()
