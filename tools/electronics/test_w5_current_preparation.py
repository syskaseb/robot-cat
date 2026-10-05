from pathlib import Path
import json
import unittest

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'hardware/electronics/full-cat'

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

class CurrentPreparation(unittest.TestCase):
    def test_twelve_looms_remain_uncut_and_screen_not_operating_limit(self):
        d=read(BASE/'w5-loop-preparation-r1/preparation.json')
        self.assertEqual(len(d['looms']),12)
        self.assertEqual(len({r['loom'] for r in d['looms']}),12)
        self.assertFalse(d['full_operating_range_approved'])
        self.assertFalse(d['physical_pass'])
        self.assertEqual(d['nominal_factory_blanks_with_reserve_sum_mm'],8080)
        for r in d['looms']:
            self.assertLessEqual(r['nominal_common_trial_blank_mm'],900)
            self.assertEqual(r['factory_length_nominal_mm'],900)
            self.assertIn('Keep900mm untrimmed',r['bench_preparation'])
            self.assertFalse(r['continuous_cable_sweep_verified'])
            self.assertTrue(r['numerical_screen_is_not_cable_clearance'])

    def test_one_factory_sku_for_thirteen_physical_cables(self):
        d=read(BASE/'w5-one-order-candidate-r1/quantities.json')
        rows={r['id']:r for r in d['lines']}
        self.assertEqual(len(rows),115)
        self.assertEqual(len(d['lines']),115)
        self.assertNotIn('p0:BUS-PIGTAIL-P0',rows)
        r=rows['factory:Waveshare34172']
        self.assertEqual(r['planning_quantity'],3)
        self.assertEqual(r['factory_cables_installed'],13)
        self.assertEqual(r['factory_pack_spares'],5)
        self.assertEqual(r['roles_installed'],{'BUS_D_G_shared':1,'leg_continuous_looms':12})
        self.assertEqual(r['product_binding']['supplier_sku'],'34172')
        self.assertEqual(sum(x.get('factory_cables_installed',0) for x in rows.values()),13)

    def test_material_bounds_not_installed_census_or_selection(self):
        d=read(BASE/'w5-one-order-candidate-r1/quantities.json')
        rows={r['id']:r for r in d['lines']}
        t=rows['tie:111-02370']
        self.assertEqual(t['conservative_stock_upper_bound'],384)
        self.assertEqual(t['planning_quantity'],400)
        self.assertEqual(t['current_W5_new_installed'],86)
        self.assertFalse(t['exact_installed_total_verified'])
        self.assertEqual(rows['tie:111-02189']['installed'],12)
        self.assertEqual(rows['tie:111-02189']['product_binding']['supplier_sku'],'329-T18L9C2')
        for k in ('selected','W1_complete','W5_complete','K3_complete','physical_pass'):
            self.assertFalse(d[k])
        for r in d['lines']:
            if 'product_binding' in r:
                self.assertEqual(r['planning_quantity'],r['product_binding']['planning_quantity'],r['id'])

if __name__=='__main__':unittest.main()
