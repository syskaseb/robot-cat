import json,unittest
from compose_body36_fit_contribution import compose,fit_blank,OUT


class BodyFitContributionTests(unittest.TestCase):
    def test_current36_share_twelve_source_cables_and_four_real_donors(self):
        macro=json.loads((OUT/'body36-shared-macro-layout.json').read_text())
        base=json.loads((OUT/'body36-recovery-layout.json').read_text())
        contract=json.loads((OUT/'body36-current-contract.json').read_text())
        extensions=json.loads((OUT/'leg-extension-budget-plan.json').read_text())
        routes={n:base['routes'][n] for n in macro['retained_route_ids']};routes.update(macro['qualified_changed_routes'])
        rows={r['wire']:r for r in contract['rows']};rows.update({r['wire']:r for r in macro['changed_rows']})
        parts,units=compose(list(rows.values()),routes,extensions)
        self.assertEqual(len(parts),48);self.assertEqual(len(units),16)
        self.assertEqual(sum(n.startswith('DONOR/') for n in units),4)
        self.assertTrue(all(len(r['conductors'])==3 for r in units.values()))
        self.assertTrue(all(r['actual_cut_mm'] is None for r in parts))

    def test_blank_does_not_silently_exceed_real900_factory_length(self):
        self.assertEqual(fit_blank(850),870)
        with self.assertRaises(AssertionError):fit_blank(890)


if __name__=='__main__':unittest.main()
