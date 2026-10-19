import unittest
import numpy as np
from feline_signed_voxels import raster,deposit,union_integer_boxes


def cube(low,high):
    v=np.array([[x,y,z] for x in (low,high) for y in (low,high) for z in (low,high)],float)
    faces=((0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3))
    return np.array([[v[a],v[b],v[c]] for a,b,c,d in faces for a,b,c in ((a,b,c),(a,c,d))])


class SignedVoxels(unittest.TestCase):
    def test_range_union_exact_for_clipped_overlapping_boxes(self):
        rng=np.random.default_rng(20261019)
        for count in (1,17,1000):
            low=rng.integers(-5,25,size=(count,3));high=low+rng.integers(0,6,size=(count,3))
            new=np.zeros((23,19,27),bool);old=new.copy();old[1,1,1]=new[1,1,1]=True
            for a,b in zip(low,high):
                a=np.maximum(a,0);b=np.minimum(b,np.array(old.shape)-1)
                if np.all(b>=a):old[tuple(slice(x,y+1) for x,y in zip(a,b))]=True
            union_integer_boxes(new,low,high)
            self.assertTrue(np.array_equal(old,new))
    def test_rotated_deposit_byte_identical_to_former_offset_oracle(self):
        import itertools
        rng=np.random.default_rng(45);source=rng.random((11,17,13))>.7;origin=np.array([-9.,-11.,-7.])
        for angle in (0,.2,1.15,2.9):
            r=np.array([[np.cos(angle),-np.sin(angle),0],[np.sin(angle),np.cos(angle),0],[0,0,1.]])
            t=np.array([-3.3,2.7,-1.9]);new=np.zeros((23,25,21),bool);old=new.copy()
            deposit(new,source,np.array([-5.,-7.,-9.]),origin,rotation=r,translation=t)
            points=(np.array([-5.,-7.,-9.])+np.argwhere(source))@r.T+t
            expansion=np.sqrt(3)/2;size=np.array(old.shape);high_world=origin+size-1
            points=points[np.all(points>=origin-expansion-1,1)&np.all(points<=high_world+expansion+1,1)]
            low=np.floor(points-origin-expansion-.5).astype(int);high=np.ceil(points-origin+expansion+.5).astype(int)
            for offset in itertools.product(*(range(int(d)+1) for d in np.max(high-low,axis=0))):
                q=low+offset;valid=np.all(q<=high,1)&np.all(q>=0,1)&np.all(q<size,1);q=q[valid];old[tuple(q.T)]=True
            self.assertTrue(np.array_equal(old,new))
    def test_skip_already_marked_cells_is_byte_identical(self):
        mesh=np.concatenate((cube(0,16),cube(5,11),cube(0,16)))
        classify=lambda p:bool(np.all(p>0)&np.all(p<16)&~(np.all(p>5)&np.all(p<11)))
        a,old=raster(mesh,classify_region=classify,skip_marked=False)
        b,new=raster(mesh,classify_region=classify,skip_marked=True)
        self.assertTrue(np.array_equal(a,b));self.assertTrue(np.array_equal(old,new))
    def test_closed_source_interior_not_false_free(self):
        origin,mask=raster(cube(0,10));self.assertTrue(mask[tuple((np.array([5,5,5])-origin).astype(int))])
        self.assertFalse(mask[tuple((np.array([-2,-2,-2])-origin).astype(int))])
    def test_disconnected_cubes_do_not_fill_gap(self):
        origin,mask=raster(np.concatenate((cube(0,4),cube(10,14))))
        self.assertFalse(mask[tuple((np.array([7,7,7])-origin).astype(int))])
    def test_sealed_air_cavity_not_filled_as_material(self):
        triangles=np.concatenate((cube(0,16),cube(5,11)))
        classify=lambda p:bool(np.all(p>0)&np.all(p<16)&~(np.all(p>5)&np.all(p<11)))
        origin,mask=raster(triangles,classify_region=classify)
        self.assertFalse(mask[tuple((np.array([8,8,8])-origin).astype(int))])
        self.assertTrue(mask[tuple((np.array([3,3,3])-origin).astype(int))])
    def test_rotated_volume_deposit_has_actual_centre(self):
        origin,mask=raster(cube(0,4));target=np.zeros((30,30,30),bool)
        rot=np.array([[0,-1,0],[1,0,0],[0,0,1]])
        deposit(target,mask,origin,np.array([-10,-10,-10]),rotation=rot,translation=[0,0,0])
        self.assertTrue(target[8,12,12]);self.assertFalse(target[25,25,25])


if __name__=='__main__':unittest.main()
