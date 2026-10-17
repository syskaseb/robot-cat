"""Nominal-frame regression tests; not physical connector/pinout approval."""
import json
import unittest
import numpy as np
from plan_feline_endpoints import source_port_frames,transfer_port,owner
from plan_feline_layout import OUT


class PortFrames(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan=json.loads((OUT/'module-layout.json').read_text())
        cls.frames=source_port_frames(cls.plan)

    def test_twelve_nominal_frames_have_equal_size(self):
        self.assertEqual(len(self.frames),12)
        for f in self.frames.values():
            old=np.array(f['source_nominal_bounds_mm']);new=np.array(f['snapshot_bounds_mm'])
            np.testing.assert_allclose(old[1]-old[0],new[1]-new[0],atol=.03)

    def test_every_station_port_transfers_to_own_case_face(self):
        groups={g['role']:g for g in self.plan['groups']}
        for group,f in self.frames.items():
            for port,p in f['ports'].items():
                logical=next(k for k,v in f['logical_to_physical_common_rail_cavity'].items() if k==port)
                role=group.split(':')[1]+'.'+logical
                _,q,d=transfer_port(self.plan,role,p,f['nominal_outward_axis'],self.frames)
                lo,hi=np.array(groups[group]['candidate_bounds_mm'])
                self.assertLess(np.linalg.norm(np.maximum(np.maximum(lo-q,q-hi),0)),.03,role)
                self.assertAlmostEqual(np.linalg.norm(d),1,places=6)

    def test_front_station_historical_translation_is_not_silently_lost(self):
        f=self.frames['WAGO:FL_P']
        np.testing.assert_allclose(f['nominal_to_snapshot_translation_mm'],[100,-5,0],atol=.01)
        _,q,_=transfer_port(self.plan,'FL_P.1',[-69.5,80,19.5],[0,0,1],self.frames)
        self.assertLess(abs(q[0]),110)

    def test_battery_body_role_is_not_pack_factory_lead(self):
        self.assertEqual(owner('BAT.plus',{g['role']:g for g in self.plan['groups']}),'XT60')

    def test_stale_world_point_cannot_override_registered_nominal_cavity(self):
        f=self.frames['WAGO:D_RL'];role='D_RL.2'
        _,correct,d=transfer_port(self.plan,role,f['ports']['2'],[0,0,1],self.frames)
        _,stale,d2=transfer_port(self.plan,role,[999,999,999],[1,0,0],self.frames)
        np.testing.assert_allclose(stale,correct)
        np.testing.assert_allclose(d,d2)

    def test_neck_torso_union_has_no_artificial_margin_gap(self):
        from plan_feline_interior import inside_shared
        points=np.array([[x,22.5,53] for x in np.linspace(-175,-125,101)])
        self.assertTrue(inside_shared(points,4.1).all())


if __name__=='__main__':unittest.main()
