"""No world rebuild: verify current source identity, full9 and saved shapes."""
import json,math,unittest,tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import numpy as np
import FreeCAD as A
import Part
from plan_feline_layout import OUT
from feline_source_saddles import segment
from receive_feline_rrp_shared_height import load


class EarlyU1PairTests(unittest.TestCase):
    def test_motion_label_requires_all36_poses_and_body_is_checked_first(self):
        import receive_feline_jpwm_whole_pose as receiver
        body=Part.makeBox(2,2,2,A.Vector(-1,-1,-1))
        poses=[dict(name='leg',pose=i,bounds=[[-1,-1,-1],[1,1,1]],r=np.eye(3),t=[0,0,0]) for i in range(36)]
        actors={'JPWMSource:wire':Part.makeBox(1,1,1,A.Vector(10,10,10)),'Ref_Material_JPWM_0_0':body}
        world=SimpleNamespace(motion=poses,rest={'leg':body.copy()})
        with tempfile.TemporaryDirectory(prefix='codex-u1-motion-test-') as folder:
            with patch.object(receiver,'OUT',Path(folder)):
                result=receiver.receive_sampled_motion(world,actors,'test',{})
                self.assertEqual(len(result['checks']),1)
                self.assertTrue(next(iter(result['checks'])).startswith('Ref_Material_JPWM_0_0|'))
                world.motion=poses[:1]
                with self.assertRaisesRegex(AssertionError,'36 distinct'):
                    receiver.receive_sampled_motion(world,actors,'missing',{})

    def test_preserves_bare_pads_and_full_curved_grip(self):
        old=json.loads((OUT/'n01-U1-frontband-common-plan.json').read_text())
        new=json.loads((OUT/'n01-U1-early-pair.json').read_text())
        self.assertEqual(new['status'],'U1_EARLY_PAIR_STATIC36_RECEIVED_FULL123_OPEN')
        self.assertFalse(new['failures']);self.assertFalse(new['N01_complete'])
        self.assertGreater(new['stand1_overlap_mm3'],1)
        for eid,spec in new['specs'].items():
            for k in ('bare_parts','pad_world_mm','selected_carrier_pad_identity','bare_radius_mm'):
                self.assertEqual(spec[k],old['specs'][eid][k])
            edges=[segment(r) for r in spec['parts']];end=new['updates'][eid]
            self.assertAlmostEqual(sum(e.Length for e in edges),end['source_prefix_length_mm'])
            a,b=end['full_grip_arclength_mm'];self.assertAlmostEqual(b-a,9)
            self.assertAlmostEqual(edges[-1].Curve.Radius,12.4)
            self.assertEqual(end['routing_exit_axis'],[0,1,0])
            self.assertLess((edges[-1].valueAt(edges[-1].LastParameter)-A.Vector(*end['routing_exit_mm'])).Length,1e-6)
            self.assertLess((edges[0].valueAt(edges[0].FirstParameter)-A.Vector(*old['specs'][eid]['parts'][0]['start'])).Length,1e-6)
            self.assertTrue(end['grip_is_curved_not_straight_chord'])
        actors=load(new);self.assertEqual(len(actors),5)
        self.assertTrue(all(s.isValid() and len(s.Solids)==1 for s in actors.values()))
        nylon=actors['U1Relief:E2pair:band'].fuse(actors['U1Relief:E2pair:head'])
        self.assertTrue(nylon.isValid());self.assertEqual(len(nylon.Solids),1)
        self.assertAlmostEqual(actors['U1Relief:E2pair:head'].Volume,5*5.3*4.3)


if __name__=='__main__':unittest.main()
