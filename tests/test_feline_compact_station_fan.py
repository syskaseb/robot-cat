import json
from pathlib import Path
import sys
import unittest
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/cad'))
from feline_compact_station_fan import unit,legacy_unit,rise_unit
from feline_station_zone_domains import materialise
from feline_remaining_kits import candidates,materialise as remaining_material
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from feline_compact_after_land import unit as after_unit
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'


class CompactFan(unittest.TestCase):
    def test_Psys_whole_fan_rises_above_ACTUAL_minus24_clamp(self):
        stations={s['ref']:s for s in json.loads((OUT/'n01-flat-station-architecture.json').read_text())['stations']}
        choice=json.loads((OUT/'n01-two-lane-comb-joint.json').read_text())['chosen']['P_SYS']
        c=dict(slot=choice['slot'],base_recipe=choice['recipe']);old=legacy_unit(stations['P_SYS'],c);model=rise_unit(stations['P_SYS'],c)
        groups,_=candidates();r=next(r for r in groups['Anchor:Fore'] if r['axis_X_mm']==-24)
        hardware,_=remaining_material('Anchor:Fore',r);query=SolidQueries()
        self.assertLess(query.distance(old['parts']['wire:P_SYS.3'],hardware['RailClamp2Screw']),1.25)
        for n,s in model['parts'].items():
            if not n.startswith('wire:'):
                self.assertLess(s.cut(old['parts'][n]).Volume,1e-7)
                self.assertLess(old['parts'][n].cut(s).Volume,1e-7)
            for other,t in hardware.items():
                if bbox_lower_bound(s.BoundBox,t.BoundBox)>=1.25:continue
                self.assertGreaterEqual(query.distance(s,t),1.25-1e-6,(n,other))
        serial=lambda x:json.dumps(x,default=lambda a:a.tolist(),sort_keys=True)
        self.assertEqual(serial(model['reused_jacket_lands']),serial(old['reused_jacket_lands']))
        for w in model['wires']:
            self.assertGreaterEqual(w['R_mm'],w['minimum_R_mm'])
            for n,s in model['parts'].items():
                if not n.startswith('wire:'):self.assertLess(model['parts']['wire:'+w['endpoint']].common(s).Volume,1e-7)

    def test_shared_legacy_rule_preserves_all_stock_and_protected_W043(self):
        stations={s['ref']:s for s in json.loads((OUT/'n01-flat-station-architecture.json').read_text())['stations']}
        selected=json.loads((OUT/'n01-two-lane-comb-joint.json').read_text())['chosen'];count=0
        for ref,choice in selected.items():
            if choice['kind']!='received_legacy_unit':continue
            st=stations[ref];model=legacy_unit(st,dict(slot=choice['slot'],base_recipe=choice['recipe']))
            before,_=materialise(st,choice['slot'],choice['recipe'])
            for n,s in before.items():
                if not n.startswith('wire:'):
                    self.assertLess(s.cut(model['parts'][n]).Volume,1e-7)
                    self.assertLess(model['parts'][n].cut(s).Volume,1e-7)
            count+=1
            if ref=='P_SYS':
                self.assertEqual(len(model['reused_jacket_lands']),1)
                self.assertEqual(model['reused_jacket_lands'][0]['wire'],'W043')
                self.assertEqual(len(model['wires']),3)
        self.assertEqual(count,6)

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
