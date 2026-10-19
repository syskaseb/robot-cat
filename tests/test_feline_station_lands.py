import json
from pathlib import Path
import sys
import unittest
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/cad'))
from compose_feline_shared_layout import station_model,station_lands
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'


class AllStationLands(unittest.TestCase):
    def test_all86_including_preserved_W043_and_vertical_cases(self):
        stations={s['ref']:s for s in json.loads((OUT/'n01-flat-station-architecture.json').read_text())['stations']}
        chosen=json.loads((OUT/'n01-two-lane-comb-joint.json').read_text())['chosen']
        result=[]
        for group,st in stations.items():
            rows=station_lands(st,station_model(st,chosen[group]));result+=rows
            self.assertEqual(len(rows),len(st['ports']))
            self.assertTrue(all(r['grip_length_mm']==9 and r['radius_mm']>0 for r in rows))
        self.assertEqual(len(result),86)
        self.assertEqual(len({r['endpoint'] for r in result}),86)
        old=next(r for r in result if r['wire']=='W043')
        self.assertTrue(old['not_new_connector'])
        self.assertEqual(old['grip_length_mm'],9)


if __name__=='__main__':unittest.main()
