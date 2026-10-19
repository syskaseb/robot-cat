import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
from compose_feline_shared_end_plan import station_ends,bank_end,inline_end,balance_contract,source_end


class SharedEnds(unittest.TestCase):
    def test_source_end_keeps_actual_mouth_and_full_after_arc_grip(self):
        row=dict(id='W064/single/end')
        recipe=dict(ref=row['id'],point_mm=[1,2,3],departure_axis=[1,0,0],grip_start_mm=[4,5,6],
            grip_end_mm=[4,5,15],grip_axis=[0,0,1],R_mm=25.2,first_project_mm=0,sweep_degrees=60)
        source_end(row,recipe)
        self.assertEqual(row['point_mm'],[1,2,3])
        self.assertEqual(row['jacket_grip9_mm'],[[4,5,6],[4,5,15]])
        self.assertFalse(row['full_middle_route_accepted'])
        with self.assertRaises(AssertionError):source_end(dict(id='wrong'),recipe)

    def test_station_mapping_uses_physical_end_and_wire_not_old_group_alias(self):
        rows=[dict(endpoint='G1.2',wire='W001',group='WAGO:G1_CP2',point_mm=[99,99,99])]
        models={'G1':[dict(endpoint='G1.2',wire='W001',point_mm=[1,2,3],departure_axis=[1,0,0],
            grip_start_mm=[1,2,3],grip_end_mm=[10,2,3],minimum_R_mm=12.4)]}
        self.assertEqual(station_ends(rows,models),1)
        self.assertEqual(rows[0]['point_mm'],[1,2,3])
        self.assertFalse(rows[0]['full_middle_route_accepted'])

    def test_after_bend_bank_grip_preserves_mouth(self):
        row={};recipe=dict(point_mm=[0,0,0],departure_axis=[0,-1,0],bend_unit=[1,0,0],R_mm=12.4,first_mm=9,grip_site='AFTER_BEND')
        bank_end(row,recipe)
        self.assertEqual(row['point_mm'],[0,0,0])
        self.assertEqual(row['jacket_grip9_mm'],[[12.4,-21.4,0],[21.4,-21.4,0]])

    def test_inline_accounting_never_becomes_a_jacket_or_new_connector(self):
        row=dict(point_mm=None);inline_end(row,dict(rotation_rows=[[0,-1,0],[1,0,0],[0,0,1]],centre_mm=[1,2,3]),-1)
        self.assertIsNone(row['point_mm'])
        self.assertEqual(row['jacket_routing_point_mm'],[1,-19,3])
        self.assertEqual(row['jacket_grip9_mm'][1],[1,-28,3])

    def test_balance_four_branches_are_separate_and_unknown_cavities_stay_unknown(self):
        e=dict(balance_interface=[dict(tap='BAT.B'+str(i),to='P309.'+str(i),physical_GTech_cavity=None,ID_must_not_be_used=True) for i in range(4)])
        result=balance_contract(e)
        self.assertTrue(result['not_in_existing_123_portions_or_246_ends'])
        self.assertFalse(result['physical_GTech_pinout_assigned'])
        self.assertTrue(all(r['physical_GTech_cavity'] is None for r in result['branches']))


if __name__=='__main__':unittest.main()
