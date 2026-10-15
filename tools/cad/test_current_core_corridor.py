import unittest
import numpy as np
from current_core_corridor import corridor
from plan_current_mta_interfaces import line


class EmptyScene:
    def clear(self,points,row):return True


class CurrentCoreCorridor(unittest.TestCase):
    def test_real_cardinal_source_tangents_both_search_directions(self):
        for axis in ((0,0,1),(-1,0,0),(1,0,0)):
            start=[0,0,0];free=[5*v for v in axis]
            end=[60,80,100];outside=[60,80,109]
            row=dict(wire='fixture',bodyward_bundle_tangent=list(axis),source_free_axis=list(axis),
                free_start=free,free_end=outside,source_land=line(start,free),
                receiving_land=line(outside,end),receiver_outward_axis=[0,0,1],
                capacity_before_terminal_mm=850,terminal_allowance_project_mm=11)
            for backward in (False,True):
                with self.subTest(axis=axis,backward=backward):
                    result,points=corridor(EmptyScene(),row,backward)
                    self.assertIsNotNone(points,result)
                    parts=result['parts'];self.assertEqual(parts[0]['start'],start)
                    self.assertEqual(parts[-1]['end'],end)
                    first=parts[1]
                    if first['kind']=='bezier':tangent=np.asarray(first['poles_mm'][1])-first['poles_mm'][0]
                    elif first['kind']=='line':tangent=np.asarray(first['end'])-first['start']
                    else:continue # Arc tangent fixture covered by exact_quarter tests.
                    self.assertAlmostEqual(float(np.dot(tangent/np.linalg.norm(tangent),axis)),1,places=7)
                    self.assertGreaterEqual(result['minimum_sampled_R_mm'],10)


if __name__=='__main__':unittest.main()
