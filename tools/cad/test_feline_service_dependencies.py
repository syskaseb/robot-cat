"""Receipt regression: do not promote service hypotheses to material PASS."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'


class ServiceDependencies(unittest.TestCase):
    def setUp(self):
        self.r=json.loads((OUT/'n01-service-dependency-decision-20261023.json').read_text())

    def test_sources_unchanged(self):
        for p,h in self.r['source_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),h,p)

    def test_no_false_material_or_service_approval(self):
        self.assertFalse(self.r['S0']['actual_collision_proved'])
        self.assertTrue(self.r['S0']['removing_key_does_not_remove_fixed_neck'])
        self.assertFalse(self.r['routine_FPI']['sequence_approved'])
        self.assertFalse(self.r['rare_Pi_BUS']['sequence_approved'])
        self.assertFalse(self.r['N01_complete'])
        self.assertFalse(self.r['physical_pass'])
        self.assertTrue(self.r['routine_FPI']['fixed_boundaries_are_NOT_connectors'])

    def test_saved_changed_hypotheses(self):
        bus=json.loads((OUT/'n01-BUS-module-service-retreat-sample.json').read_text())
        self.assertGreater(bus['checks']['Ref_Material_BUSsupplier0_0_0|SharedBUS:TailCarrier']['common_mm3'],68)
        lift=json.loads((OUT/'n01-Pi-mated-USB-lift-service-sample.json').read_text())
        self.assertAlmostEqual(lift['recipe']['jacket_length_mm'],452,places=5)
        self.assertGreaterEqual(lift['recipe']['minimum_turn_R_mm'],30)
        self.assertIn('turn|CurrentMiddle:W009',lift['failures'])
        self.assertTrue(lift['continuous_motion_not_checked'])


if __name__=='__main__':unittest.main()
