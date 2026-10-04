import json,unittest
from w5_leg_end_preparation_r1 import ROOT,build


class ContinuousLoomEndTests(unittest.TestCase):
    def setUp(self):
        rels={
            'mapping':'hardware/electronics/full-cat/w5-leg-source-map-r1/interface.json',
            'bank':'hardware/electronics/full-cat/servo-fuse-bank-electrical-r2/interface.json',
            'process':'hardware/reference/leg-cable-2026-10-04/TE-output-process.json',
            'cable':'hardware/reference/leg-cable-2026-10-04/facts.json'}
        self.result=build(**{k:json.loads((ROOT/p).read_text(encoding='utf-8')) for k,p in rels.items()})

    def test_no_duplicate_local_v_stock_or_fuse_bypass(self):
        self.assertEqual(self.result['body_connections'],dict(WAGO221415=24,TE25201842=12))
        for loom in self.result['looms']:
            v=next(e for e in loom['ends'] if e['body_contact'].endswith('.out'))
            self.assertEqual(v['body_contact'],'F_'+loom['loom']+'.out')
            self.assertEqual(v['additional_local_wire_or_terminal_quantity'],0)
        self.assertEqual(self.result['new_splices'],0)

    def test_no_fake_cuts_cavity_numbers_or_selected_stock(self):
        for loom in self.result['looms']:
            for end in loom['ends']:
                self.assertIsNone(end['actual_cut_mm'])
                self.assertIsNone(end['factory_plug_cavity_number'])
        self.assertEqual(self.result['candidate_purchase']['cables'],12)
        self.assertFalse(self.result['selected'])
        self.assertFalse(self.result['W5_complete'])


if __name__=='__main__':unittest.main()
