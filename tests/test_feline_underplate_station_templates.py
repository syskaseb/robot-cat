import json
from pathlib import Path
import sys
import unittest
import FreeCAD as A
import Part
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
from feline_underplate_station_templates import build_underplate

OUT=Path(__file__).resolve().parents[1]/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'


class UnderplateTemplates(unittest.TestCase):
    def test_complete_after_arc_grips_and_own_material(self):
        stations=json.loads((OUT/'n01-flat-station-architecture.json').read_text())['stations']
        for ref in ('D_FL','FL_P','P_FRONT','G1'):
            st=next(s for s in stations if s['ref']==ref);large=st['flat_dimensions_pitch_departure_thickness_mm'][2]>10
            dims=[37.,22.,11.] if large else [30.,9.,19.];centre=[46.,-40.,-14. if large else -13.]
            slot=dict(profile='large' if large else 'standard',pose_family='UNDER_PLATFORM_SHARED_REMOVABLE_COMBS',centre_mm=centre,dimensions_mm=dims)
            m=build_underplate(st,slot);parts=m['parts']
            self.assertAlmostEqual(parts['head_budget'].Volume,216)
            self.assertEqual(len(m['wires']),len(st['ports']))
            self.assertLess(m['nylon_loop_upper_bound_mm'],100)
            for w in m['wires']:
                self.assertEqual(w['grip_length_mm'],9);self.assertGreaterEqual(w['R_mm'],next(p['minimum_project_R_mm'] for p in st['ports'] if p['endpoint']==w['endpoint']))
                s=parts['wire:'+w['endpoint']]
                for n in ('case','split_common_comb','band_budget','head_budget'):
                    self.assertLess(s.common(parts[n]).Volume,1e-5,(ref,w['endpoint'],n))
            self.assertLess(parts['head_budget'].common(parts['split_common_comb']).Volume,1e-5)


if __name__=='__main__':unittest.main()
