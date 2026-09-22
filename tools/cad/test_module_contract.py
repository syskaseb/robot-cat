"""ROS/FreeCAD-free checks of migration ownership and BOM coverage."""
import json
import unittest

import pilot
import tail_module
from package_pilot import bom_instances


class ModuleContractTests(unittest.TestCase):
    def test_owner_objects_are_unique(self):
        for module, names in pilot.MODULES.items():
            self.assertEqual(len(names), len(set(names)), module)
        for _, (owner, name, _) in pilot.mappings().items():
            self.assertIn(name, pilot.MODULES[owner])

    def test_scope_is_exactly_18_plus_27(self):
        mapping = pilot.mappings()
        self.assertEqual(len(mapping), 45)
        self.assertEqual(len(tail_module.mappings()), 27)
        plan = json.loads((pilot.BASE / "assembly-plan.json").read_text())
        self.assertTrue(set(mapping) <= {r["name"] for r in plan["components"]})
        moving = {r["name"] for r in plan["components"] if r["name"] in mapping and r["stage"] == "Motion_Tail_Yaw"}
        self.assertEqual(moving, {"TailRoot29", "InnerSpacer34", "SpindleCap34", "SpindleBolt34", "SpindleNut34"})

    def test_aux_and_tail_bom_cover_links_without_overlap(self):
        aux = bom_instances(json.loads((pilot.ROOT / "hardware/bom/aux-pilot.json").read_text()))
        tail = bom_instances(json.loads((pilot.ROOT / "hardware/bom/tail-support.json").read_text()))
        self.assertFalse(aux & tail)
        self.assertEqual(aux | tail, set(pilot.mappings()))

    def test_bom_rejects_duplicate_identity(self):
        bom = {"parts": [{"id": "P", "quantity": 1, "assembly_names": ["a"]}]}
        bom["parts"].append({"id": "P", "quantity": 1, "assembly_names": ["b"]})
        with self.assertRaises(AssertionError):
            bom_instances(bom)

    def test_bom_rejects_wrong_quantity_or_duplicate_instance(self):
        bom = {"parts": [{"id": "P", "quantity": 2, "assembly_names": ["a"]}]}
        with self.assertRaises(AssertionError):
            bom_instances(bom)
        bom["parts"][0]["quantity"] = 1
        bom["mating_parts_not_counted_again"] = ["a"]
        with self.assertRaises(AssertionError):
            bom_instances(bom)

    def test_bridge_remains_aux_driven_not_replaced_by_old_v34(self):
        self.assertEqual(pilot.mappings()["TailBridge29"][:2], ("tail/TailMount", "TailBridge35"))
        self.assertNotIn("TailBridge29", tail_module.mappings())
        self.assertNotIn("MG92BOutput29", pilot.mappings())  # horn is still unresolved


if __name__ == "__main__":
    unittest.main()
