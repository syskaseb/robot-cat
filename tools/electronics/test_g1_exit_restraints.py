"""Affected interface and selection checks; no FreeCAD or hardware startup."""
import hashlib,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/electronics/full-cat/g1-exit-restraints-finish-r1'
def read(p):return json.loads(p.read_text(encoding='utf-8'))

class G1ExitRestraints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.i=read(OUT/'interface.json');cls.c=read(OUT/'checks.json')
    def test_only_two_existing_electrical_routes(self):
        self.assertEqual(self.i['affected_routes'],['W061/G1.5','W060/G1.2'])
        self.assertTrue(self.i['unchanged_electrical_endpoints'])
        self.assertEqual(self.i['new_routes_selected'],[])
    def test_individual_ties_no_common_mixed_diameter_cap(self):
        self.assertEqual(self.i['ties']['replaces'],2);self.assertEqual(self.i['ties']['selected'],2)
        self.assertEqual(self.i['ties']['net_added'],0);self.assertEqual(self.i['ties']['working_total'],93)
        self.assertEqual(self.i['ties']['SKU'],'111-02370')
        self.assertEqual(self.i['strap_side_offsets_mm'],[-3,3])
    def test_cage_order_reserved_not_full_routes(self):
        self.assertEqual(self.i['G1_labels_plus_X'],['.1','.5','.3','.4','.2'])
        self.assertEqual(self.i['G1_cage_X_mm'],[51,58.5,66,73.5,81])
        self.assertTrue(self.c['neighbouring_stubs_only'])
    def test_four_full_passages_and_finite_troughs(self):
        self.assertEqual(len(self.c['full_through_slots']),4)
        self.assertTrue(self.c['finite_open_troughs'])
        self.assertGreaterEqual(min(self.c['minimum_floor_mm'].values()),2.4)
    def test_real_native_parameter_probe_and_relocated_reopen(self):
        a,b,c=self.c['parameter_probe_volumes_mm3'];self.assertNotAlmostEqual(a,b,places=5);self.assertAlmostEqual(a,c,places=5)
        self.assertTrue(self.c['relocated_reopen']);self.assertTrue(self.c['native_saved_before_recompute'])
        self.assertEqual(self.c['fully_constrained_added_sketches'],3);self.assertEqual(self.c['strict_BOP_errors'],0)
    def test_affected_interfaces_and_closed_export(self):
        self.assertEqual(self.c['status'],'G1_INDEPENDENT_RESTRAINTS_COMPLETE');self.assertFalse(self.c['hits'])
        self.assertTrue(self.c['mesh_export_complete']);self.assertTrue(self.c['closed']);self.assertEqual(self.c['components'],1)
        x,y,z=self.c['dimensions_mm'];self.assertLessEqual(x+10,256);self.assertLessEqual(y+10,256);self.assertLessEqual(z,256)
    def test_no_global_or_physical_pass(self):
        self.assertFalse(self.c['physical_pass']);self.assertFalse(self.c['W5_complete']);self.assertFalse(self.c['whole_assembly_collision_free'])
        self.assertFalse(self.i['physical_pass']);self.assertFalse(self.i['W5_complete'])
    def test_current_source_pins_unchanged(self):
        for path,digest in self.c['source_sha256'].items():self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),digest,path)
    def test_rejected_front_ground_corridors_not_selected(self):
        for rev in (3,4,5):
            trial=read(ROOT/f'hardware/electronics/full-cat/body-ground-front-shared-r{rev}/checks.json')
            self.assertEqual(trial['status'],'REJECTED');self.assertFalse(trial['selected']);self.assertTrue(trial['hits'])
    def test_package_changes_only_deck_and_no_order_quantities(self):
        import package_g1_exit_restraints_r41 as P
        a=P.read(P.PARENT/'selection.json');q=P.read(P.PARENT/'one-order-quantities.json')
        b,r=P.payload(a,q,self.c)
        self.assertEqual({v['identity'] for v,w in zip(a['prints'],b['prints']) if v!=w},{'electronics:DeckP10-cover-mount'})
        self.assertEqual(len(b['prints']),71);self.assertEqual(b['installed_petg_parts'],110);self.assertEqual(b['fit_samples'],4)
        self.assertEqual(r['lines'],q['lines']);self.assertEqual(len(r['lines']),114)

if __name__=='__main__':unittest.main()
