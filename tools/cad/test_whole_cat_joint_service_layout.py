import unittest
from whole_cat_joint_service_layout import recipe


class JointServiceRecipe(unittest.TestCase):
    def test_coupled_aux_input_is_not_stretched(self):
        plan=recipe()
        self.assertEqual(set(plan['AUX_cell_members']),
            {'F_AUX_CP2','Access_F_AUX','P_REAR_CP2','XA01_SHORT_CP2','XA01_SHORT_STRIP_CP2'})
        self.assertTrue(plan['derivation']['XA01_rigid_translation_preserves_29mm_blank'])

    def test_all_mta_and_access_zones_allocated_before_supports(self):
        plan=recipe()
        self.assertEqual(set(plan['MTA_centres_mm']),{'FL','FR','RL','RR'})
        for gap in ['S0_key_to_left_bank_service_X_gap_mm',
                    'MTA_bottom_to_controller_top_mm','MTA_top_to_relocated_AUX_bottom_mm']:
            self.assertGreaterEqual(plan['derivation'][gap],2)
        self.assertFalse(plan['complete_harness'])
        self.assertFalse(plan['selected'])
        self.assertFalse(plan['physical_pass'])


if __name__=='__main__':unittest.main()
