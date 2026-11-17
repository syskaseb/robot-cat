import FreeCAD as A, json, time
from pathlib import Path
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent
def bb(s):
 b=s.BoundBox;return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def lower(a,b):
 a=bb(a);b=bb(b);return sum(max(0,a[i]-b[i+3],b[i]-a[i+3])**2 for i in range(3))**.5
def run():
 rows=[];first=None;t=time.perf_counter()
 for yaw,pitch in [(0,0),(-20,-10),(-20,0),(-20,10),(0,-10),(0,10),(20,-10),(20,0),(20,10)]:
  for hn,kind in [('MG92B_Head_pitch','yaw'),('HEAD_YAW_FORK_FIXED_PITCH_HOUSING','yaw'),('HEAD_MOVING_SENSOR_FRAME_AND_COVER_SPINE','pitch')]:
   q=D.getObject(hn).Shape.copy()
   if kind=='pitch':q.rotate(V(-135,0,121),V(0,1,0),pitch)
   q.rotate(V(-106,0,127),V(0,0,1),yaw)
   for pn in ['Pi_components_and_cooling','Pi_GPIO1992_factory_female','Pi_USB_DATA_Delock_mating','Pi4B_actual_PCB']:
    s=D.getObject(pn).Shape;l=lower(s,q);r={'Pi':pn,'head':hn,'yaw':yaw,'pitch':pitch,'bound_lower':l,'threshold':1.25}
    if l>=1.25:r.update(method='actual_bound_lower',clear_scoped=True)
    else:
     valid=s.isValid() and q.isValid();dist=s.distToShape(q)[0] if valid else None;r.update(method='named_actual_nearshape',valid=valid,gap=dist,clear_scoped=valid and dist>=1.25-1e-7)
     if not r['clear_scoped']:
      if valid:
       c=s.common(q);r.update(common=c.Volume,common_valid=c.isValid())
      if first is None:first=r
    rows.append(r)
    (P/'independent-head-nine-sample-gate.json').write_text(json.dumps({'rows':rows,'first':first,'whole_motion_PASS':False,'seconds':time.perf_counter()-t,'scope':'selectedONEverticalfixedPi only; independent of rearF0HOLD. Stop on first sample falsifier; no pose repair/grid.'},indent=2)+'\n',encoding='utf-8')
    if first:break
   if first:break
  if first:break
 print(json.dumps({'first':first,'checks':len(rows),'seconds':time.perf_counter()-t}))
run()
