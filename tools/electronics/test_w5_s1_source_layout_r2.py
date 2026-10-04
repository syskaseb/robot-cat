import math,unittest
from w5_s1_source_layout_r2 import layout


class JointSourceTests(unittest.TestCase):
    def test_complete_paths_and_static_radius(self):
        rows=layout();self.assertEqual(len(rows),4)
        for r in rows:
            self.assertGreater(r['nominal_trial_blank_mm'],r['exposed_path_mm']+52.7)
            for a,b in zip(r['edges'],r['edges'][1:]):
                self.assertLess(math.dist(a['end'],b['start']),1e-7)
            for e in r['edges']:
                if e['kind']=='arc':self.assertGreaterEqual(e['radius_mm'],25.2)
            self.assertLess(math.dist(r['edges'][-1]['end'],r['end']),1e-7)

    def test_not_pwm_cage_and_real_system_displacement(self):
        rows={r['wire']:r for r in layout()}
        self.assertEqual(rows['W065']['start'],[32,13.6,129])
        self.assertEqual(rows['W067']['start'][2],102.5)
        self.assertEqual(rows['W068']['start'][2],102.5)


if __name__=='__main__':unittest.main()
