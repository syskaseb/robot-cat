"""Reuse common family contracts and verify the new complete ATO level."""
import unittest
import open_prototype_source_ato_level as G
from test_open_prototype_rear_face import RearFace

class AtoLevel(RearFace):
    @classmethod
    def setUpClass(cls):cls.p=G.build_geometry();cls.old=G.G.T.build()

    def test_ato_level_and_unchanged_terminal_geometry(self):
        a=self.p['rear_level_allocation']
        self.assertAlmostEqual(a['entry_level_mm'],144.8+2.1+.1)
        self.assertEqual(self.p['s1_module'],G.B.read(G.PRIOR_PLAN)['family']['s1_module'])
        self.assertFalse(self.p['s1_geometry_changed'])
        self.assertEqual(self.p['reused_ring_case_proof']['producer_snapshot'],'a97c50e')
        self.assertEqual(self.p['changed_case_names'],['P_REAR'])
        self.assertEqual(set(self.p['changed_path_names']),{'W064','W065','W067','W068','W044','W052','F_AUX/input'})

if __name__=='__main__':unittest.main()
