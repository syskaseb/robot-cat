import unittest
from receiver_domain_solver import solve


class DomainSolverTest(unittest.TestCase):
    def test_propagates_forced_value_across_chain(self):
        result,stats=solve({'a':[0],'b':[0,1],'c':[0,1]},lambda a,x,b,y:x!=y if {a,b} in ({'a','b'},{'b','c'}) else True)
        self.assertEqual(result,{'a':0,'b':1,'c':0})
        self.assertEqual(stats['nodes'],1)
    def test_unsatisfiable_triangle_requires_branching(self):
        result,stats=solve({n:[0,1] for n in 'abc'},lambda a,x,b,y:x!=y)
        self.assertIsNone(result)
        self.assertEqual(stats['status'],'contradiction_in_received_domains')
    def test_expired_budget_is_not_impossibility(self):
        result,stats=solve({'a':[0,1],'b':[0,1]},lambda *args:True,seconds=-1)
        self.assertIsNone(result)
        self.assertEqual(stats['status'],'budget_exhausted')


if __name__=='__main__':unittest.main()
