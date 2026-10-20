import json,unittest
import FreeCAD as A
import Part
from plan_feline_layout import OUT
from plan_feline_mta_shared_crowns import plan_parts
from plan_feline_n01_shared import pipe


class ClipBounds(unittest.TestCase):
    def test_actual_slab_bounds_respect_boolean_planes(self):
        source=json.loads((OUT/'n01-MTA-whole-corridor.json').read_text())
        for r in source['recipes'].values():
            _,_,rows=plan_parts(r);crown=pipe(rows,2.1)
            slab=crown.common(Part.makeBox(80,200,2,A.Vector(-40,-100,-36)))
            self.assertTrue(slab.isValid());self.assertGreater(slab.Volume,0)
            b=slab.optimalBoundingBox(False,False)
            self.assertGreaterEqual(b.ZMin,-36-1e-6)
            self.assertLessEqual(b.ZMax,-34+1e-6)


if __name__=='__main__':unittest.main()
