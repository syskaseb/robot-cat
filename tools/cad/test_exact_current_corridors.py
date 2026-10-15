import unittest
import FreeCAD as A
import Part
from exact_current_corridors import ExactOracle,route
from plan_current_mta_interfaces import line

class FakeOracle:
    def __init__(self,allowed):self.allowed=allowed;self.checks=0;self.blockers={}
    def clear(self,part,row):self.checks+=1;return self.allowed

class ExactRoutingTests(unittest.TestCase):
    def test_fast_wire_rejection_preserves_exact_threshold(self):
        row=dict(wire='test',loom='FL1',core='D')
        for separation,allowed in ((2.2,False),(2.3,True)):
            other=Part.makeLine(A.Vector(0,separation,0),A.Vector(10,separation,0))
            oracle=ExactOracle({}, {'other':(other,1)})
            self.assertEqual(oracle.clear(line([0,0,0],[10,0,0]),row),allowed)

    def test_actual_bore_is_not_rejected_by_its_box(self):
        body=Part.makeBox(10,10,10).cut(Part.makeCylinder(2,10,A.Vector(0,5,5),A.Vector(1,0,0)))
        oracle=ExactOracle({'parent':body},{})
        row=dict(wire='test',loom='FL1',core='D')
        self.assertTrue(oracle.clear(line([0,5,5],[10,5,5]),row))
        self.assertFalse(oracle.clear(line([-5,1,5],[15,1,5]),row))

    def test_bounded_graph_reports_exhaustion_not_impossibility(self):
        row=dict(wire='test',source_land=line([0,0,0],[0,0,5]),free_start=[0,0,5],free_end=[60,0,60],
                 receiving_parts=[line([60,0,60],[69,0,60])],bodyward_bundle_tangent=[0,0,1],
                 receiver_outward_axis=[-1,0,0],capacity_before_terminal_mm=400,terminal_allowance_project_mm=11)
        q,error=route(FakeOracle(False),row,max_seconds=2,max_states=10)
        self.assertIsNone(q);self.assertIn('NOT_GEOMETRIC_IMPOSSIBILITY',error['reason'])
        q,error=route(FakeOracle(True),row,max_seconds=2,max_states=10)
        self.assertIsNone(error);self.assertGreater(q['spare_before_trim_mm'],0)
        self.assertGreaterEqual(q['minimum_sampled_R_mm'],10)

if __name__=='__main__':unittest.main()
