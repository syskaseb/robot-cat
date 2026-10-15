import unittest
import FreeCAD as A
import Part
from current_fl_ground_feed import geometry


class FLGroundFeedTests(unittest.TestCase):
    def test_root_and_independent_nominal_jacket(self):
        g=geometry()
        self.assertEqual(g['recipe']['end'],'FL_G')
        self.assertEqual(g['recipe']['parent'],'FrontLeftFixedCarrier')
        wire=Part.makeCylinder(2.1,9,A.Vector(-139.5,84,112.5))
        for k in ('body','band'):self.assertLess(g[k].common(wire).Volume,1e-6)
        self.assertEqual(len(g['body'].Solids),1)
        self.assertLess(g['body'].common(g['band']).Volume,1e-6)


if __name__=='__main__':unittest.main()
