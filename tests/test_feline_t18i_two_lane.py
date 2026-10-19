import json
from pathlib import Path
import sys
import unittest
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/cad'))
from feline_t18i_two_lane import unit
from feline_t18i_selected_head import unit as original
from feline_fore_power_pair import SolidQueries,pair_spacing
from feline_solid_distance import bbox_lower_bound
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'


class TwoLane(unittest.TestCase):
    def test_all_mouths_and_9mm_grips_preserved(self):
        stations=json.loads((OUT/'n01-flat-station-architecture.json').read_text())['stations']
        st=next(s for s in stations if s['ref']=='G2')
        for side in (-1,1):
            slot=dict(id=0,profile='standard',centre_mm=[0.,side*66.,45.26],dimensions_mm=[30.,19.,9.],side=side,tier='interdeck')
            before=original(st,slot);after=unit(st,slot,1)
            self.assertLess(before['parts']['case'].cut(after['parts']['case']).Volume,1e-8)
            for a,b in zip(before['wires'],after['wires']):
                self.assertEqual(a['point_mm'],b['point_mm']);self.assertEqual(a['departure_axis'],b['departure_axis'])
                self.assertEqual(b['grip_length_mm'],9);self.assertEqual(a['minimum_R_mm'],b['minimum_R_mm'])
                self.assertLess(before['parts']['wire:'+a['endpoint']].cut(after['parts']['wire:'+b['endpoint']]).Volume,1e-7)
                for n in ('case','split_common_comb','band_budget','head_budget'):
                    self.assertLess(after['parts']['wire:'+b['endpoint']].common(after['parts'][n]).Volume,1e-7)

    def test_adjacent_full_units_have_real_shared_air_gaps(self):
        stations={s['ref']:s for s in json.loads((OUT/'n01-flat-station-architecture.json').read_text())['stations']}
        q=SolidQueries()
        for side in (-1,1):
            a=unit(stations['D_FL'],dict(id=0,profile='standard',centre_mm=[0.,side*66.,45.26],dimensions_mm=[30.,19.,9.],side=side,tier='interdeck'),0)
            b=unit(stations['G2'],dict(id=1,profile='standard',centre_mm=[31.25,side*66.,45.26],dimensions_mm=[30.,19.,9.],side=side,tier='interdeck'),1)
            for n,s in a['parts'].items():
                for other,t in b['parts'].items():
                    kind=lambda name:'wire' if name.startswith('wire:') else 'project_stock_reservation' if 'budget' in name else 'proposal_material'
                    minimum=pair_spacing('A:'+n,dict(kind=kind(n)),'B:'+other,dict(kind=kind(other)))
                    if bbox_lower_bound(s.BoundBox,t.BoundBox)>=minimum:continue
                    self.assertGreaterEqual(q.distance(s,t),minimum-1e-6,(side,n,other))


if __name__=='__main__':unittest.main()
