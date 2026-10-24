"""Receipt integrity: failed strict geometry cannot become a service PASS."""
import hashlib,json,unittest,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'

class ReceiptTests(unittest.TestCase):
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
