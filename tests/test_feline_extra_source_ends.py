"""Source ownership/count regression; does not qualify mechanical fit."""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'


class ExtraSourceEnds(unittest.TestCase):
    def setUp(self):self.p=json.loads((OUT/'n01-extra-circuit-source-ends.json').read_text())

    def test_internal_external_partition_is_not_extra_wires(self):
        p=self.p
        self.assertEqual(p['schematic_extra_sections'],45)
        self.assertEqual(len(p['retained_U1_internal_sections'])+p['external_schematic_sections'],45)
        self.assertEqual(p['external_schematic_sections'],34)
        self.assertEqual(len(p['current_external_ends']),22)
        self.assertEqual(len(p['remaining_external_sections_without_current_full_end_pair']),23)
        self.assertFalse(p['N01_complete']);self.assertFalse(p['physical_pass'])

    def test_source_guides_are_not_silently_declared_current_pins(self):
        self.assertEqual(len(self.p['source_guides']),74)
        self.assertTrue(all(r['guide_end_is_not_automatically_pin_or_mouth'] for r in self.p['source_guides']))
        self.assertTrue(all(not r['current_port_transfer_qualified'] for r in self.p['source_guides']))

    def test_all_five_Pi_housing_exits_expose_current_roof_conflict(self):
        rows=[r for r in self.p['current_external_ends'] if r['current_group']=='Pi4']
        self.assertEqual(len(rows),5)
        self.assertTrue(all(abs(r['point_mm'][2]-115.7)<1e-5 for r in rows))
        self.assertTrue(all(r['above_torso_roof_112'] for r in rows))


if __name__=='__main__':unittest.main()
