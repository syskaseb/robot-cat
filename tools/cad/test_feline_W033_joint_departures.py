"""Regression of the coherent departure packet; no whole-plan score implied."""
import json,unittest
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_fore_power_pair import pair_spacing
import feline_tangent_routes as ft


class JointDepartures(unittest.TestCase):
    def test_receipt_and_retained_interfaces(self):
        r=json.loads((OUT/'n01-W033-joint-departures-received.json').read_text())
        for p,h in r['source_sha256'].items():self.assertEqual(sha(ROOT/p),h,p)
        self.assertEqual(sha(ROOT/r['bundle']),r['bundle_sha256'])
        self.assertFalse(r['selected']);self.assertFalse(r['N01_complete']);self.assertFalse(r['physical_pass'])
        self.assertTrue(all(c['ok'] for c in r['checks'].values()))
        self.assertEqual(r['grip_first9_probes'],210)
        self.assertTrue(r['grip_first9_probes_inside'])
        self.assertAlmostEqual(ft.length(r['whole_recipe']),r['whole_length_mm'])
        self.assertGreaterEqual(ft.min_radius(r['whole_recipe']),12.4)
        for wire,parts in r['row_recipes'].items():
            raw=json.loads((OUT/f'n01-FR-outboard-row-{wire}-static.json').read_text())
            self.assertFalse(raw['errors']);self.assertEqual(parts,raw['parts'][:len(parts)])
            self.assertEqual(parts[0]['length'],9)
            self.assertEqual(parts[0]['start'][2],74);self.assertEqual(parts[0]['end'][2],83)
            # A shortened prefix is a material subset. Reuse its earlier distances.
            for name,c in raw['checks'].items():
                minimum=.15 if name=='VerticalGuide:FR' else .2 if name.startswith('VerticalCuff:') else 1.25
                self.assertGreaterEqual(c['gap_mm']+1e-6,minimum,(wire,name,c))
        self.assertTrue(r['W031_W035_continuations_OPEN'])
        self.assertTrue(r['changed_source_boundary_binding_W031_W033_W035_OPEN'])


if __name__=='__main__':unittest.main()
