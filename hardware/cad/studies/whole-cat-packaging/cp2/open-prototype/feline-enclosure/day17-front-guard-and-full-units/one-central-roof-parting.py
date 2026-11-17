import FreeCAD as A,FreeCADGui as G,Part,json,math
from pathlib import Path
P=Path(__file__).parent;D=A.ActiveDocument;V=A.Vector
put=lambda n,j:(P/n).write_bytes((json.dumps(j,indent=2)+'\n').encode())
def bb(s):
 b=s.optimalBoundingBox(False,True);return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
D.save();cap=D.getObject('HC_BACK_UPPER');old=cap.Shape.copy();old.exportBrep(str(P/'source87c_HC_BACK_UPPER.brep'))
# One actual functionalcentralroofparting, leaving realY+-49 sourceprimarylands.
cut=Part.makeBox(100,72,100,V(-216,-36,149.5));q=old.cut(cut).removeSplitter();cap.Shape=q
rows=[]
for y,p,n in [(0,0,'N17_FFC200_OCCUPIED_0_0'),(-20,10,'N17_FFC200_OCCUPIED_m20_10'),(20,10,'N17_FFC200_OCCUPIED_20_10')]:
 f=D.getObject(n).Shape.copy();f.rotate(V(-106,0,127),V(0,0,1),-y);f.rotate(V(-135,0,121),V(0,1,0),-p);c=f.common(q);rows.append({'y':y,'p':p,'field_local_bounds':bb(f),'field_WORLD_bounds':bb(D.getObject(n).Shape),'remaining_commonV':c.Volume,'gap':f.distToShape(q)[0]})
put('actual-one-central-roof-parting.json',{'source_bounds':bb(old),'remaining_bounds':bb(q),'remaining_valid':q.isValid(),'remaining_solids':len(q.Solids),'explicit_retired_roof':str(cut.BoundBox),'protected_outside_missing':old.cut(cut).cut(q).Volume,'rows':rows,'member_replacement':'centralroof function replaced by movingarch + latefixedshoulderguard; notunplug/cutstock, notyetwholeclosurePASS'})
for n in ['MAIN_Pololu4853','AUX_Pololu4092','LanbergUSB500','Pi_USB_DATA_Delock_mating','A17_INTEGRAL_FRONT_DECK_AND_N1']:
 o=D.getObject(n)
 if o:print(n,bb(o.Shape))
D.recompute();D.save();print(json.dumps({'roof':bb(q),'solids':len(q.Solids),'rows':rows}))
