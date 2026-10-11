"""Planning contracts only, not material or hardware acceptance."""
import contextlib, io, json, math, unittest
from plan_current_main_east_comb import build,OUT


class MainEastComb(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with contextlib.redirect_stdout(io.StringIO()):cls.p=build()
        cls.old=json.loads((OUT/'main-pi-plan.json').read_text())

    def test_whole_four_route_scope(self):
        self.assertEqual(set(self.p['routes']),{'W077','W078','W079','W080'})
        self.assertEqual(set(self.p['grips']),{'W060','W078','W079','W080'})
        self.assertFalse(self.p['selected']);self.assertFalse(self.p['W5_complete'])

    def test_independent_nine_mm_lands(self):
        for g in self.p['grips'].values():
            self.assertAlmostEqual(math.dist(g['start_mm'],g['end_mm']),9)
        for n in ('W078','W079','W080'):
            g=self.p['grips'][n]
            self.assertTrue(any(math.dist(s['start'],g['start_mm'])<1e-7 and
                math.dist(s['end'],g['end_mm'])<1e-7 or
                math.dist(s['end'],g['start_mm'])<1e-7 and
                math.dist(s['start'],g['end_mm'])<1e-7 for s in self.p['routes'][n]['parts']))

    def test_protected_lap_is_straight_eight(self):
        f=self.p['routes']['W077']['parts'][-1]
        c=self.p['routes']['W078']['parts'][0]
        self.assertEqual(f['kind'],'line')
        self.assertAlmostEqual(f['length_mm'],8)
        self.assertLess(math.dist(f['start'],c['start']),1e-7)
        self.assertFalse(self.p['retained_source_splice'])

    def test_original_board_and_sealed_usb_ends(self):
        for n in ('W079','W080'):
            self.assertEqual(self.p['routes'][n]['parts'][0]['start'],self.old['routes'][n]['parts'][0]['start'])
            self.assertEqual(self.p['routes'][n]['parts'][-1]['end'],self.old['routes'][n]['parts'][-1]['end'])
        self.assertEqual(self.p['routes']['W078']['parts'][-1]['end'],self.old['routes']['W078']['parts'][-1]['end'])
        self.assertTrue(self.p['retained_MAIN_return'])

    def test_whole_screen_and_lengths(self):
        self.assertEqual(self.p['rejected'],[])
        for n,r in self.p['routes'].items():
            self.assertAlmostEqual(r['guide_mm'],sum(s['length_mm'] for s in r['parts']))
            self.assertLessEqual(r['guide_mm']+(8 if n=='W077' else 3),100 if n=='W077' else 150 if n=='W078' else 250)


if __name__=='__main__':unittest.main()
