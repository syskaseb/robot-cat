"""Constructive N01 shared print, not released N03 production hardware.

Inputs are frozen current source shapes in world millimetres. Purchased parts
are never fused, cut or repositioned. Existing support subfeatures are one
printed parent according to their constructors and positive joint graph.
"""
import FreeCAD as A
import Part
import numpy as np


def box(lo,hi):
    return Part.makeBox(*(b-a for a,b in zip(lo,hi)),A.Vector(*lo))


def seat(start,axis,side,length=9.,radius=1.55):
    """Open pad plus the selected 2.5x1.2 band and 5x4.3x5.3 head envelope."""
    t=np.array(axis,float);u=np.array(side,float);v=np.cross(t,u)
    m=A.Matrix();m.A11,m.A21,m.A31=t;m.A12,m.A22,m.A32=u;m.A13,m.A23,m.A33=v
    f=A.Placement(A.Vector(*start),A.Rotation(m));g=radius+.15;h=g+.5;c=length/2
    def cell(lo,hi):
        s=box(lo,hi);s.Placement=f*s.Placement;return s
    pad=cell([0,g,-h],[length,4.5,h])
    band=cell([c-1.25,-g-1.2,-h-1.4],[c+1.25,5.7,h+1.4]).cut(
        cell([c-1.35,-g,-h-.2],[c+1.35,4.5,h+.2]))
    head=cell([c-2.5,5.7,-2.65],[c+2.5,10,2.65])
    pad=pad.cut(band.makeOffsetShape(.2,1e-6))
    for s in [pad,band,head]:s.check(True);assert len(s.Solids)==1
    return dict(pad=pad,band=band,head=head)


def construct(parents,receiver_cap,gap_x,outer_y=-94.2,rear_beam_mm=3.):
    assert 3.<=rear_beam_mm<=3.25
    bed=parents['BankBed'];rr=parents['RRGuide'];carrier=parents['DRRCarrier']
    power=parents['PowerParent']
    comb=receiver_cap.cut(box([72,-65.6,-.501],[100,-60,6.5]))
    left_lower=box([68,-67.6,7],[70.5,-63.6,37.5])
    rear_return=box([68,-79.75,34.5],[70.5,-63.6,37.5])
    rear_upright=box([68,-79.75,34.5],[70.5,-76.75,54.5])
    rear_beam=box([68,-79.75,54.5-rear_beam_mm],[106,-76.75,54.5])
    left=left_lower.multiFuse([rear_return,rear_upright,rear_beam])
    right=box([101.5,-67.6,7],[104,-63.6,53.5])
    ledge=box([68,-64.3,7],[104,-60.85,8])
    for x in [76.5,81.25,86,90.75,95.5]:
        ledge=ledge.cut(Part.makeCylinder(1.7,12,A.Vector(x,-65.6,10),A.Vector(0,0,-1)))
    low=seat([76.5,-81.65,-13.15],[0,1,0],[-1,0,0],length=3.5)
    low_web=box([72,-83.35,-13.15],[74,-81.35,7.25]).fuse(box([72,-83.35,6.5],[74,-68.5,8]))
    mid=seat([gap_x,-71,77.8],[0,1,0],[1,0,0])
    y=parents['PowerGapY']
    post=box([105,y-1.5,52.5],[108,y+1.5,81])
    cross=box([103.5,-72.2,79.5],[114.5,-69.2,82.5])
    cells=dict(comb=comb,left_hanger=left,right_hanger=right,ledge=ledge,
        low_pad=low['pad'],low_web=low_web,RRguide=rr,W011pad=mid['pad'],
        RRpost=post,RRcross=cross,common_power_parent=power,bed=bed)
    values=list(cells.values());frame=values[0].multiFuse(values[1:])
    frame.check(True);assert len(frame.Solids)==1
    source=seat([21.35,outer_y,29],[0,0,1],[1,0,0])
    bridge=box([23.05,outer_y-2.2,36.5],[26.05,outer_y+2.2,40.5])
    for y in [-95.5,-90]:bridge=bridge.cut(box([22,y-1.4,39],[27,y+1.4,40.5]))
    source_frame=carrier.fuse(source['pad']).fuse(bridge)
    source_frame.check(True);assert len(source_frame.Solids)==1
    return dict(frame=frame,source_frame=source_frame,cells=cells,
                W011_seat=mid,W012_low_seat=low,W012_source_seat=source)
