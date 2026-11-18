"""Finish the four witnessed printed crossings with the purchased modules held in place."""
from pathlib import Path
import json,math,ast
import FreeCAD as A,FreeCADGui as G,Part
P=Path(__file__).parent;D=A.ActiveDocument;V=A.Vector
assert Path(D.FileName).resolve()==(P/"body-reception.FCStd").resolve()
for f in ast.parse((P/"integrate-reception.py").read_bytes()).body:
    if isinstance(f,ast.FunctionDef) and f.name in ("show","box","fuse","passage"):exec(compile(ast.Module([f],type_ignores=[]),str(P),"exec"))
facts={};teal=(.23,.40,.42);char=(.15,.16,.18)
def adopt(n,s,old,color,extra=None):
    ok=s.isValid() and len(s.Solids)==1 and all(v<.001 for v in (extra or {}).values())
    facts[n]=dict(solids=len(s.Solids),valid=s.isValid(),active=ok,conditions=extra or {})
    if ok:show(n,s,old,color)
def write():(P/"finished-landings.json").write_bytes((json.dumps(facts,indent=1)+"\n").encode())
# Keep the tie and its lower seat. Finish the old transverse foot flush
# with the underside of the supported cable, away from the fork material.
f=D.BR_YAW_FORK_WITH_SADDLE.Shape
cut=box(-141,-73,127.65,12.5,13.5,5)
adopt("BR_FINISHED_YAW_SADDLE",f.cut(cut).removeSplitter(),"BR_YAW_FORK_WITH_SADDLE",teal,
      {"source_fork_removed":D.HEAD_YAW_FORK_FIXED_PITCH_HOUSING.Shape.common(cut).Volume})
old=D.F2_COMMON_PI_BUS_PCA_RECEIVER.Shape;relief=box(-61,-61,77.8,36,31,43)
rib=fuse(box(-79,-36,90.5,6,12,4.4),box(-79,-36,91.5,6,5,47.5),box(-79,-55.5,135.5,6,25,3.5),
         box(-79,-55.5,135.5,63,5,3.5),box(-20,-55.5,92,4,5,46.5))
carrier=fuse(old.cut(relief),rib)
ns=("PBAY_P_REAR","PBAY_F_AUX","PBAY_F_HY","Motor_ATO4A_1_3","Motor_ATO4A__1_3","Motor_ATO4A_1_4","Pi4B_actual_PCB")
adopt("BR_FORE_ROOT_PI_CARRIER",carrier,"BR_PI_CARRIER_AROUND_LANE",(.18,.24,.28),{n:rib.common(D.getObject(n).Shape).Volume for n in ns})
facts["new_rib_existing_join"]=rib.common(old).Volume;write()
# This standing semicircle is the verified fixed 39 mm radius of the whole
# extension. Open the stationary inner throat along the complete jacket.
def radial(r,t):return V(-111-r*math.sin(t),-54.6,119.5-r*math.cos(t))
def arc(r,rev=False):
    vs=[radial(r,v) for v in (0,math.pi/2,math.pi)];return Part.Arc(*(vs[::-1] if rev else vs)).toShape()
edges=[arc(42.6),Part.makeLine(radial(42.6,math.pi),radial(35.4,math.pi)),arc(35.4,True),Part.makeLine(radial(35.4,0),radial(42.6,0))]
path=Part.Face(Part.Wire(edges)).extrude(V(0,7.2,0)).fuse(box(-112,-55,154.9,46,8,7.2)).fuse(box(-112,-59.2,74.3,32,16.4,12.4))
c=D.BR_CHEST_WITH_COVERED_ENTRIES.Shape
adopt("BR_CHEST_EXTENSION_ENTRY",c.cut(path).removeSplitter(),"BR_CHEST_WITH_COVERED_ENTRIES",char)
# Only the upper positive return has penetrated the retained skull back.
# Preserve the lower continuous side material and both original head joints.
regions=json.loads((P/"covered-passages.json").read_bytes());region=passage(regions["tof"]["pitch"]).common(box(-179,0,158,110,100,52))
b=D.BR_PARTED_SKULL_BACK.Shape;s=b.cut(region).removeSplitter()
ss=sorted(s.Solids,key=lambda v:v.Volume,reverse=True)
facts["cut_back_island_volumes"]=[v.Volume for v in ss]
if len(ss)>1 and sum(v.Volume for v in ss[1:])<.05:s=ss[0]
limits={}
for y in (-73,73):
    land=Part.makeCylinder(4.1,12,V(-165,y,145),V(1,0,0));limits[str(y)]=abs(b.common(land).Volume-s.common(land).Volume)
adopt("BR_BACK_UPPER_RETURN",s,"BR_PARTED_SKULL_BACK",char,limits)
facts["physical_PASS"]=False;write()
D.Label="Body reception - frozen whole front fit";D.recompute();G.runCommand("Std_Save")
