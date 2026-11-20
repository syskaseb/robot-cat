"""Whole S0 high-outlet layout on its existing posts, using fixed-radius bends."""
from pathlib import Path
from runpy import run_path
from zipfile import ZipFile
from xml.etree import ElementTree
import hashlib
import json
import math
import numpy as np
import FreeCAD as App
import Part

p=Path(__file__).resolve().parent
V=App.Vector
g=run_path(str(p.parent/'20F/clocked.py'))
src_path=p.parent/'20D/whole-cat20D.FCStd'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(src_path)=='b1549964028b289ccc9b27adb023ed804f331b8f4fa23159c00a072975a750e9'
box=g['box']
sweep=g['sweep']
circle=g['circle']
unit=g['unit']
bounds=g['bounds']
common=g['common']
case='S0_body'
ring_in='S0_ring_IN_0_0'
ring_out='S0_ring_OUT_0_0'
pin_in=V(166.5,74,104.5)
pin_out=V(190.5,74,104.5)
r=27.3
outer_r=3.35
in_clock=-30.
out_axis=V(.25,0,math.sqrt(1-.25*.25))
out_clock=-30-math.degrees(math.acos(out_axis.x))
d_hi=V(-.6,-.8,0)
# The E1 frame web starts at Y34.5 and Z104.9. Lay the whole
# descending tangent to keep its projected Y at 30.7 at that level.
drop_y_to_z=(52.0-30.7)/(104.9-62.0)
drop_z=math.sqrt((1-.55**2)/(1+drop_y_to_z**2))
d_drop=V(.55,drop_y_to_z*drop_z,-drop_z)
d_final=V(-1,0,0)
mouth_out=pin_out+out_axis*26.9
psys=V(165,52,62)
lead_start=mouth_out+out_axis*2.5

def turned(shape,origin,angle):
    s=shape.copy()
    s.rotate(origin,V(0,1,0),angle)
    return s

def transformed_axes(a,b):
    return r*math.tan(math.acos(a.dot(b))/2)*(a+b)

def xyz(v):
    return [round(q,6) for q in v]

displacements=[transformed_axes(i,j) for i,j in ((out_axis,d_hi),(d_hi,d_drop),(d_drop,d_final))]
d=psys-lead_start
for dv in displacements:
    d=d-dv
axis_tuple=(d_hi,d_drop,d_final)
straight=np.linalg.solve(np.array([list(q) for q in axis_tuple]).T,list(d))
assert min(straight)>0
out_edges={'axial_from_full_OUT_barrel':Part.makeLine(mouth_out,lead_start)}
pos=lead_start
for role,t,u,extension in zip(('raise_outboard','clear_side_of_E1','turn_to_P_SYS'),(out_axis,d_hi,d_drop),
                              axis_tuple,straight):
    edge,end=circle(pos,t,u,r)
    out_edges[role]=edge
    pos=end+float(extension)*u
    out_edges[role+'_straight']=Part.makeLine(end,pos)
assert pos.distanceToPoint(psys)<1e-6
related=list(dict.fromkeys(g['names']+[
    'S0_nut_IN_0_0','S0_nut_OUT_0_0','S0_stud_IN_0_0','S0_stud_OUT_0_0','S0_washer_IN_0_0',
    'S0_washer_OUT_0_0','S0_neck','S0_key','Monitor_MOD05015','OP_S1_PRIMARY_CASE_CONSERVATIVE',
    'E19_ForeBase','G19_PermaProto1608','E19_ReSpeakerSource','S0_body','PBAY_F_TY','D19_BODY_CONTROL_TRUNK',
    'E19_BatteryDoor','C20_BatteryUpperBridge','F19_RearCap','E19_KeyedTail','PBAY_POST_F0'
]))
stack_names=[n for n in related if n.startswith('S0_') and n!='S0_key']
def solid_hit(a,b):
    s=common(a,b)
    if not s:return None
    return (round(s.Volume,6),bounds(s),
            [xyz(x.Point) for x in s.Vertexes][:12])

def source_shapes():
    ss=g['read_source'](related)
    assert all(n in ss for n in stack_names+['E19_RearBase','E1_populated_prototype_board'])
    return ss

def chosen_rings(src):
    return {ring_in:turned(src[ring_in],pin_in,in_clock),ring_out:turned(src[ring_out],pin_out,out_clock)}
if __name__=='__main__':
    src=source_shapes()
    rings=chosen_rings(src)
    with_rings={**src,**rings}
    print('angles',in_clock,out_clock,'OUT mouth',xyz(mouth_out),'length',sum(e.Length for e in out_edges.values()),
          'straight',straight.tolist(),flush=True)
    for n,shape in rings.items():
        print(n,'bounds',bounds(shape),flush=True)
        for a,s in with_rings.items():
            if a==n or not (h:=solid_hit(shape,s)):continue
            print('hit',a,h,flush=True)
    for k,e in out_edges.items():
        s=sweep(e,outer_r)
        print(k,round(e.Length,3),bounds(s),flush=True)
        for n,actor in with_rings.items():
            h=solid_hit(s,actor)
            if h:print('hit',n,h,flush=True)
