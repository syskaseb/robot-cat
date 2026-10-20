"""Reuse primitive geometry; remove edges that fail changed occupancy only."""
import numpy as np
from scipy.sparse import coo_matrix
from plan_feline_tangent_corridor_network import DIRECTIONS,primitive


def filter_existing(ids,graph,free,radius,step=4):
    cells=np.argwhere(ids>=0);base=np.empty((len(cells),3),int);base[ids[tuple(cells.T)]]=cells*step
    assert graph.shape==(6*len(cells),)*2
    old=graph.tocoo();keep=np.ones(len(old.data),bool)
    for h,d in enumerate(DIRECTIONS):
        for j,t in enumerate(DIRECTIONS):
            ix=np.flatnonzero((old.row%6==h)&(old.col%6==j))
            if not len(ix):continue
            points=primitive(d,t,radius,step);start=base[old.row[ix]//6]
            assert np.array_equal(start+np.rint(points[-1]).astype(int),base[old.col[ix]//6]),'Wrong cached primitive endpoint'
            live=np.ones(len(ix),bool)
            for offset in np.unique(np.rint(points).astype(int),axis=0):
                q=start+offset;assert np.all(q>=0) and np.all(q<np.asarray(free.shape))
                live &= free[tuple(q.T)]
            keep[ix]=live
    new=coo_matrix((old.data[keep],(old.row[keep],old.col[keep])),shape=graph.shape).tocsr()
    return new,dict(parent_primitives=len(keep),reused_primitives=int(keep.sum()),removed_by_changed_space=int((~keep).sum()),
        existing_constructive_arcs_not_regenerated=True,newly_free_cells_not_added_to_parent_classes=True)
