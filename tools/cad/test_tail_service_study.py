"""Check saved study provenance without importing FreeCAD or approving a print."""
import json
import unittest

import pilot
from release_check import sha256, verify


class TailServiceStudyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder = pilot.CAD / "studies/tail-coupling"
        cls.report = json.loads((cls.folder / "service-audit.json").read_text())

    def test_evidence_matches_cad_script_and_unchanged_robot(self):
        self.assertEqual(self.report["study_sha256"], sha256(self.folder / "TailCouplingService.FCStd"))
        self.assertEqual(self.report["tool_sha256"], sha256(pilot.ROOT / "tools/cad/tail_service_study.py"))
        self.assertEqual(len(self.report["unchanged_robot_files"]), 9)
        for name, digest in self.report["unchanged_robot_files"].items():
            self.assertEqual(digest, sha256(pilot.ROOT / name), name)
        self.assertFalse(self.report["cad_saved_by_audit"])

    def test_nut_only_path_has_controls_and_preserves_seat(self):
        path = self.report["nut_path"]
        self.assertEqual(path["required_removed_components"], ["SpindleBolt34"])
        self.assertEqual([s["nut_shift_x_mm"] for s in path["samples"]], [9.5 - i * .25 for i in range(39)])
        self.assertTrue(all(not s["collisions"] for s in path["samples"]))
        self.assertGreater(max(s["old_root_overlap_mm3"] for s in path["samples"]), 1)
        self.assertGreater(max(s["retained_axial_bolt_overlap_mm3"] for s in path["samples"]), 1)
        seat = self.report["nut_seat_contact_mm2"]
        self.assertGreater(seat["baseline"], 5)
        self.assertAlmostEqual(seat["baseline"], seat["study"], places=6)
        self.assertEqual(seat["top_z_mm"], 98.4)

    def test_standalone_relocation_and_geometric_scope(self):
        self.assertEqual(self.report["solid_count"], 1)
        self.assertTrue(self.report["strict_bop_passed"])
        self.assertEqual(len(self.report["fully_constrained_sketches"]), 3)
        self.assertEqual(self.report["relocation"]["documents_loaded"], 1)
        self.assertEqual(self.report["relocation"]["external_links"], 0)
        self.assertTrue(self.report["relocation"]["fresh_process"])
        self.assertEqual(self.report["expected_cut_comparison"]["difference_volumes_mm3"], [0, 0])
        self.assertFalse(self.report["print_release"])

    def test_concept_manifest_checks_integrity_but_refuses_print(self):
        manifest = json.loads((pilot.ROOT / "hardware/releases/tail-service-study.json").read_text())
        result = verify(pilot.ROOT, manifest)
        self.assertTrue(result["integrity_ok"], result)
        self.assertEqual(result["readiness"], "concept")
        self.assertFalse(verify(pilot.ROOT, manifest, True)["integrity_ok"])
        self.assertEqual(manifest["gates"]["assembly"]["status"], "open")
        self.assertEqual(manifest["gates"]["loads"]["status"], "open")


if __name__ == "__main__":
    unittest.main()
