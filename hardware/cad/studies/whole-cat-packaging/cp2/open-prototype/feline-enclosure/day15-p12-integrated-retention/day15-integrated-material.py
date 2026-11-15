import FreeCAD as A,FreeCADGui as G,Part,MeshPart,json,math,time
from pathlib import Path
V=A.Vector;D=A.getDocument('DAY15_P12_INTEGRATED');P=Path(D.FileName).parent;plan=json.loads((P/'whole-integrated-plan.json').read_bytes());T=time.perf_counter();before={n:D.getObject(n).Shape.copy() for n in ['P10_front_gate','P11_rear_gate','P12_common_deck_speaker']};parts=dict(before);members=[];cuts=[];grup=D.addObject('App::DocumentObjectGroup','INTEGRATED_GUIDE_AND_CARRIER_CHANGED_MATERIAL');r=dict(status='BUILDING_ONE_COUPLED_INTERFACE',Pi=[],guide=[],carrier=[],first_falsifier=None)
def box(x,y,z,dx,dy,dz):return Part.makeBox(dx,dy,dz,V(x,y,z))
def hx(af,z,h):
 rr=af/math.sqrt(3);pp=[V(rr*math.cos(math.pi/6+i*math.pi/3),rr*math.sin(math.pi/6+i*math.pi/3),z) for i in range(7)];return Part.Face(Part.Wire(Part.makePolygon(pp).Edges)).extrude(V(0,0,h))
def hull(pp):
 q=sorted(set(pp));cross=lambda o,a,b:(a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0]);a=[];b=[]
 for p in q:
  while len(a)>1 and cross(a[-2],a[-1],p)<=0:a.pop()
  a.append(p)
 for p in reversed(q):
  while len(b)>1 and cross(b[-2],b[-1],p)<=0:b.pop()
  b.append(p)
 return a[:-1]+b[:-1]
def feed(af,x,y,wy,z,h):
 rr=af/math.sqrt(3);pp=hull([(x+rr*math.cos(math.pi/6+i*math.pi/3),yy+rr*math.sin(math.pi/6+i*math.pi/3)) for yy in [y,wy] for i in range(6)]);return Part.Face(Part.Wire(Part.makePolygon([V(a,b,z) for a,b in pp+[pp[0]]]).Edges)).extrude(V(0,0,h))
pi_cut=None
for i,st in enumerate(plan['sets']):
 x,y=st['axis'];owner=st['owner'];foot=Part.makeCylinder(4.5,4.1,V(x,y,92.42)).fuse(Part.makeCone(4.5,2.5,2,V(x,y,96.52)));contact=parts[owner].common(foot).Volume;parts[owner]=parts[owner].fuse(foot);members.append((owner,'Pi_foot'+str(i),foot));nf=feed(5.2,x,y,st['wellY'],94.42,2.1);well=Part.makeCylinder(3.1,5,V(x,st['wellY'],94.42));bore=Part.makeCylinder(1.375,8,V(x,y,92.3));cut=nf.fuse(well).fuse(bore);parts[owner]=parts[owner].cut(cut);cuts.append(cut);pi_cut=cut if pi_cut is None else pi_cut.fuse(cut)
 r['Pi'].append(dict(axis=[x,y],owner=owner,actual_positive_added_root=contact,nutroof2=True,floor2=True,source_post_height3=True,toploadingwell=[x,st['wellY']],initiallay='well open beforePCB; dropfullnut vertically thenpushside8mm; upperwasher/bolt afterPi; no virtualthread'))
# Two purposeful matchedcloth guidevoids, roundedXZ corners, whole protected CSseats stayoutside.
guidecuts=[]
for station in [29.5,52.5]:
 w=16.2;h=5.2;rr=.4;z=86.1;void=box(station-w/2+rr,-30,z,w-2*rr,60,h).fuse(box(station-w/2,-30,z+rr,w,60,h-2*rr))
 for xx in [station-w/2+rr,station+w/2-rr]:
  for zz in [z+rr,z+h-rr]:void=void.fuse(Part.makeCylinder(rr,60,V(xx,-30,zz),V(0,1,0)))
 guidecuts.append(void);parts['P12_common_deck_speaker']=parts['P12_common_deck_speaker'].cut(void);r['guide'].append(dict(station=station,width=w,voidZ=[86.1,91.3],full_two_layers4p4=True,nominal_own_clearance=[.6,.4],remaining_rail_roof4p7=True,minimum_rail_section18p8=True,sidewalls='originalprotectedrail eachsideX, no detachedparts or labelOWN'))
allcut=pi_cut
for q in guidecuts:allcut=allcut.fuse(q)
# ONE real lowercarrier connectedmembers; no oldunbuilt tray/crossarms as secondphysicalparent.
C=[]
def cm(name,s):C.append((name,s));return s
cm('tray',box(-5,-21,60.8,113,42,4.2))
for x in [5,95]:
 cm('crossarm'+str(x),box(x,-45,62,5,90,3))
 for y in [-45,41]:cm('deckfoot'+str(x)+'_'+str(y),box(x,y,48.52,5,4,14.48))
cm('MTA_commonfloor',box(-98,-48.5,64,177,10.1,3));cm('frontloadpad',box(-98,-48.5,64,8,17.5,3));cm('frontflange',box(-98,-39,64,4,8,12));cm('rearloadpad',box(91,-39,62,9,8,5));cm('rearflange',box(91,-39,64,4,8,12))
# Samecarrier two broadendstops, not pressure onsoftpack; completeMTAhold-down physicalcasefitremainsadjustabletrial.
cm('batteryendstopfront',box(-5,-21,65,3,42,3));cm('batteryendstoprear',box(104.5,-21,65,3.5,42,3))
carrier=C[0][1]
for n,s in C[1:]:carrier=carrier.fuse(s)
for station in [29.5,52.5]:carrier=carrier.cut(box(station-8.1,-26,62.8,16.2,52,3))
frontbore=Part.makeCylinder(1.65,20,V(-110,-35,70),V(1,0,0));rearbore=Part.makeCylinder(1.65,30,V(80,-35,70),V(1,0,0));carrier=carrier.cut(frontbore).cut(rearbore);parts['P10_front_gate']=parts['P10_front_gate'].cut(frontbore);parts['P11_rear_gate']=parts['P11_rear_gate'].cut(rearbore)
parts['P19_shared_lower_carrier']=carrier
for n,s in parts.items():
 assert s.isValid(),n
 o=D.getObject(n) or D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=(.35,.65,.8);grup.addObject(o);s.exportBrep(str(P/(n+'.brep')))
 # Each fullsavedmaterial first, beforefullneighbors.
 r.setdefault('parts',[]).append(dict(name=n,valid=True,solids=len(s.Solids),bounds=str(s.BoundBox),volume=s.Volume))
for o in D.getObject('Retained_whole_layout_REFERENCE').Group:
 if o.Name=='Battery_tray_shared' or o.Name.startswith(('Battery_crossarm_','Battery_edgepost_')):o.ViewObject.Visibility=False
(P/'material-build-first.json').write_bytes((json.dumps(r,indent=2)+'\n').encode());D.recompute();D.save()
# Membercoverage exceptdeclaredfunctionalholes/guidecuts, includingcarrier actualallmembers.
for owner,name,s in members:
 intended=s.cut(allcut);m=intended.cut(parts[owner]);r['Pi'].append(dict(member=name,owner=owner,missing=m.Volume));assert m.Volume<1e-5
for name,s in C:
 intended=s.cut(frontbore).cut(rearbore)
 for station in [29.5,52.5]:intended=intended.cut(box(station-8.1,-26,62.8,16.2,52,3))
 m=intended.cut(carrier);r['carrier'].append(dict(member=name,missing=m.Volume));assert m.Volume<1e-5
for n in ['P10_front_gate','P11_rear_gate','P12_common_deck_speaker']:
 expected=before[n].cut(allcut).cut(frontbore if n=='P10_front_gate' else rearbore if n=='P11_rear_gate' else Part.makeCompound([]));missing=expected.cut(parts[n]);r.setdefault('protected_original',[]).append(dict(name=n,undeclared_missing=missing.Volume));assert missing.Volume<1e-5
r['status']='MATERIAL_MEMBERS_SAVED_AND_COVERED_BEFORE_CHEAP_KIT_GATE';r['seconds']=time.perf_counter()-T;(P/'material-result.json').write_bytes((json.dumps(r,indent=2)+'\n').encode());print(json.dumps(dict(status=r['status'],parts=r['parts'],seconds=r['seconds'])))
