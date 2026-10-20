import json,unittest
import FreeCAD as A
import Part
from plan_feline_layout import OUT
from receive_feline_rrp_shared_height import load
from feline_source_saddles import segment


class SharedForeCarrierTests(unittest.TestCase):
    def test_whole_source_pack_has_full_grips_and_one_structural_owner(self):
        p=json.loads((OUT/'n01-shared-fore-current-sources.json').read_text())
        self.assertFalse(p['N01_complete']);self.assertFalse(p['failures'])
        shapes=load(p);self.assertEqual(len(shapes),28)
        self.assertTrue(all(s.isValid() and s.Solids for s in shapes.values()))
        recipe=p['print_recipe'];self.assertTrue(recipe['whole_valid']);self.assertEqual(recipe['whole_solids'],1)
        self.assertLess(max(recipe['whole_envelope_45Z_mm']),250)
        self.assertTrue(recipe['shared_existing_members_referenced_NOT_duplicated'])
        self.assertTrue(recipe['open_trough_not_nine_rigid_bores'])
        self.assertAlmostEqual(shapes['BundleTie:FLHead'].Volume,5*4.3*5.3)
        nylon=shapes['BundleTie:FL'].fuse(shapes['BundleTie:FLHead'])
        self.assertTrue(nylon.isValid());self.assertEqual(len(nylon.Solids),1)
        old=json.loads((OUT/'n01-FL9-inboard-whole-plan.json').read_text())
        fl=[r for r in p['updates'].values() if r['group']=='NineWireCuffFL'];self.assertEqual(len(fl),9)
        for r in fl:
            self.assertEqual(r['point_mm'][0],-87);self.assertTrue(r['moving_seam_unchanged'])
            self.assertTrue(r['full_moving_flex_NOT_qualified'])
            self.assertTrue(r['independent_individual_termination_relief_NOT_inferred'])
            self.assertEqual(r['full_grip_arclength_mm'],[0,9])
            edge=segment(old['routes'][r['id']]);param=edge.FirstParameter+(edge.LastParameter-edge.FirstParameter)*9/edge.Length
            self.assertLess((edge.valueAt(param)-A.Vector(*r['jacket_grip9_mm'][1])).Length,1e-6)
            self.assertLess((edge.valueAt(edge.LastParameter)-A.Vector(*r['routing_exit_mm'])).Length,1e-6)
        self.assertEqual(len(p['updates']),10)

    def test_monitor_is_rooted_provisional_not_invented_PCB_pads(self):
        p=json.loads((OUT/'n01-Monitor-front-tray.json').read_text())
        self.assertFalse(p['failures']);self.assertFalse(p['N01_complete'])
        self.assertTrue(p['root_joint']['whole_1Solid'])
        self.assertGreater(p['root_joint']['overlap_mm3'],1)
        self.assertTrue(p['root_joint']['unchanged_existing_four_battery_bolt_interfaces'])
        self.assertTrue(p['actual_monitor_mounting_pads_NOT_inferred'])
        self.assertTrue(p['balance_factory_length_pinout_and_surface_fit_delivery_gates'])
        self.assertTrue(p['no_new_balance_extension_or_SKU_authorized'])


if __name__=='__main__':unittest.main()
