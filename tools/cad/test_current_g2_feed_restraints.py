import unittest
import FreeCAD as A
import Part
from current_g2_feed_restraints import geometry


class G2FeedTests(unittest.TestCase):
    def test_four_actual_mouths_and_independent_small_wire(self):
        g=geometry()
        self.assertEqual(g['Heavy3']['recipe']['wires'],['W061','W062','W063'])
        self.assertEqual(g['BUS_G']['recipe']['wires'],['W003'])
        for y,r in [(34.5,2.1),(39.25,2.1),(44,2.1),(48.75,1)]:
            wire=Part.makeCylinder(r,9,A.Vector(101.5,y,155),A.Vector(1,0,0))
            for q in g.values():
                for k in ('body','band'):self.assertLess(q[k].common(wire).Volume,1e-6)

    def test_bands_and_existing_floor_do_not_intersect(self):
        g=geometry()
        floor=Part.makeBox(35.5,30,3,A.Vector(82.5,29,145.01))
        for q in g.values():
            self.assertLess(q['band'].common(floor).Volume,1e-6)
            self.assertGreater(q['body'].common(floor).Volume,0)
        for a in g['Heavy3'].values():
            if not hasattr(a,'common'):continue
            for b in (g['BUS_G']['body'],g['BUS_G']['band']):
                self.assertLess(a.common(b).Volume,1e-6)


if __name__=='__main__':unittest.main()
