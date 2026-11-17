import FreeCAD as A,FreeCADGui as G,Part,json,math,time
from pathlib import Path
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent
def put(n,x):(P/n).write_bytes((json.dumps(x,indent=2)+'\n').encode())
def bx(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def bb(s):
 b=s.BoundBox;return[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def add(n,s,col=(.43,.62,.64)):
 o=D.getObject(n) or D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=col;o.ViewObject.Visibility=True;return o
def fu(ss):
 s=ss[0]
 for q in ss[1:]:s=s.fuse(q)
 return s
def hexnut(x,y,z):
 pts=[V(x+2.887*math.cos(i*math.pi/3),y,z+2.887*math.sin(i*math.pi/3)) for i in range(6)]
 return Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(0,2,0)).cut(Part.makeCylinder(1.1,2.2,V(x,y-.1,z),V(0,1,0)))
def washer(x,y,z):return Part.makeCylinder(3,.5,V(x,y,z),V(0,1,0)).cut(Part.makeCylinder(1.35,.7,V(x,y-.1,z),V(0,1,0)))
def run():
 # ONE fixed receiving interface: fullports face INNERbody, wholeboard sideplane
 # chosen from lowerfork continuousXY bound and actual MTA/inline/P01 bay.
 tr=A.Placement(V(-167,-99.9,0),A.Rotation(V(0,0,1),180))
 for n in ['Pi4B_actual_PCB','Pi_components_and_cooling','Pi_GPIO1992_factory_female','Pi_USB_DATA_Delock_mating']:
  o=D.getObject(n);o.Placement=tr.multiply(o.Placement)
 front=D.getObject('RG_FRONT_GRID_WITH_INTEGRAL_HEAD_RECEIVER');oldfront=front.Shape.copy()
 # Actual connected outsidebackbone, not a floating table. PCB backsideY-68,
 # 3mm post to-71, 3mm openframe to-74; sourcegrid root atZ45.52.
 members=[bx(-127,-74,45.52,87,3,56.98)]
 # Remove empty centralarea, leaving two vertical ribs and two crossmembers.
 members[0]=members[0].cut(bx(-117.5,-74.1,52,47,3.2,37))
 for x in [-122.5,-64.5]:
  for z in [46,95]:members.append(Part.makeCylinder(3.5,3,V(x,-71,z),V(0,1,0)))
 # Three connections to actual sharedcrossbars, all outside source P01steel.
 for x in [-100,-45]:members.append(bx(x,-74,45.52,6,52,3))
 # Frontlower mount at46 is external to sourceP01Xmin-86, side root outsideY.
 new=fu([oldfront]+members)
 for x in [-122.5,-64.5]:
  for z in [46,95]:new=new.cut(Part.makeCylinder(1.4,9,V(x,-75,z),V(0,1,0)))
 front.Shape=new
 hardware=[]
 # Heads facebody(+Y), fullshaft goesback(-Y). UnderheadY-65.9, tip-77.9;
 # fullnut(-76.5..-74.5), washers/board/posts/frame actualstack.
 for x in [-122.5,-64.5]:
  for z in [46,95]:
   pre='FS_PI_'+str(x)+'_'+str(z)
   s=Part.makeCylinder(1.25,12,V(x,-77.9,z),V(0,1,0)).fuse(Part.makeCylinder(2.25,2.5,V(x,-65.9,z),V(0,1,0)))
   add(pre+'_M2p5x12_full',s,(.67,.68,.7));add(pre+'_portwasher',washer(x,-66.4,z),(.67,.68,.7));add(pre+'_backwasher',washer(x,-74.5,z),(.67,.68,.7));add(pre+'_fullnut',hexnut(x,-76.5,z),(.67,.68,.7))
   hardware.append({'axis':[x,z],'underheadY':-65.9,'tipY':-77.9,'fullnutY':[-76.5,-74.5],'nutengagement':2,'tipbeyondnut':1.4,'type':'M2.5x12 socket +2fullwashers+fullM2.5nut','quantity':1,'status':'NEEDED_UNCONFIRMED'})
 # Common rear powerreceiver actually joins existingrear negative rail and
 # crossmembers. Source F0 unchanged; openends and untensionedfactoryleads.
 rear=D.getObject('RG_REAR_GRID_WITH_STEPPED_RECEIVING_CROSSMEMBER');oldrear=rear.Shape.copy()
 rm=[bx(103,y,49.52,70,4,3) for y in [-15,11]]
 rm += [bx(x,-24,49.52,w,39,3) for x,w in [(108,10),(126,7)]]
 rm += [bx(108,-24,45.52,10,5,7),bx(126,-24,45.52,7,5,7)]
 # POSTperch positiveY beyond tailbase, fully joined atX158; not separatefloatingstock.
 rm += [bx(158,-24,49.52,6,64,3),bx(144,20,49.52,20,20,6)]
 # Fullwindow tie bridges connectsidecradle. Feedslot dimensions are declared
 # capacity3.8x2.2, notmeasuredstrapstock; selectedzip-tie actualFIT retained.
 for x in [111,159]:
  for y in [-22,17.5]:
   b=bx(x,y,49.52,8,5,8);b=b.cut(bx(x+2,y-.1,51.52,3.8,5.2,2.2));rm.append(b)
  rm.append(bx(x,-22,49.52,8,39,3))
 r=fu([oldrear]+rm);rear.Shape=r
 D.recompute();D.save()
 put('actual-receiving-members-and-hardware.json',{'PiSourceBounds':{n:bb(D.getObject(n).Shape) for n in ['Pi4B_actual_PCB','Pi_components_and_cooling','Pi_GPIO1992_factory_female','Pi_USB_DATA_Delock_mating']},'PiCSI':[-86.5,-60.9,54],'whole_side_interface':'Portside towardinner+Y, fullbodyconnectors/headmotion together. No headsource/boughtshapechange.','root':['3mm openfixedsideframe','4x3mmposts onprimary58x49','2actualcrossbararms tosourcefrontgrid'],'Pi_hardware':hardware,'Pi_stack':{'upperwasher':.5,'PCB':1.6,'post':3,'openframe':3,'backwasher':.5,'fullnut':2,'total_underhead':10.6,'tip_remaining':1.4},'openframe_valid':new.isValid(),'front_solids':len(new.Solids),'rear_valid':r.isValid(),'rear_solids':len(r.Solids),'sourcefront_missing_afteraddedinterface':oldfront.cut(new).Volume,'sourcerear_missing':oldrear.cut(r).Volume,'newmembers_missing_front':[q.cut(new).Volume for q in members],'newmembers_missing_rear':[q.cut(r).Volume for q in rm],'sourcegrid_parting_common':new.common(r).Volume,'post_case_bearing':'nominal planeZ55.52; no suppliercasepressureproof','F0_bearing':'nominalcradleZ52.52 fullunitretained; actualplasticseat/contactsafeONEFIT3. OpenXfactoryends; case independently held via2selectedtie bridges, notleadpull.','tie_stock':'T30L/T18selected source stock binding/feed/head/lap stillphysicalFIT; no newpurchase/no shorteningelectrical/textile units; no capacityPASSfromslotonly','initialorder':['emptyfixedgrids/sidePi throughsets beforewholehead/MTA/PCA-E1kit','realPi backsidewasher/nut held fromouternegativeY; fullR3driver frominnerbody beforecases','headfixedsaddle thenwholefactoryhorn/bearings/caps, movingloombeforeclosure','rearF0/feedties/POST andfullXT60 beforetailcaps/S0 andbankhandlay','factoryends remainwhole, nofictionalE1unplug; bodycoverslate'],'printbounds':[{'n':n,'bounds':bb(s),'maxXYZ_with4brim':max(s.BoundBox.XLength,s.BoundBox.YLength,s.BoundBox.ZLength)+8} for n,s in [('front',new),('rear',r)]],'status':'REALIZED_NOMINAL_MATERIAL_BEFORE_FOREIGN_GATES; no wholePASS/STLyet'})
 print(json.dumps({'frontsolids':len(new.Solids),'rearsolids':len(r.Solids),'objects':len(D.Objects),'CSI':[-86.5,-60.9,54]}))
run()
