import json
from pathlib import Path
import sys
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
from feline_flat_station_templates import build
from feline_zone_station_templates import zone_build,vertical_build

OUT=Path(__file__).resolve().parents[1]/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'


class ZoneStationTemplates(unittest.TestCase):
    def test_vertical_full_source_rigid_rotation_has_no_reflection(self):
        stations=json.loads((OUT/'n01-flat-station-architecture.json').read_text())['stations']
        for st in stations:
            if st['fixed_identity_pose']:continue
            pitch,depth,height=st['flat_dimensions_pitch_departure_thickness_mm'];centre=np.array([46.,65.6,90.]);dims=np.array([pitch,height,depth])
            slot=dict(profile='large' if height>10 else 'standard',pose_family='VERTICAL_DEPARTURE_TWO_SIDE_TIERS',centre_mm=centre.tolist(),bounds_mm=[(centre-dims/2).tolist(),(centre+dims/2).tolist()])
            for lever in (-1,1):
                m=vertical_build(st,slot,-1,lever,1)
                self.assertAlmostEqual(np.linalg.det(m['source_case_rotation_rows']),1)
                self.assertTrue(m['actual_source_handedness_preserved_by_proper_rotation'])
                for w in m['wires']:
                    self.assertTrue(np.allclose(w['departure_axis'],[0,0,-1]));self.assertEqual(w['first_mm'],9)
                    self.assertEqual(w['endpoint'],next(p['endpoint'] for p in st['ports'] if p['wire']==w['wire']))
                    self.assertAlmostEqual(np.linalg.norm(np.array(w['before_arc_grip_line_mm'])[1]-w['before_arc_grip_line_mm'][0]),9)

    def test_complete_rigid_kit_translation_preserves_sources_and_radii(self):
        stations=json.loads((OUT/'n01-flat-station-architecture.json').read_text())['stations']
        count=0
        for st in stations:
            if st['fixed_identity_pose']:continue
            pitch,depth,height=st['flat_dimensions_pitch_departure_thickness_mm']
            centre=np.array([-72.,49.3396+1.25+pitch/2,45.])
            slot=dict(profile='large' if height>10 else 'standard',centre_mm=centre.tolist(),bounds_mm=[(centre-[depth/2,pitch/2,height/2]).tolist(),(centre+[depth/2,pitch/2,height/2]).tolist()])
            for departure in (-1,1):
                m=zone_build(st,slot,departure);old=build(dict(st,row_families=['inner','outer']),'outer',1,departure,-72.,None,'OUTWARD_CONCENTRIC','SIDE')
                delta=centre-np.array(old['centre_mm'])
                self.assertTrue(np.allclose(m['points'],old['points']+delta))
                self.assertEqual(len(m['wires']),len(st['ports']))
                for wire,parent in zip(m['wires'],old['wires']):
                    self.assertEqual(wire['endpoint'],parent['endpoint']);self.assertEqual(wire['R_mm'],parent['R_mm'])
                    self.assertEqual(wire['first_mm'],9);self.assertEqual(wire['radius'],parent['radius'])
                    self.assertTrue(np.allclose(wire['points'],parent['points']+delta))
                self.assertTrue(m['legacy_translated_return_NOT_an_approved_carrier'])
            count+=len(st['ports'])
        self.assertEqual(count,sum(len(s['ports']) for s in stations if not s['fixed_identity_pose']))

    def test_fixed_identity_is_not_translated(self):
        st=next(s for s in json.loads((OUT/'n01-flat-station-architecture.json').read_text())['stations'] if s['fixed_identity_pose'])
        slot=dict(profile='fixed_P_SYS',centre_mm=st['source_world_centre_mm'])
        m=zone_build(st,slot,1)
        self.assertEqual(m['centre_mm'],st['source_world_centre_mm']);self.assertEqual(m['departure_X'],-1)
        self.assertEqual([w['wire'] for w in m['reused_jacket_lands']],['W043'])


if __name__=='__main__':unittest.main()
