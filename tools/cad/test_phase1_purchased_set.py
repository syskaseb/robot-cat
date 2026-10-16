import unittest
from bind_phase1_purchased_set import matches


class CommercialMatching(unittest.TestCase):
    def test_washer_not_equivalent_by_thread(self):
        r={'dimensions_mm':dict(ID=2.2,OD=4.5,t=.3)}
        self.assertTrue(matches('M2 washer OD4.5',r))
        self.assertFalse(matches('M2 washer OD4.3',r))
        self.assertFalse(matches('M2 washer OD5',r))

    def test_screw_length_not_nearest_length(self):
        r={'dimensions_mm':dict(d=3,L=45)}
        self.assertTrue(matches('M3x45',r));self.assertFalse(matches('M3x50',r))

    def test_nut_not_screw(self):
        r={'dimensions_mm':dict(d=2.5,AF=5,H=2)}
        self.assertTrue(matches('M2.5 nut',r));self.assertFalse(matches('M2 nut',r))


if __name__=='__main__':unittest.main()
