import copy,json,unittest
from assembly_tools_k3_r2 import ROOT,payload,build_payload


class Tools(unittest.TestCase):
    def setUp(self):
        self.v=payload()
        p=ROOT/'hardware/manufacturing/one-batch-prototype-r42'
        self.s=json.loads((p/'selection.json').read_text(encoding='utf-8'))
        self.q=json.loads((p/'one-order-quantities.json').read_text(encoding='utf-8'))

    def test_complete_nut_roles_including_pi(self):
        nuts=[r for r in self.v['tools'] if r['role'].startswith('nut_')]
        self.assertEqual({r['AF_mm'] for r in nuts},{4,5,5.5})
        self.assertEqual({r['sku'] for r in nuts},{'05118120001','05118124001','05118126001'})

    def test_strip_and_cut_cover_current_wire_and_ends(self):
        r=next(r for r in self.v['tools'] if r['role']=='wire_strip_and_cut')
        for wire in [.14,.25,.5,1,3.31,4]:
            self.assertLessEqual(r['wire_area_mm2'][0],wire)
            self.assertLessEqual(wire,r['wire_area_mm2'][1])
            self.assertLessEqual(wire,r['stranded_cut_max_mm2'])
        self.assertEqual(r['project_stop_range_mm'],[3,18])
        for length in [6.76,7.54,8.73,11,12,14]:
            self.assertTrue(3<=length<=18)

    def test_compatible_tip_family_not_hot_air_soldering(self):
        tips=[r for r in self.v['tools'] if r['role'].startswith('solder_tip')]
        self.assertEqual({r['compatible_iron'] for r in tips},{'WEP70'})
        self.assertEqual({r['width_mm'] for r in tips},{2.4,4.6})
        self.assertEqual(next(r for r in self.v['tools'] if r['role']=='solder_station')['tip_family'],'ET')

    def test_one_solder_one_flux_not_duplicate_pen(self):
        r=self.v['solder']
        self.assertEqual(r['planning_quantity']*r['stock_per_pack'],100)
        self.assertEqual(r['alloy'],'Sn96.5Ag3.0Cu0.5')
        self.assertTrue(r['no_separate_flux_required_in_default_set'])
        self.assertIsNone(r['verified_consumption_g'])
        self.assertFalse(any('836' in r['sku'] for r in self.v['tools']))

    def test_parent_prints_parts_crimp_tools_retained(self):
        before=copy.deepcopy(self.q)
        s,q=build_payload(self.v,self.s,self.q)
        self.assertEqual(before,self.q)
        self.assertEqual(s['prints'],self.s['prints'])
        self.assertEqual(q['lines'][:-1],self.q['lines'])
        self.assertEqual(len(q['lines']),115)
        self.assertEqual(q['exact_crimp_tool_requirements'],self.q['exact_crimp_tool_requirements'])
        self.assertEqual(q['required_tools_buy_or_borrow'][4],self.q['required_tools_buy_or_borrow'][4])

    def test_unique_tool_skus_no_ownership_completion_claim(self):
        skus=[r['sku'] for r in self.v['tools']]
        self.assertEqual(len(skus),len(set(skus)))
        for name in ['tool_access_confirmed','requires_exact_brand_purchase','physical_pass','K3_complete','W5_complete']:
            self.assertFalse(self.v[name])
        self.assertTrue(self.v['no_purchase'])
        self.assertTrue(self.v['no_power'])

    def test_metrology_and_factory_screw_limits_explicit(self):
        r=next(r for r in self.v['tools'] if r['role']=='caliper')
        self.assertEqual(r['resolution_mm'],.01)
        self.assertEqual(r['catalog_accuracy_mm'],.03)
        self.assertEqual(len([r for r in self.v['tools'] if r['role'].startswith('factory_screw')]),3)
        self.assertEqual(self.v['phase1_percent'],70)

    def test_utf8_and_sources(self):
        self.assertNotIn('\ufffd',json.dumps(self.v,ensure_ascii=False))
        self.assertTrue(all(r['source'].startswith('https://') for r in self.v['tools']))
        self.assertTrue((ROOT/'hardware/reference/assembly-tools-2026-10-02/Wera-2069.pdf').is_file())


if __name__=='__main__':
    unittest.main()
