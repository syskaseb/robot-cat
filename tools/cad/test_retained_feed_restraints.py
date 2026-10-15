import unittest
from prepare_retained_feed_restraints import prepare,straight_at

class FeedBindingTest(unittest.TestCase):
    def test_all_ten_actual_occupied_ends_have_existing_land(self):
        result=prepare();self.assertFalse(result['missing']);self.assertEqual(len(result['restraints']),10)
        self.assertEqual(len({(r['group'],r['wire']) for r in result['restraints']}),10)
        self.assertEqual(result['quantities']['lacing_nominal_total_mm'],1500)
        self.assertFalse(result['selected']);self.assertFalse(result['W5_complete'])
    def test_wrong_direction_or_short_real_land_rejected(self):
        segments=[dict(parts=[dict(kind='line',start=[0,0,0],end=[0,0,9])])]
        self.assertIsNotNone(straight_at([0,0,0],[0,0,1],segments))
        self.assertIsNone(straight_at([0,0,0],[0,1,0],segments))
        segments[0]['parts'][0]['end']=[0,0,8]
        self.assertIsNone(straight_at([0,0,0],[0,0,1],segments))

if __name__=='__main__':unittest.main()
