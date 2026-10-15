import unittest
from allocate_g1_root_path import root_orders

class WholeRootOrdersTests(unittest.TestCase):
    def test_six_whole_axis_orders_preserve_actual_endpoints(self):
        start=[-74,-84.2375,112];goal=[-40,-54,144.5]
        plans=list(root_orders(start,goal))
        self.assertEqual(len(plans),6)
        self.assertEqual(len({tuple(tuple(p) for p in path) for _,path in plans}),6)
        for order,path in plans:
            self.assertEqual(path[0],start);self.assertEqual(path[-1],goal)
            self.assertEqual(len(path),4)
            for a,b in zip(path,path[1:]):self.assertEqual(sum(x!=y for x,y in zip(a,b)),1)
        self.assertEqual(start,[-74,-84.2375,112]);self.assertEqual(goal,[-40,-54,144.5])

if __name__=='__main__':unittest.main()
