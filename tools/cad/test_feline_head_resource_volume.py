"""A valid-looking zero-volume sweep must never qualify a neck corridor."""
import json,math,sys,unittest
from unittest.mock import patch
from receive_feline_shared_corridor_space import candidates,transition_separation_bound


class HeadResourceVolume(unittest.TestCase):
    def test_central_floor_preserves_all_source_jackets_changes_whole_resource(self):
        with patch.object(sys,'argv',['resource-test','--head-neck-under-bridge']):old=candidates()
        with patch.object(sys,'argv',['resource-test','--head-neck-central-floor']):new=candidates()
        for a,b in zip(old[:3],new[:3]):
            for key in ('start_mm','end_mm','path_length_mm','radius_mm','full9_grip_mm'):
                self.assertEqual(a[key],b[key])
        r=new[-1];self.assertEqual(r['end_mm'],[-70.,-14.,-37.34])
        self.assertEqual(r['name'],'HP_central_underfloor')
        self.assertAlmostEqual(r['shape'].Volume,r['analytic_expected_volume_mm3'],places=4)
        self.assertGreater(r['minimum_inner_resource_bend_R_mm'],12.4)

    def test_continuous_flattening_separation_bound(self):
        with patch.object(sys,'argv',['resource-test','--head-neck-flat-ribbon']):
            rows=[r for r in candidates() if r['kind']=='head_transition_nominal_jacket']
        for i,row in enumerate(rows):
            for other in rows[i+1:]:
                bound=transition_separation_bound(row,other)
                json.dumps(bound)
                self.assertTrue(bound['ok'],bound)
                self.assertGreater(bound['axis_discretization_error_bound_mm'],0)
                self.assertLess(bound['axis_discretization_error_bound_mm'],.011)
        self.assertAlmostEqual(transition_separation_bound(rows[0],rows[1])['gap_lower_bound_mm'],.3623544552,places=7)

    def test_nonzero_correct_profile_and_path_volume(self):
        for mode in ('--head-neck-inboard','--head-neck-overbridge','--head-neck-top-entry','--head-neck-flat-ribbon','--head-neck-under-bridge'):
            with patch.object(sys,'argv',['resource-test',mode]):rows=candidates()
            json.dumps([{k:v for k,v in row.items() if k!='shape'} for row in rows])
            for row in rows:
                if 'analytic_expected_volume_mm3' not in row:continue
                s=row['shape'];self.assertTrue(s.isValid());self.assertEqual(len(s.Solids),1)
                self.assertGreater(s.Volume,0)
                self.assertAlmostEqual(s.Volume,math.pi*row.get('radius_mm',4.)**2*row['path_length_mm'],places=3)
                if 'minimum_inner_resource_bend_R_mm' in row:
                    self.assertGreaterEqual(row['minimum_inner_resource_bend_R_mm'],row['minimum_wire_R_mm'])
                if 'continuous_curvature' in row:self.assertGreaterEqual(row['continuous_curvature']['minimum_radius_mm'],12.4)


if __name__=='__main__':unittest.main()
