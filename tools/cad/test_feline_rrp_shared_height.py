import json, math, unittest
import numpy as np
from plan_feline_layout import OUT
from receive_feline_rrp_shared_height import source_path, gallery, load


class SharedHeight(unittest.TestCase):
    def test_current_actual_budgets_define_nonempty_vertical_interval(self):
        doc=json.loads((OUT/'n01-shared-Pi-carrier-r3-core-received.json').read_text())
        height,r=gallery(load(doc))
        self.assertGreater(height,93.8);self.assertLess(height,94.25)
        self.assertAlmostEqual(height,sum(r['interval_mm'])/2)

    def test_first_full_nine_arc_unchanged_before_new_shared_height(self):
        q=[6.125,69.5,98];height=94.02726902604963
        rows,end,d=source_path(q,height)
        self.assertAlmostEqual(end[2],height)
        self.assertTrue(np.allclose(d,[0,-1,0]))
        first_angle=math.acos(1-(98-height)/(2*25.2))
        self.assertGreater(first_angle,9/25.2)
        self.assertAlmostEqual(sum(p['length_mm'] for p in source_path(q,height,2.5)[0]),sum(p['length_mm'] for p in rows)-2.5)


if __name__=='__main__':unittest.main()
