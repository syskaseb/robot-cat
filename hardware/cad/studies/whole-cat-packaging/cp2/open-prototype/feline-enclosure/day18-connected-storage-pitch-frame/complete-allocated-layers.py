import FreeCAD as A,json,pathlib
D=A.ActiveDocument;P=pathlib.Path(__file__).parent;V=A.Vector;changes=[]
def mv(names,old,new,angle=0):
 R=A.Rotation(V(1,0,0),angle);T=A.Placement(V(*new)-R.multVec(V(*old)),R)
 for n in names:
  o=D.getObject(n);v=o.Shape.Volume;o.Placement=T.multiply(o.Placement);b=o.Shape.BoundBox
  changes.append(dict(name=n,volume_before=v,volume_after=o.Shape.Volume,bounds=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax],transform=T.toMatrix().A))
# Whole low speaker takes the side acoustic lane between GPIO-end and MTA, not the DATA plug volume.
mv(['Speaker'],[-10,-7.5,84.5],[-44,44.5,98.5],90)
mv(['MAX98357A_amp']+[o.Name for o in D.Objects if o.Name.startswith('CB_AMP_') and o.ViewObject.Visibility],[0,0,0],[-9,0,0])
mv(['TTP223_touch'],[-45,27,134],[-31,-6,146])
fore=[];rear=[]
for o in D.Objects:
 if not o.Name.startswith('WAGO415_data') or not o.ViewObject.Visibility:continue
 b=o.Shape.BoundBox
 if b.XMin<0 and b.YMin<-56 and b.ZMin>130:fore.append(o.Name)
 if b.XMin>80 and b.YMax<0:rear.append(o.Name)
mv(fore,[0,0,0],[0,1.5,0])
mv(rear,[0,0,0],[7,0,0])
(P/'coherent-layer-completion-delta.json').write_bytes((json.dumps(dict(changes=changes,reason='Complete full fixed side acoustic lane, touch-access plane and terminal assembly around complete relocated E1; no bought shape changed; retired mounts remain unbuilt',invalidated_interfaces=['speaker holder/acoustic opening','AMP common support','TTP fixed support/BCM27 budget','rear negative terminal common rail/branch upper lengths','fore negative outer terminal common rail']),indent=2)+'\n').encode())
print('FUNCTIONAL_LAYER_COMPLETION',len(changes),fore,rear)
