"""Common pad constructor guards, not integrated layout acceptance."""
import unittest,math
import numpy as np
import FreeCAD as A
import Part
from feline_shared_pi_carrier import saddle


class CommonPad(unittest.TestCase):
    def check_pad(self,starts,t,r):
        pad,kit,proof=saddle([(q,t) for q in starts],r)
        self.assertEqual(len(proof['per_wire_full9_mm']),len(starts))
        for q in starts:
            wire=Part.makeCylinder(r,9,A.Vector(*q),A.Vector(*t))
            self.assertLess(pad.common(wire).Volume,1e-5)
            self.assertGreaterEqual(pad.distToShape(wire)[0],.149)
            for s in kit.values():self.assertLess(s.common(wire).Volume,1e-5)
        self.assertTrue(pad.isValid());self.assertEqual(len(pad.Solids),1)
        self.assertAlmostEqual(kit['head'].Volume,5*4.3*5.3,places=5)
        return pad,kit

    def test_two_power_channels_on_existing_parallel_straights(self):
        self.check_pad([[112.4,62.5181,101.6],[108.9,62.5181,101.6]],[0,1,0],1.55)

    def test_four_signal_channels_with_one_common_axis_station(self):
        t=np.array([math.sqrt(.5),math.sqrt(.5),0]);u=np.array([-t[1],t[0],0])
        starts=[np.array([19.061,-1.611,75.7])+u*d for d in (0,-1.796,-3.592,-7.184)]
        pad,kit=self.check_pad(starts,t,.7)
        self.assertLess(kit['head'].BoundBox.ZMax,85)


if __name__=='__main__':unittest.main()
