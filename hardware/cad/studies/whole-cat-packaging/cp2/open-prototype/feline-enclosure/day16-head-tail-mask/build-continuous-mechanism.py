import FreeCAD as A,FreeCADGui as G,Part,json,math,time
from pathlib import Path
from datetime import datetime,timezone
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def cy(x,y,z,r,h,a=V(0,0,1)):return Part.makeCylinder(r,h,V(x,y,z),a)
def fu(ss):
 s=ss[0]
 for q in ss[1:]:s=s.fuse(q)
 return s
def tr(s,r,p):
 q=s.copy();q.rotate(V(),r.Axis,math.degrees(r.Angle));q.translate(p);return q
def ring(z,r,R,h):return cy(0,0,z,R,h).cut(cy(0,0,z-.01,r,h+.02))
def wr(n,d):(P/n).write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
def run():
 if D.getObject('CONTINUOUS_HEAD_TAIL_REAL_PRINTS'):return print('already built; use native checkpoint')
 t=time.perf_counter();gr=D.addObject('App::DocumentObjectGroup','CONTINUOUS_HEAD_TAIL_REAL_PRINTS');ref=D.addObject('App::DocumentObjectGroup','HEAD_FACTORY_REFERENCE_NOT_BOM');parts=[];metals=[];log=[]
 def add(n,s,col=(.22,.55,.61),group=gr,show=True):
  o=D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=col;o.ViewObject.Visibility=show;group.addObject(o);return o
 def part(n,ss,cuts=[],r=None,p=None):
  s=fu(ss)
  for q in cuts:s=s.cut(q)
  missing=[q.cut(fu(cuts)).cut(s).Volume if cuts else q.cut(s).Volume for q in ss]
  if r is not None:s=tr(s,r,p)
  o=add(n,s);parts.append(o);log.append(dict(part=n,valid=s.isValid(),solids=len(s.Solids),intended_missing=missing,volume=s.Volume));return o
 def hardware(n,p,a,L,protr=1,M=2):
  a.normalize();u=V(1,0,0) if abs(a.x)<.9 else V(0,1,0);v=a.cross(u);nt=1.6 if M==2 else 1.3;af=4 if M==2 else 3.2;wh=.3 if M==2 else .25;hr=1.9 if M==2 else 1.6;hh=2 if M==2 else 1.3;wrad=2.5 if M==2 else 1.75
  def cylinder(pt,r,h):return Part.makeCylinder(r,h,pt,a)
  np=p+a*(L-protr-nt);rr=af/math.sqrt(3);poly=[np+(u*math.cos(k*math.pi/3)+v*math.sin(k*math.pi/3))*rr for k in range(6)];nut=Part.Face(Part.makePolygon(poly+[poly[0]])).extrude(a*nt).cut(cylinder(np-a*.01,M/2,nt+.02))
  shapes=[('full_screw',cylinder(p,M/2,L).fuse(cylinder(p-a*hh,hr,hh))),('headwasher',cylinder(p,wrad,wh).cut(cylinder(p-a*.01,M/2+.1,wh+.02))),('nutwasher',cylinder(np-a*wh,wrad,wh).cut(cylinder(np-a*(wh+.01),M/2+.1,wh+.02))),('fullnut',nut)]
  for tag,s in shapes:metals.append(add(n+'_'+tag,s,(.7,.71,.74)))
  return dict(role=n,M=M,length=L,fullnut=True,washers=2,tip_protrusion=protr,status='NEEDED_UNCONFIRMED')
 # One actual source model, no printed spline. Factory horn is NOT in its six solids.
 source=Part.Shape();source.read('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/reference/component-selection-2026-09-22/mg92b-adafruit-2307.step')
 poses={'YAW':(A.Rotation(V(0,0,1),90),V(-126,0,95),25,46,58),'PITCH':(A.Rotation(V(1,0,0),-90),V(-155,-22,141),36,41,50),'TAIL':(A.Rotation(V(0,0,1),-90),V(185,0,112),25,32,48)};bom=[];couplers={}
 for tag,(rot,pos,bottom,top,end) in poses.items():
  old=D.getObject('MG92B_'+{'YAW':'Head_yaw','PITCH':'Head_pitch','TAIL':'Tail'}[tag]);old.Shape=tr(source,rot,pos);old.Label='FULL SOURCE 6solids / '+tag+' / horn+screw originalunits FIT3; NO splineprinted'
  # Whole cross-reference from local source record; capacity, not manufacturer material.
  horn=fu([box(-11,-2.1,13.08,28,4.2,1.95),box(-1.925,-8.35,13.08,3.85,16.7,1.95),cy(0,0,10.5,3.6,5.33),cy(0,0,14.62,2,1.33)])
  add(tag+'_FACTORY_HORN_COMMUNITY_REFERENCE_NOT_SUPPLIER',tr(horn,rot,pos),(.85,.5,.15),ref,False)
  screwcap=cy(0,0,11.83,1.5,4).fuse(cy(0,0,15.83,2.75,2.4));add(tag+'_ORIGINAL_M3x4_PRESENCE_NOT_THREAD_PROOF',tr(screwcap,rot,pos),(.9,.5,.2),ref,False)
  frame=fu([box(-13.5,-11,12,33,22,4.25),cy(-15,-8.5,12,3.3,4.25),cy(21,8.5,12,3.3,4.25)])
  pocket=fu([box(-11.3,-2.4,12.5,28.6,4.8,4),box(-2.225,-8.65,12.5,4.45,17.3,4),cy(0,0,11.9,4.3,7)])
  frame=frame.cut(pocket);dowels=[box(-9.5,7.5,16,3,3,1.75),box(6.5,-10.5,16,3,3,1.75)];frame=fu([frame]+dowels)
  bore=fu([cy(-15,-8.5,10,1.1,12),cy(21,8.5,10,1.1,12)])
  lower=frame.cut(bore);neg=part(tag+'_HORN_KEY_HALF_NEG',[lower.common(box(-30,-20,10,30,40,10))],r=rot,p=pos);poshalf=part(tag+'_HORN_KEY_HALF_POS',[lower.common(box(0,-20,10,30,40,10))],r=rot,p=pos)
  roof=fu([box(-13.5,-11,16.25,33,22,2.4),cy(-15,-8.5,16.25,3.3,2.4),cy(21,8.5,16.25,3.3,2.4)]).cut(cy(0,0,16,3.1,3))
  roof=roof.cut(box(-9.6,7.4,16.2,3.2,3.2,1.7)).cut(box(6.4,-10.6,16.2,3.2,3.2,1.7))
  shaft=ring(18,3.1,3.95,end-18);shoulder=ring(bottom-1.5,3.1,5,1.5)
  rotor=part(tag+'_HORN_ROOF_JOURNAL',[roof,shaft,shoulder],[bore],rot,pos);couplers[tag]=rotor
  for j,(x,y) in enumerate([(-15,-8.5),(21,8.5)]):bom.append(hardware(tag+'_HORN_CAP_M2_'+str(j),pos+rot.multVec(V(x,y,18.95)),rot.multVec(V(0,0,-1)),10,1.15))
 # Fixed yaw housing: change ONLY inner-race rubbing lip into real outer-race lip.
 p10=D.getObject('P10_front_gate');old10=p10.Shape.copy();lipcut=cy(-126,0,118.99,9,1.02);p10.Shape=p10.Shape.cut(lipcut)
 bosses=[];cuts=[];cap=[ring(141,9,15.5,4)]
 for sy in [-1,1]:
  y=14.5*sy;boss=cy(-126,y,130,3.5,11).cut(cy(-126,0,119,11.1,27));bosses.append(boss);cap.append(cy(0,y,141,3.5,4));cuts += [cy(-126,y,130,1.1,16),box(-128.41,min(y,sy*23)-2.2,131.9,4.82,abs(23*sy-y)+4.4,1.8)]
 p10.Shape=fu([p10.Shape]+bosses)
 for q in cuts:p10.Shape=p10.Shape.cut(q)
 # localcap atxy0 -> yawcentre; matched full M2recess/actual nutfeed.
 caps=fu(cap);caps.translate(V(-126,0,0));cc=[]
 for sy in [-1,1]:
  y=14.5*sy;cc += [cy(-126,y,140,1.1,7),cy(-126,y,142.5,2.6,3)];bom.append(hardware('YAW_FIXED_CAP_'+str(sy),V(-126,y,142.8),V(0,0,-1),12,2.8))
 part('YAW_FIXED_OUTER_RACE_CAP',[caps],cc)
 for tag,z,inner,outer,h in [('YAW_OUTER_RACE_SPACER',127,9,11,7),('YAW_INNER_RACE_SPACER',127,4.05,5,7),('YAW_TOP_THRUST',141,4.05,5,6)]:s=ring(z,inner,outer,h);s.translate(V(-126,0,0));part(tag,[s])
 # Actualyawfork carries the fixedpitch housing + whole servo, not cosmetic skin.
 bearing=cy(-155,8.5,141,13,10.5,V(0,1,0)).cut(cy(-155,8.4,141,7,5.7,V(0,1,0))).cut(cy(-155,14,141,8.1,5.1,V(0,1,0)))
 forkss=[box(-139,-50,147,20,69,6),box(-161,8.5,147,42,5,6),bearing,box(-145,-30,118.5,7,7,35)]
 for z in [122,149.5]:forkss.append(box(-148,-30,z-3.5,10,2.5,7))
 forkcuts=[cy(-126,0,145,4.05,12),cy(-145,0,150,1.1,35,V(1,0,0))]
 for z in [128,154]:forkss.append(cy(-155,8.5,z,3.5,10.5,V(0,1,0)));forkcuts.append(cy(-155,6,z,1.1,20,V(0,1,0)))
 fork=part('HEAD_YAW_FORK_FIXED_PITCH_HOUSING',forkss,forkcuts)
 bom.append(hardware('YAW_SHAFT_FORK_POSITIVE_CROSSPIN',V(-139.3,0,150),V(1,0,0),25,2.8))
 cp=[];cpc=[]
 for z in [128,154]:cp.append(cy(-155,19,z,3.5,1.5,V(0,1,0)));cpc.append(cy(-155,18,z,1.1,8,V(0,1,0)));bom.append(hardware('PITCH_BEARING_CAP_'+str(z),V(-155,8.2,z),V(0,1,0),16,1.8))
 cp.append(cy(-155,19,141,13,1.5,V(0,1,0)).cut(cy(-155,18.9,141,7,1.7,V(0,1,0))));part('PITCH_FIXED_OUTER_RACE_CAP',cp,cpc)
 part('PITCH_INNER_THRUST_SPACER',[cy(-155,19,141,5,3,V(0,1,0)).cut(cy(-155,18.99,141,4.05,3.02,V(0,1,0)))])
 # One commonsensorframe; realYoverlap fixesoldY21->22gap. Spine keeps casebolts outsideports.
 ps=[box(-224.6,-32,106,3,62,73),box(-224.6,22,137,69.6,6,8),cy(-155,22,141,7,6,V(0,1,0))];pc=[cy(-155,21,141,4.05,9,V(0,1,0)),cy(-166,25,141,1.1,26,V(1,0,0)),box(-225,-8.5,145,4,17,10)]
 for sy in [-1,1]:
  y=49*sy
  for z in [130,166]:ps += [box(-224.6,min(29*sy,y)-2,z-2,6,abs(y-29*sy)+4,4),box(-221.6,y-2,z-2,55.6,4,4),box(-169,y-3.5,z-3.5,3,7,7)];pc += [cy(-226,y,z,1.1,12,V(1,0,0)),cy(-172,y,z,1.1,14,V(1,0,0))]
 # NoseU-brace places wholeToF close to muzzle; realtwo manufacturer holes, headeredge free.
 ps.append(box(-244,-12,113,22.4,4,20))
 for z in [116.54,129.24]:ps.append(box(-244,-12,z-3,3,11,6));pc.append(cy(-246,-3.81,z,1.1,9,V(1,0,0)))
 for y in [-10.5,10.5]:
  for z in [152.6,165.1]:pc.append(cy(-226,y,z,1.1,9,V(1,0,0)))
 plate=part('HEAD_MOVING_SENSOR_FRAME_AND_COVER_SPINE',ps,pc);bom.append(hardware('PITCH_SHAFT_FRAME_POSITIVE_CROSSPIN',V(-162.3,25,141),V(1,0,0),20,3.8))
 # Realremovable servo saddles: flange pads BELOWear, no newlayer underfactorycentrescrew.
 for tag,(rot,pos,bottom,top,end) in poses.items():
  ss=[box(-10,-10.5,-5.5,2.5,31.5,2.5),box(7.5,-10.5,-5.5,2.5,31.5,2.5)];cut=[]
  for v in [-8.5,19]:ss.append(box(-10,v-1.9,-5.5,20,3.8,2.5));cut.append(cy(0,v,-7,.9,10));bom.append(hardware(tag+'_SOURCE_EAR_'+str(v),pos+rot.multVec(V(0,v,.25)),rot.multVec(V(0,0,-1)),8,.7,1.6))
  if tag=='YAW':
   for u in [-9.5,9.5]:ss += [box(u-2,-26,-5.5,4,18,8.9),box(u-3.5,-27.5,1,7,7,2.4)];cut.append(cy(u,-24,-8,1.1,14));world=pos+rot.multVec(V(u,-24,3.7));bom.append(hardware('YAW_SADDLE_ROOT_'+str(u),world,V(0,0,-1),14,1.4));p10.Shape=p10.Shape.fuse(box(-106,u-3.5,88,8,7,8)).cut(cy(-102,u,83,1.1,18))
  elif tag=='PITCH':
   for v in [-8.5,19]:ss.append(box(8.5,v-3.5,-5.5,7,7,2.5));cut.append(cy(11.5,v,-8,1.1,9));world=pos+rot.multVec(V(11.5,v,-2.7));bom.append(hardware('PITCH_SADDLE_ROOT_'+str(v),world,V(0,-1,0),10,2.8))
  else:
   for u in [-10,10]:ss.append(box(u-3.5,-3.5,-5.5,7,7,2.5));cut.append(cy(u,0,-8,1.1,10));world=pos+rot.multVec(V(u,0,-2.7));bom.append(hardware('TAIL_SADDLE_ROOT_'+str(u),world,V(0,0,-1),10,2.2))
  part(tag+'_REAL_REMOVABLE_SERVO_SADDLE',ss,cut,rot,pos)
 # TailP07actual lowerroot preserved; purposefulcase pocket/receivingplanes, twooutside towers.
 p7=D.getObject('P07_open_tail_root_U');old7=p7.Shape.copy();root=old7.cut(box(160,-20,106.5,55,40,2)).cut(box(178.7,-6.25,89,23.1,12.5,35));ts=[root]
 for sy in [-1,1]:ts += [box(171,12 if sy>0 else -35,104.1,37,23,2.4),box(176,31 if sy>0 else -35,105,18,4,39)]
 topbridge=box(164,-35,141,45,70,3).cut(cy(185,0,140,15.6,5));ts.append(topbridge);p7.Shape=fu(ts)
 for y in [-10,10]:p7.Shape=p7.Shape.cut(cy(185,y,98,1.1,14)).cut(box(182.59,min(y,22 if y>0 else -22)-2.2,101.4,4.82,abs(y-(22 if y>0 else -22))+4.4,2.1))
 cart=[cy(185,0,136,15.5,12).cut(cy(185,0,137,11.1,12)),cy(185,0,144,23.5,4).cut(cy(185,0,143.99,11.1,4.02))];cartcuts=[cy(185,0,135.9,9,1.2)]
 tc=[cy(185,0,148,23.5,4).cut(cy(185,0,147.99,9,4.02))];tcc=[]
 for y in [-20,20]:cartcuts.append(cy(185,y,140,1.1,10));tcc.extend([cy(185,y,147,1.1,7),cy(185,y,149.5,2.6,4)]);p7.Shape=p7.Shape.cut(cy(185,y,138,1.1,7));bom.append(hardware('TAIL_CARTRIDGE_CAP_ROOT_'+str(y),V(185,y,149.8),V(0,0,-1),14,3.3))
 part('TAIL_FIXED_BEARING_CARTRIDGE',cart,cartcuts);part('TAIL_FIXED_OUTER_RACE_CAP',tc,tcc)
 for n,z,ir,orr,h in [('TAIL_OUTER_RACE_SPACER',144,9,11,4),('TAIL_INNER_THRUST',144,4.05,5,10)]:s=ring(z,ir,orr,h);s.translate(V(185,0,0));part(n,[s])
 # Curvedoutertail abovefunctionalroot retained; no lengthening. Newhollowwall/rootplug.
 oldtail=D.getObject('Ola_tail_ENVELOPE');outer=oldtail.Shape.copy();w=[Part.Wire(Part.makeCircle(r,V(x,0,z),V(1,0,1))) for x,z,r in [(185,142,5.6),(210,165,4.6),(229,199,2.6),(232.5,211.6,.6)]];inner=Part.makeLoft(w,True,False);tail=outer.cut(inner).common(box(170,-20,153,90,40,90));plug=outer.common(box(170,-20,153,50,40,9));hub=cy(185,0,154,7,6).cut(cy(185,0,153.9,4.05,6.2));tailpart=part('TAIL_ROTATING_HOLLOW_REAL_ROOT',[tail,plug,hub,box(185,-6,154,17,12,6)],[cy(185,-13,157,1.1,28,V(0,1,0))]);tailpart.ViewObject.ShapeColor=(.09,.09,.1);bom.append(hardware('TAIL_POSITIVE_CROSSPIN',V(185,-7.3,157),V(0,1,0),20,3.8));oldtail.ViewObject.Visibility=False;oldtail.Label='RETIRED visualroot below153 / unchangedcurvedouterabove153 now hollowworkingpart'
 for n in ['Neck_shared_root','HEAD_MOVING_SENSOR_PLATE_PROPOSED','HEAD_MOVING_PITCH_ARM_PROPOSED','HEAD_BEARING_UPPER_RETAINER_NOT_SKIN']:
  o=D.getObject(n)
  if o:o.ViewObject.Visibility=False;o.Label='RETIRED UNBUILT role replaced by real continuousmechanism / '+n
 D.Label='DAY16 CONTINUOUS HEAD TAIL / FACTORY HORN CAPTURE NOMINAL FIT3';D.recompute();D.saveAs(str(P/'head-tail-mask.FCStd'));G.getDocument(D.Name).Modified=False
 wr('mechanism-realization.json',dict(utc=datetime.now(timezone.utc).isoformat(),source_actual3MG6solids=True,factoryhorn_NOT_inSTEP=True,communitycross_is_capacity_not_manufacturer=True,original_factoryhorn_and_screw_retained=True,no_printed_spline=True,no_print_under_factory_centrescrew=True,head_factoryscrew_M3x4_label_NOT_threadmeasurement=True,sourceSTEPcentralbore_not_threadqualification=True,parts=log,fasteners=bom,project_travel=dict(yawZ20=True,pitchY10=True,tailZ20=True,no_power=True),actualheadload='P10actualbridge->608outerraces->independentjournalinnerfaces->crosspin/yawfork->688->headplate/crosspin->sensors/covers',actualtailload='P07actualbase->outside_towers/bridge->separatebearingcartridge608->journal->crosspin/rootshoe->retainedcurvedtail',assembly='benchhorn+twokeyhalves+roof; originalfactoryscrew seated throughcentralaccess, NOaddedstack; yawunit frombelowthen realremovablesaddle; pitchunit from-Ythen saddle/headplate/crosspin; tailunitfromaboveP07withnewseparatebearingcartridge then nuts/cap androotshoe; skinsLATE',physical_FIT3='one actualMG/horn/screw and608/688 seats/races measured; communityhorn has no manufacturerholes guarantee',tailfunctional_root_replaced_below153=True,tailoutside_above153_same_outersource_subset=True,bought_bearings_unchanged=True,no_STLrelease=True,wholekit_ready=False,physical_pass=False,actual_fit_cut_slack=None,seconds=time.perf_counter()-t,objects=len(D.Objects)))
 print(json.dumps(dict(saved=D.FileName,parts=len(parts),construction_defects=[q for q in log if not q['valid'] or q['solids']!=1 or max(q['intended_missing'] or [0])>1e-5],objects=len(D.Objects),seconds=time.perf_counter()-t)))
run()
