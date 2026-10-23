"""Receipt regression: do not promote service hypotheses to material PASS."""
import hashlib
import json
from pathlib import Path
import unittest
from graphlib import TopologicalSorter

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'


class ServiceDependencies(unittest.TestCase):
    def setUp(self):
        self.r=json.loads((OUT/'n01-service-dependency-decision-20261023.json').read_text())

    def test_sources_unchanged(self):
        for p,h in {**self.r['source_sha256'], **self.r.get('sequence_source_sha256', {})}.items():
            self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),h,p)

    def test_sequence_has_no_cycle_or_fake_connector(self):
        s=self.r['shared_sequence']; ops=s['operations']
        order=list(TopologicalSorter({r['id']:set(r['requires']) for r in ops}).static_order())
        self.assertEqual(len(order),len(ops))
        self.assertLess(order.index('release_W009'),order.index('lift_mated10'))
        self.assertLess(order.index('lift_mated10'),order.index('unplug_USB_A'))
        self.assertLess(order.index('unplug_USB_A'),order.index('remove_Pi'))
        self.assertTrue(s['routine_FPI']['leg_fixed_boundaries_are_not_connectors'])
        self.assertTrue(s['routine_FPI']['bank_ends_are_not_assumed_detachable'])
        self.assertEqual(s['current_terminal_pairs']['W009/body'][1]['endpoint'],'D_FR.3')
        self.assertEqual(len(s['current_terminal_pairs']),15)
        self.assertTrue(s['USB_data']['additional_to_123_portions'])
        self.assertFalse(s['assembly_approved'])
        self.assertTrue(s['W009_connected_parking_alternative']['length_is_NOT_available_service_slack'])
        self.assertEqual(s['D_FR_release_constraints']['other_occupied_wires'],['W007','W008','W010','W011'])

    def test_positive_substep_cannot_close_missing_operations(self):
        r=self.r['lifted_USB_A_withdrawal']
        self.assertFalse(r['failures']); self.assertFalse(r['errors'])
        self.assertGreaterEqual(r['lifted_carrier_gap_mm'],.5)
        self.assertGreater(r['BUSsupplier11_gap_mm'],10)
        self.assertTrue(r['partial_scene_only'])
        self.assertFalse(r['complete_service_received'])
        self.assertTrue(any(x['status']=='missing' for x in self.r['shared_sequence']['operations']))
        self.assertFalse(self.r['N01_complete'])

    def test_no_false_material_or_service_approval(self):
        self.assertFalse(self.r['S0']['actual_collision_proved'])
        self.assertTrue(self.r['S0']['removing_key_does_not_remove_fixed_neck'])
        self.assertFalse(self.r['routine_FPI']['sequence_approved'])
        self.assertFalse(self.r['rare_Pi_BUS']['sequence_approved'])
        self.assertFalse(self.r['N01_complete'])
        self.assertFalse(self.r['physical_pass'])
        self.assertTrue(self.r['routine_FPI']['fixed_boundaries_are_NOT_connectors'])

    def test_comb_opening_is_only_a_constructive_substep(self):
        c=self.r['D_FR_comb_opening']
        self.assertEqual(c['motion_mm'],[[0,0,1.8],[0,9,0]])
        for motion in ('lift','slide'):
            self.assertFalse(c[motion]['errors'])
            self.assertFalse(c[motion]['failures'])
        self.assertTrue(c['future_native_split_required'])
        self.assertFalse(c['full_D_FR_service_approved'])
        self.assertFalse(c['N01_complete'])

    def test_full_reserved_USB_stroke_not_replaced_by_shorter_pass(self):
        e=self.r['USB_reserved15_extension']
        self.assertGreater(e['carrier_common_mm3'],4.5)
        self.assertFalse(e['full15_with_fixed_arm_approved'])
        self.assertTrue(e['first12_not_full_withdrawal'])
        step=next(x for x in self.r['shared_sequence']['operations'] if x['id']=='unplug_USB_A')
        self.assertEqual(step['status'],'missing')

    def test_saved_changed_hypotheses(self):
        bus=json.loads((OUT/'n01-BUS-module-service-retreat-sample.json').read_text())
        self.assertGreater(bus['checks']['Ref_Material_BUSsupplier0_0_0|SharedBUS:TailCarrier']['common_mm3'],68)
        lift=json.loads((OUT/'n01-Pi-mated-USB-lift-service-sample.json').read_text())
        self.assertAlmostEqual(lift['recipe']['jacket_length_mm'],452,places=5)
        self.assertGreaterEqual(lift['recipe']['minimum_turn_R_mm'],30)
        self.assertIn('turn|CurrentMiddle:W009',lift['failures'])
        self.assertTrue(lift['continuous_motion_not_checked'])


if __name__=='__main__':unittest.main()
