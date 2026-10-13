"""Tight current cable budgets and endpoint continuity for corridor recipes."""
import json
import math
import unittest
from plan_body_fanout_layout import OUT,prepared_rows,corridor


class ClearScene:
    def clear(self,points,row):return True


class BlockedScene:
    def clear(self,points,row):return False


class CorridorTest(unittest.TestCase):
    def test_three_shortest_current_budgets(self):
        rows=prepared_rows(json.loads((OUT/'body-fanout-work-contract.json').read_text()))
        for row in sorted(rows,key=lambda r:r['capacity_before_terminal_mm'])[:3]:
            route,points=corridor(ClearScene(),row)
            self.assertIsNotNone(points,(row['wire'],route))
            self.assertGreaterEqual(route['spare_before_trim_mm'],0)
            self.assertGreaterEqual(route['minimum_sampled_R_mm'],10)
            self.assertLess(math.dist(route['parts'][-1]['end'],row['receiver_point_mm']),1e-8)
            for a,b in zip(route['parts'],route['parts'][1:]):
                self.assertLess(math.dist(a['end'],b['start']),1e-8)

    def test_closed_neighbourhood_does_not_invent_a_path(self):
        row=prepared_rows(json.loads((OUT/'body-fanout-work-contract.json').read_text()))[0]
        route,points=corridor(BlockedScene(),row)
        self.assertIsNone(points)
        self.assertEqual(route['search_states'],1)


if __name__=='__main__':unittest.main()
