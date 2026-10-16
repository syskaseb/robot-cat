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

    def test_lower_feed_and_branch_loops_are_allocated_at_distinct_levels(self):
        original=json.loads((OUT/'remaining25-interface-allocation.json').read_text())
        old={g['id']:g for g in original['groups']}
        thin=profile(old['FL_P_BRANCH3'],[0,1,0],1)
        fat=profile(old['W026/custom/end'],[-1,0,0],1)
        self.assertGreater(thin['band'].common(fat['band']).Volume,.5)
        revised,_=apply_layout(original);groups={g['id']:g for g in revised['groups']}
        for wid,leg in [('W026','FL'),('W037','FR'),('W045','RL'),('W053','RR')]:
            self.assertEqual(groups[wid+'/custom/end']['centre_world_mm'][2],26.5)
            branch=profile(groups[leg+'_P_BRANCH3'],[0,1,0],1)
            for n in groups[wid+'/custom/end']['normal_candidates']:
                incoming=profile(groups[wid+'/custom/end'],n,1)
                for a in ('body','band'):
                    for b in ('body','band'):
                        self.assertLess(branch[a].common(incoming[b]).Volume,1e-6)


if __name__=='__main__':unittest.main()
