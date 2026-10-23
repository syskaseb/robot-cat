"""Regression for local topology only; never awards whole service or N01."""
import json
import unittest
import FreeCAD
from repair_feline_usb_grip_topology import build, strict
from receive_feline_pi_split_service_space import independent
from receive_feline_rrp_shared_height import load
from check_main_p0_placement import ROOT, sha
from plan_feline_layout import OUT


class LocalTopology(unittest.TestCase):
    def test_strict_rebuild_and_scope(self):
        receipt = json.loads((OUT/'n01-USB-release-grip-topology-repaired.json').read_text())
        saved = load(receipt)
        base = load(json.loads((OUT/'n01-Pi-open-cradle-joint.json').read_text()))
        fresh, recipe, fixed, tool = build(base['mobile'])
        for name, shape in {**fresh, 'mobile_repaired': fixed, 'GPIO_recut_tool': tool}.items():
            strict(shape)
            strict(saved[name])
            self.assertLess(independent(shape).cut(independent(saved[name])).Volume, 1e-5, name)
            self.assertLess(independent(saved[name]).cut(independent(shape)).Volume, 1e-5, name)
        for path, digest in receipt['source_sha256'].items():
            self.assertEqual(sha(ROOT/path), digest, path)
        self.assertFalse(recipe['cable_changed'])
        self.assertTrue(recipe['band_external_clearance_recheck_required'])
        self.assertFalse(any(receipt[k] for k in ('selected', 'N01_complete', 'physical_pass', 'complete_service_received')))
        self.assertLess(fresh['band'].common(fresh['carrier']).Volume, 1e-7)
        self.assertLess(fresh['head'].common(fresh['carrier']).Volume, 1e-7)


if __name__ == '__main__':
    unittest.main()
