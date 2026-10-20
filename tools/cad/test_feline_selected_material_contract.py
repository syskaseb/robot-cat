import unittest
from feline_selected_material_contract import load
from plan_feline_inward_output_joints import return_loop


class SelectedMaterial(unittest.TestCase):
    def test_composite_helu_role_keeps_selected_bend(self):
        r,_,_=load()
        for w in ('W026','W037','W045','W053'):
            self.assertGreaterEqual(r['portions'][w+'/custom']['minimum_project_R_mm'],25.2)
            self.assertGreaterEqual(r['portions'][w+'/custom']['project_radius_mm'],2.1-1e-6)

    def test_existing_fixed_logic_not_promoted_to_power_profile(self):
        r,_,_=load()
        self.assertEqual(r['portions']['XS11/extra']['project_radius_mm'],.4)
        self.assertEqual(r['portions']['XS11/extra']['minimum_project_R_mm'],.5)

    def test_whole_return_loop_keeps_both_full_lands_and_length(self):
        rows=return_loop([-57.5,15,-34],[-1,0,0],[-92.75,45,-34])
        self.assertGreaterEqual(rows[0]['length_mm'],9.25)
        self.assertGreaterEqual(rows[-1]['length_mm'],9.25)
        self.assertLessEqual(sum(r['length_mm'] for r in rows),100)


if __name__=='__main__':unittest.main()
