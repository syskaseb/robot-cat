"""Cheap plan contracts; no CAD rebuild and no acceptance from a partial gate."""
import math
import unittest
from open_prototype_receiving_gallery_recovery import build, G
from open_prototype_bundle_spines import sub, cross, dot


def geometric_length(parts):
    total=0
    for p in parts:
        if p['kind']=='line':total+=math.dist(p['start'],p['end']);continue
        a,b,c=p['start'],p['mid'],p['end']
        area2=math.sqrt(dot(cross(sub(b,a),sub(c,a)),cross(sub(b,a),sub(c,a))))
        radius=math.dist(a,b)*math.dist(b,c)*math.dist(c,a)/(2*area2)
        assert abs(radius-6)<1e-7
        angle=2*math.asin(min(1,math.dist(a,c)/(2*radius)))
        total+=radius*angle
    return total


class ReceivingContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.plan,cls.proof,cls.changed=build()

    def test_ends_lengths_radii_and_continuity(self):
        ports={r['role']:r for r in self.plan['ports']}
        for row in self.plan['holders']:
            with self.subTest(holder=row['holder']):
                parts=row['input_parts']
                self.assertEqual(parts[0]['start'],row['input_mm'])
                self.assertEqual(parts[-1]['end'],ports[row['target']]['point_mm'])
                for a,b in zip(parts,parts[1:]):self.assertLess(math.dist(a['end'],b['start']),1e-7)
                self.assertAlmostEqual(geometric_length(parts),row['input_centreline_mm'],places=7)
                self.assertGreaterEqual(math.dist(parts[-1]['start'],parts[-1]['end']),9-1e-7)
                self.assertLessEqual(row['input_blank_mm'],row['input_limit_mm'])
                if row['holder'] in ('F_HY','F_HP','F_TY'):
                    self.assertAlmostEqual(math.dist(parts[0]['start'],parts[0]['end']),3)

    def test_no_topology_or_result_inflation(self):
        self.assertEqual(len(self.plan['ports']),100)
        self.assertEqual(sum(r['occupied'] for r in self.plan['ports']),86)
        self.assertEqual(len(self.plan['main_targets']),8)
        self.assertEqual(len(self.plan['S1']),4)
        self.assertEqual(self.plan['main_targets']['W042'],'P_FRONT.5')
        self.assertFalse(self.plan['selected']);self.assertFalse(self.plan['stage_completed'])
        self.assertTrue(all(r['full_route_and_replacement_of_legacy_920mm_open'] for r in self.plan['S1']))

    def test_delta_only_reuses_unchanged_inputs(self):
        old=G.read(G.PLAN)
        for oldrow,newrow in zip(old['mts'],self.plan['mts']):
            if oldrow['centre_mm']!=newrow['centre_mm']:self.assertIn(newrow['native'],self.changed)
        for oldrow,newrow in zip(old['holders'],self.plan['holders']):
            if oldrow['input_parts']!=newrow['input_parts']:self.assertIn(newrow['holder']+'/input',self.changed)
        self.assertEqual(old['distribution'],self.plan['distribution'])
        self.assertEqual(old['S1'],self.plan['S1'])
        self.assertEqual(len(self.proof['errors']),0)


if __name__=='__main__':unittest.main()
