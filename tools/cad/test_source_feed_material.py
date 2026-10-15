import unittest
from reconcile_source_feed_material import contribution


class SourceMaterialTests(unittest.TestCase):
    def rows(self):
        return [dict(wire=n,sku='HELU23802',guide_mm=100,rail_strip_mm=14,ring_barrel_allowance_mm=14.452)
                for n in ('W064','W065','W067','W068')]

    def test_exactly_four_blanks_no_extra_legacy_wire(self):
        q=contribution(self.rows())
        self.assertEqual(q['nominal_fit_blank_sum_mm'],600)
        self.assertEqual(q['extra_920mm_cable_quantity'],0)
        self.assertTrue(all(r['actual_cut_mm'] is None for r in q['wires']))
        self.assertFalse(q['selected']);self.assertFalse(q['W5_complete'])

    def test_missing_or_duplicate_feed_is_not_complete(self):
        rows=self.rows();rows[-1]['wire']='W064'
        with self.assertRaises(AssertionError):contribution(rows)
        with self.assertRaises(AssertionError):contribution(self.rows()[:3])


if __name__=='__main__':unittest.main()
