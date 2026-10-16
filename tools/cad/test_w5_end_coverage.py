import unittest
from compose_w5_end_coverage import exact_cover


class EndCoverageTests(unittest.TestCase):
    def test_missing_end_is_not_hidden_by_same_count(self):
        with self.assertRaises(AssertionError):exact_cover(['A','B'],[{'id':'A'},{'id':'C'}])
    def test_duplicate_end_is_rejected(self):
        with self.assertRaises(AssertionError):exact_cover(['A','B'],[{'id':'A'},{'id':'A'}])
    def test_complete_ids(self):exact_cover(['A','B'],[{'id':'B'},{'id':'A'}])


if __name__=='__main__':unittest.main()
