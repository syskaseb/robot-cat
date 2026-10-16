import unittest
from compose_w5_materials import bulk_stock


class MaterialTests(unittest.TestCase):
    def test_bulk_stock_never_rounds_below_nominal(self):
        draw=dict(LAPP0107001=1880,LAPP4126002S=1185,TKD2500125=2310,HELU23802=6660)
        rows=bulk_stock(draw)
        self.assertEqual([r['project_stock_mm'] for r in rows],[2000,2000,3000,7000])
        self.assertTrue(all(r['project_stock_mm']>=r['nominal_fit_draw_mm'] for r in rows))
        self.assertTrue(all(r['actual_owned_stock_mm'] is None and not r['purchase_unit_verified'] for r in rows))


if __name__=='__main__':unittest.main()
