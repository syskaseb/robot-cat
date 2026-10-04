import copy
import unittest
from w5_source_material_contribution_r2 import reconcile, PRINTS


class SourceFamilyStock(unittest.TestCase):
    def fixture(self):
        old = [{'identity': ident, 'quantity': 1} for ident, action, *_ in PRINTS if action == 'replace']
        rows = [dict(role='platformBolt', supplier_id='M3x12', quantity=2),
                dict(role='platformNut', supplier_id='nut', quantity=2),
                dict(role='platformWasher', supplier_id='washer', quantity=4)]
        roof = [dict(role='roofBolt', supplier_id='M3x16', quantity=4),
                dict(role='roofNut', supplier_id='nut', quantity=4),
                dict(role='roofWasher', supplier_id='washer', quantity=8)]
        return {}, dict(prints=old), dict(allocations=rows), dict(allocations=roof)

    def test_replacements_are_not_extra_prints(self):
        result, rows, _, totals = reconcile(*self.fixture())
        self.assertEqual((result['prints']['replaced'], result['prints']['additional']), (4, 3))
        self.assertEqual(result['prints']['candidate_jobs'], 7)
        self.assertEqual(len(rows), 7)
        self.assertEqual(totals, dict(M3x12=2, M3x16=4, nut=6, washer=12))

    def test_no_input_mutation(self):
        inputs = self.fixture(); before = copy.deepcopy(inputs)
        reconcile(*inputs)
        self.assertEqual(inputs, before)

    def test_double_counted_addition_rejected(self):
        inputs = self.fixture()
        inputs[1]['prints'].append(dict(identity='body:source-hood-west', quantity=1))
        with self.assertRaises(AssertionError):
            reconcile(*inputs)

    def test_missing_replaced_role_rejected(self):
        inputs = self.fixture(); inputs[1]['prints'].pop()
        with self.assertRaises(AssertionError):
            reconcile(*inputs)

    def test_duplicate_allocation_rejected(self):
        inputs = self.fixture(); inputs[3]['allocations'][0]['role'] = 'platformBolt'
        with self.assertRaises(AssertionError):
            reconcile(*inputs)


if __name__ == '__main__':
    unittest.main()
