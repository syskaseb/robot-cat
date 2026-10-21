import tempfile
import unittest
import hashlib
import numpy as np
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import FreeCAD as A
import Part
import receive_feline_jpwm_whole_pose as receiver


class FirstStaticHold(unittest.TestCase):
    def check(self,fixed,own=None,mates=()):
        with tempfile.TemporaryDirectory() as temp, patch.object(receiver,'OUT',Path(temp)):
            return receiver.screen_rear_gallery(
                SimpleNamespace(bus={'name':'not-present'}),fixed,
                {n:dict(kind='PETG') for n in ('actor',*fixed)},
                {'actor':Part.makeBox(1,1,1)}, {'actor':'changed'}, {}, {},
                own_clearances=own,own_face_mates=mates,fail_fast=True)

    def test_named_zero_does_not_accept_volume_overlap(self):
        result=self.check({'seat':Part.makeBox(1,1,1,A.Vector(.5,0,0))},
                          {('actor','seat'):0.})
        self.assertEqual(result['status'],'JPWM_REAR_GALLERY_WHOLE16_STATIC_HOLD_PARTIAL')
        self.assertGreater(result['checks']['actor|seat']['common_mm3'],0)
        self.assertTrue(result['remaining_pairs_NOT_received'])

    def test_named_own_gap_does_not_relax_foreign_part(self):
        result=self.check({'seat':Part.makeBox(1,1,1,A.Vector(1.15,0,0)),
                           'foreign':Part.makeBox(1,1,1,A.Vector(0,1.5,0))},
                          {('actor','seat'):0.})
        # The positive own gap can be received by the exact box lower bound
        # before a narrow-phase query; it must not appear as a failed pair.
        self.assertNotIn('actor|seat',result['failures'])
        self.assertEqual(result['failures'],['actor|foreign'])
        self.assertEqual(result['checks']['actor|foreign']['minimum_mm'],1.25)

    def test_exact_named_face_is_received_before_foreign_hold(self):
        result=self.check({'prefix':Part.makeBox(1,1,1,A.Vector(1,0,0)),
                           'foreign':Part.makeBox(1,1,1,A.Vector(0,1.5,0))},
                          mates=(('actor','prefix'),))
        self.assertTrue(result['checks']['actor|prefix']['ok'])
        self.assertEqual(result['failures'],['actor|foreign'])


class CurrentCurveMotionBound(unittest.TestCase):
    def setup_scene(self,inside=False):
        body=Part.makeBox(40,40,40,A.Vector(-20,-20,-20)) if inside else Part.makeBox(2,2,2,A.Vector(-1,-1,-1))
        actor=Part.makeTorus(10,.5)
        curve=Part.Wire([Part.makeCircle(10)])
        b=body.BoundBox
        motions=[dict(name='body',pose=i,r=np.eye(3),t=np.zeros(3),
                      bounds=[[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]]) for i in range(36)]
        digest=hashlib.sha256(actor.exportBrepToString().encode()).hexdigest()
        return SimpleNamespace(motion=motions,rest={'body':body}),{'wire':actor},{'wire':(curve,.5,digest)}

    def test_sufficient_actual_curve_bound_receives_all36_without_tube_queries(self):
        from feline_fore_power_pair import SolidQueries
        world,actors,profiles=self.setup_scene()
        with tempfile.TemporaryDirectory() as temp, patch.object(receiver,'OUT',Path(temp)), patch.object(SolidQueries,'distance',side_effect=AssertionError('unnecessary tube query')):
            result=receiver.receive_sampled_motion(world,actors,'motion',{},curve_profiles=profiles)
        self.assertEqual(len(result['checks']),36)
        self.assertTrue(all(r['ok'] for r in result['checks'].values()))

    def test_curve_inside_material_still_requires_actual_solid_query(self):
        from feline_fore_power_pair import SolidQueries
        world,actors,profiles=self.setup_scene(inside=True)
        with tempfile.TemporaryDirectory() as temp, patch.object(receiver,'OUT',Path(temp)), patch.object(SolidQueries,'distance',return_value=0.) as actual:
            result=receiver.receive_sampled_motion(world,actors,'motion',{},curve_profiles=profiles)
        actual.assert_called_once()
        self.assertFalse(next(iter(result['checks'].values()))['ok'])

    def test_profile_cannot_be_attached_to_changed_actor(self):
        world,actors,profiles=self.setup_scene()
        actors['wire'].translate(A.Vector(1,0,0))
        with self.assertRaises(AssertionError):
            receiver.receive_sampled_motion(world,actors,'unused',{},curve_profiles=profiles)


if __name__=='__main__':unittest.main()
