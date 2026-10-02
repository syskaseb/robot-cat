import copy,unittest
from nonfastener_offers_r3 import PARENT,OUT,BATCH,read,update_quantities,validate_catalog

class FinishedCart(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.offer=read(OUT/'offer-review.json');cls.old=read(PARENT/'one-order-quantities.json')
        cls.new=update_quantities(cls.old,cls.offer)

    def test_only_one_purchase_replaced(self):
        self.assertEqual(len(self.new['lines']),114)
        self.assertFalse(any(r['id']=='connector:2147632112' for r in self.new['lines']))
        r=next(r for r in self.new['lines'] if r['id']=='connector:2147632113')
        self.assertEqual((r['planning_quantity'],r['retail_order_quantity'],r['pack_excess_quantity']),(2,10,8))

    def test_other_purchase_roles_unchanged(self):
        self.assertEqual([r for r in self.old['lines'] if r['id']!='connector:2147632112'],
            [r for r in self.new['lines'] if r['id']!='connector:2147632113'])

    def test_contact_and_route_not_inferred(self):
        d=self.offer['manufacturer_drawing'];t=self.offer['trim_recipe']
        self.assertEqual(d['same_terminal'],'430310001')
        self.assertEqual(t['nominal_finished_L_mm'],150)
        self.assertEqual(t['offcut_interval_at_nominal_finished_L_mm'],[70,80])
        self.assertIsNone(t['actual_cut_mm'])
        self.assertFalse(self.offer['physical_pass'])

    def test_wrong_contact_or_shorter_lead_rejected(self):
        o=copy.deepcopy(self.offer);o['manufacturer_drawing']['same_terminal']='430300001'
        with self.assertRaises(AssertionError):update_quantities(self.old,o)
        o=copy.deepcopy(self.offer);o['manufacturer_drawing']['purchased_length_L_mm']=[70,80]
        with self.assertRaises(AssertionError):update_quantities(self.old,o)

    def test_current_cart_complete_not_whole_robot(self):
        if not (BATCH/'selection.json').exists():self.skipTest('Before packaging')
        s=read(BATCH/'selection.json');validate_catalog(read(BATCH/'nonfastener-catalog.json'))
        self.assertEqual(s['prints'],read(PARENT/'selection.json')['prints'])
        self.assertTrue(s['K2_complete']);self.assertFalse(s['W5_complete'])
        self.assertEqual(read(BATCH/'validation.json')['open_phase1'],['E3','W5','K3','A2','A3'])

    def test_missing_offer_invalidates_cart(self):
        if not (BATCH/'nonfastener-catalog.json').exists():self.skipTest('Before packaging')
        c=read(BATCH/'nonfastener-catalog.json');c['rows'][0]['supplier_sku']=None
        with self.assertRaises(AssertionError):validate_catalog(c)

if __name__=='__main__':unittest.main()
