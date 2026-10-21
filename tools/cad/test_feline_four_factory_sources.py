import unittest
import numpy as np
from connect_feline_four_factory_sources import field_link,options
from receive_feline_underplate_return_gallery import forward


class FactorySourceLinks(unittest.TestCase):
    def test_intermediate_field_block_is_not_hidden_by_clear_endpoints(self):
        rows=[];forward(rows,[0,0,0],[1,0,0],20)
        free=np.ones((31,11,11),bool);origin=np.array([-5,-5,-5])
        self.assertTrue(field_link(rows,free,origin))
        free[15,5,5]=False
        self.assertFalse(field_link(rows,free,origin))

    def test_endpoint_exclusion_is_explicit_not_whole_link_clearance(self):
        rows=[];forward(rows,[0,0,0],[1,0,0],20)
        free=np.ones((31,11,11),bool);origin=np.array([-5,-5,-5]);free[5,5,5]=False
        self.assertFalse(field_link(rows,free,origin))
        self.assertTrue(field_link(rows,free,origin,skip_first=8))

    def test_link_family_keeps_actual_minimum_radius(self):
        choices=options([0,0,0],[1,0,0],[45,30,15],[0,1,0])
        self.assertTrue(choices)
        for rows in choices:
            self.assertTrue(all(r.get('radius_mm',100)>=12.4-1e-6 for r in rows))


if __name__=='__main__':unittest.main()
