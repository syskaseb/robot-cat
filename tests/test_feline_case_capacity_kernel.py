import sys
import unittest
from pathlib import Path
import numpy as np
from scipy.ndimage import minimum_filter
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
from plan_feline_global_case_capacity import kernel_size,points_from_ids


class CaseKernel(unittest.TestCase):
    def test_entire_source_box_not_just_centre(self):
        self.assertEqual(kernel_size([51,20.25,22]),(15,7,7))
        a=np.ones((25,15,15),dtype=np.uint8);a[6,7,7]=0
        result=minimum_filter(a,size=kernel_size([51,20.25,22]),mode='constant',cval=0)
        self.assertTrue(a[12,7,7])
        self.assertFalse(result[12,7,7])

    def test_all_axial_dimensions_round_outward(self):
        for dimensions in ([51,20.25,22],[22,51,20.25],[20.25,22,51]):
            size=np.array(kernel_size(dimensions))
            self.assertTrue(np.all((size-1)/2*4>=np.array(dimensions)/2))
            self.assertTrue(np.all(size%2==1))

    def test_voxel_coordinate_frame_roundtrip(self):
        dims=np.array([337,209,173]);lo=np.array([-147,-104,-54]);q=np.array([[0,0,0],[336,208,172],[80,60,50]])
        ids=(q[:,0]*dims[1]+q[:,1])*dims[2]+q[:,2]
        np.testing.assert_array_equal(points_from_ids(ids,lo,dims),q+lo)


if __name__=='__main__':unittest.main()
