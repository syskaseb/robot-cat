import copy
import hashlib
from pathlib import Path
import tempfile
import unittest

from release_check import REQUIRED_GATES, verify


class ReleaseCheckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "part.txt").write_bytes(b"proof")
        self.manifest = {"schema_version": 1, "readiness": "prototype",
                         "files": [{"path": "part.txt", "sha256": hashlib.sha256(b"proof").hexdigest()}],
                         "gates": {g: {"status": "open", "reason": "Pending test"} for g in REQUIRED_GATES}}

    def test_valid_prototype_not_print_ready(self):
        self.assertTrue(verify(self.root, self.manifest)["integrity_ok"])
        self.assertFalse(verify(self.root, self.manifest, True)["integrity_ok"])

    def test_changed_file_fails(self):
        (self.root / "part.txt").write_bytes(b"changed")
        self.assertFalse(verify(self.root, self.manifest)["integrity_ok"])

    def test_empty_manifest_fails(self):
        self.assertFalse(verify(self.root, {})["integrity_ok"])

    def test_print_ready_requires_every_gate(self):
        self.manifest["readiness"] = "print-ready"
        self.assertFalse(verify(self.root, self.manifest)["integrity_ok"])
        for gate in self.manifest["gates"].values():
            gate.update(status="pass", evidence=["part.txt"])
        self.assertTrue(verify(self.root, self.manifest, True)["integrity_ok"])
        del self.manifest["gates"]["fit"]
        self.assertFalse(verify(self.root, self.manifest)["integrity_ok"])

    def test_unhashed_evidence_fails(self):
        self.manifest["gates"]["geometry"].update(status="pass", evidence=["other.json"])
        self.assertFalse(verify(self.root, self.manifest)["integrity_ok"])

    def test_paths_and_missing_files_fail(self):
        for value in ["../part.txt", "/part.txt", "C:/part.txt", "x\\part.txt", "missing.txt"]:
            with self.subTest(value=value):
                data = copy.deepcopy(self.manifest)
                data["files"][0]["path"] = value
                self.assertFalse(verify(self.root, data)["integrity_ok"])

    def test_duplicates_and_invalid_gate_fail(self):
        self.manifest["files"] *= 2
        self.assertFalse(verify(self.root, self.manifest)["integrity_ok"])
        self.manifest["files"] = self.manifest["files"][:1]
        self.manifest["gates"]["geometry"] = "pass"
        self.assertFalse(verify(self.root, self.manifest)["integrity_ok"])


if __name__ == "__main__":
    unittest.main()
