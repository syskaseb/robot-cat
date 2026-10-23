import json,unittest
import FreeCAD as A
import Part
from check_feline_service_translation import sweep_convex_case
from plan_feline_layout import OUT


class ContinuousService(unittest.TestCase):
    def test_box_translation_volume(self):
        shape=Part.makeBox(22,37,11)
        sweep=sweep_convex_case(shape,(0,0,70))
        self.assertAlmostEqual(sweep.Volume,22*37*81,places=5)
        self.assertAlmostEqual(sweep.common(shape).Volume,shape.Volume,places=5)
        end=shape.copy();end.translate(A.Vector(0,0,70))
        self.assertAlmostEqual(sweep.common(end).Volume,end.Volume,places=5)

    def test_conditional_is_not_received_service(self):
        result=json.loads((OUT/'n01-FPI-conditional-three-phase-service.json').read_text())
        self.assertEqual(len(result['checks']),37)
        self.assertTrue(all(v['ok'] for v in result['checks'].values()))
        self.assertFalse(result['errors'])
        self.assertIn('Print_P0_BATTERY_CARRIER_R4',result['removed_parts_assumed_not_qualified'])
        self.assertNotIn('Print_P0_BATTERY_PLATE_R4',result['removed_parts_assumed_not_qualified'])
        self.assertFalse(result['complete_service_received'])
        self.assertFalse(result['N01_complete'])

    def test_prerequisites_not_silently_waived(self):
        result=json.loads((OUT/'n01-FPI-service-sequence-prerequisite-holds.json').read_text())
        for key in ('P_SYS_up','P_SYS_inward'):
            self.assertTrue(result[key]['failures'])
            self.assertFalse(result[key]['errors'])
        self.assertTrue(result['normal_scene_unchanged'])
        self.assertFalse(result['N01_complete'])


if __name__=='__main__':unittest.main()
