import json
from pathlib import Path
import sys
import unittest
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/cad'))
from feline_remaining_kits import candidates,materialise
from feline_shared_frame import build,box,material_connections
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'


class ActualClampFrame(unittest.TestCase):
    def test_all4_actual_axes_full_stack_and_washer_bearing_survive(self):
        groups,_=candidates();chosen={};parts={}
        for group,x in (('Anchor:Fore',-48),('Anchor:Rear',72)):
            recipe=next(r for r in groups[group] if r['axis_X_mm']==x)
            chosen[group]=dict(recipe=recipe)
            pp,_=materialise(group,recipe)
            parts.update({'Station:'+group+':'+n:s for n,s in pp.items()})
        inventory=json.loads((OUT/'n01-current-packaging-inventory.json').read_text())
        fixed={r['name']:box(*r['bounds_mm']) for r in inventory['fixed'] if r['name'].startswith('StructureReserve:BankBed')}
        frame,meta,mates=build(chosen,parts,fixed)
        connections=material_connections(frame)
        self.assertTrue(connections)
        self.assertTrue(all(r['common_mm3']>1e-7 for r in connections))
        self.assertEqual(len(mates),4)
        for group in chosen:
            for index in chosen[group]['recipe']['clamp_indices']:
                root='Station:'+group+':'
                seat=frame[f'ClampSeat:{index}'];washer=parts[root+f'RailClamp{index}TopWasher']
                self.assertLess(seat.common(washer).Volume,1e-7)
                # Solid/solid Boolean common omits a lower-dimensional
                # face mate. Measure the actual coplanar faces, not Volume.
                self.assertLess(seat.distToShape(washer)[0],1e-6)
                self.assertGreater(next(r for r in mates if r['clamp']==index)['washer_planar_bearing_area_mm2'],10)
                screw=parts[root+f'RailClamp{index}Screw']
                for name,s in frame.items():
                    self.assertLess(s.common(screw).Volume,1e-7,(name,index))
        self.assertTrue(all(r['pad_bearing_area_mm2']>=60 for r in mates))


if __name__=='__main__':unittest.main()
