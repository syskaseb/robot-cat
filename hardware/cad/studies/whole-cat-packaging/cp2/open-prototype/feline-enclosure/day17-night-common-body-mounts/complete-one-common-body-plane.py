import FreeCAD as A,FreeCADGui as G,Part,json,math,time
from pathlib import Path
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent
def put(n,x):(P/n).write_bytes((json.dumps(x,indent=2)+'\n').encode())
def bx(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def cyl(x,y,z,r,h,axis=V(0,0,1)):return Part.makeCylinder(r,h,V(x,y,z),axis)
def fu(ss):
 s=ss[0]
 for q in ss[1:]:s=s.fuse(q)
 return s
def vol(s):return 0. if s.isNull() or not s.Vertexes else s.Volume
def bb(s):
 b=s.BoundBox;return[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def add(n,s,kind='steel'):
 o=D.getObject(n) or D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=(.67,.68,.7) if kind=='steel' else (.4,.61,.63);o.ViewObject.Visibility=True;return o
def ring(p,axis,ro,ri,h):return Part.makeCylinder(ro,h,p,axis).cut(Part.makeCylinder(ri,h+.02,p-axis*.01,axis))
def nut(p,axis,af,h,r):
 a=V(axis);u=V(1,0,0)
 if abs(a.dot(u))>.9:u=V(0,1,0)
 v=a.cross(u);v.normalize();u=v.cross(a);u.normalize()
 pts=[p+(u*math.cos(i*math.pi/3)+v*math.sin(i*math.pi/3))*af/math.sqrt(3) for i in range(6)]
 return Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(a*h).cut(Part.makeCylinder(r,h+.02,p-a*.01,a))
HW=[]
def setY(tag,x,z,pcb=15.4,plate=20,L=12,board=1.6):
 u=pcb-.5;ax=V(0,1,0)
 add(tag+'_M2x'+str(L),cyl(x,u,z,1,L,ax).fuse(cyl(x,u-2,z,1.9,2,ax)))
 add(tag+'_frontwasher',ring(V(x,u,z),ax,2.5,1.1,.5));add(tag+'_backwasher',ring(V(x,plate+3,z),ax,2.5,1.1,.5));add(tag+'_nut',nut(V(x,plate+3.5,z),ax,4,1.6,1.0))
 HW.append({'role':tag,'type':'M2x'+str(L)+' socket/2washers/fullM2nut','qty':1,'axis':[x,z],'underheadY':u,'tipY':u+L,'nutY':[plate+3.5,plate+5.1],'tip_projection':u+L-(plate+5.1),'status':'NEEDED_UNCONFIRMED'})
def setZ(tag,x,y,pcb,base,L,board=1.6):
 # Heads belowplate, fullnut abovePCB: avoids parkedtip towardbattery.
 under=base-.5;ax=V(0,0,1)
 add(tag+'_M2x'+str(L),cyl(x,y,under,1,L).fuse(cyl(x,y,under-2,1.9,2)))
 add(tag+'_basewasher',ring(V(x,y,under),ax,2.5,1.1,.5));add(tag+'_PCBwasher',ring(V(x,y,pcb+board),ax,2.5,1.1,.5));add(tag+'_nut',nut(V(x,y,pcb+board+.5),ax,4,1.6,1.0))
 HW.append({'role':tag,'type':'M2x'+str(L)+' socket/2washers/fullM2nut','qty':1,'axis':[x,y],'underheadZ':under,'tipZ':under+L,'nutZ':[pcb+board+.5,pcb+board+2.1],'tip_projection':under+L-(pcb+board+2.1),'assembly':'preloadheads BEFOREcell; PCB+nutslater openbody','status':'NEEDED_UNCONFIRMED'})
def run():
 t=time.perf_counter();front=D.getObject('RG_FRONT_GRID_WITH_INTEGRAL_HEAD_RECEIVER');old=Part.Shape();old.read(str(P/'source6553-front-grid.brep'))
 # Whole affectedsources once: move actual MAIN/AUX families together+10Z,
 # AMP wholecover onto samecommonplane's negativeY audio shelf.
 moved=json.loads((P/'realized-common-plane-checkpoint.json').read_text())['moved_whole_modules']
 o=D.getObject('BNO085');before=bb(o.Shape);o.Placement.Base+=V(3,0,0);moved.append({'n':'BNO085','before':before,'after':bb(o.Shape),'ports':'wholeSPI8/fanout route OPEN; E1edgekeeper gap solved bycoallocation beforecontact'})
 # One integralcommonbackplane: actualtwo roots oncurrentfrontgrid/headreceiver.
 columns=[bx(x,20,45.52,6,3,55.48) for x in [-78,-45]]
 panel=bx(-78.5,20,98,164.5,3,36)
 for b in [(-63,19.9,110.8,48,3.2,13), (3,19.9,103,44,3.2,24),(57.4,19.9,108.5,14.8,3.2,12.5)]:panel=panel.cut(bx(*b))
 members=columns+[panel];cuts=[]
 # PCA: cachedfour actualsource cylinders determine axes, notboxcorners.
 pca=[]
 for f in D.getObject('PCA9685_Adafruit815_PCB').Shape.Faces:
  s=f.Surface
  if hasattr(s,'Radius') and abs(s.Radius-1.25)<1e-6:pca.append((round(s.Center.x,6),round(s.Center.z,6)))
 pca=sorted(set(pca));assert len(pca)==4
 for i,(x,z) in enumerate(pca):
  members.append(cyl(x,17,z,3.25,3,V(0,1,0)));cuts.append(cyl(x,16.9,z,1.1,10,V(0,1,0)));setY('CB_PCA_'+str(i),x,z)
 # E1 wholepopulatedkit: realopeninsulatingedgecage+lift-offBUS capfingers.
 # Contactlands explicitlynominalFR4edgeFIT3, notcomponentpressureproof.
 members += [bx(-2,17,98,54,6,2),bx(-2,7,98,2,16,32),bx(50,7,98,2,16,32)]
 members += [bx(0,7,98,1.5,10,2),bx(48.5,7,98,1.5,10,2),bx(-2,6,100,3.5,1,3),bx(48.5,6,100,3.5,1,3)]
 # BNO primary25.4x22.86 nominalPCB centredinsidecurrentcover; no false
 # supplierworlddatum/physicalSMDpressure. Twoopposedupperholes suffice.
 bno=[]
 for i,x in enumerate([57.64,77.96]):
  z=124.24;bno.append([x,z]);members.append(bx(x-3.25,20,103.92,6.5,3,26.08));members.append(cyl(x,17,z,3.25,3,V(0,1,0)));cuts.append(cyl(x,16.9,z,1.1,10,V(0,1,0)));setY('CB_BNO_'+str(i),x,z)
 # BUS bridge receivingbosses outsidefullPCA/E1/BNO body/boardedges.
 for x in [-75,85.5]:members.append(bx(x-3.5,16.5,127,7,7,7));cuts.append(cyl(x,20,120,1.7,20))
 # Shared lower powerplane abovewholecell, not old1.48airbearing.
 power=bx(-6,-10,78.5,64,36.75,3).cut(bx(-2,-6,78.4,56,28.75,3.2));members.append(power);members.append(bx(-45,20,78.5,42,3,3));members.append(bx(17.491,-10,78.5,5.5,36.75,3))
 main=[]
 for f in D.getObject('MAIN_Pololu4853').Shape.Faces:
  s=f.Surface
  if hasattr(s,'Radius') and abs(s.Radius-1.0922)<1e-5:main.append((round(s.Center.x,6),round(s.Center.y,6)))
 main=sorted(set(main));assert len(main)==2
 for i,(x,y) in enumerate(main):
  members.append(bx(49.5,y-2.75,78.5,8.5,5.5,3));members.append(cyl(x,y,81.5,2.75,4.5));cuts.append(cyl(x,y,78.4,1.1,10));setZ('CB_MAIN_'+str(i),x,y,86,78.5,12,1.5748)
 aux=[]
 for f in D.getObject('AUX_Pololu4092').Shape.Faces:
  s=f.Surface
  if hasattr(s,'Radius') and abs(s.Radius-1.09)<1e-5:aux.append((round(s.Center.x,6),round(s.Center.y,6)))
 aux=sorted(set(aux));assert len(aux)==3
 for i,(x,y) in enumerate(aux):members.append(cyl(x,y,81.5,2.75,7));cuts.append(cyl(x,y,78.4,1.1,13));setZ('CB_AUX_'+str(i),x,y,88.5,78.5,16,1.57)
 # AMP drawing17.78x19.05 nominalPCBplane105, actualcover retainedwhole.
 members += [bx(-11,-40,95.5,6,63,3),bx(-11,17,95.5,6,6,7.5),bx(-11,-40,98,6,24,4),bx(-28,-40,99,23,24,3)]
 for i,x in enumerate([-22.85,-10.15]):
  y=-21.015;members.append(cyl(x,y,102,2.75,3));cuts.append(cyl(x,y,98.9,1.1,9));setZ('CB_AMP_'+str(i),x,y,105,99,12)
 # Usefulleft wing forpairedP_SYS/F_PI withoutcrossingPCA orAMP body.
 members += [bx(-78,-83.5,112,6,106.5,3),bx(-78,-83.5,115,6,35,9.5)]
 members += [bx(-78,-87,121.5,76,39.5,3),bx(-57,-46,116.875,49,4,3),bx(-57,-42,116.875,7,18,3),bx(-78,-46,115,21,4,4.875)]
 # P_SYScase lowercapture withopen+X mouth andlever-UP centre.
 members += [bx(-28,-87,124.5,2,40,3),bx(-26,-87,124.5,22,1.5,3),bx(-26,-48.5,124.5,22,1,3)]
 members += [bx(-4,-85.5,124.5,1.5,3,2),bx(-4,-51.5,124.5,1.5,3,2)]
 for y in [-79,-55]:members.append(cyl(-31,y,124.5,3.5,11));cuts.append(cyl(-31,y,123.5,1.1,18))
 # Savewholematerial BEFOREaffectedchecks; emptycuts are handledsafely.
 planned=fu(members);complete=old.fuse(planned)
 for c in cuts:complete=complete.cut(c)
 assert complete.isValid();front.Shape=complete
 # Real removable BUS/E1cap (separateprint), notfictional integral removal.
 bridge=bx(-78.5,17,134,167.5,6.5,3).fuse(bx(-40.5,-22,134,47,39,3))
 for x in [-75,85.5]:bridge=bridge.fuse(bx(x-3.5,16.5,134,7,7,3)).cut(cyl(x,20,133.9,1.7,4))
 for x in [0,48.5]:bridge=bridge.fuse(bx(x,15.4,130,1.5,1.6,4)).fuse(bx(x,15.4,134,1.5,8.1,3))
 busaxes=[]
 for i,x in enumerate([-35.5,1.5]):
  for j,y in enumerate([-18.5,9.5]):
   bridge=bridge.fuse(cyl(x,y,137,2.75,3)).cut(cyl(x,y,133.9,1.1,7));busaxes.append([x,y]);setZ('CB_BUS_'+str(i)+'_'+str(j),x,y,140,134,12)
 add('CB_REMOVABLE_BUS_E1_BRIDGE',bridge,'print')
 # Whole2M3x16 bridge sets, headsabove andfullnutsoutsidePCB edges.
 for i,x in enumerate([-75,85.5]):
  add('CB_BRIDGE_'+str(i)+'_M3x16',cyl(x,20,121.5,1.5,16).fuse(cyl(x,20,137.5,2.75,3)))
  add('CB_BRIDGE_'+str(i)+'_upperwasher',ring(V(x,20,137),V(0,0,1),3.5,1.6,.5));add('CB_BRIDGE_'+str(i)+'_lowerwasher',ring(V(x,20,126.5),V(0,0,1),3.5,1.6,.5));add('CB_BRIDGE_'+str(i)+'_nut',nut(V(x,20,124.1),V(0,0,1),5.5,2.4,1.3))
 # One commonP_SYS keeper, ends only; leverfield remainsopenmiddle.
 keep=bx(-34.5,-88,135.5,7,40.5,3)
 for y in [-87,-50]:keep=keep.fuse(bx(-27.5,y,135.5,19.5,2.5,3))
 for i,y in enumerate([-79,-55]):
  keep=keep.cut(cyl(-31,y,135.4,1.1,4));add('CB_PSYS_'+str(i)+'_M2x16',cyl(-31,y,123,1,16).fuse(cyl(-31,y,139,1.9,2)));add('CB_PSYS_'+str(i)+'_topwasher',ring(V(-31,y,138.5),V(0,0,1),2.5,1.1,.5));add('CB_PSYS_'+str(i)+'_bottomwasher',ring(V(-31,y,126),V(0,0,1),2.5,1.1,.5));add('CB_PSYS_'+str(i)+'_nut',nut(V(-31,y,124.4),V(0,0,1),4,1.6,1))
 add('CB_REMOVABLE_PSYS_LOWER_BODY_KEEPER',keep,'print')
 # Retire only OLD UNBUILT displacedmount roles; no selectedboughtunitremoved.
 oldnom=D.getObject('STATIONARY_REAL_MOUNTS_NOMINAL')
 if oldnom:oldnom.ViewObject.Visibility=False
 D.recompute();D.save()
 put('completed-common-plane-checkpoint.json',{'moved_whole_modules':moved,'PCA_actual_axes':pca,'MAIN_actual_axes':main,'AUX_actual_axes':aux,'BNO_nominal_primary_axes':bno,'BUS_nominal_primary_axes':busaxes,'nominal_datums':{'PCA':'actualnativePCB15.4..17/4r1.25 cylinders','MAIN':'actualhorizontalPCBfaceZ76 andnativeboreaxes, moved+10 ->86..87.5748, notbboxassumption','AUX':'actualPCB78.5..80.07 moved+10 ->88.5..90.07; full9.5field retained','BUS':'primary42x33 centeredinsideconstructorPCBfootprint, nominalPCB140..141.6 actualdeliveryFIT3; invalidwholeSTEPnotused','BNO':'primary25.4x22.86/20.32x17.78, nominalPCB15.4..17 centredinsidecurrentinstallation; actualrev/safeannulusFIT3','AMP':'primary17.78x19.05/2holes12.7, nominalPCB105..106.6 centredinsidewholecover; actualheader/revFIT3','E1':'wholepopulatedfield50x10x30 kept; edgecontactrails/fingersnominalFR4safeedgesFIT3, no inventedmountingholes'},'hardware':HW,'new_front_valid':complete.isValid(),'new_front_solids':len(complete.Solids),'bridge_valid':bridge.isValid(),'keeper_valid':keep.isValid(),'sourcefront_volume':old.Volume,'new_front_volume':complete.Volume,'positivecolumn_roots':[vol(q.common(old)) for q in columns],'separate_front_bridge_common':vol(complete.common(bridge)),'separate_front_keeper_common':vol(complete.common(keep)),'member_coverage_pending_affected_checks':True,'retired':'oldSTATIONARY_REAL_MOUNTS_NOMINAL group/sourceunbuiltroles only; oldactualcap/headers notdeleted; newbodyfieldROOT replacesbodymountfunction','assembly':['base/splices/Pi fullsets beforebodyequipment; P01axes unchanged','preloadMAIN/AUXscrews frombelow BEFOREcell, nutslaterabovePCBs','PCA/E1kit installedwhole; backnutsbeforeMTA tiers; no virtualE1unplug','AMP/BNO thenwholeBUS/E1bridge andfull2M3sets beforelatecovers','P_SYS casehandlay+5mouthchambers thencommonkeeper; FHACwholefactoryendsbeforelatecasebands','fullbattery/textile200units preserved; bodycoverslast/partialdemount permitted'],'wholekit':False,'physicalPASS':False,'FFC_ToF_JR':'previousselectedrecipeHOLD/connectedmotionOPEN, notblockedindependentbodymounts','new_hardware':'NEEDED_UNCONFIRMED only; nopurchase/inventoryassertion','seconds':time.perf_counter()-t})
 print(json.dumps({'objects':len(D.Objects),'front_solids':len(complete.Solids),'bridge_solids':len(bridge.Solids),'keeper_solids':len(keep.Solids),'rootvol':[vol(q.common(old)) for q in columns],'hwsets':len(HW),'seconds':time.perf_counter()-t}))
run()
