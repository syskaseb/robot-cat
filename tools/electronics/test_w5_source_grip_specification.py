import json
from pathlib import Path
import unittest
from w5_source_grips_native_r1 import SEATS

ROOT=Path(__file__).resolve().parents[2]


class SourceSeatSpecificationTests(unittest.TestCase):
    def test_each_clamp_on_straight_insulation_not_bend(self):
        data=json.loads((ROOT/'hardware/electronics/full-cat/w5-s1-source-layout-r8/intent.json').read_text(encoding='utf-8'))
        self.assertEqual(set(SEATS), {'W064','W065','W067','W068'})
        for row in data['routes'][:4]:
            x,y,z,_=SEATS[row['wire']]
            found=[e for e in row['edges'] if e['kind']=='line'
                   and max(abs(e['start'][i]-e['end'][i]) for i in (0,1))<1e-6
                   and abs(e['start'][0]-x)<1e-6 and abs(e['start'][1]-y)<1e-6
                   and min(e['start'][2],e['end'][2])<=z-3
                   and max(e['start'][2],e['end'][2])>=z+3]
            self.assertEqual(len(found),1,row['wire'])

    def test_supplier_band_and_head_not_wire_OD(self):
        r=json.loads((ROOT/'hardware/reference/hellermann-11102370-2026-10-04/dimensions.json').read_text(encoding='utf-8'))
        self.assertEqual((r['length_mm'],r['band_width_mm'],r['band_thickness_mm']),(145,2.5,1.2))
        self.assertLess(r['band_width_mm'],3.2)
        self.assertLess(r['band_thickness_mm'],1.7)
        self.assertLess(35+r['head_length_mm']+20,r['length_mm'])


if __name__=='__main__':unittest.main()
