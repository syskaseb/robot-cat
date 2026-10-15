import copy,json,unittest
from canonical_body_rows import normalize,selected_rows
from direct_terminal_approaches import simplify
from plan_body36_receiver_space import P


class DirectApproachTests(unittest.TestCase):
    def test_only_optional_pending_loops_removed_all_physical_lands_unchanged(self):
        macro=json.loads((P.OUT/'body36-shared-macro-layout.json').read_text())
        base=json.loads((P.OUT/'body36-recovery-layout.json').read_text())
        rows=normalize(macro,base,selected_rows(P.OUT/'receiver-joint-selection.json',P.ROOT))
        before=copy.deepcopy(rows);current=simplify(rows,macro['remaining_wire_ids'])
        self.assertEqual(rows,before)
        for n in ('W004','W069'):
            self.assertEqual(current[n]['receiving_land'],before[n]['receiving_land'])
            self.assertEqual(current[n]['receiver_point_mm'],before[n]['receiver_point_mm'])
            self.assertEqual(current[n]['receiving_parts'],[before[n]['receiving_land']])
            self.assertEqual(current[n]['receiver_outward_axis'],[0.,0.,1.])
            self.assertEqual(current[n]['receiving_grip_part_index'],0)
        for n in set(rows)-{'W004','W069'}:self.assertEqual(current[n],before[n],n)
        self.assertEqual(current['W022']['receiving_grip_part_index'],2)


if __name__=='__main__':unittest.main()
