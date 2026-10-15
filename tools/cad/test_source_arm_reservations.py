import unittest
import FreeCAD as A
import Part
from source_arm_reservations import Reservations


class SourceReservationsTests(unittest.TestCase):
    def make(self,targets,wires):
        return Reservations(targets,wires,{}, {},{},[],
            dict(name='Support',code=None,moving=False,arm_half_widths_world_mm=[2,2,2]),
            [-20,-20,-20],[30,20,20],{}, {})

    def test_tangent_face_is_not_positive_material_overlap(self):
        q=self.make({'Foreign':Part.makeBox(10,10,10,A.Vector(5,-5,-5))},{})
        self.assertTrue(q.clear([0,0,0]))
        self.assertTrue(q.clear([3,0,0]))
        self.assertFalse(q.clear([3.1,0,0]))

    def test_wire_radius_and_sampling_inflation_reject_only_planning(self):
        q=self.make({}, {'Wire':(Part.makeLine(A.Vector(-10,0,0),A.Vector(10,0,0)),1)})
        self.assertTrue(q.clear([0,4,0]))
        self.assertFalse(q.clear([0,3,0]))


if __name__=='__main__':unittest.main()
