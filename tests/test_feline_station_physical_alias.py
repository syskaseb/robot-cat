import json
from pathlib import Path
import sys
import unittest
import FreeCAD as A
import Part
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
from feline_station_zone_domains import materialise,signature
from feline_station_joint_allocation import physical_key

OUT=Path(__file__).resolve().parents[1]/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'


class PhysicalAlias(unittest.TestCase):
    def test_mirrored_historical_axes_same_actual_complete_unit(self):
        plan=json.loads((OUT/'n01-flat-station-architecture.json').read_text());sts={r['ref']:r for r in plan['stations']}
        zones=json.loads((OUT/'n01-case-zone-allocation.json').read_text());slots={r['id']:r for r in zones['candidates']}
        for recipe in (dict(slot_id=15,family='FLAT',departure=-1,bend_mode='OUTWARD_CONCENTRIC'),
                       dict(slot_id=156,family='UNDER_PLATFORM_SHARED_REMOVABLE_COMBS',bend_side=1,head_side=1)):
            a=sts['D_FL'];b=sts['D_RR']
            self.assertNotEqual(signature(a,recipe),signature(b,recipe))
            self.assertEqual(physical_key(a,recipe),physical_key(b,recipe))
            aa,ak=materialise(a,slots[recipe['slot_id']],recipe);bb,bk=materialise(b,slots[recipe['slot_id']],recipe)
            self.assertEqual(list(ak.values()),list(bk.values()))
            for s,t in zip(aa.values(),bb.values()):
                self.assertLess(s.cut(t).Volume+t.cut(s).Volume,1e-5)


if __name__=='__main__':unittest.main()
