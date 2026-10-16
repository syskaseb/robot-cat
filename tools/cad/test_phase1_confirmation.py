import unittest
from confirm_phase1_result import validate_score


class ConfirmationTests(unittest.TestCase):
    def test_fixed_counter_and_additive_result(self):
        s=dict(fixed_total=20,confirmed_result_ids=['M1','W5'],result_count=2,result_percent=10)
        self.assertEqual(validate_score(s,'K1'),['M1','W5','K1'])
        with self.assertRaises(AssertionError):validate_score(s,'E3')
        with self.assertRaises(AssertionError):validate_score(s,'W5')
        s['fixed_total']=19
        with self.assertRaises(AssertionError):validate_score(s,'K1')


if __name__=='__main__':unittest.main()
