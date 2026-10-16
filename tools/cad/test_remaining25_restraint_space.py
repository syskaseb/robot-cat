import unittest
import FreeCAD as A
import Part
import json
from plan_remaining25_restraint_space import own_wire_name,profile
from remaining25_restraint_layout import apply_layout,OUT


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

    def test_two_layout_changes_keep_all_physical_ends_and_other_groups(self):
        original=json.loads((OUT/'remaining25-interface-allocation.json').read_text())
        p,_=apply_layout(original)
        self.assertEqual(len(p['groups']),54)
        bound=[e for g in p['groups'] for e in g['ends']]
        self.assertEqual((len(bound),len(set(bound))),(63,63))
        groups={g['id']:g for g in p['groups']}
        self.assertEqual(groups['W026/factory/start'],next(g for g in original['groups'] if g['id']=='W026/factory/start'))
        g=groups['W027/single/end'];q=profile(g,[1,0,0],1)
        self.assertLess(q['body'].BoundBox.ZMax,65.99)
        self.assertEqual(q['recipe']['foot_sign'],-1)
        common=groups['P_REAR_TWO_EQUAL_FEEDS']
        self.assertEqual(len(common['ends']),2)
        self.assertGreater(common['available_common_straight_mm'],9)
        for n in common['normal_candidates']:profile(common,n,1)


if __name__=='__main__':unittest.main()
