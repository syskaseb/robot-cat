"""Conservative raster + CLOSED-volume filling for routing proposals only.

Triangle/box SAT includes triangle interiors; solid interiors are occupied,
not the false free space of an unsigned surface-distance field. Exact valid
BRep acceptance is still required for every resulting whole route/support.
"""
import itertools
import numpy as np
from scipy.ndimage import binary_fill_holes,label


def raster(triangles,step=1.,classify_region=None,skip_marked=True):
    tri=np.asarray(triangles,float).reshape(-1,3,3);assert len(tri) and np.isfinite(tri).all()
    origin=np.floor(tri.min(axis=(0,1))/step)*step-2*step
    size=np.ceil((tri.max(axis=(0,1))-origin)/step).astype(int)+3
    assert np.prod(size)<24000000,('Bounded source voxel memory',size)
    occupied=np.zeros(tuple(size),bool);half=step/2
    for t in tri:
        low=np.maximum(0,np.floor((t.min(0)-origin-half)/step).astype(int))
        high=np.minimum(size-1,np.ceil((t.max(0)-origin+half)/step).astype(int))
        if skip_marked and occupied[tuple(slice(a,b+1) for a,b in zip(low,high))].all():continue
        ids=np.stack(np.meshgrid(*(np.arange(a,b+1) for a,b in zip(low,high)),indexing='ij'),axis=-1).reshape(-1,3)
        if skip_marked:
            ids=ids[~occupied[tuple(ids.T)]]
            if not len(ids):continue
        points=origin+ids*step
        edges=np.roll(t,-1,axis=0)-t
        axes=np.vstack((np.eye(3),np.cross(edges[0],edges[1]),np.cross(edges[:,None,:],np.eye(3)[None,:,:]).reshape(-1,3)))
        axes=axes[np.linalg.norm(axes,axis=1)>1e-12]
        projected=t@axes.T;centres=points@axes.T;radius=half*np.abs(axes).sum(1)
        hit=np.all((projected.min(0)-centres<=radius+1e-8)&(projected.max(0)-centres>=-radius-1e-8),axis=1)
        q=ids[hit];occupied[tuple(q.T)]=True
    filled=binary_fill_holes(occupied)
    if classify_region is None:occupied=filled
    else:
        # SAT surfaces partition volume. One exact point per enclosed FREE
        # region distinguishes real material from sealed air cavities, without
        # millions of OCC isInside calls. Boundary voxels remain conservative.
        regions,count=label(filled&~occupied)
        for region in range(1,count+1):
            cells=np.argwhere(regions==region)
            if len(cells) and classify_region(origin+cells[0]*step):occupied[regions==region]=True
    return origin,occupied


def union_integer_boxes(destination,low,high):
    """Exactly OR inclusive integer boxes using eight signed corner updates.

    This changes only the union implementation, not any source cube expansion,
    orientation, clipping or occupancy. The former offset/scatter oracle is
    retained in regression tests, including clipped and overlapping boxes.
    """
    size=np.array(destination.shape);low=np.maximum(low,0);high=np.minimum(high,size-1)
    valid=np.all(high>=low,axis=1);low=low[valid];high=high[valid]
    if not len(low):return
    start=low.min(0);stop=high.max(0)+1
    extent=stop-start;delta=np.zeros(tuple(extent+1),np.int32)
    low=low-start;high=high-start+1
    for corner in itertools.product((0,1),repeat=3):
        q=np.where(np.asarray(corner),high,low)
        np.add.at(delta,tuple(q.T),(-1)**sum(corner))
    for axis in range(3):np.cumsum(delta,axis=axis,dtype=np.int32,out=delta)
    destination[tuple(slice(int(a),int(b)) for a,b in zip(start,stop))]|=delta[:-1,:-1,:-1]>0


def deposit(destination,source,source_origin,origin,step=1.,rotation=None,translation=None):
    """A rotated occupied source voxel is enclosed by its full corner bounds.

    This is a conservative planning overapproximation, not a rotated BRep.
    The sphere radius covers the entire rotated cube before raster deposit.
    """
    if rotation is None:
        offset=(np.asarray(source_origin)-origin)/step
        assert np.allclose(offset,np.rint(offset))
        offset=np.rint(offset).astype(int);low=np.maximum(0,offset);high=np.minimum(destination.shape,offset+source.shape)
        if np.all(high>low):
            a=tuple(slice(int(x),int(y)) for x,y in zip(low,high))
            b=tuple(slice(int(x),int(y)) for x,y in zip(low-offset,high-offset))
            destination[a]|=source[b]
        return
    points=source_origin+np.argwhere(source)*step
    if not len(points):return
    if rotation is not None:points=points@np.asarray(rotation).T+np.asarray(translation)
    # Cover every source cube, not only its rounded transformed centre.
    expansion=np.sqrt(3)*step/2 if rotation is not None else step/2
    high_world=origin+(np.array(destination.shape)-1)*step
    points=points[np.all(points>=origin-expansion-step,1)&np.all(points<=high_world+expansion+step,1)]
    if not len(points):return
    low=np.floor((points-origin-expansion-step/2)/step).astype(int)
    high=np.ceil((points-origin+expansion+step/2)/step).astype(int)
    union_integer_boxes(destination,low,high)
