"""Fast geometric planning contracts, no scene rebuild or files written."""
import copy,json,math,unittest
from allocate_current_hip_space import curve_at,OUT


class HipAllocationContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=json.loads((OUT/'hip-axial-loom-plan.json').read_text())['loops']

    def test_nominal_recipes_are_fixed_length(self):
        for source in self.rows:
            for d in ([0,0,1],[0,source['side'],0]):
                r=dict(source,midpoint_direction=d)
                q=curve_at(r,0)
                self.assertIsNotNone(q)
                self.assertAlmostEqual(sum(p['length_mm'] for p in q),126,places=5)
                self.assertAlmostEqual(q[0]['length_mm'],9)
                self.assertAlmostEqual(q[-1]['length_mm'],9)
                self.assertGreaterEqual(min(p['radius_mm'] for p in q if p['kind']!='line'),31)

    def test_both_anchor_endpoints_are_retained(self):
        for source in self.rows:
            r=dict(source,midpoint_direction=[0,0,1]);q=curve_at(r,0)
            self.assertLess(math.dist(q[0]['start'],r['fixed_anchor_world_mm']),1e-7)
            self.assertLess(math.dist(q[-1]['end'],r['moving_anchor_rest_world_mm']),1e-7)
            for a,b in zip(q,q[1:]):self.assertLess(math.dist(a['end'],b['start']),1e-7)

    def test_recipe_does_not_mutate_qualified_input(self):
        r=copy.deepcopy(self.rows[0]);r['midpoint_direction']=[0,0,1]
        before=copy.deepcopy(r)
        curve_at(r,-15);curve_at(r,0);curve_at(r,15)
        self.assertEqual(r,before)


if __name__=='__main__':unittest.main()
