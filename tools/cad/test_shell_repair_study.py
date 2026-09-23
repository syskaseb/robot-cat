"""Regression checks for rejected repair evidence; no CAD libraries required."""
import json
import math
import unittest

import pilot
from release_check import sha256, verify


class ShellRepairStudyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder = pilot.CAD / "studies/shell-repair"
        cls.baseline = json.loads((cls.folder / "baseline.json").read_text())
        cls.trial = json.loads((cls.folder / "continuity-trial.json").read_text())

    def test_source_and_assembly_checkpoint_unchanged(self):
        self.assertEqual(self.baseline["source_sha256"], sha256(pilot.CAD / "modules/shell/Shell.FCStd"))
        manifest = json.loads((pilot.ROOT / "hardware/releases/modular-pilot.json").read_text())
        self.assertTrue(verify(pilot.ROOT, manifest)["integrity_ok"])
        self.assertFalse(self.baseline["cad_saved"])

    def test_failed_baseline_cannot_be_mistaken_for_strict_success(self):
        self.assertEqual({r["name"] for r in self.baseline["objects"]}, {"Shell35Source", "Shell35"})
        for row in self.baseline["objects"]:
            self.assertTrue(row["valid"])
            self.assertEqual(row["solids"], 1)
            errors = "\n".join(row["strict_bop_errors"])
            self.assertEqual(errors.count("GeomAbs_C0"), 22)
            self.assertEqual(errors.count("InvalidCurveOnSurface"), 4)

    def test_trial_provenance_and_no_approval(self):
        self.assertFalse(self.trial["accepted"])
        self.assertEqual(self.trial["cadquery_ocp"], "7.8.1.1")
        for row in self.trial["rows"]:
            old = next(b for b in self.baseline["objects"] if b["name"] == row["source"])
            self.assertEqual(row["input_sha256"], old["brep_sha256"])

    def test_both_candidate_audits_are_complete_and_rejected(self):
        for mode in ("fixed", "split"):
            audit = json.loads((self.folder / ("audit-" + mode + ".json")).read_text())
            self.assertTrue(audit["complete"])
            self.assertFalse(audit["installed"])
            self.assertFalse(audit["print_ready"])
            self.assertEqual(audit["source_sha256"], self.baseline["source_sha256"])
            self.assertEqual({r["source"] for r in audit["rows"]}, {"Shell35Source", "Shell35"})
            for row in audit["rows"]:
                trial = next(t for t in self.trial["rows"] if t["source"] == row["source"])
                self.assertEqual(row["candidate_sha256"], trial[mode + "_sha256"])
                self.assertFalse(row["topology_passed"])
                self.assertTrue(row["strict_bop_errors"])
                for field in ("volume_delta_mm3", "area_delta_mm2", "max_bbox_delta_mm"):
                    self.assertTrue(math.isfinite(row[field]))

    def test_fault_localization_matches_baseline_not_a_new_approval(self):
        report = json.loads((self.folder / "fault-locations.json").read_text())
        self.assertFalse(report["installed"])
        self.assertFalse(report["print_ready"])
        for row in report["rows"]:
            old = next(b for b in self.baseline["objects"] if b["name"] == row["source"])
            self.assertEqual(row["brep_sha256"], old["brep_sha256"])
            self.assertEqual(len(row["faults"]), 24)
            curve_faults = [f for f in row["faults"] if f["status"].endswith("InvalidCurveOnSurface")]
            self.assertEqual(len(curve_faults), 2)
            expected_face = 244 if row["source"] == "Shell35" else 242
            for fault in curve_faults:
                self.assertEqual([s["face_index"] for s in fault["subshapes"] if s["face_index"]], [expected_face])

    def test_manifest_preserves_failed_geometry_gate(self):
        manifest = json.loads((self.folder / "study-manifest.json").read_text())
        self.assertTrue(verify(pilot.ROOT, manifest)["integrity_ok"])
        self.assertFalse(verify(pilot.ROOT, manifest, True)["integrity_ok"])
        self.assertEqual(manifest["gates"]["geometry"]["status"], "fail")
        self.assertEqual(manifest["readiness"], "concept")


if __name__ == "__main__":
    unittest.main()
