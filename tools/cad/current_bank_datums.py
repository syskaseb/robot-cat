"""Read bank world datums from the CURRENT placed solids, never old origins.

Housing/ATO solids are project nominal envelopes, not measured part profiles.
Their placement is nevertheless authoritative for their own assembly frame.
"""
import re
import FreeCAD as A
import Part


def bounds(shape):
    b=shape.BoundBox
    return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]


def datums(targets):
    slots={}
    for name,shape in targets.items():
        match=re.fullmatch(r'(F_([LR])([1-6])_CP2)_(Housing|ATO|IN|OUT)(?:/.*)?',name)
        if not match:continue
        key,side,index,kind=match.groups();slot=slots.setdefault(key,dict(id=key,side=side,index=int(index),parts={}))
        if kind in slot['parts']:
            assert slot['parts'][kind]['bounds_mm']==bounds(shape),('Inconsistent bank aliases',name)
        slot['parts'][kind]=dict(name=name,bounds_mm=bounds(shape))
    assert len(slots)==12,'Need all12 placed bank components'
    rows=[]
    for key,r in sorted(slots.items()):
        assert set(r['parts'])=={'Housing','ATO','IN','OUT'},key
        h=r['parts']['Housing']['bounds_mm'];a=r['parts']['ATO']['bounds_mm']
        centre=[(h[0]+h[3])/2,(h[1]+h[4])/2]
        assert abs((a[0]+a[3])/2-centre[0])<1e-6 and abs((a[1]+a[4])/2-centre[1])<1e-6
        assert abs(a[2]-h[5])<1e-6,'Nominal inserted fuse flange datum changed'
        r.update(centre_xy_mm=centre,flange_top_z_mm=h[5],
                 placement_basis='Current placed Housing/ATO world BReps; one placement only',
                 geometry_basis='Existing project nominal envelopes, not measured inserted fuse or holder taper',
                 previous_wrong_centre_y_mm=58 if r['side']=='L' else -58)
        rows.append(r)
    return rows


def nominal_sweep(row,travel_mm=35):
    assert travel_mm>0
    a=row['parts']['ATO']['bounds_mm'];x,y,z,X,Y,Z=a
    return Part.makeBox(X-x,Y-y,Z-z+travel_mm,A.Vector(x,y,z))
