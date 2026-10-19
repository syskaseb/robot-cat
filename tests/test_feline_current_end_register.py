import json
from pathlib import Path
import unittest

OUT=Path(__file__).resolve().parents[1]/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'


class EndRegister(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=json.loads((OUT/'n01-current-246-end-register.json').read_text())
        cls.rows=cls.doc['endpoints'];cls.byid={r['id']:r for r in cls.rows}

    def test_all_accounting_ends_without_invented_connections(self):
        self.assertEqual(len(self.rows),246);self.assertEqual(len(self.byid),246)
        self.assertEqual(len(self.doc['portions']),123)
        self.assertTrue(all(len(v)==2 for v in self.doc['portions'].values()))
        self.assertEqual(self.doc['internal_U1_sections_not_duplicated'],11)
        self.assertFalse(self.doc['N01_complete'])

    def test_current_source_frames_not_double_placed(self):
        self.assertEqual(self.byid['W008/body/start']['point_mm'],[-75.5,-33.6,69.4])
        for r in self.rows:
            if r['group']=='JPWM':
                self.assertAlmostEqual(r['point_mm'][1],-78.8)
                self.assertLess(abs(r['point_mm'][0]+65),16)
                self.assertGreater(r['point_mm'][2],80)

    def test_jacket_is_not_a_guessed_solder_pad(self):
        self.assertEqual(len(self.doc['actual_saved_Pi_pipe_cap_receipts']),7)
        self.assertEqual(self.doc['explicit_pipe_holds'],[])
        rows=[r for r in self.rows if r['pose_status']=='CURRENT_JACKET_BOUNDARY_SOLDER_PAD_REMAINS_SEPARATE']
        self.assertEqual(len(rows),12)
        for r in rows:
            self.assertIsNone(r['point_mm'])
            self.assertIsNotNone(r['jacket_routing_point_mm'])
            self.assertFalse(r['supplier_datum_guaranteed'])


if __name__=='__main__':unittest.main()
