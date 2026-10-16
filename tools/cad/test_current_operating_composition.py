import unittest
from compose_current_operating_native import compose


class OperatingCompositionTests(unittest.TestCase):
    def test_replacements_are_not_extra_frames_and_rail_lacing_is_not_doubled(self):
        names=['UpperCarrier001','FrontLeftFixedCarrier','FrontRightFixedCarrier','RearLeftFixedCarrier','RearRightFixedCarrier','LeftRiser']+['CAP'+str(i) for i in range(7)]
        old=dict(prints=[dict(part=n,path=n+'.old') for n in names],native_current_candidate_lacing_blanks=61)
        changed=['UpperCarrier001','SourceGripRail','FrontRightFixedCarrier','RearLeftFixedCarrier','RearRightFixedCarrier']
        native=dict(status='FIVE_OPERATING_NATIVE_PRINT_REPLACEMENTS_COMPLETE',parts=[dict(part=n,object=n,native='native',relocated_reopen=True,parameter_restore_mm=[0,.2,0]) for n in changed],
            exports=[dict(part=n,path=n+'.new',sha256='test',printing={'fits_with_5mm_brim':True}) for n in changed])
        prints,lace=compose(old,native)
        self.assertEqual(len(prints),14);self.assertEqual(lace['current_candidate_blanks'],85)
        self.assertEqual(next(r for r in prints if r['part']=='FrontLeftFixedCarrier')['path'],'FrontLeftFixedCarrier.old')


if __name__=='__main__':unittest.main()
