"""Rejoin an ACTUAL positive curve below a blocking retained support.

De Casteljau preserves its subsequent geometry exactly. This is not joining
only the old end datum with a different curve through occupied space.
"""
import copy,math
from plan_current_moving_looms import metrics
from shared_body36_macro_routes import finish

def split(part,t):
    assert part['kind']=='bezier' and 0<t<1
    a,b,c,d=part['poles_mm']
    mix=lambda p,q:[(1-t)*x+t*y for x,y in zip(p,q)]
    ab,bc,cd=mix(a,b),mix(b,c),mix(c,d);abc,bcd=mix(ab,bc),mix(bc,cd);point=mix(abc,bcd)
    result=[]
    for poles in ([a,ab,abc,point],[point,bcd,cd,d]):
        length,radius,_=metrics(poles,400)
        result.append(dict(kind='bezier',start=poles[0],end=poles[-1],poles_mm=poles,length_mm=length,sampled_radius_mm=radius))
    return result

def at_rising_plane(part,axis,value):
    points=part['poles_mm'];assert all(a[axis]<=b[axis] for a,b in zip(points,points[1:]))
    assert points[0][axis]<value<points[-1][axis]
    low,high=0.,1.
    for _ in range(48):
        t=(low+high)/2;s=1-t
        height=s**3*points[0][axis]+3*s*s*t*points[1][axis]+3*s*t*t*points[2][axis]+t**3*points[3][axis]
        if height<value:low=t
        else:high=t
    return split(part,(low+high)/2)[1]

def splice(row,prefix,received,part_index,axis,plane):
    row=copy.deepcopy(row);part=at_rising_plane(received['parts'][part_index],axis,plane)
    tail=[part,*copy.deepcopy(received['parts'][part_index+1:])]
    row['free_end']=part['start'];v=[a-b for a,b in zip(part['poles_mm'][0],part['poles_mm'][1])];n=math.sqrt(sum(x*x for x in v))
    row['receiver_outward_axis']=[x/n for x in v]
    row['receiving_grip_part_index']+=len(tail)-len(row['receiving_parts']);row['receiving_parts']=tail
    q,error=finish(row,prefix,'rejoin_actual_received_Bezier_below_Foundation_then_inherit_tail')
    if q:q['received_curve_splice']=dict(part_index=part_index,plane_axis=axis,plane_mm=plane,retained_tail_parts=len(tail))
    return row,q,error
