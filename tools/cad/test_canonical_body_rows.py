import copy
import json
import unittest
from canonical_body_rows import normalize, selected_rows
from plan_body36_receiver_space import P


class CanonicalRowsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parent = json.loads((P.OUT / 'body36-shared-macro-layout.json').read_text())
        cls.base = json.loads((P.OUT / 'body36-recovery-layout.json').read_text())
        cls.selected = selected_rows(P.OUT / 'receiver-joint-selection.json', P.ROOT)

    def test_selected_receiver_removes_unqualified_extra_arc(self):
        rows = normalize(self.parent, self.base, self.selected)
        self.assertEqual(rows['W022']['receiving_parts'], self.selected['W022']['receiving_parts'])
        self.assertEqual(len(rows['W022']['receiving_parts']), 5)
        self.assertEqual(rows['W022']['receiving_grip_part_index'], 2)
        self.assertEqual(rows['W022']['receiver_outward_axis'], [1, 0, 0])
        self.assertEqual(rows['W022']['free_end'], rows['W022']['receiving_parts'][0]['start'])

    def test_normalization_does_not_double_pack_or_mutate_positive_rows(self):
        before = copy.deepcopy(self.parent)
        rows = normalize(self.parent, self.base, self.selected)
        again = dict(self.parent, changed_rows=list(rows.values()))
        self.assertEqual(rows, normalize(again, self.base, self.selected))
        self.assertEqual(before, self.parent)
        for row in self.parent['changed_rows']:
            if row['wire'] not in self.parent['remaining_wire_ids']:
                self.assertEqual(rows[row['wire']], row)
        self.assertEqual(rows['W004']['free_start'], rows['W004']['source_parts'][-1]['end'])


if __name__ == '__main__':
    unittest.main()
