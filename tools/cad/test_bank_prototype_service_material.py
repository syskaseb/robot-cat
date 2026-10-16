import json,unittest
import FreeCAD as A
import Part
from bank_prototype_service_material import material
from plan_current_harness_interfaces import OUT


class ServiceMaterialTests(unittest.TestCase):
    def test_park_transform_is_bound_to_actual_rail_and_source_points(self):
        plan=json.loads((OUT/'bank-prototype-service-plan.json').read_text());q=material(plan)
        self.assertAlmostEqual(q['parking_cup_floor_z_mm'],plan['removable_rail']['parked_tab_floor_z_mm'])
        for wire,port in plan['removable_rail']['occupied_ports'].items():
            if wire=='W043':continue
            p=q['pose'].multVec(A.Vector(*plan['P_SYS']['ports'][port]))
            expected=plan['removable_rail']['parking_transform']['resulting_free_end_points_mm'][wire]
            self.assertAlmostEqual(p.y,expected[1]);self.assertAlmostEqual(p.z,expected[2])
        for name,s in q['parts'].items():self.assertEqual(len(s.Solids),1,name)


if __name__=='__main__':unittest.main()
