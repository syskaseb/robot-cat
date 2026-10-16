import unittest
from confirm_phase1_result import validate_score


class Refresh(unittest.TestCase):
    def test_refresh_does_not_award_another_point(self):
        s=dict(fixed_total=20,confirmed_result_ids=['M1','K1'],result_count=2,result_percent=10)
        self.assertEqual(validate_score(s,'K1',True),s['confirmed_result_ids'])
        with self.assertRaises(AssertionError):validate_score(s,'K2',True)
        with self.assertRaises(AssertionError):validate_score(s,'E3',True)


if __name__=='__main__':unittest.main()
