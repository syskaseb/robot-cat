import copy, unittest
from fixed_fastener_skus_r1 import ROOT,OUT,PARENT,read,compile_cart

class FixedFastenerTests(unittest.TestCase):
    def setUp(self):
        self.q=read(PARENT/'one-order-quantities.json')
        self.a=read(OUT/'allocation.json')

    def test_all_fixed_roles_are_mapped_once(self):
        cart=compile_cart(self.q,self.a)
        self.assertEqual((len(cart),sum(len(r['roles']) for r in cart)),(29,33))

    def test_added_frame_screws_not_pi_screws(self):
        cart=compile_cart(self.q,self.a)
        frame=next(r for r in cart if 'added:FASTENER-M2P5X12-P0' in r['quantity_ids'])
        pi=next(r for r in cart if 'fastener:Pi:M2.5x16' in r['quantity_ids'])
        self.assertEqual((frame['planning_quantity'],pi['planning_quantity']),(6,6))
        self.assertNotEqual(frame['supplier_sku'],pi['supplier_sku'])

    def test_same_size_roles_are_summed_not_replaced(self):
        cart=compile_cart(self.q,self.a)
        row=next(r for r in cart if r['supplier_sku']=='0912A2-M020X012VISK')
        self.assertEqual([r['planning_quantity'] for r in row['roles']],[18,6])
        self.assertEqual(row['planning_quantity'],24)
        self.assertEqual(next(r for r in cart if r['supplier_sku']=='SKL000623')['planning_quantity'],22)

    def test_retail_pack_excess_not_installed_quantity(self):
        cart=compile_cart(self.q,self.a)
        row=next(r for r in cart if r['supplier_sku']=='1755994')
        self.assertEqual((row['planning_quantity'],row['retail_order_quantity'],row['pack_excess_quantity']),(15,100,85))
        self.assertEqual(next(r for r in cart if r['supplier_sku']=='VV0763')['retail_order_quantity'],10)

    def test_missing_role_is_rejected(self):
        a=copy.deepcopy(self.a);a['rows'].pop()
        with self.assertRaises(AssertionError):compile_cart(self.q,a)

    def test_duplicate_role_is_rejected(self):
        a=copy.deepcopy(self.a);a['rows'][1]['quantity_ids'].append(a['rows'][0]['quantity_ids'][0])
        with self.assertRaises(AssertionError):compile_cart(self.q,a)

    def test_missing_frame_spares_rejected(self):
        a=copy.deepcopy(self.a);a['added_quantity']['planning_quantity']=4
        with self.assertRaises(AssertionError):compile_cart(self.q,a)

    def test_short_thread_is_rejected(self):
        a=copy.deepcopy(self.a);a['nominal_thread_intervals'][1]['b']=2
        with self.assertRaises(AssertionError):compile_cart(self.q,a)

    def test_wrong_washer_merge_is_rejected(self):
        a=copy.deepcopy(self.a)
        row=next(r for r in a['rows'] if r['supplier_sku']=='00125202')
        row['dimensions_mm']['OD']=4.5
        with self.assertRaises(AssertionError):compile_cart(self.q,a)

    def test_unknown_retail_multiple_is_rejected(self):
        a=copy.deepcopy(self.a);a['rows'][0]['retail_multiple_pieces']=None
        with self.assertRaises(AssertionError):compile_cart(self.q,a)

if __name__=='__main__':unittest.main()
