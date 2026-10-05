from pathlib import Path
import json,unittest
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'hardware/electronics/full-cat'
def read(rel):return json.loads((BASE/rel).read_text(encoding='utf-8'))

class CoverServiceConnection(unittest.TestCase):
    def test_deck_cut_with_disconnected_supports_is_rejected(self):
        d=read('w5-deck-service-relief-r1/allocation.json')
        self.assertEqual(d['virtual_Cut_solids'],3)
        self.assertFalse(d['protected_interfaces_clear'])
        self.assertTrue(d['native_builder_must_not_run'])
        self.assertFalse(d['selected'])

    def test_upper_saddle_retains_real_connections_and_unchanged_interfaces(self):
        d=read('w5-cover-upper-front-passages-r1/checks.json')
        self.assertEqual(d['hits'],[]);self.assertEqual(d['errors'],[])
        self.assertEqual(d['patch_solids'],1)
        self.assertGreaterEqual(d['minimum_inner_ligament_mm'],3)
        self.assertTrue(all(x>1 for x in d['actual_patch_contacts_mm3'].values()))
        self.assertTrue(d['no_Deck_cut']);self.assertTrue(d['no_wire_paths_changed'])
        self.assertEqual(d['new_print_jobs'],0);self.assertEqual(d['new_screws'],0)
        self.assertEqual(set(d['remove_original_bridges']),{'SouthRimWest','SouthRimSteppedEnd'})
        self.assertGreater(d['continuous_new_bridge_Deck_lift_clearance_bound_mm'],12)

    def test_native_is_a_received_prototype_not_a_service_pass(self):
        d=read('w5-cover-upper-front-native-r1/checks.json')
        self.assertEqual(d['solids'],1);self.assertEqual(d['BOP_errors'],0)
        self.assertTrue(d['closed_STLs']);self.assertTrue(d['relocated_reopen'])
        self.assertEqual(d['parameter_probe_mm'],[.4,.5,.4])
        self.assertLess(d['probe_mm3'],d['nominal_mm3'])
        self.assertLessEqual(max(d['dimensions_mm'])+6,256)
        self.assertTrue(d['shared_module_service_pending'])
        self.assertFalse(d['W5_complete']);self.assertFalse(d['physical_pass'])

if __name__=='__main__':unittest.main()
