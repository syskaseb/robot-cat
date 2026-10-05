"""Preparation accounting checks; no physical/electrical safety qualification."""
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
PREP=ROOT/'hardware/electronics/full-cat/w5-prototype-preparation-r2/preparation.json'


class PrototypePreparation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=json.loads(PREP.read_text(encoding='utf-8'))
        cls.rows={r['wire']:r for r in cls.p['P0']}

    def test_all_logical_connections_preserved(self):
        graph=json.loads((ROOT/'hardware/electronics/power-platform/wiring-p0.json').read_text(encoding='utf-8'))
        self.assertEqual(set(self.rows),{r['id'] for r in graph['wires']})
        for r in graph['wires']:
            self.assertEqual((self.rows[r['id']]['a'],self.rows[r['id']]['b']),(r['a'],r['b']))
        self.assertEqual(len(self.p['AUX']),6)
        self.assertFalse(self.p['individual_blank_unresolved_wire_ids'])

    def test_factory_looms_counted_once(self):
        looms=self.p['continuous_factory_looms']
        self.assertEqual(len(looms),12)
        self.assertEqual(len({r['loom'] for r in looms}),12)
        for loom in looms:
            cores=[r for r in self.rows.values() if r.get('factory_loom')==loom['loom']]
            self.assertEqual(len(cores),3)
            self.assertTrue(all(r['nominal_preparation_blank_mm'] is None for r in cores))
            self.assertLessEqual(loom['common_blank_mm'],loom['nominal_length_mm'])
        self.assertEqual(self.p['shared_BUS_cable']['quantity'],1)
        self.assertEqual(self.p['shared_BUS_cable']['nominal_mm'],900)

    def test_no_legacy_or_factory_double_charge(self):
        stock=self.p['affected_material_stock']
        self.assertEqual(stock['HELU23802']['nominal_total_mm'],3910)
        self.assertTrue(stock['legacy_source920mm_not_added'])
        self.assertEqual(stock['LAPP0107001']['nominal_mm'],2880+self.rows['W001']['nominal_preparation_blank_mm'])
        self.assertTrue(self.rows['W076']['retained_factory_F0_lead'])
        self.assertEqual(self.rows['W076']['nominal_preparation_blank_mm'],80)
        for r in self.rows.values():
            if r.get('composite_factory_lead'):
                self.assertIsNone(r['nominal_preparation_blank_mm'])
                self.assertGreater(r['nominal_extension_blank_mm'],0)
        for name in ('LAPP0107001','TKD2500125'):
            r=stock[name];self.assertGreaterEqual(r['candidate_stock_m']*1000,r['nominal_mm']+r.get('fitting_allowance_mm',0))
        r=stock['HELU23802'];self.assertGreaterEqual(r['candidate_stock_m']*1000,r['total_with_allowance_mm'])

    def test_preparation_not_fabricated_completion(self):
        for k in ('selected','W1_complete','W5_complete','A2_complete','K3_complete','physical_pass'):
            self.assertFalse(self.p[k],k)
        self.assertTrue(self.p['open_gates'])


if __name__=='__main__':unittest.main()
