"""Evidence regression tests, not certification of a physical MG92B batch."""
import json
import unittest
import pilot
from release_check import sha256


class MG92BReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder = pilot.ROOT / "hardware/reference/mg92b-horn-2026-09-23"
        cls.measure = json.loads((cls.folder / "measurements.json").read_text())
        cls.clearance = json.loads((cls.folder / "conditional-clearance.json").read_text())

    def test_provenance(self):
        self.assertEqual(self.measure["reference_sha256"], sha256(self.folder / "MG92BCommunityReference.FCStd"))
        self.assertEqual(self.measure["tool_sha256"], sha256(pilot.ROOT / "tools/cad/probe_mg92b_reference.py"))
        self.assertEqual(self.clearance["reference_sha256"], self.measure["reference_sha256"])
        self.assertEqual(self.clearance["diagnostic_sha256"], sha256(self.folder / "MG92BClearanceReference.FCStd"))
        self.assertEqual(self.clearance["tool_sha256"], sha256(pilot.ROOT / "tools/cad/probe_mg92b_clearance.py"))

    def test_small_reference_not_original_python_document(self):
        self.assertFalse(self.measure["upstream_document_opened"])
        self.assertFalse(self.measure["supplier_certified"])
        self.assertEqual(len(self.measure["objects"]), 2)
        arm = next(o for o in self.measure["objects"] if o["source_object"] == "Fusion105")
        self.assertEqual(len(arm["primitive_inputs"]), 4)
        for got, wanted in zip(arm["size_xyz_mm"], [28, 5.45, 16.7]):
            self.assertAlmostEqual(got, wanted, places=6)
        self.assertTrue(all(o["strict_bop_passed"] for o in self.measure["objects"]))

    def test_sensitivity_samples_and_no_fit_approval(self):
        self.assertEqual(len(self.clearance["rows"]), 72)
        self.assertFalse(self.clearance["proves_actual_horn_fit"])
        for report in (self.measure, self.clearance):
            self.assertFalse(report["installed_in_robot"])
            self.assertFalse(report["print_ready"])
        self.assertEqual([r["samples_with_intersection"] for r in self.clearance["summary"]], [3, 24, 24])
        for dz in [-1.8, 0, 1.8]:
            self.assertEqual([r["clocking_deg"] for r in self.clearance["rows"] if r["height_offset_mm"] == dz], list(range(0, 360, 15)))

    def test_robot_files_unchanged(self):
        self.assertEqual(len(self.clearance["unchanged_robot_files"]), 9)
        for path, digest in self.clearance["unchanged_robot_files"].items():
            self.assertEqual(sha256(pilot.ROOT / path), digest, path)


if __name__ == "__main__":
    unittest.main()
