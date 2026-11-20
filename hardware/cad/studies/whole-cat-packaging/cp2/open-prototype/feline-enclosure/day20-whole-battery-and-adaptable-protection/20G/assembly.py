"""Prewire both existing S0 stacks on an open bench, then seat S0 before E1."""
from pathlib import Path
from runpy import run_path
import math
import FreeCAD as App
import Part

p=Path(__file__).resolve().parent
g=run_path(str(p/'candidate.py'))
V=App.Vector
box=g['box']; common=g['common']; bounds=g['bounds']
src=g['source_shapes']()
rings=g['chosen_rings'](src)
parts={**src,**rings}
stack={n:parts[n] for n in g['stack_names']}
holds=['E19_RearBase','H19_FrontFrame','E19_EarlyS0Brace','PBAY_P_SYS','PBAY_F_PI','PCA9685_Adafruit815_PCB',
       'S0_key','E19_KeyedTail','D19_BODY_CONTROL_TRUNK','G19_Group_POWER','G19_Group_I2S','H19_PowerBranch',
       'E19_BatteryDoor','C20_BatteryUpperBridge','H19_Wires_speaker','NIGHT_INLINE_RR_W052','NIGHT_INLINE_RR_W053']
stack_growth=64.
inboard=-6.
def shift(s,dd):
    a=s.copy();a.translate(dd);return a
def bbvals(s):
    b=s.BoundBox
    return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def under(s,dy):
    return shift(s,V(0,dy,0))
def drop_shape(n,s):
    t=under(s,inboard)
    b=bbvals(t)
    if n in ('S0_body','S0_neck') and len(t.Solids)==1:
        z=(b[2]+b[5])/2
        core=box([b[0],b[1],z,b[3],b[4],z+stack_growth])
        return t.fuse(core).fuse(shift(t,V(0,0,stack_growth))).removeSplitter()
    return box([*b[:3],*b[3:5],b[5]+stack_growth])
def axial_shape(n,s):
    b=bbvals(s)
    if n in ('S0_body','S0_neck'):
        a=V((b[0]+b[3])/2,b[1]+inboard,(b[2]+b[5])/2)
        return Part.makeCylinder((b[3]-b[0])/2,b[4]-b[1]-inboard,a,V(0,1,0))
    b[1]+=inboard
    return box(b)
def record(a,b):
    h=common(a,b)
    if h:
        return {'overlap_mm3':round(h.Volume,6),'bounds_mm':bounds(h),
                'vertex_xyz':[g['xyz'](v.Point) for v in h.Vertexes][:16]}
    return None
if __name__=='__main__':
    for phase,shape in [('vertical_top_drop',drop_shape),('axial_seating',axial_shape)]:
        print(phase,flush=True)
        for n,s in stack.items():
            q=shape(n,s)
            for key in holds:
                target=parts.get(key)
                if target is None or key=='S0_key':
                    continue
                if hit:=record(q,target):print(n,key,hit,flush=True)
    for at in ('IN','OUT'):
        other='OUT' if at=='IN' else 'IN'
        x,z=(166.5,104.5) if at=='IN' else (190.5,104.5)
        tool=Part.makeCylinder(12,34,V(x,70.95,z),V(0,-1,0))
        for obj in (f'S0_ring_{other}_0_0',f'S0_nut_{other}_0_0',f'S0_washer_{other}_0_0',
                    f'S0_stud_{other}_0_0',f'S0_ring_{at}_0_0'):
            if hit:=record(tool,stack[obj]):print('bench socket',at,obj,hit,flush=True)
    # Leave the wedge and E1 out of the bench operation. Check rigid source
    # E1 placement past both already tightened rings in the on-frame stack.
    e1=src['E1_populated_prototype_board']
    b=bbvals(e1);b[5]+=64
    lift=box(b)
    print('E1 upper insertion after S0',flush=True)
    for n,s in stack.items():
        if hit:=record(lift,s):print('E1 vs',n,hit,flush=True)
    regions={
      'P_SYS.1_lever_approach':box([156,48.3,67.5,166.5,56.8,89]),
      'P_SYS.1_terminal_hand_space':box([165,47.5,57.5,184,57.,79.5]),
    }
    print('end access with E1 in place',flush=True)
    for label,s in regions.items():
        for obj in ['E19_RearBase','E1_populated_prototype_board','S0_body','PBAY_F_PI','C20_MTA_RR',
                    'S0_ring_IN_0_0','S0_ring_OUT_0_0','D19_SIDE_BUNDLE_POS']:
            if hit:=record(s,parts[obj]):print(label,obj,hit,flush=True)
