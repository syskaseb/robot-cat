import json
from pathlib import Path
import sys
import unittest
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/cad'))
from feline_shared_straight_combs import unit as original,slots
from feline_t18i_selected_head import unit,source
from feline_fore_power_pair import pair_spacing
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'


class SelectedHead(unittest.TestCase):
    def test_existing_nylon_policy_is_not_a_rigid_case_waiver(self):
        tie=dict(kind='project_stock_reservation');wire=dict(kind='wire');case=dict(kind='proposal_material')
        self.assertEqual(pair_spacing('Current:head_budget',tie,'Current:wire:1',wire),.2)
        self.assertEqual(pair_spacing('Current:head_budget',tie,'Current:case',case),1.25)
        self.assertEqual(pair_spacing('Current:split_common_comb',case,'Current:wire:1',wire),1.25)

    def test_manufacturer_tolerance_envelope_and_original_inputs_preserved(self):
        doc=source();self.assertEqual(doc['installed_head_local_u_n_t_upper_mm'],[4.3,5.3,5.0])
        stations=json.loads((OUT/'n01-flat-station-architecture.json').read_text())['stations']
        for ref in ('D_FL','FL_P','P_FRONT','G1'):
            st=next(s for s in stations if s['ref']==ref)
            profile='large' if st['flat_dimensions_pitch_departure_thickness_mm'][2]>10 else 'standard'
            for side in (-1,1):
                slot=next(s for s in slots() if s['profile']==profile and s['side']==side)
                before=original(st,slot);after=unit(st,slot)
                self.assertEqual(before['wires'],after['wires'])
                for name,a in before['parts'].items():
                    b=after['parts'][name]
                    if name=='head_budget':
                        self.assertAlmostEqual(b.Volume,113.95)
                        self.assertLess(b.cut(a).Volume,1e-7)
                    else:self.assertLess(a.cut(b).Volume+b.cut(a).Volume,1e-7,(ref,name))
                for w in after['wires']:
                    self.assertLess(after['parts']['head_budget'].common(after['parts']['wire:'+w['endpoint']]).Volume,1e-7)


if __name__=='__main__':unittest.main()
