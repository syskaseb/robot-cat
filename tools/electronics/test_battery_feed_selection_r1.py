"""Small selected-interface checks, not another whole-robot audit."""
from pathlib import Path
import csv,json,unittest
ROOT=Path(__file__).resolve().parents[2]
def read(rel):return json.loads((ROOT/rel).read_text(encoding='utf-8'))


class SelectedFeed(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s=read('hardware/manufacturing/one-batch-prototype-r48/selection.json')
        cls.q=read('hardware/manufacturing/one-batch-prototype-r48/one-order-quantities.json')
        cls.c=read('hardware/electronics/full-cat/battery-feed-selected-r1/interface.json')
        cls.g=read('hardware/electronics/full-cat/battery-feed-access-finish-r1/checks.json')

    def test_only_local_result_counted(self):
        self.assertEqual(self.s['phase1_percent'],70)
        self.assertFalse(self.s['W5_complete']);self.assertFalse(self.c['physical_pass'])
        self.assertEqual(self.g['hits'],[]);self.assertEqual(self.g['errors'],[])
        self.assertEqual(len(self.g['tool_access_contacts']),5)
        self.assertIn('before routing',self.c['conditions'][0])
        self.assertEqual(read(self.g['parent_check'])['status'],'REJECTED_PAIR')

    def test_one_current_deck_and_bridge(self):
        self.assertEqual(len(self.s['prints']),72)
        self.assertEqual(self.s['installed_jobs'],68)
        self.assertEqual(sum(r['quantity'] for r in self.s['prints'] if r['purpose']=='installed_candidate'),111)
        for identity in ('electronics:DeckP10-cover-mount','electronics:F0-XT60-source-bridge'):
            rows=[r for r in self.s['prints'] if r['identity']==identity];self.assertEqual(len(rows),1)
            self.assertTrue((ROOT/rows[0]['stl']).is_file());self.assertTrue((ROOT/rows[0]['native']).is_file())

    def test_matched_mounts_and_removed_wrong_holes(self):
        self.assertEqual(self.g['mount_xy'],[[-10,53],[61,53]])
        self.assertTrue(self.g['old_holes_absent']);self.assertTrue(self.g['relocated_reopen'])

    def test_endpoints_preserved_and_only_two_new_blanks(self):
        old=read('hardware/electronics/full-cat/body-harness-w5-r2/interface.json')['conductors']
        new=read(self.s['body_harness'])['conductors']
        self.assertEqual([(r['id'],r['a'],r['b'],r['net']) for r in new],[(r['id'],r['a'],r['b'],r['net']) for r in old])
        self.assertEqual(sum(r.get('nominal_selected_blank_mm') is not None for r in new),12)
        changed=[r['id'] for r,o in zip(new,old) if r!=o];self.assertEqual(set(changed),{'W001','W075'})
        self.assertEqual(self.c['wire_blanks_mm'],{'W001':140,'W075':40})
        cuts=list(csv.DictReader((ROOT/self.s['current_wire_cut_sheet']).read_text(encoding='utf-8').splitlines()))
        self.assertEqual(len(cuts),80)
        self.assertEqual(sum(bool(r['nominal_selected_blank_mm']) for r in cuts),12)
        self.assertEqual(next(r['nominal_selected_blank_mm'] for r in cuts if r['id']=='W001'),'140')

    def test_exact_fastener_offers_reused_without_duplicates(self):
        cart=read(self.s['fixed_fastener_cart'])['rows'];self.assertEqual(len(cart),29)
        self.assertEqual(len({(r['supplier'],r['supplier_sku']) for r in cart}),29)
        for sku,count in [('0912A2-M020X012VISK',26),('00125202',78),('SKL000381',101)]:
            row=next(r for r in cart if r['supplier_sku']==sku)
            self.assertEqual(row['planning_quantity'],count)
            self.assertEqual(sum(r['planning_quantity'] for r in row['roles']),count)

    def test_tie_pack_and_existing_wire_stock(self):
        self.assertEqual(len(self.q['lines']),109)
        tie=next(r for r in self.q['lines'] if r['id']=='tie:111-02370')
        self.assertEqual((tie['installed'],tie['planning_quantity']),(102,200))
        cat=read(self.s['nonfastener_catalog'])['rows']
        self.assertEqual(next(r for r in cat if r['quantity_id']=='tie:111-02370')['planning_quantity'],200)
        wire=next(r for r in self.q['lines'] if r['id']=='p0:WIRE-INLET-BLACK12-P0')
        self.assertEqual(wire['planning_quantity'],2)
        stock=read(self.s['current_stock_ledger'])['stock']
        lapp=next(r for r in stock if r['stock_id']=='LAPP 0107001')
        self.assertEqual((lapp['selected_BAT_allocation_mm'],lapp['battery_legacy_reserve_mm'],lapp['unallocated_input_budget_mm']),(140,0,1860))


if __name__=='__main__':unittest.main()
