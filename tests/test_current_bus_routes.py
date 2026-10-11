import unittest,json,math,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/body-harness-checkpoint'

class BUSRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=json.loads((OUT/'BUS-routes-plan.json').read_text())
        cls.binding=json.loads((OUT/'BUS-port-binding.json').read_text())
    def test_two_cores_one_factory_cable_not_two_purchases(self):
        self.assertEqual(set(self.p['routes']),{'W002','W003'})
        self.assertEqual(self.p['factory_cables_installed'],1)
        self.assertTrue(self.binding['V_contact_and_wire_removed_before_installation'])
        self.assertEqual(self.binding['placement_bound_to_current_native_supplier_solids'],[0,1,2])
    def test_continuity_exact_length_and_nine_mm_grip(self):
        for n,r in self.p['routes'].items():
            q=r['parts']
            self.assertTrue(all(math.dist(a['end'],b['start'])<1e-6 for a,b in zip(q,q[1:])))
            self.assertAlmostEqual(sum(t['length_mm'] for t in q),r['guide_mm'],places=6)
            self.assertEqual(q[-1]['length_mm'],9)
            self.assertLess(r['minimum_factory_blank_project_mm'],850)
            self.assertGreater(r['minimum_factory_blank_project_mm'],300)
            self.assertEqual(self.p['source_prefixes'][n][2]['length_mm'],9)
    def test_manufacturer_binding_is_not_a_plug_fit_or_W5_claim(self):
        self.assertFalse(self.binding['received_revision_keyed_plug_fit_continuity_Cu_OD_and_actual_exit_verified'])
        for p in (self.p,self.binding):
            self.assertFalse(p['selected']);self.assertFalse(p['W5_complete']);self.assertFalse(p['physical_pass'])
        self.assertTrue(self.p['reservations_are_conservative_planning_not_material_collision_evidence'])
    def test_all_current_pins_match(self):
        for p in (self.p,self.binding):
            for name,digest in p['source_sha256'].items():
                self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),digest,name)
    def test_native_is_a_restored_replacement_not_whole_W5(self):
        p=json.loads((OUT/'BUS-native-checks.json').read_text())
        self.assertTrue(p['parameter_1p6_1p7_1p6_restore'])
        self.assertTrue(p['fresh_relocated_reopen'])
        self.assertEqual(p['volume_added_outside_qualified_material_mm3'],0)
        self.assertLess(p['extra_slot_corner_removal_mm3'],1)
        self.assertLess(max(p['export']['size_mm'])+10,256)
        self.assertIn('not another physical plate',p['export']['replaces'])
        self.assertFalse(p['selected']);self.assertFalse(p['W5_complete']);self.assertFalse(p['print_ready'])
        for name,digest in p['source_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),digest,name)
        self.assertEqual(hashlib.sha256((ROOT/p['model']).read_bytes()).hexdigest(),p['model_sha256'])
        self.assertEqual(hashlib.sha256((ROOT/p['export']['path']).read_bytes()).hexdigest(),p['export']['sha256'])

if __name__=='__main__':unittest.main()
