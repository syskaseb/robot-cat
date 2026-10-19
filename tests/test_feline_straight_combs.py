import json
from pathlib import Path
import sys
import unittest
import FreeCAD as A
import Part

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/cad'))
from feline_shared_straight_combs import slots,unit
from feline_simple_comb_joint import physical_key
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'


class StraightCombs(unittest.TestCase):
    def test_source_ports_full9_land_and_lateral_head(self):
        stations=json.loads((OUT/'n01-flat-station-architecture.json').read_text())['stations']
        for ref in ('D_FL','FL_P','P_FRONT','G1'):
            st=next(s for s in stations if s['ref']==ref)
            profile='large' if st['flat_dimensions_pitch_departure_thickness_mm'][2]>10 else 'standard'
            for side in (-1,1):
                slot=next(s for s in slots() if s['profile']==profile and s['side']==side)
                m=unit(st,slot);parts=m['parts']
                self.assertAlmostEqual(parts['case'].Volume,st['source_part_record']['volume_mm3'])
                self.assertAlmostEqual(parts['head_budget'].Volume,216)
                self.assertLess(m['nylon_loop_upper_bound_mm'],100)
                self.assertEqual(len(m['wires']),len(st['ports']))
                for w in m['wires']:
                    self.assertEqual(w['grip_length_mm'],9)
                    self.assertGreaterEqual(w['minimum_R_mm'],next(p['minimum_project_R_mm'] for p in st['ports'] if p['endpoint']==w['endpoint']))
                    for n in ('case','split_common_comb','band_budget','head_budget'):
                        self.assertLess(parts['wire:'+w['endpoint']].common(parts[n]).Volume,1e-5,(ref,side,n))
                self.assertLess(parts['head_budget'].common(parts['split_common_comb']).Volume,1e-5)

    def test_no_fake_large_interdeck_acceptance(self):
        slot=next(s for s in slots() if s['profile']=='large' and s['tier']=='interdeck')
        self.assertAlmostEqual(52-slot['centre_mm'][2]-slot['dimensions_mm'][2]/2,1.24)
        self.assertLess(52-slot['centre_mm'][2]-slot['dimensions_mm'][2]/2,1.25)

    def test_physical_alias_keys_match_received_actual_constructors(self):
        stations={s['ref']:s for s in json.loads((OUT/'n01-flat-station-architecture.json').read_text())['stations']}
        receiver=json.loads((OUT/'n01-straight-combs-received.json').read_text())
        for r in receiver['units'].values():
            if r.get('physical_key'):
                self.assertEqual(physical_key(stations[r['ref']],r['slot']),r['physical_key'],r['ref'])


if __name__=='__main__':unittest.main()
