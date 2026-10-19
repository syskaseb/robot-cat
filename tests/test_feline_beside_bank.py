import json
from pathlib import Path
import subprocess
import sys
import types
import unittest
import FreeCAD as A
import Part

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/cad'))
from feline_beside_bank_plan import slots,unit
from feline_underplate_station_templates import build_underplate
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'


class BesideBank(unittest.TestCase):
    def test_complete_sources_grips_and_own_fit(self):
        stations=json.loads((OUT/'n01-flat-station-architecture.json').read_text())['stations']
        for ref in ('D_FL','FL_P','P_FRONT','G1'):
            st=next(s for s in stations if s['ref']==ref)
            profile='large' if st['flat_dimensions_pitch_departure_thickness_mm'][2]>10 else 'standard'
            for side in (-1,1):
                slot=next(s for s in slots() if s['profile']==profile and s['centre_mm'][1]*side>0)
                m=unit(st,slot)
                self.assertEqual(len(m['wires']),len(st['ports']))
                self.assertAlmostEqual(m['parts']['head_budget'].Volume,216)
                self.assertLess(m['nylon_loop_upper_bound_mm'],100)
                for w in m['wires']:
                    self.assertEqual(w['grip_length_mm'],9)
                    self.assertGreaterEqual(w['R_mm'],next(p['minimum_project_R_mm'] for p in st['ports'] if p['endpoint']==w['endpoint']))
                    for n in ('case','split_common_comb','band_budget','head_budget'):
                        self.assertLess(m['parts']['wire:'+w['endpoint']].common(m['parts'][n]).Volume,1e-5,(ref,side,n))

    def test_default_underplate_receipt_geometry_unchanged(self):
        source=subprocess.run(['git','show','8733e08f:tools/cad/feline_underplate_station_templates.py'],cwd=ROOT,capture_output=True,check=True).stdout
        legacy=types.ModuleType('legacy_underplate');exec(compile(source,'legacy_underplate','exec'),legacy.__dict__)
        stations=json.loads((OUT/'n01-flat-station-architecture.json').read_text())['stations']
        for ref in ('D_FL','P_FRONT'):
            st=next(s for s in stations if s['ref']==ref)
            large=st['flat_dimensions_pitch_departure_thickness_mm'][2]>10
            slot=dict(profile='large' if large else 'standard',pose_family='UNDER_PLATFORM_SHARED_REMOVABLE_COMBS',centre_mm=[46.,-40.,-14. if large else -13.],dimensions_mm=[37.,22.,11.] if large else [30.,9.,19.])
            before=legacy.build_underplate(st,slot)['parts'];after=build_underplate(st,slot)['parts']
            self.assertEqual(set(before),set(after))
            for name,a in before.items():
                b=after[name]
                self.assertLess(a.cut(b).Volume+b.cut(a).Volume,1e-5,(ref,name))


if __name__=='__main__':unittest.main()
