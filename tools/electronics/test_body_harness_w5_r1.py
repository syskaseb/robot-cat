import copy
import unittest
from body_harness_w5_r1 import build, validate


class HarnessRecipes(unittest.TestCase):
    def setUp(self):
        self.data=build()

    def test_selected_role_map(self):
        self.assertEqual(validate(self.data)["end_recipes"],160)

    def test_twelve_looms_not_thirtysix(self):
        result=validate(self.data)
        self.assertEqual(result["factory_leg_harnesses"],12)
        self.assertEqual(result["moving_conductors"],36)

    def test_old_pi_limit_not_reused(self):
        rows={w["id"]:w for w in self.data["conductors"]}
        self.assertGreater(rows["W079"]["nominal_cut_bound_mm"],250)
        self.assertIsNone(rows["W079"]["limit_mm"])
        self.assertEqual(rows["W079"]["nominal_cut_bound_mm"],rows["W080"]["nominal_cut_bound_mm"])

    def test_leg_second_port_empty(self):
        ends=[e for w in self.data["conductors"] for e in w["ends"] if "second_parallel_socket" in e]
        self.assertEqual(len(ends),36)
        self.assertTrue(all(e["second_parallel_socket"]=="NC" for e in ends))

    def test_balance_id_not_invented(self):
        self.assertIsNone(self.data["balance"]["exact_GTech_cavity_mapping"])
        self.assertFalse(self.data["W5_complete"])

    def test_wrong_leg_power_endpoint_detected(self):
        bad=copy.deepcopy(self.data)
        bad["conductors"][19]["b"]="F_FR1.out"
        with self.assertRaises(ValueError):validate(bad)

    def test_false_fit_claim_detected(self):
        bad=copy.deepcopy(self.data)
        bad["physical_pass"]=True
        with self.assertRaises(ValueError):validate(bad)

    def test_duplicate_label_detected(self):
        bad=copy.deepcopy(self.data)
        bad["conductors"].append(copy.deepcopy(bad["conductors"][0]))
        with self.assertRaises(ValueError):validate(bad)


if __name__=="__main__":
    unittest.main()
