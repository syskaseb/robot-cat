import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
from plan_current_mta_interfaces import plan,R

class MtaInterfacePlanTests(unittest.TestCase):
    def test_both_actual_ends_and_custom_return_cavities(self):
        p=plan();self.assertEqual(4,len(p['holders']));self.assertEqual(8,len(p['joints']))
        self.assertEqual({'W041','W026','W042','W037','W044','W045','W052','W053'},
                         {v['body_conductor_id'] for v in p['factory_routes'].values()})
        self.assertTrue(all(j['custom_entry_mm']!=j['factory_entry_mm'] for j in p['joints']))
    def test_factory_curves_have_real_lands_and_budget(self):
        for row in plan()['factory_routes'].values():
            q=row['parts'];self.assertEqual(9,q[0]['length_mm']);self.assertEqual(9,q[-1]['length_mm'])
            self.assertGreater(row['margin_mm'],0)
            self.assertTrue(all(e['radius_mm']==R for e in q if e['kind']=='arc'))
            self.assertTrue(all(a['end']==b['start'] for a,b in zip(q,q[1:])))
    def test_no_partial_credit_or_double_stock(self):
        p=plan();self.assertFalse(p['selected'] or p['physical_pass'] or p['W5_complete'])
        self.assertEqual(9,p['quantity_reconciliation']['candidate_total_not_purchase'])
        self.assertTrue(all(j['casing_mm'][5]<160 for j in p['joints']))
        self.assertTrue(all(j['casing_mm'][1]>=-100 and j['casing_mm'][4]<=100 for j in p['joints']))
        self.assertTrue(all(h['casing_mm'][5]<160 and h['casing_mm'][1]>=-100 and h['casing_mm'][4]<=100 for h in p['holders']))
        self.assertEqual({'WAGO221-2411'},{j['sku'] for j in p['joints']})
        for j in p['joints']:
            for a,b,u in zip(j['factory_entry_mm'],j['custom_entry_mm'],j['custom_departure_axis']):
                self.assertAlmostEqual(b-a,35.5*u)
if __name__=='__main__':unittest.main()
