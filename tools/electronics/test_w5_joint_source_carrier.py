"""Guard the one changed source interface, without requiring FreeCAD."""
import json
from pathlib import Path
import unittest
from w5_leg_joint_source_layout_r1 import source_edges

ROOT=Path(__file__).resolve().parents[2]


class JointSourceCarrier(unittest.TestCase):
    def test_same_net_free_cage_and_unchanged_switch_end(self):
        rows=json.loads((ROOT/'hardware/electronics/full-cat/w5-s1-source-layout-r8/intent.json').read_text(encoding='utf-8'))['routes']
        before=json.loads(json.dumps(rows))
        old=next(r for r in rows if r['wire']=='W064')['edges']
        new=source_edges(rows)
        self.assertEqual(rows,before, 'Do not mutate received geometry')
        self.assertEqual(len(new),17)
        self.assertEqual(new[0]['start'],[-16.5,11,113.5])
        self.assertEqual(new[1]['start'][:2],[-16.5,36.2])
        self.assertEqual(new[4:],old[4:])
        self.assertEqual(new[3]['end'],old[3]['end'])
        self.assertEqual(new[-1]['end'],old[-1]['end'])
        for a,b in zip(new,new[1:]): self.assertEqual(a['end'],b['start'])
        graph=json.loads((ROOT/'hardware/electronics/power-platform/wiring-p0.json').read_text(encoding='utf-8'))
        self.assertFalse(any('P_FRONT.4' in (r['a'],r['b']) for r in graph['wires']))
        row=next(r for r in graph['wires'] if r['id']=='W064')
        self.assertIn('P_FRONT.1',(row['a'],row['b']))


if __name__=='__main__': unittest.main()
