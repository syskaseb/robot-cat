"""Whole extra interface source-frame regressions, no geometry acceptance."""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'


class ExtraInterfaceContract(unittest.TestCase):
    def setUp(self):
        self.p=json.loads((OUT/'n01-all-extra-interface-contract.json').read_text())
        self.ends={e['endpoint']:e for r in self.p['sections'] for e in r['ends']}

    def test_every_extra_external_section_has_two_owned_ends(self):
        self.assertEqual(len(self.p['sections']),34)
        self.assertTrue(all(len(r['ends'])==2 and all(e['group'] for e in r['ends']) for r in self.p['sections']))
        self.assertEqual(self.p['fixed_pairs'],26)
        self.assertEqual(self.p['unplaced_module_endpoints'],8)
        self.assertFalse(self.p['N01_complete'])

    def test_FHAC_wire_exit_not_case_centre(self):
        self.assertEqual(len(self.p['source_local_fuse_ports']),6)
        for v in self.p['source_local_fuse_ports'].values():
            self.assertAlmostEqual(v[2],-1)
            self.assertAlmostEqual(abs(v[0]),25.5)

    def test_AUX_jacket_and_copper_overlap_preserved(self):
        for ref in ('AUX.VIN','AUX.VOUT','AUX.GND'):
            e=self.ends[ref]
            self.assertEqual(e['bare_to_jacket_source_overlap_mm'],3)
            self.assertAlmostEqual(e['source_point_mm'][2],91.32)
            self.assertAlmostEqual(e['bare_tip_source_point_mm'][2],94.32)

    def test_Yaw_neck_registration_once_not_B1_source(self):
        receipt=json.loads((OUT/'n01-selected-local-head-tail-sources.json').read_text())
        for ref in ('C_HY.V+','C_HY.GND','C_HY.PWM'):
            e=self.ends[ref];self.assertAlmostEqual(e['point_mm'][0],-152)
            native=next(r for r in receipt['boundaries'] if r['endpoint']==ref)
            for a,b in zip(e['point_mm'],native['current_point_mm']):self.assertAlmostEqual(a,b,places=9)
            self.assertLess(native['native_gap_mm'],1e-5)
            self.assertEqual(native['correction_delta_mm'],[42,0,-25])
            self.assertTrue(e['accounting_boundary_not_connector_pin'])
        self.assertFalse(self.ends['C_HY.PWM']['receiver_mould_face_qualification_pending'])

    def test_Tail_current_accounting_not_old_display_curve_or_fake_plug(self):
        for ref in ('C_TY.V+','C_TY.GND','C_TY.PWM'):
            e=self.ends[ref];self.assertEqual(e['point_mm'][0],88)
            self.assertTrue(e['accounting_boundary_not_connector_pin'])
            self.assertEqual(e['source_case_bounds_mm'],[125,-54,107,155,-42,117])


if __name__=='__main__':unittest.main()
