import FreeCAD as A,Part,math,json,time
from pathlib import Path
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent
ns={'__file__':str(P/'build-real-hollow-body.py')};exec((P/'build-real-hollow-body.py').read_text(encoding='utf-8').split('def run():')[0],ns)
stations=ns['stations'];put=ns['put'];box=ns['box'];fuse=ns['fuse'];bb=ns['bb'];obj=ns['obj']
def pars(x):
 for a,b in zip(stations,stations[1:]):
  if a[0]<=x<=b[0]:
   u=(x-a[0])/(b[0]-a[0]);return [x]+[a[i]*(1-u)+b[i]*u for i in range(1,4)]
 return list(stations[0] if x<stations[0][0] else stations[-1])
def arc(s,sy,inset=0):
 x,ry,lo,hi=s;ry-=inset;lo+=inset;hi-=inset;c=(lo+hi)/2;rz=(hi-lo)/2;pts=[]
 for k in range(25):
  t=-math.pi/2+math.pi*k/24;co=max(0,math.cos(t));si=math.sin(t)
  pts.append(V(x,sy*ry*co**(2/2.6),c+rz*math.copysign(abs(si)**(2/2.6),si)))
 q=Part.BSplineCurve();q.interpolate(pts);return q.toShape(),pts
def profile(s,sy,hollow=True):
 a,ap=arc(s,sy)
 if not hollow:return Part.Wire([a,Part.makeLine(ap[-1],ap[0])])
 b,bp=arc(s,sy,2);b.reverse()
 return Part.Wire([a,Part.makeLine(ap[-1],bp[-1]),b,Part.makeLine(bp[0],ap[0])])
def run():
 t=time.perf_counter();D.save();raw=[]
 for tag in ['F_NEG','F_POS','R_NEG','R_POS']:
  o=D.getObject('HB_'+tag)
  if not (P/(o.Name+'.raw-unreceived.brep')).exists():o.Shape.exportBrep(str(P/(o.Name+'.raw-unreceived.brep')))
  raw.append({'name':o.Name,'volume':o.Shape.Volume,'valid':o.Shape.isValid()})
 if not (P/'raw-periodic-split-representation-HOLD.json').exists():put('raw-periodic-split-representation-HOLD.json',{'parts':raw,'reason':'Periodic full-shell split returned one invalid part and inconsistent total split volume; no STL accepted. Rebuild SAME section-function as four direct half-ring lofts.'})
 root=D.getObject('TAIL_ROTATING_HOLLOW_REAL_ROOT').Shape;tr=max(math.hypot(v.Point.x-140,v.Point.z-130) for v in root.Vertexes)+1.25
 tail=Part.makeCylinder(tr,root.BoundBox.YLength+2.5,V(140,root.BoundBox.YMin-1.25,130),V(0,1,0))
 cuts=[box(-190,-77,79,108,154,106),tail,Part.makeCylinder(23,100,V(88.5,-145,108),V(0,1,0)),box(104.5,-145,104.5,44,62,28),Part.makeCylinder(17,100,V(49,-145,119),V(0,1,0))]
 cuts += [Part.makeCylinder(20,55,V(x,82,122.5),V(0,1,0)) for x in [-76,-24]]
 cooling=Part.makeCompound([Part.makeCylinder(2.5,60,V(x,-145,z),V(0,1,0)) for x in [-119,-109,-99,-89,-79,-69,-59,-49] for z in [66,78,90]])
 mic=Part.makeCompound([Part.makeCylinder(2,55,V(x,-10,143),V(0,0,1)) for x in [27,45,63,81,94]])
 rows=[]
 for tag,sy,lo,hi in [('F_NEG',-1,-168,10),('F_POS',1,-168,10),('R_NEG',-1,10,197),('R_POS',1,10,197)]:
  ss=[pars(lo)]+[list(s) for s in stations if lo<s[0]<hi]+[pars(hi)]
  q=Part.makeLoft([profile(s,sy) for s in ss],True,False)
  outside=Part.makeLoft([profile(s,sy,False) for s in ss],True,False)
  # Real end cap on front and rump; no provisional solid outer is selected material.
  if lo==-168:q=q.fuse(outside.common(box(-168,-140,20,2,280,190)))
  if hi==197:q=q.fuse(outside.common(box(195,-140,20,2,280,190)))
  for c in cuts+[cooling,mic]:
   if c.BoundBox.intersect(q.BoundBox):q=q.cut(c)
  for x in [-70,70,145]:
   if not lo<x<hi:continue
   old=D.getObject('CLOSED_BODY_'+('front' if x<30 else 'rear')+'_'+('positive' if sy>0 else 'negative')).Shape
   tab=old.common(box(x-6,66 if sy>0 else -86,43.62,12,20,2.4))
   rib=box(x-6,65 if sy>0 else -123,43.62,12,58,2.4).common(outside)
   deck=D.getObject('P02_front_deck' if x<30 else 'P03_rear_deck_integrated_load_yoke').Shape
   rib=rib.cut(deck).cut(Part.makeCylinder(1.7,20,V(x,sy*72,35)))
   q=q.fuse(tab).fuse(rib)
  # Six actual keyed BASE bolts retain the covers. Crown uses a slip-key,
  # avoiding hidden screw access after the electronics have been installed.
  cx=-40 if lo==-168 else 45;top=pars(cx)[3]
  flange=box(cx-7,-6 if sy<0 else 0,top-7.5,14,6,6)
  key=box(cx-5,0,top-4,10,4,2)
  if sy<0:q=q.fuse(flange).fuse(key)
  else:q=q.fuse(flange).cut(box(cx-5.25,-.25,top-4.25,10.5,4.5,2.5))
  # SAME received side-tool access: the new wall must not close the approach.
  for x in [-70,70,145]:
   if lo<x<hi:q=q.cut(box(x-16.2,70 if sy>0 else -115,40.87,32.4,45,2.75))
  q=q.removeSplitter();o=obj('HB_'+tag,q)
  rows.append({'name':o.Name,'valid':q.isValid(),'solids':len(q.Solids),'volume':q.Volume,'bounds':bb(q),'crown_slip_key':[cx,0,top-3],'base_bolts_are_retention':True})
  D.recompute();D.save();put('direct-half-ring-body-checkpoint.json',{'rows':rows,'cursor':len(rows),'seconds':time.perf_counter()-t,'scope':'Direct hollow profile loft, four separate physical prints; raw failed periodic split retained','wholePASS':False})
 print(json.dumps({'rows':rows,'seconds':time.perf_counter()-t}))
run()
