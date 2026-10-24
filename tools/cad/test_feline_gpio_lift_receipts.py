"""Receipt integrity: failed strict geometry cannot become a service PASS."""
import ast,hashlib,json,unittest,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'

class ReceiptTests(unittest.TestCase):
    def test_split_carrier_remains_proposal_with_explicit_prerequisites(self):
        r=json.loads((OUT/'n01-stationary-GPIO-carrier-split-20261024.json').read_text())
        self.assertFalse(r['N01_complete']);self.assertFalse(r['selected_native_changed'])
        self.assertFalse(r['Pi_pose_changed']);self.assertFalse(r['physical_pass'])
        self.assertEqual(len(r['geometry']),5)
        e=r['evidence'];self.assertTrue(e['own_motion']['accepted'])
        self.assertTrue(e['fixed_external_refined']['necessary_prefix_clear'])
        self.assertEqual(e['joint_boss_space']['failures'],[])
        self.assertEqual(e['housing_tie_space']['failures'],[])
        self.assertTrue(e['prerequisites_not_yet_qualified'])
        archive=ROOT/r['bundle']
        self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(),r['bundle_sha256'])
        with zipfile.ZipFile(archive) as z:
            for row in r['geometry']:
                self.assertTrue(row['strict_reopen'])
                self.assertEqual(hashlib.sha256(z.read(row['entry'])).hexdigest(),row['sha256'])
        for p,digest in r['source_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),digest)

    def test_mated_gpio_is_only_necessary_prefix_proof(self):
        r=json.loads((OUT/'n01-mated-GPIO-prefix-motion-20261024.json').read_text())
        self.assertTrue(r['necessary_prefix_clear'])
        self.assertFalse(r['full_five_leads_qualified'])
        self.assertFalse(r['whole_service_qualified'])
        self.assertFalse(r['N01_complete'])
        self.assertEqual(len(r['refined_pairs']),15)
        for row in r['refined_pairs'].values():
            self.assertTrue(row['strict_valid'])
            self.assertTrue(row['continuous_clear'])
            self.assertGreater(row['certified_lower_bound_mm'],row['minimum_required_mm'])
            intervals=sorted(row['certified_intervals'])
            self.assertEqual(intervals[0][0],0)
            self.assertEqual(intervals[-1][1],10)
            self.assertTrue(all(a[1]==b[0] for a,b in zip(intervals,intervals[1:])))
        for p,digest in r['source_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),digest)

    def test_continuous_translation_bound(self):
        source=ast.parse((ROOT/'tools/cad/check_feline_current_gpio_release.py').read_text())
        function=next(n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='certify')
        env={};exec(compile(ast.Module(body=[function],type_ignores=[]),'certify','exec'),env)
        clear=env['certify'](lambda z:.15)
        self.assertTrue(clear['continuous_clear'])
        rows=sorted(clear['certified_intervals'])
        self.assertEqual(rows[0][0],0);self.assertEqual(rows[-1][1],40)
        self.assertTrue(all(a[1]==b[0] for a,b in zip(rows,rows[1:])))
        self.assertTrue(all(r[2]>0 for r in rows))
        hit=env['certify'](lambda z:abs(z-20)-.1)
        self.assertFalse(hit['continuous_clear'])

    def test_current_gpio_receipt_not_old_invalid_carrier(self):
        r=json.loads((OUT/'n01-current-carrier-GPIO-release-20261024.json').read_text())
        self.assertEqual(r['current_carrier_source'],'removable_USB_planning_witness.fixed_beam')
        self.assertEqual(len(r['checks']),12);self.assertTrue(r['continuous_changed_pairs_clear'])
        self.assertFalse(r['N01_complete']);self.assertFalse(r['physical_pass'])
        self.assertFalse(r['counterhold_access_received'])
        self.assertEqual(len(r['retained_mount_continuous_checks']),4)
        self.assertTrue(all(v['continuous_clear'] for v in r['retained_mount_continuous_checks'].values()))
        for row in r['checks'].values():
            self.assertTrue(row['continuous_clear']);self.assertEqual(row['unresolved_intervals'],[])
        for p,digest in r['source_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),digest)

    def test_component_reconstruction_is_preserved_but_not_complete(self):
        r=json.loads((OUT/'n01-Pi-component-reconstruction-20261024.json').read_text())
        self.assertEqual(r['component_count'],33);self.assertEqual(r['strict_errors'],{})
        self.assertFalse(r['N01_complete']);self.assertFalse(r['equivalent_union_proven'])
        self.assertFalse(r['load_path_proven']);self.assertTrue(r['omitted'])
        archive=ROOT/r['bundle']
        self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(),r['bundle_sha256'])
        with zipfile.ZipFile(archive) as z:
            for row in r['geometry']:
                self.assertTrue(row['strict_reopen'])
                self.assertEqual(hashlib.sha256(z.read(row['entry'])).hexdigest(),row['sha256'])

    def test_both_probes_explicitly_ineligible(self):
        for f in ('n01-stationary-GPIO-Pi-lift-20261024.json','n01-board-only-GPIO-lift-20261024.json'):
            r=json.loads((OUT/f).read_text())
            self.assertEqual(r['status'],'DIAGNOSTIC_ONLY_STRICT_CARRIER_BREP_HOLD')
            self.assertFalse(r['N01_complete']);self.assertFalse(r['physical_pass'])
            self.assertFalse(r['whole_service_approved'])
            self.assertTrue(r['numerical_gaps_and_overlaps_are_not_qualified_geometry_evidence'])
            self.assertEqual(len(r['strict_source_validation']),3)
            self.assertTrue(all(not x['strict_valid'] for x in r['strict_source_validation'].values()))

    def test_original_inputs_preserved(self):
        r=json.loads((OUT/'n01-stationary-GPIO-Pi-lift-20261024.json').read_text())
        for name,digest in r['source_sha256'].items():
            self.assertEqual(hashlib.sha256((OUT/name).read_bytes()).hexdigest(),digest)
        self.assertEqual(len(r['stationary']),10)
        self.assertEqual(len(r['checks'])+len(r['mating_or_generic_reservations']),len(r['moving'])*10)
        self.assertEqual(r['errors'],{})

    def test_board_probe_preserves_gpio_receipt_link(self):
        r=json.loads((OUT/'n01-board-only-GPIO-lift-20261024.json').read_text())
        name='n01-stationary-GPIO-Pi-lift-20261024.json'
        self.assertEqual(r['source_sha256'][name],hashlib.sha256((OUT/name).read_bytes()).hexdigest())
        self.assertFalse(r['continuous_path_qualified'])

if __name__=='__main__':unittest.main()
