import unittest
from current_rest_pose import is_rest,is_physical_reference


class CurrentRestPoseTests(unittest.TestCase):
    def test_splice_branch_identity_is_not_an_angle(self):
        for n in ('Band_RL3/Splice/1/0/0','Root/FrontLeftHipExtension/2/0','Source/FrontLeftHipExtension/body/0','chosen/FL1/0'):
            self.assertTrue(is_rest(n),n)
        for n in ('Band_RL3/Splice/1/-15/0','Band_RL3/Splice/0/0/15','Root/FrontLeftHipExtension/2/-15','Source/FrontLeftHipExtension/body/15','chosen/FL1/-15'):
            self.assertFalse(is_rest(n),n)
    def test_access_tools_are_not_installed_material(self):
        for n in ('ServiceATO/F_L1','ServiceJaw/F_R1/1','RailHoleKeepout0','RailNutTrapKeepout1','RailDriverKeepout0'):
            self.assertFalse(is_physical_reference(n))
        self.assertTrue(is_physical_reference('SourceCaseAdhesive/MTACase_FL'))
    def test_explicit_head_and_independent_leg_axes(self):
        for n in ('head/0/0/Head','headref/0/Interface','headwire/0/W','factory/0','P0_Part_34/0/0/0','leg/FL1/0/0'):
            self.assertTrue(is_rest(n),n)
        for n in ('head/15/0/Head','head/0/5/Head','headref/-15/Interface','P0_Part_34/0/-15/0','leg/FL1/15/0'):
            self.assertFalse(is_rest(n),n)

    def test_numeric_part_id_is_not_a_motion_angle(self):
        for n in ('RailM3_0/Screw','SourceCase/MTACase_FL','CurrentSaddleBand/W041/custom/start','Physical/34','Other/35/36'):
            self.assertTrue(is_rest(n),n)


if __name__=='__main__':unittest.main()
