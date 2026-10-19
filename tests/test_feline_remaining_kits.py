import json
from pathlib import Path
import sys
import unittest
import FreeCAD as A
import Part
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/cad'))
from feline_remaining_kits import candidates,materialise
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'


class RemainingKits(unittest.TestCase):
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
