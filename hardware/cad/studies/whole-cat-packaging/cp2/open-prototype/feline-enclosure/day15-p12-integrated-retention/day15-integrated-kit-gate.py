import FreeCAD as A,Part,json,math,time
from pathlib import Path
V=A.Vector;D=A.getDocument('DAY15_P12_INTEGRATED');P=Path(D.FileName).parent;plan=json.loads((P/'whole-integrated-plan.json').read_bytes());T=time.perf_counter();r=dict(status='RUNNING_CHEAP_CHANGED_KIT_GATE',bounds=0,checks=[],first_falsifier=None)
def save():r['seconds']=time.perf_counter()-T;(P/'whole-kit-first-gate.json').write_bytes((json.dumps(r,indent=2)+'\n').encode())
def lo(s,q):
 a=s.BoundBox;b=q.BoundBox;return math.sqrt(sum(max(0,getattr(a,t+'Min')-getattr(b,t+'Max'),getattr(b,t+'Min')-getattr(a,t+'Max'))**2 for t in 'XYZ'))
def gate(n,s,m,q,limit=1.25,role='foreign'):
 lb=lo(s,q)
 if lb>limit+1e-5:r['bounds']+=1;return True
 gap=s.distToShape(q)[0];c=s.common(q) if gap<1e-6 or limit==0 else None;row=dict(a=n,b=m,gap=gap,limit=limit,role=role,common=None if c is None else c.Volume,valid=True if c is None else c.isValid());r['checks'].append(row)
 ok=(c.isValid() and c.Volume<1e-5) if limit==0 else gap>=limit-1e-6
 if not ok:r['status']='FIRST_KIT_HOLD_STOP_ONE_HYPOTHESIS';r['first_falsifier']=row;s.exportBrep(str(P/'kit-witness-a.brep'));q.exportBrep(str(P/'kit-witness-b.brep'));save()
 return ok
def hx(af,z,h):
 rr=af/math.sqrt(3);p=[V(rr*math.cos(math.pi/6+i*math.pi/3),rr*math.sin(math.pi/6+i*math.pi/3),z) for i in range(7)];return Part.Face(Part.Wire(Part.makePolygon(p).Edges)).extrude(V(0,0,h))
def fullfeed(x,y,wy):
 # Exact fullhexnut continuoustranslation as hull, sameorientations as trap.
 rr=5/math.sqrt(3);pp=[(x+rr*math.cos(math.pi/6+i*math.pi/3),yy+rr*math.sin(math.pi/6+i*math.pi/3)) for yy in [y,wy] for i in range(6)];q=sorted(set(pp));cross=lambda o,a,b:(a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0]);a=[];b=[]
 for p in q:
  while len(a)>1 and cross(a[-2],a[-1],p)<=0:a.pop()
  a.append(p)
 for p in reversed(q):
  while len(b)>1 and cross(b[-2],b[-1],p)<=0:b.pop()
  b.append(p)
 poly=a[:-1]+b[:-1];s=Part.Face(Part.Wire(Part.makePolygon([V(xx,yy,94.52) for xx,yy in poly+[poly[0]]]).Edges)).extrude(V(0,0,2));up=hx(5,94.52,11.48);up.translate(V(x,wy,0));return s.fuse(up)
def ringfield(station):
 # Analytic roundedrectangle annulusYZ extruded15 inX: full2.2ribbon, not a purchasedbox.
 def rounded(w,h,rr):
  y=-w/2;z=75.75-h/2;s=Part.makeBox(15,w-2*rr,h,V(station-7.5,y+rr,z)).fuse(Part.makeBox(15,w,h-2*rr,V(station-7.5,y,z+rr)))
  for yy in [y+rr,y+w-rr]:
   for zz in [z+rr,z+h-rr]:s=s.fuse(Part.makeCylinder(rr,15,V(station-7.5,yy,zz),V(1,0,0)))
  return s
 return rounded(46.4,25.9,4.1).cut(rounded(42,21.5,1.9))
fields=[]
for i,x in enumerate([29.5,52.5]):
 loop=ringfield(x);tailLength=plan['whole_stock']['full_remaining_tail'];vertical=tailLength-32-3*math.pi/2;top=Part.makeBox(15,32,2.2,V(x-7.5,-22,88.7));corner=Part.makeCylinder(4.1,15,V(x-7.5,-22,86.8),V(1,0,0)).cut(Part.makeCylinder(1.9,15,V(x-7.5,-22,86.8),V(1,0,0))).common(Part.makeBox(15,5,5,V(x-7.5,-27,86.8)));down=Part.makeBox(15,2.2,vertical,V(x-7.5,-26.1,86.8-vertical));closure=Part.makeBox(20,23,6,V(x-10,-11.5,88.5))
 for kind,s in [('bodyloop_full2p2',loop),('whole_tail',top.fuse(corner).fuse(down)),('closure_fullunit_projectfield',closure)]:
  assert s.isValid();n='STRAP'+str(i)+'_'+kind;o=D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=(.9,.5,.1);o.ViewObject.Transparency=65;fields.append((n,s));r.setdefault('whole_stock',[]).append(dict(name=n,volume=s.Volume,tail_length=tailLength if kind=='whole_tail' else None,closure_actualFIT=True,tail_endZ=86.8-vertical if kind=='whole_tail' else None))
D.recompute();D.save()
def run():
 for st in plan['sets']:
  for n in st['names']:
   for pn in ['P10_front_gate','P12_common_deck_speaker']:
    if not gate(n,D.getObject(n).Shape,pn,D.getObject(pn).Shape,0,'matched_full_internal_stock'):return
  feed=fullfeed(*st['axis'],st['wellY'])
  for pn in ['P10_front_gate','P12_common_deck_speaker']:
   if not gate('full_nut_TOP_THEN_SIDE_'+str(st['axis']),feed,pn,D.getObject(pn).Shape,0,'initialbeforePi no phantomsideexit'):return
 r['Pi_all4_stock_and_full_top_side_feed_clear']=True;save()
 # First real carrierroot/parting gate. Positiveoverlap with separateframe is NOT a root.
 carrier=D.getObject('P19_shared_lower_carrier').Shape
 for pn in ['P10_front_gate','P11_rear_gate','P12_common_deck_speaker']:
  if not gate('P19_shared_lower_carrier',carrier,pn,D.getObject(pn).Shape,0,'separateprint actualrootnonpenetration'):return
 for foot in [(5,-45),(5,41),(95,-45),(95,41)]:
  f=Part.makeBox(5,4,.05,V(foot[0],foot[1],48.52));gap=min(f.distToShape(D.getObject(pn).Shape)[0] for pn in ['P02_front_deck','P03_rear_deck_integrated_load_yoke']);r.setdefault('feet',[]).append(dict(foot=foot,gap=gap));
  if gap>1e-6:r['first_falsifier']=dict(kind='FOOT_NO_ACTUAL_CONTACT',foot=foot,gap=gap);r['status']='FIRST_KIT_HOLD_STOP_ONE_HYPOTHESIS';save();return
 for n,s in fields:
  for pn in ['P10_front_gate','P11_rear_gate','P12_common_deck_speaker','P13_BUS_bridge','P19_shared_lower_carrier']:
   if not gate(n,s,pn,D.getObject(pn).Shape,0 if pn in ['P12_common_deck_speaker','P19_shared_lower_carrier'] else 1.25,'declaredmodelednylonguide/carrier matchedonly elseforeign'):return
  if not gate(n,s,'Battery_GEA223S30X6GT',D.getObject('Battery_GEA223S30X6GT').Shape,0,'declarednoncompressivewholeloopretention'):return
 r['status']='PI_FEED_CARRIER_ROOTS_AND_WHOLE_STRAP_FIELDS_CLEAR_FIRST_SCOPED';save()
run();print(json.dumps(dict(status=r['status'],bounds=r['bounds'],checks=len(r['checks']),first=r['first_falsifier'],Pi_scope=r.get('Pi_all4_stock_and_full_top_side_feed_clear'),seconds=r['seconds'])))
