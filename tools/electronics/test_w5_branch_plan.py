import unittest
import w5_branch_tiered_corridors as p


class JointBranchContract(unittest.TestCase):
    def test_complete_departure_scope(self):
        self.assertEqual(len(p.targets),24)
        self.assertEqual(set(p.targets),set(p.previous.base.plan['choices']))

    def test_retained_and_reopened_disjoint(self):
        self.assertFalse(p.todo & {r['wire'] for r in p.received['accepted']})
        self.assertEqual(len(p.received['accepted']),25)

    def test_immutable_endpoints_and_radii(self):
        for row in p.rows:
            if row['wire'] not in p.todo:continue
            candidates=list(p.variants(row))
            self.assertTrue(candidates)
            for r in candidates:
                self.assertEqual(r['a']['edges'][0]['start'],row['a_datum']['point_mm'])
                self.assertEqual(r['middle'][0],r['a']['tip'])
                self.assertEqual(r['middle'][-1],row['target'])
                self.assertEqual(r['radius_mm'],row['radius_mm'])


if __name__=='__main__':unittest.main()
