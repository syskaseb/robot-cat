import unittest
from prepare_retained19_end_bindings import cavity,role_order


class PhysicalCavityTest(unittest.TestCase):
    def test_w066_recipe_direction_not_blind_electrical_list_order(self):
        guide=dict(electrical_roles=['P_SYS.1','S0.out'],segments=[dict(endpoints=['S0.OUT.barrel_tip','P_SYS.1'])])
        self.assertEqual(role_order(guide)[0],['S0.out','P_SYS.1'])
    def test_factory_extension_outer_roles_only(self):
        guide=dict(electrical_roles=['F0.out','S0.in'],segments=[
            dict(endpoints=['F0.out','POST_F0.1']),dict(endpoints=['POST_F0.2','S0.IN.barrel_tip'])])
        self.assertEqual(role_order(guide)[0],['F0.out','S0.in'])
    def test_unknown_recipe_direction_is_labeled_not_invented(self):
        guide=dict(electrical_roles=['a','b'],segments=[{}])
        roles,basis=role_order(guide)
        self.assertEqual(roles,['a','b']);self.assertIn('unverified',basis)

    def test_permuted_ground_point_not_moved_twice(self):
        d={'RR_G.1':dict(physical_project_cavity=4,point_mm=[109.75,-90,79.5])}
        self.assertEqual(cavity('RR_G.1',d,{}),('RR_G.4',[109.75,-90,79.5]))
    def test_data_bridge_alias_applied_before_lookup(self):
        d={'D_RL.5':dict(physical_project_cavity=5,point_mm=[1,2,3])}
        self.assertEqual(cavity('D_RL.1',d,{'D_RL.1':'D_RL.5'}),('D_RL.5',[1,2,3]))
    def test_other_role_kept_uninvented(self):
        self.assertEqual(cavity('S0.in',{},{}),('S0.in',None))


if __name__=='__main__':unittest.main()
