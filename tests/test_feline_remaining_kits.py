import json
from pathlib import Path
import sys
import unittest
import FreeCAD as A
import Part
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/cad'))
from feline_remaining_kits import candidates,materialise,source_wire_signature
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'


class RemainingKits(unittest.TestCase):
    def test_after_arc_grips_preserve_entire_existing_wire_and_all9mm(self):
        groups,_=candidates();group='Bank:W059/body/end'
        after=[r for r in groups[group] if r.get('grip_site')=='AFTER_BEND']
        self.assertTrue(after)
        for r in after[:3]:
            old=next(x for x in groups[group] if x.get('grip_site') is None and
                     source_wire_signature(group,x)==source_wire_signature(group,r) and
                     x['complete_band_head_degrees']==r['complete_band_head_degrees'])
            before,_=materialise(group,old);now,_=materialise(group,r)
            name=next(n for n in now if n.startswith('wire:'))
            self.assertLess(before[name].cut(now[name]).Volume,1e-7)
            self.assertLess(now[name].cut(before[name]).Volume,1e-7)
            self.assertAlmostEqual(before[name].Volume,now[name].Volume,places=6)
            for n,s in now.items():
                if n!=name:self.assertLess(now[name].common(s).Volume,1e-7,n)
            self.assertEqual(r['existing_after_arc_straight_grip_mm'],9)

    def test_only_remaining27_and_source_all24_mouths(self):
        groups,pins=candidates()
        self.assertEqual(len(groups),27)
        self.assertEqual(sum(n.startswith('Bank:') for n in groups),24)
        proof=json.loads((OUT/'n01-flat20-field-modulejoint.json').read_text())
        for p in proof['bank_joint_full_source_ports']:
            for r in groups['Bank:'+p['id']]:
                self.assertTrue(np.allclose(r['point_mm'],p['start_mm'],atol=1e-10))
                self.assertTrue(np.allclose(r['departure_axis'],p['departure_axis'],atol=1e-10))
                self.assertEqual(r['R_mm'],p['bend_R_mm'])
        for group in ('Bank:W027/single/end','Bank:W028/single/end','Anchor:Fore','F_PWM_whole'):
            parts,kinds=materialise(group,groups[group][0])
            self.assertEqual(set(parts),set(kinds))
            self.assertTrue(all(s.isValid() and s.Solids for s in parts.values()))
            if group=='Anchor:Fore':self.assertEqual(len(parts),12)
            if group=='F_PWM_whole':self.assertEqual(len(parts),11)
            if group=='Bank:W028/single/end':
                wire=next(s for n,s in parts.items() if n.startswith('wire:'))
                for n,s in parts.items():
                    if not n.startswith('wire:'):self.assertLess(wire.common(s).Volume,1e-7,n)


if __name__=='__main__':unittest.main()
