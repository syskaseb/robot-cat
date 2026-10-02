"""Changed retail bindings cannot alter geometry, circuits or needed quantities."""
import copy, unittest
from nonfastener_offers_r2 import read, update_quantities, PARENT, OUT, BATCH

class RetailBindings(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old = read(PARENT/'one-order-quantities.json')
        cls.review = read(OUT/'offer-review.json')
        cls.new = update_quantities(cls.old, cls.review)
        cls.rows = {r['id']: r for r in cls.new['lines']}

    def test_needed_quantities_unchanged(self):
        self.assertEqual([(r['id'],r['planning_quantity'],r['unit']) for r in self.old['lines']],
                         [(r['id'],r['planning_quantity'],r['unit']) for r in self.new['lines']])

    def test_pack_not_extra_installed_components(self):
        red = self.rows['connector:2147612113']
        self.assertEqual((red['planning_quantity'],red['retail_order_quantity'],red['pack_excess_quantity']), (2,10,8))
        h = self.rows['connector:430200201']
        self.assertEqual((h['planning_quantity'],h['retail_order_quantity'],h['pack_excess_quantity']), (1,3,2))
        self.assertEqual(self.rows['tie:111-01910']['retail_order_quantity'], 100)

    def test_factory_wire_identity_and_pending_not_hidden(self):
        for part in ('2147612113','2147611113','2147632112'):
            self.assertEqual(self.rows['connector:'+part]['product_binding']['manufacturer_part'], part)
        self.assertIn('29week', self.rows['connector:2147632112']['product_binding']['supplier_constraint'])
        self.assertFalse(self.review['K2_complete'])
        self.assertFalse(self.review['W5_complete'])
        self.assertFalse(self.review['physical_pass'])

    def test_wrong_part_rejected(self):
        r = copy.deepcopy(self.review)
        r['resolved'][2]['manufacturer_part'] = '2147612112'
        with self.assertRaises(AssertionError): update_quantities(self.old, r)

    def test_other_rows_byte_equivalent(self):
        changed = {r['quantity_id'] for r in self.review['resolved']+self.review['pending']}
        self.assertEqual([r for r in self.old['lines'] if r['id'] not in changed],
                         [r for r in self.new['lines'] if r['id'] not in changed])

    def test_selected_pack_and_prints_preserved(self):
        if not (BATCH/'selection.json').exists(): self.skipTest('Package not generated yet')
        before, after = read(PARENT/'selection.json'), read(BATCH/'selection.json')
        self.assertEqual(before['prints'], after['prints'])
        catalog = read(BATCH/'nonfastener-catalog.json')
        self.assertEqual(len(catalog['rows']), 83)
        self.assertEqual(catalog['retail_offer_or_availability_pending'], ['connector:2147632112'])
        self.assertEqual(next(r for r in catalog['rows'] if r['quantity_id']=='tie:111-02370')['planning_quantity'], 200)

if __name__ == '__main__': unittest.main()
