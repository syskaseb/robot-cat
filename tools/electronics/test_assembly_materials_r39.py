"""Material stock reconciliation, inherited print set and rejected-route boundary."""
import copy
import unittest
from package_assembly_materials_r39 import ROOT, OUT, PARENT, read, build_payload

class Materials(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = read(OUT/"materials.json")
        cls.s = read(PARENT/"selection.json")
        cls.q = read(PARENT/"one-order-quantities.json")

    def test_five_categories_six_unique_skus(self):
        self.assertEqual(len(self.m["replaces_generic_ids"]), 5)
        self.assertEqual(len(self.m["lines"]), 6)
        self.assertEqual(len({r["manufacturer_sku"] for r in self.m["lines"]}), 6)
        for r in self.m["lines"]:
            self.assertTrue(r["manufacturer_url"].startswith("https://"))
            self.assertTrue(r["supplier_url"].startswith("https://"))

    def test_no_duplicate_allowances_or_parent_mutation(self):
        before = copy.deepcopy(self.q)
        s, q = build_payload(self.m, self.s, self.q)
        self.assertEqual(before, self.q)
        self.assertEqual(len(q["lines"]), 114)
        self.assertNotIn("consumable:p0:5", {r["id"] for r in q["lines"]})
        old = set(self.m["replaces_generic_ids"])
        retained = [r for r in before["lines"] if r["id"] not in old]
        self.assertEqual(q["lines"][:len(retained)], retained)
        self.assertEqual(s["prints"], self.s["prints"])

    def test_shared_small_ties_not_counted_again(self):
        _, q = build_payload(self.m, self.s, self.q)
        ties = [r for r in q["lines"] if r["id"] == "tie:111-02370"]
        self.assertEqual(len(ties), 1)
        self.assertEqual(ties[0]["installed"], 90)
        self.assertEqual(ties[0]["planning_quantity"], 100)
        large = next(r for r in self.m["lines"] if r["id"] == "consumable:p0:1")
        self.assertEqual(large["existing_working_allowance"]+large["unallocated_stock"], 100)
        self.assertEqual(large["specification"]["supplier_length_mm"], 190)

    def test_paired_hook_loop_and_small_braid_pack(self):
        rows = {r["id"]:r for r in self.m["lines"]}
        for key in ("consumable:p0:2", "consumable:p0:3"):
            r = rows[key]
            self.assertEqual(r["stock_per_pack"]*r["purchase_pack_count"], r["existing_working_allowance"]+r["unallocated_stock"])
        self.assertEqual(rows["consumable:p0:2"]["planning_quantity"], 1)
        self.assertEqual(rows["consumable:p0:3"]["stock_per_pack"], 5)

    def test_epoxy_not_structural_or_fake_petg_rating(self):
        r = next(r for r in self.m["lines"] if r["id"] == "consumable:p0:4")
        self.assertIsNone(r["specification"]["printed_PETG_bond_strength"])
        self.assertEqual(r["specification"]["tds_working_life_max_minutes_at_22C"], 4)
        self.assertFalse(self.m["assembly_recipe"]["physical_tests_done"])
        self.assertIn("stalową", self.m["assembly_recipe"]["load_path"])
        self.assertTrue((ROOT/r["tds_local"]).is_file())

    def test_no_false_completion(self):
        self.assertEqual(self.m["phase1_percent"], 70)
        for key in ("K3_complete", "W5_complete", "physical_pass"):
            self.assertFalse(self.m[key])
        self.assertTrue(self.m["no_auto_order"])

    def test_two_failed_routes_not_selected(self):
        for version, count in ((1,3), (2,7)):
            c = read(ROOT/f"hardware/electronics/full-cat/body-ground-front-return-r{version}/checks.json")
            self.assertEqual(c["status"], "REJECTED")
            self.assertEqual(len(c["hits"]), count)
            self.assertTrue(all(r["hit_mm3"] > 0 for r in c["hits"]))

    def test_utf8_polish_and_small_abrasive_pack(self):
        self.assertIn("Źródła", self.m["lines"][0]["note"])
        self.assertNotIn("\ufffd", (OUT/"materials.json").read_text(encoding="utf-8"))
        r = next(r for r in self.m["lines"] if r["id"].endswith(":abrasive"))
        self.assertEqual(r["stock_per_pack"], 5)
        self.assertEqual(r["ean"], "3165140614696")

if __name__ == "__main__":
    unittest.main()
