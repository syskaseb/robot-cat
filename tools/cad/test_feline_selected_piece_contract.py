"""Guard selected physical roles before any new geometry/cut-list work."""
import gzip,json,unittest
import FreeCAD
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_selected_piece_contract import load
from receive_feline_existing_lower_caps import current


class SelectedPieces(unittest.TestCase):
    def test_all_selected_roles_without_historical_cuts(self):
        r,_=load()
        self.assertEqual(len(r['portions']),123)
        self.assertEqual(len(r['bound_portions']),123)
        self.assertEqual(r['unbound_factory_or_composite_roles'],[])
        self.assertFalse(r['selected_SKUs_changed'])
        self.assertFalse(r['old_stock_cut_lengths_imported'])
        self.assertEqual(r['selected_material_git_blob'],'5f84d783936589ad4f32117193e4cf037b9b9cba')
        self.assertTrue(r['grouped_source_donor_factory_roles'])

    def test_physical_families_not_capacity_envelopes(self):
        r,_=load()
        for p in r['portions'].values():
            sku=p['selected_sku']
            if sku=='HELU23802' or sku.startswith('MTA0100335'):
                self.assertEqual(p['project_radius_mm'],2.1)
                self.assertGreaterEqual(p['minimum_project_R_mm'],25.2)
            if sku in ('HELU23301','HELU23302','HELU23308'):
                self.assertEqual(p['project_radius_mm'],1.05)
                self.assertGreaterEqual(p['minimum_project_R_mm'],12.6)
            if sku in ('HELU23501','HELU23502'):
                self.assertEqual(p['project_radius_mm'],1.25)
                self.assertGreaterEqual(p['minimum_project_R_mm'],15.)
            if sku.startswith('Molex'):
                self.assertEqual(p['project_radius_mm'],.925)
                self.assertIn('225mm',p['selected_physical_unit'])

    def test_existing_lower_cap_not_fabricated_nine(self):
        _,rows,_=current()
        for w in ('W041','W042','W044','W052'):
            r=next(e for e in rows if e['id']==w+'/custom/start')
            self.assertAlmostEqual(r['source_prefix_length_mm'],9.25,5)
            self.assertNotEqual(r['point_mm'],r['routing_exit_mm'])
            self.assertFalse(r['full_middle_route_accepted'])

    def test_main_tool_sequence_not_whole_harness_extraction(self):
        f=OUT/'n01-MAIN-fastener-sequence-received.json';r=json.loads(f.read_text())
        for p,h in r['source_sha256'].items():self.assertEqual(sha(ROOT/p),h)
        self.assertFalse(r['failures']);self.assertEqual(r['checks'],19)
        self.assertIn('MainSupported:band',r['temporarily_removed_actual_parts'])
        self.assertIn('MainSupported:head',r['temporarily_removed_actual_parts'])
        self.assertTrue(any('F_PI/splice/harness release remains' in s for s in r['sequence']))
        pf=ROOT/r['pair_rows'];self.assertEqual(sha(pf),r['pair_rows_sha256'])
        self.assertTrue(all(v['ok'] for v in json.loads(gzip.decompress(pf.read_bytes())).values()))

    def test_coupled_factory_math_not_a_world_acceptance(self):
        r=json.loads((OUT/'n01-remaining-factory-input-plan.json').read_text())
        self.assertEqual(len(r['pairs']),6);self.assertTrue(all(p['ok'] for p in r['pairs']))
        self.assertFalse(r['N01_complete']);self.assertFalse(r['native_changed'])
        for route in r['routes'].values():
            self.assertEqual(route['minimum_R_mm'],25.2)
            self.assertEqual(route['full_grip_arclength_intervals_mm'][0],[0,9])
            self.assertTrue(route['old_factory_seat_fit_NOT_inherited'])


if __name__=='__main__':unittest.main()
