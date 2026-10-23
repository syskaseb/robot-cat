"""Negative evidence stays negative; no production/N01 credit from screens."""
import json
import unittest
from plan_feline_layout import OUT


class ServiceRejections(unittest.TestCase):
    def test_hatch_retains_connected_plate_but_hits_belly_supports(self):
        p=json.loads((OUT/'n01-Monitor-service-hatch-proposal.json').read_text())
        self.assertTrue(p['geometry']['fixed_valid'])
        self.assertEqual(p['geometry']['fixed_solids'],1)
        self.assertEqual(p['geometry']['hatch_solids'],1)
        self.assertEqual(p['geometry']['closed_overlap_mm3'],0)
        self.assertIn('hatch_closed|BellyFoot1',p['failures'])
        self.assertIn('hatch_closed|BellyFoot2',p['failures'])
        self.assertFalse(p['errors'])
        self.assertFalse(p['selected'])
        self.assertFalse(p['N01_complete'])

    def test_axial_withdrawal_and_slide_are_not_service_acceptance(self):
        p=json.loads((OUT/'n01-FPI-axial-withdrawal-necessary.json').read_text())
        self.assertFalse(p['checks']['Station:P_SYS:case']['ok'])
        self.assertIn('W043',p['excluded_with_unresolved_wire_release'])
        q=json.loads((OUT/'n01-FPI-slide-down-service-necessary.json').read_text())
        self.assertFalse(q['checks']['case_axial_sweep|P_SYS_entry:W068']['ok'])
        self.assertFalse(q['checks']['cap_down_after_slide|MonitorTray:rooted_pocket']['ok'])
        self.assertFalse(q['N01_complete'])
        self.assertFalse(q['physical_pass'])


if __name__=='__main__':unittest.main()
