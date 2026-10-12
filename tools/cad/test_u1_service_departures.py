import copy,unittest
from unittest.mock import patch
import plan_u1_service_departures as D
import check_u1_service_departures as C


class ServiceDepartureTests(unittest.TestCase):
    def test_only_two_superseded_wire_hits_may_be_inherited(self):
        g=dict(pairs=30,reused_prior_pairs=372,errors=[],reservation_resolutions=[],
               contacts=[dict(b='XL01'),dict(b='XL09'),dict(b='XL01')],source_sha256={})
        C.inherited_gate(g)
        for key,value in [('errors',['bad shape']),('reservation_resolutions',[dict(b='XL01')]),
                          ('contacts',[dict(b='W003')]*3)]:
            bad=copy.deepcopy(g);bad[key]=value
            with self.assertRaises(AssertionError):C.inherited_gate(bad)
        g['source_sha256']={'changed':'old'}
        with patch.object(C,'SHA',return_value='new'):
            with self.assertRaises(AssertionError):C.inherited_gate(g)

    def test_terminal_exception_is_only_axial_radius_not_whole_connector(self):
        parts=[D.M.line([46.5,-39.75,141],[37.5,-39.75,141])]
        result=C.clipped_terminal(parts,.7)
        self.assertEqual(parts[-1]['end'],[37.5,-39.75,141])
        self.assertEqual(result[-1]['start'],parts[-1]['start'])
        self.assertAlmostEqual(result[-1]['end'][0],38.21)
        self.assertAlmostEqual(result[-1]['length_mm'],8.29)
        parts[-1]['end'][0]=37.6
        with self.assertRaises(AssertionError):C.clipped_terminal(parts,.7)

    def test_departures_keep_same_nine_mm_lands_and_bend_outward(self):
        logic=D.M.line([73.81,-13.97,94.3202],[73.81,-13.97,85.3202])
        tail=D.M.line([73.81,19.05,85.3202],[73.81,19.05,94.3202])
        p={'complete_routes':{'XL01':{'parts':[logic]},'XL09':{'parts':[tail]}}}
        a,b=D.outward_prefixes(p)
        self.assertEqual(a[0],D.M.reverse([logic])[0]);self.assertEqual(b[0],tail)
        self.assertAlmostEqual(D.F.validate(a,10),9+5*D.math.pi+12)
        self.assertAlmostEqual(D.F.validate(b,6),9+3*D.math.pi+12)
        self.assertLess(a[-1]['end'][0],64.5);self.assertLess(b[-1]['end'][0],64.5)

    def test_own_bare_join_is_not_whole_wire_exception(self):
        route=[D.M.line([0,0,0],[0,0,9]),D.M.line([0,0,9],[3,0,9])]
        bare=[D.M.line([0,0,-3],[0,0,0])]
        clipped=C.clipped_own_join(route,bare,1)
        self.assertEqual(clipped[0]['start'],[0,0,1]);self.assertEqual(clipped[1],route[1])
        with self.assertRaises(AssertionError):C.clipped_own_join(route,[D.M.line([5,0,0],[6,0,0])],1)


if __name__=='__main__':unittest.main()
