import json,unittest
from plan_axial_source_supports import P,C,arm_box,port_arm_halves


class SourceArmEntries(unittest.TestCase):
    def test_all_eight_world_profiles_match_port_frame_and_clear_own_wire(self):
        plan=json.loads((P.OUT/'body-axial-layout-chosen.json').read_text())
        for row in plan['hips']:
            pose=next(p for p in row['poses'] if p['angle']==0)
            wire=P.wire(pose['parts']+row['source_parts'])
            for moving in (False,True):
                _,port=C.make_port(row,moving);goal=port['arrival_world_mm']
                half=port_arm_halves(port['recipe']);seed=arm_box(goal,goal,half)
                self.assertAlmostEqual(seed.Volume,96,places=5)
                self.assertLess(seed.common(port['band']).Volume,1e-6)
                self.assertGreater(seed.common(port['body']).Volume,1)
                self.assertGreaterEqual(seed.distToShape(wire)[0],3.25-1e-6,(row['loom'],moving,half))


if __name__=='__main__':unittest.main()
