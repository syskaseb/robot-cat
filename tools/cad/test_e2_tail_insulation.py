import json,unittest
import plan_e2_tail_insulation as E


class TailWrapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.p=E.allocation()

    def test_wraps_are_valid_single_envelopes_and_stop_before_pcb(self):
        for s in self.p['envelopes'].values():
            self.assertTrue(s.isValid());self.assertEqual(len(s.Solids),1)
            self.assertFalse(s.check(True))
        for r in self.p['rows'].values():
            self.assertAlmostEqual(r['PCB_bottom_world_Z_mm']-r['wrap_stop_world_Z_mm'],.2002)

    def test_terminals_grip_lands_and_exact_length_change(self):
        original=json.loads(self.p['source'].read_text())['changed_E2_routes']
        for n in self.p['rows']:
            old=original[n]['parts']+original[n+'_bare']['parts']
            new=self.p['routes'][n]['parts']+self.p['routes'][n+'_bare']['parts']
            self.assertEqual(old[0]['start'],new[0]['start']);self.assertEqual(old[-1]['end'],new[-1]['end'])
            self.assertEqual(old[0],new[0])
            self.assertAlmostEqual(E.P.wire(new).Length,E.P.wire(old).Length)
            self.assertEqual(original[n+'_bare']['parts'],new[-len(original[n+'_bare']['parts']):])

    def test_wrap_envelopes_have_no_mutual_contact(self):
        a,b=self.p['envelopes'].values()
        self.assertLess(a.common(b).Volume,1e-5)
        # These are two fixed compliant insulators; touching is permitted,
        # but interpenetrating nominal envelopes must not be hidden.
        self.assertGreater(a.distToShape(b)[0],.3)

    def test_both_wraps_clear_the_other_complete_jacket_and_copper(self):
        for name,shape in self.p['envelopes'].items():
            owner=name.replace('_BoardInsulation','')
            for n,r in self.p['routes'].items():
                if n in (owner,owner+'_bare'):continue
                self.assertGreaterEqual(shape.distToShape(E.P.wire(r['parts']))[0],r['radius']-1e-5)


if __name__=='__main__':unittest.main()
