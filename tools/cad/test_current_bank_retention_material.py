import unittest
from current_bank_retention_material import geometry


class BankLayoutTests(unittest.TestCase):
    def test_one_component_set_and_all_fasteners(self):
        q=geometry()
        self.assertEqual((len(q['prints']),len(q['feet']),len(q['hardware'])),(6,4,24))
        self.assertEqual((len(q['ATO_access']),len(q['recipe']['holders'])),(12,12))
        self.assertEqual(len({r['id'] for r in q['recipe']['fasteners']}),8)
        self.assertTrue(all(r['tip_past_nut_mm']==.5 for r in q['recipe']['fasteners']))
        self.assertFalse(q['recipe']['M4_complete'])
        self.assertTrue(all(v['parent_path'] is None for v in q['feet'].values()))


if __name__=='__main__':unittest.main()
