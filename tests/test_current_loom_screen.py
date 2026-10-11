import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/cad'))
from screen_current_moving_looms import only_new_pairs,pose_row,OUT,SHA

class LoomScreen(unittest.TestCase):
    def test_samples_do_not_retest_unchanged_pairs(self):
        old=[dict(wire=n,OD_mm=6,segments=[dict(kind='line',start=[0,0,0],end=[10,0,0],length_mm=10)]) for n in ('old1','old2')]
        self.assertEqual(only_new_pairs(old,[]),[])
        self.assertEqual(len(only_new_pairs(old,[dict(old[0],wire='new')])),2)

    def test_motion_receipt_covers32_changed_leg_groups_without_claiming_full_motion(self):
        p=json.loads((OUT/'moving-looms-motion-screen.json').read_text())
        self.assertEqual(len(p['cases']),32)
        self.assertEqual(len({(r['leg'],r['hip'],r['knee']) for r in p['cases']}),32)
        self.assertFalse(p['selected']);self.assertFalse(p['W5_complete']);self.assertFalse(p['physical_pass'])
        for n,h in p['source_sha256'].items():self.assertEqual(SHA(ROOT/n),h,n)

    def test_full_path_includes_departures_and_returns(self):
        p=json.loads((OUT/'moving-looms-plan.json').read_text())
        for r in p['looms']:
            v=next(v for v in r['poses'] if not any(v['angles']))
            row=pose_row(r,v)
            self.assertEqual(row['segments'][0]['start'],v['start'])
            self.assertEqual(row['segments'][-1]['end'],r['body_dock_mm'])

if __name__=='__main__':unittest.main()
