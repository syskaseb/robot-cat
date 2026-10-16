import unittest
import FreeCAD as A
import Part
from plan_remaining25_restraint_space import own_wire_name,profile


class OwnWireTests(unittest.TestCase):
    def test_factory_alias_is_same_wire_not_neighbour(self):
        self.assertTrue(own_wire_name('wire/W026_FACTORY',{'W026'}))
        self.assertTrue(own_wire_name('wire/W026_CUSTOM',{'W026'}))
        self.assertFalse(own_wire_name('wire/W027_FACTORY',{'W026'}))
        self.assertFalse(own_wire_name('wire/W0260',{'W026'}))

    def test_real_own_wire_clearance_not_foreign_margin(self):
        g=dict(project_radius_mm=2.1,axis=[1,0,0],centre_world_mm=[0,0,0],land_mm=9)
        q=profile(g,[0,1,0],1)
        w=Part.makeLine(A.Vector(-9,0,0),A.Vector(9,0,0))
        gap=q['band'].distToShape(w)[0]
        self.assertAlmostEqual(gap,2.3,places=6)
        self.assertGreater(gap,2.1)
        self.assertLess(gap,2.35)


if __name__=='__main__':unittest.main()
