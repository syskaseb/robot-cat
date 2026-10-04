from pathlib import Path
import json,unittest
from w5_leg_joint_source_layout_r1 import plan,source_edges
from w5_rounded_path import corner_offsets

ROOT=Path(__file__).resolve().parents[2]


class JointSourceLayout(unittest.TestCase):
    def test_all_36_nets_breakouts_and_twelve_v_unchanged(self):
        old=json.loads((ROOT/'hardware/electronics/full-cat/w5-leg-fanouts-r5/intent.json').read_text())['routes']
        before=json.dumps(old,sort_keys=True)
        rows=plan(old)
        self.assertEqual(before,json.dumps(old,sort_keys=True))
        self.assertEqual(len(rows),36)
        for a,b in zip(old,rows):
            for key in ('wire','loom','role','body_end','servo_end'):
                self.assertEqual(a[key],b[key])
            self.assertEqual(a['waypoints_mm'][-1],b['waypoints_mm'][-1])
            if a['role']=='V':self.assertEqual(a,b)
            else:
                self.assertEqual(b['real_half_turn']['straight_cage_entry_mm'],1)
                self.assertEqual(b['real_half_turn']['tilt_deg'],90)
                self.assertAlmostEqual(b['waypoints_mm'][2][2],133.5)
                corner_offsets(b['waypoints_mm'][2:],10)

    def test_changed_source_first_four_edges_join_unchanged_te_side(self):
        rows=json.loads((ROOT/'hardware/electronics/full-cat/w5-s1-source-layout-r8/intent.json').read_text())['routes']
        old=next(r for r in rows if r['wire']=='W064')['edges']
        new=source_edges(rows)
        self.assertEqual(len(new),17)
        self.assertEqual(new[0]['start'],[-16.5,11,113.5])
        self.assertEqual(new[4:],old[4:])
        self.assertEqual(new[-1]['end'],old[-1]['end'])
        for a,b in zip(new,new[1:]):
            self.assertEqual(a['end'],b['start'])

    def test_fourth_front_physical_slot_was_nc(self):
        graph=json.loads((ROOT/'hardware/electronics/power-platform/wiring-p0.json').read_text())
        self.assertFalse(any('P_FRONT.4' in (w['a'],w['b']) for w in graph['wires']))
        w=next(w for w in graph['wires'] if w['id']=='W064')
        self.assertEqual({w['a'],w['b']},{'P_FRONT.1','S1.3'})


if __name__=='__main__':unittest.main()
