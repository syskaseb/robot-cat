"""Affected prototype interface evidence, not a physical qualification."""
import json
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"hardware/electronics/full-cat/body-data-bridges-r7"
def read(n):return json.loads((OUT/("interface.json" if n=="plan.json" else n)).read_text(encoding="utf-8"))

class DataBridgeTests(unittest.TestCase):
    def test_three_labels_and_exact_end_roles(self):
        self.assertEqual(read("plan.json")["ends"],{"W007":["D_FL.5","D_FR.1"],"W011":["D_FR.5","D_RR.1"],"W012":["D_RR.5","D_RL.1"]})
    def test_cage_permutation_does_not_duplicate_cages(self):
        order=read("plan.json")["datum_overrides"]["D_RR_physical_cages_left_to_right"]
        self.assertEqual(sorted(order),[f"D_RR.{i}" for i in range(1,6)])
        self.assertEqual(order[2],"D_RR.1")
        other=read("plan.json")["datum_overrides"]["D_RL_physical_cages_left_to_right"]
        self.assertEqual(sorted(other),[f"D_RL.{i}" for i in range(1,6)])
        self.assertEqual(other[0],"D_RL.1")
    def test_six_insulation_restraints_not_contact_restraints(self):
        p=read("plan.json");self.assertEqual(len(p["anchors"]),6)
        self.assertEqual(len({(n,e) for n,e,_,_ in p["anchors"]}),6)
        self.assertEqual(p["restraints"]["quantity"],6)
    def test_all_slots_remove_full_material(self):
        c=read("checks.json");self.assertEqual(len(c["slots"]),12)
        self.assertAlmostEqual(c["removed_mm3"],307.2,places=4)
        self.assertLess(c["added_mm3"],1e-5)
        self.assertTrue(c["signed_rectangle_directions"] and c["all_actual_slot_bounds_checked"])
        self.assertEqual(c["short_source_saddle_length_mm"],2.5)
        self.assertEqual(c["source_tie_y_mm"],-29)
    def test_slot_pairs_have_at_least_two_mm_nominal_land(self):
        s=read("checks.json")["slots"]
        for i,(x,y,w,h) in enumerate(s):
            for xx,yy,ww,hh in s[i+1:]:
                gx=max(0,abs(x-xx)-(w+ww)/2);gy=max(0,abs(y-yy)-(h+hh)/2)
                self.assertGreaterEqual((gx*gx+gy*gy)**.5,2-1e-6)
    def test_lengths_have_strip_and_rework_reserve(self):
        rows=read("checks.json")["lengths"]
        self.assertEqual(sum(r["proposed_blank_mm"] for r in rows.values()),600)
        self.assertTrue(all(r["blank_margin_mm"]>=20 and r["actual_strip_mm"] is None for r in rows.values()))
    def test_nominal_manufacturer_strip_not_cut_allowance(self):
        p=read("plan.json")["connector_datums"]
        self.assertEqual(p["nominal_strip_length_mm"],11)
        self.assertEqual(p["strip_spec_source"]["author"],"WAGO")
    def test_native_and_mesh_have_checked_source(self):
        c=read("checks.json")
        self.assertTrue(c["relocated_reopen_recompute"] and c["closed"])
        self.assertEqual(c["components"],1);self.assertEqual(c["strict_BOP_errors"],0)
        self.assertLessEqual(max(c["dimensions_mm"])+10,256)
        self.assertTrue(c["supported_native_reopen_recompute"])
        self.assertEqual(c["fully_constrained_added_saddle_sketches"],6)
        self.assertEqual(c["sourced_T18I_thickness_mm"],1.2)
    def test_routes_restraints_and_body_no_positive_collision(self):
        self.assertEqual(read("checks.json")["hits"],[])
        b=read("current-body-checks.json");self.assertEqual(b["hits"],[])
        self.assertTrue(all(min(r["radii_mm"])>=5.2-1e-7 for r in b["arc_checks"].values()))
    def test_no_phase_or_physical_overclaim(self):
        for n in ("plan.json","checks.json","current-body-checks.json"):
            d=read(n);self.assertIs(d["physical_pass"],False);self.assertIs(d["W5_complete"],False)

if __name__=="__main__":unittest.main()
