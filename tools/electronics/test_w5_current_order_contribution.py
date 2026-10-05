import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

class CurrentOrderTests(unittest.TestCase):
    def setUp(self):
        self.r=json.loads((ROOT/'hardware/electronics/full-cat/w5-current-order-contribution-r1/stock.json').read_text(encoding='utf-8'))
    def test_unique_added_fasteners(self):
        roles=self.r['new_installed_fastener_roles']
        self.assertEqual(len(roles),len({r['role'] for r in roles}))
        self.assertEqual(sum(r['quantity'] for r in roles),40)
    def test_stock_replaces_instead_of_adding_legacy(self):
        rows={r['quantity_id']:r['planning_quantity'] for r in self.r['material_overrides']}
        self.assertEqual(rows,{'p0:WIRE-INLET-BLACK12-P0':4,'p0:WIRE-RED4-P0':5,'p0:WIRE-BLACK4-P0':3})
        self.assertTrue(self.r['old920mm_not_added'])
        self.assertTrue(self.r['old_BUS300mm_not_added'])
    def test_split_straps_not_double_counted(self):
        roles=self.r['new_T18I_roles']
        self.assertNotIn('continuous_loom_body_split',roles)
        self.assertEqual(sum(roles.values()),86)
        self.assertFalse(self.r['K3_complete'])
        self.assertFalse(self.r['selected'])

if __name__=='__main__':unittest.main()
