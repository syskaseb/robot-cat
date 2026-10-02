"""Selected W061 recipe and actual native checks; no hardware access."""
import hashlib
import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"hardware/electronics/full-cat/body-ground-bridge-finish-r5"

def read(p):return json.loads(p.read_text(encoding="utf-8"))

class GroundBridge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.i=read(OUT/"interface.json");cls.c=read(OUT/"checks.json")

    def test_one_physical_bridge_not_reversed_graph_duplicate(self):
        self.assertEqual(set(self.i["specs"]),{"W061"})
        self.assertEqual(self.i["specs"]["W061"][0],"G1.5")
        self.assertEqual(self.i["specs"]["W061"][3],"G2.1")

    def test_sourced_wire_and_radius(self):
        self.assertEqual(self.i["wire_SKU"],"TKD2500125")
        self.assertEqual(self.i["wire_OD_mm"],4.2)
        self.assertEqual(self.i["sourced_static_radius_mm"],21)

    def test_three_supported_insulation_restraints(self):
        self.assertEqual(len(self.i["anchors"]),3)
        self.assertEqual(self.i["restraints"]["quantity"],3)
        self.assertEqual(self.i["restraints"]["thickness_mm"],1.2)
        self.assertTrue(self.i["restraints_complete"])
        self.assertAlmostEqual(self.i["groove_radius_mm"]-4.2/2,.2)

    def test_passages_and_native_history(self):
        self.assertEqual(len(self.c["slots"]),6)
        self.assertAlmostEqual(self.c["removed_slot_mm3"],102.4,places=4)
        self.assertAlmostEqual(self.c["middle_removed_slot_mm3"],79.36,places=4)
        self.assertEqual(self.c["passage_planes_mm"],[105,132])
        self.assertGreaterEqual(self.c["middle_groove_floor_mm"],2)
        self.assertGreaterEqual(self.c["middle_slot_sidewall_mm"],2)
        self.assertTrue(self.c["native_saved_before_recompute"])
        self.assertTrue(self.c["relocated_reopen_recompute"])
        self.assertEqual(self.c["fully_constrained_added_sketches"],6)

    def test_real_parameter_change_and_restore(self):
        a,b,c=self.c["parameter_probe_volumes_mm3"]
        self.assertNotAlmostEqual(a,b,places=5)
        self.assertAlmostEqual(a,c,places=5)

    def test_bat_cage_and_existing_ground_feed_are_preserved(self):
        self.assertEqual(self.i["cage_labels"]["G1"][0],".1")
        self.assertEqual(self.i["cage_labels"]["G2"][-2:], [".4",".5"])
        self.assertEqual(self.i["cage_x_mm"]["G2"][-1],123)
        self.assertEqual(self.i["cage_x_mm"]["G2"][2],111)
        self.assertEqual(self.i["prototype_415_pitch_mm"],6)
        for labels in self.i["cage_labels"].values():
            self.assertEqual(set(labels),{f".{i}" for i in range(1,6)})

    def test_cut_blank_is_not_strip_length(self):
        row=self.i["lengths"]["W061"]
        self.assertEqual(row["provisional_blank_mm"],240)
        self.assertGreaterEqual(240-row["external_length_mm"],58)
        self.assertEqual(row["nominal_strip_by_end_mm"],{"G1.5":[12,14],"G2.1":11})
        self.assertNotIn("nominal_strip_each_mm",row)

    def test_current_checks_and_export_not_physical_pass(self):
        self.assertEqual(self.c["status"],"SUPPORTED_GROUND_BRIDGE_COMPLETE")
        self.assertFalse(self.c["hits"])
        self.assertEqual(self.c["new_STL"],1)
        self.assertTrue(self.c["closed"])
        self.assertEqual(self.c["components"],1)
        self.assertLessEqual(max(self.c["dimensions_mm"])+10,256)
        self.assertFalse(self.i["physical_pass"])
        self.assertFalse(self.i["W5_complete"])
        self.assertEqual(self.i["fuse_height_reserve"]["conservative_top_mm"],129.8)
        self.assertGreaterEqual(136.5-2.1-129.8,4)

    def test_pinned_current_sources_unchanged(self):
        for path,digest in self.c["source_sha256"].items():
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),digest,path)

if __name__=="__main__":unittest.main()
