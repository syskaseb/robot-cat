import unittest
import FreeCAD as A
import Part
from feline_source_restraint_plan import box,joined
from plan_feline_f0_u1_shared_bypass import construct


class SharedLoadBypass(unittest.TestCase):
    def fixture(self):
        old=joined([box([0,69,0],[2,71,32.75]),box([0,59,30.75],[2,71,32.75]),box([-5,5,0],[2,71,2])])
        post=box([0,59,30],[2,60,32.52])
        case=box([-10,-1,-1],[-8,1,1])
        return old,post,case

    def test_bypass_preserves_section_and_original_material_joint(self):
        old,post,case=self.fixture();volume=old.Volume
        obstacle=box([0,69,20],[5,71,25])
        new,proof=construct(old,post,case,{'obstacle':obstacle},{})
        self.assertAlmostEqual(old.Volume,volume)
        self.assertEqual(len(new.Solids),1)
        self.assertEqual(proof['unchanged_cross_section_mm'],[2,2])
        self.assertAlmostEqual(new.common(post).Volume,old.common(post).Volume)
        self.assertGreaterEqual(new.distToShape(obstacle)[0],1.25-1e-6)
        self.assertFalse(proof['N01_complete'])

    def test_typed_curve_is_not_treated_as_a_zero_thickness_obstacle(self):
        old,post,case=self.fixture()
        curve=Part.makeLine(A.Vector(0,70,20),A.Vector(5,70,20))
        new,proof=construct(old,post,case,{'wire':curve},{'wire':dict(nominal_profile_radius_mm=1.)})
        self.assertAlmostEqual(proof['bypass_column_X_mm'][0],7.25)


if __name__=='__main__':unittest.main()
