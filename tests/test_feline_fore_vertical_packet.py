import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
from plan_feline_fore_vertical_packet import fore_datum


class ForeDatum(unittest.TestCase):
    def test_whole_case_and_whole_grip_margins_not_just_wire(self):
        x,y,z=fore_datum(-113.15,14,-48)
        self.assertAlmostEqual(-113.15-(x+10.125),1.75)
        self.assertAlmostEqual((y-11)-14,2.25)
        lowest=z-25.5-9-6-3.55
        self.assertAlmostEqual(lowest-(-48),4.25)
        self.assertGreater(z-25.5-9-6-2.4,-48+3.25)

    def test_datum_translates_with_actual_source_constraints(self):
        a=fore_datum(-113.15,14,-48);b=fore_datum(-103.15,19,-45)
        self.assertEqual([round(y-x,8) for x,y in zip(a,b)],[10,5,3])


if __name__=='__main__':unittest.main()
