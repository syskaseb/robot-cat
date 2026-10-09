"""Current family and narrow nominal gap; delivered fit remains OPEN."""
import unittest
import test_open_prototype_source_south_ato as Base
import open_prototype_source_low_gap as G

class LowGap(Base.SouthAto):
    @classmethod
    def setUpClass(cls):cls.p=G.build_geometry();cls.old=G.G.T.build()

    def test_only_one_profile_changes_six_other_proofs_not_rerun(self):
        old=G.Prior.build()
        for key in ('stations','mta','holders','tails','s1_module','permutation','ports','body_ends'):
            self.assertEqual(self.p[key],old[key],key)
        self.assertEqual([r for r in self.p['s1_routes'] if r['wire']!='W068'],
                         [r for r in old['s1_routes'] if r['wire']!='W068'])
        self.assertEqual(self.p['changed_path_names'],['W068'])
        self.assertEqual(len(self.p['six_unchanged_radius_profiles_reused']['profiles']),6)
        gap=self.p['low_tube_corridor']
        self.assertAlmostEqual(gap['centre_level_mm'],63.25)
        self.assertAlmostEqual(gap['nominal_each_side_gap_mm'],.15)
        self.assertTrue(gap['delivered_fit_not_qualified'])
        self.assertTrue(gap['no_grip_in_narrow_corridor'])

if __name__=='__main__':unittest.main()
