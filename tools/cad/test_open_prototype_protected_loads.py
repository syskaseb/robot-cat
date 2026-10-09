import unittest,math
import open_prototype_protected_loads as L
import open_prototype_source_group as B

class LoadContracts(unittest.TestCase):
    def test_two_complete_station_feeds_without_guessed_aux_pin(self):
        p=L.build()
        self.assertEqual([r['wire'] for r in p['rows']],['XB12','XB22'])
        self.assertFalse(p['stage_completed'])
        for r in p['rows']:
            B.check_path(r['segments'],end=r['station_mm'],min_radius=12.6)
            self.assertGreaterEqual(math.dist(r['segments'][-1]['start'],r['segments'][-1]['end']),9)
            self.assertIsNone(r['nominal_cut_mm'])
        aux=next(r for r in p['remaining'] if r['wire']=='XA02')
        self.assertIsNone(aux['target_pin_mm'])

    def test_coupled_screen_keeps_tail_endpoint_blocker(self):
        p=L.build()
        self.assertFalse([r for r in p['mutual_path_preflight']['near_pairs'] if r['status']=='REJECT_PLANNING_PROXIMITY'])
        self.assertEqual(len(p['mutual_path_preflight']['declared_covered_same_conductor_joins']),2)
        tail=next(r for r in p['remaining'] if r['wire']=='XB32')
        self.assertLess(math.dist(tail['planning_witness']['sample_b_mm'],tail['exact_station_mm']),1e-7)
        pi=next(r for r in p['remaining'] if r['wire']=='PI_VIN')
        self.assertEqual(pi['physical_aliases'],['W077','W078'])

if __name__=='__main__':unittest.main()
