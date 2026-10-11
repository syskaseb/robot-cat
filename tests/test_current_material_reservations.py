import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
from current_material_reservations import FaceKeepouts,terminal_owners
from plan_current_mta_interfaces import line


class SavedSurfaceReservations(unittest.TestCase):
    def test_only_actual_owned_fuse_contact_gets_mating_exemption(self):
        self.assertEqual(terminal_owners('F_FL3'),('F_L3_CP2_OUT',))
        self.assertEqual(terminal_owners('F_RL2'),('F_L5_CP2_OUT',))
        self.assertEqual(terminal_owners('F_RR3'),('F_R6_CP2_OUT',))
        mouth=[line([0,0,0],[0,0,10])]
        q=FaceKeepouts([dict(owner='F_L3_CP2_OUT',bounds_mm=[-1,-1,0,1,1,0])])
        self.assertIsNone(q.hit(mouth,1,terminal_owners('F_FL3'),3))
        q=FaceKeepouts([dict(owner='F_L3_CP2_Housing',bounds_mm=[-1,-1,0,1,1,0])])
        self.assertIsNotNone(q.hit(mouth,1,terminal_owners('F_FL3'),3))
        q=FaceKeepouts([dict(owner='F_L3_CP2_OUT',bounds_mm=[-1,-1,7,1,1,7])])
        self.assertIsNotNone(q.hit(mouth,1,terminal_owners('F_FL3'),3))

    def test_face_keepout_is_explicitly_not_material_proof(self):
        q=FaceKeepouts([dict(owner='plate',bounds_mm=[0,0,0,10,10,0])])
        hit=q.hit([line([1,1,.5],[9,1,.5])],1)
        self.assertTrue(hit['conservative_reservation_only'])
        self.assertFalse(hit['actual_material_collision_proved'])

    def test_open_interior_is_not_filled_by_whole_part_box(self):
        q=FaceKeepouts([dict(owner='left',bounds_mm=[0,0,0,0,20,20]),
                       dict(owner='right',bounds_mm=[20,0,0,20,20,20])])
        self.assertIsNone(q.hit([line([10,5,10],[10,15,10])],3))

    def test_grid_padding_includes_thick_cable_near_cell_boundary(self):
        q=FaceKeepouts([dict(owner='plate',bounds_mm=[11,0,0,11,10,10])])
        self.assertIsNotNone(q.hit([line([13,2,2],[13,8,2])],2.1))
        self.assertIsNone(q.hit([line([13,2,2],[13,8,2])],1))


if __name__=='__main__':unittest.main()
