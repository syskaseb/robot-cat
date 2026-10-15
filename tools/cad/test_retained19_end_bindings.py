import unittest
from prepare_retained19_end_bindings import cavity


class PhysicalCavityTest(unittest.TestCase):
    def test_permuted_ground_point_not_moved_twice(self):
        d={'RR_G.1':dict(physical_project_cavity=4,point_mm=[109.75,-90,79.5])}
        self.assertEqual(cavity('RR_G.1',d,{}),('RR_G.4',[109.75,-90,79.5]))
    def test_data_bridge_alias_applied_before_lookup(self):
        d={'D_RL.5':dict(physical_project_cavity=5,point_mm=[1,2,3])}
        self.assertEqual(cavity('D_RL.1',d,{'D_RL.1':'D_RL.5'}),('D_RL.5',[1,2,3]))
    def test_other_role_kept_uninvented(self):
        self.assertEqual(cavity('S0.in',{},{}),('S0.in',None))


if __name__=='__main__':unittest.main()
