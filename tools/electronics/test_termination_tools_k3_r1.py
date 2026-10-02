import unittest
import termination_tools_k3_r1 as T

class ToolMatrixTests(unittest.TestCase):
    def setUp(self):self.v=T.matrix()
    def test_unique_tools(self):self.assertEqual(len({x['sku'] for x in self.v['tools']}),4)
    def test_one_PIDG_pair(self):self.assertEqual([p['tool'] for p in self.v['processes'][2:]],['58433-3']*2)
    def test_no_duplicate_included_die(self):self.assertNotIn('58423-1',[x['sku'] for x in self.v['tools']])
    def test_AWG12_area(self):self.assertTrue(T.within_table(3.31,6500))
    def test_4mm2_not_AWG12(self):self.assertFalse(T.within_table(4,6500))
    def test_AWG22_not_measured700(self):self.assertFalse(T.within_table(.326,700))
    def test_crimp_counts(self):self.assertEqual([p['ends'] for p in self.v['processes']],[12,12,4,2])
    def test_stripping_roles(self):self.assertEqual(self.v['processes'][1]['strip_single_mm'],[6.76,7.52])
    def test_no_completion_claim(self):self.assertFalse(self.v['K3_complete']);self.assertFalse(self.v['physical_pass'])
    def test_factory_leads_not_manual(self):self.assertEqual(len(self.v['not_manually_crimped']),2)

if __name__=='__main__':unittest.main()
