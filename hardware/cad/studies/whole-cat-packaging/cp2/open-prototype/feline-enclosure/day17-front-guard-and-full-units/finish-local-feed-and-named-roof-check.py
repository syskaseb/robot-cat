import FreeCAD as A,FreeCADGui as G,Part,json,math,time
from pathlib import Path
P=Path(__file__).parent;D=A.ActiveDocument;V=A.Vector;t0=time.perf_counter()
put=lambda n,j:(P/n).write_bytes((json.dumps(j,indent=2)+'\n').encode())
def bx(x,y,z,a,b,c):return Part.makeBox(a,b,c,V(x,y,z))
def cy(x,y,z,r,h,axis=V(0,0,1)):return Part.makeCylinder(r,h,V(x,y,z),axis)
D.save();base=D.getObject('CF17_SHARED_FIXED_PI_BUS_POWER_CARRIER');hood=D.getObject('FU17_LATE_FIXED_SHOULDER_HOOD')
# True fullAF4 antirotation below independentfullwasherfeed. Clocknut30deg, not smallerstock.
for i,y in enumerate([-19,24.5]):
 for a,b in [(y-2.7,y-2.1),(y+2.1,y+2.7)]:base.Shape=base.Shape.fuse(bx(-36.5,a,178.9,7,b-a,1.8))
 o=D.getObject('FU17_HOOD_'+str(i)+'_fullnut');s=o.Shape.copy();s.rotate(V(-33,y,179.1),V(0,0,1),30);o.Shape=s;o.Placement=A.Placement()
 hood.Shape=hood.Shape.cut(cy(-33,y,189.8,3,30))
# Standard90degree fullhead WITH .2rim, sameD4/k1.2/M2CSK10; physicalscrew coupon below.
for x in [-41.5,-4.5]:
 for z in [97,125]:
  n='CF17_BUS_CSK10_'+str(x).replace('-','m').replace('.','p')+'_'+str(z);o=D.getObject(n)
  if o:
   head=cy(x,-19.5,z,2,.2,V(0,1,0)).fuse(Part.makeCone(2,1,1,V(x,-19.3,z),V(0,1,0)));stem=cy(x,-18.3,z,1,8.8,V(0,1,0));o.Shape=head.fuse(stem);base.Shape=base.Shape.cut(head)
put('hood-real-feed-tool-and-seat.json',{'AF4fullnuts':'clocked30, opposedflatsY4 ->actual4.2antirotationslot Z178.9..180.7; fullD5washerstill5.4feedslotat180.7..181','nutwasherloading':'open+X beforehood. WasherfirstthenAF4nutbelow; upper6mmroof/capturednuts; notrequireholdingvirtualfullnutin5.4square','toptool':'2realR3throughroof190..220, M2bolt/headD3.8andwasherD5pass; actual1.5hexdriverfromabove beforeouterdecorativecovers','BUS90':'nominal4fullM2CSK10 heads D4/k1.2: .2rim+1.0cone90. Samefullnut/engagement. Supersedes87c plainfrustumprojecthead, notsuppliercut/shrink. actualheadseat/printtolerance onecoupon.'})
# A two-solid sourcebodyresult is a real remainingparting issue, notsilentlyfused/hidden.
q=D.getObject('FC_F_NEG').Shape;put('current-body-side-parting-remaining.json',{'negative_solids':[{'V':s.Volume,'bounds':str(s.BoundBox)} for s in q.Solids],'status':'IFdisconnectedmembernoexistingroot thenBODYCLOSUREHOLD; notretiredbyname/notautomaticSTL','other_bodyparts_unchanged':'sourcefloor/speaker/currentoperator/source6floorrootsoutsidetopwindow preserved'})
rows=[]
# Existing3criticalfullFFCfields only, SAMEfields no sweepreplay. Matchedmovingroofandnewfixedhood.
for y,p,n in [(0,0,'N17_FFC200_OCCUPIED_0_0'),(-20,10,'N17_FFC200_OCCUPIED_m20_10'),(20,10,'N17_FFC200_OCCUPIED_20_10')]:
 cap=D.getObject('HC_BACK_UPPER').Shape.copy();cap.rotate(V(-135,0,121),V(0,1,0),p);cap.rotate(V(-106,0,127),V(0,0,1),y);s=D.getObject(n).Shape
 for target,b in [('NEW_MOVING_ROOF',cap),('NEW_FIXED_HOOD',hood.Shape)]:
  d=s.distToShape(b)[0];rows.append({'field':n,'part':target,'gap':d,'clear':d>=1.25,'common':s.common(b).Volume if d<1.25 else 0})
 # Actualseparateprintedmoving/fixedguards needclearance, no Ownwaiver.
 d=cap.distToShape(hood.Shape)[0];rows.append({'pose':[y,p],'parting':'movingroof/fixedhood','gap':d,'clear':d>=1.25,'common':cap.common(hood.Shape).Volume if d<1.25 else 0})
put('current-named-roof-guard-and-FFC-gate.json',{'rows':rows,'physicalPASS':False,'wholekit':False,'scope':'only3existingcriticalprofiles, localnewroofs/matchedposes. Samplesnotcontinuousmotioncertificate','seconds':time.perf_counter()-t0})
# Exact changedfullCSKhead vsactualAMPmetal; otheroldreceivedpairsnotreplayed.
rr=[]
o=D.getObject('CF17_BUS_CSK10_m4p5_97')
for b in [D.getObject('CB_AMP_1_M2x12'),D.getObject('CB_AMP_1_basewasher')]:rr.append({'a':o.Name,'b':b.Name,'gap':o.Shape.distToShape(b.Shape)[0]})
put('changed-full-CSK90-metal-delta.json',{'pairs':rr,'required':1.25})
D.recompute();D.save();print(json.dumps({'fails':[r for r in rows if not r['clear']],'CSK':rr,'seconds':time.perf_counter()-t0}))
