import FreeCAD as A,FreeCADGui as G,Part,json,math,time
from pathlib import Path
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent
def put(n,x):(P/n).write_bytes((json.dumps(x,indent=2)+'\n').encode())
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def bb(s):
 b=s.BoundBox;return[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def lower(a,b):
 a=bb(a);b=bb(b);return sum(max(0,a[i]-b[i+3],b[i]-a[i+3])**2 for i in range(3))**.5
def add(n,s,col=(.45,.63,.65)):
 o=D.getObject(n) or D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=col;o.ViewObject.Visibility=True;return o
def run():
 tr=A.Placement(V(-83.5,116.5,1.5),A.Rotation(V(0,0,1),90));moves=[]
 for n in ['Pi4B_actual_PCB','Pi_components_and_cooling','Pi_GPIO1992_factory_female','Pi_USB_DATA_Delock_mating']:
  o=D.getObject(n);old=o.Shape.Volume;o.Placement=tr.multiply(o.Placement);moves.append({'n':n,'bounds':bb(o.Shape),'volume_difference':o.Shape.Volume-old})
 # Functional openfeed in OWN tailreceiver upright, not a cut through base.
 tail=D.getObject('NIGHT_YTAIL_FIXED_RECEIVER_ROOT');old=tail.Shape.copy()
 void=box(131.5,17,49,11,3.5,31);new=old.cut(void);tail.Shape=new
 put('chosen-whole-interface-premise.json',{'Pi':moves,'Pi_CSI_project_end':[-80.5,-39,54],'orientation':'fixedsideplane components/factoryGPIO face negativeY bodyavailablebay, nothead-facing-X; proper wholefourpart transform','bay_derivation':'FullDelock bottom40.1 vs actualculledsource chassis top38.52; wholePCB planeY-33.5..-31.9 outside P01railsY-27.5; bodyG1 negativeYmax-58 vsDelockmin-55.9 gives2.1. Fullsource neighbors/head9 gate follows; no posegrid.','tailplannedreplacement':{'web_source':[133,18.5,48.52,8,9,54.48],'openfeed_void':bb(void),'remaining_useful_web_section':[8,7],'web_new_frontY':20.5,'base_7mm_unchanged':True,'topbridge_and_servo_bearing_interfaces_unchanged':True,'old_volume':old.Volume,'new_volume':new.Volume,'removed':old.cut(new).Volume,'new_added':new.cut(old).Volume,'valid':new.isValid(),'solids':len(new.Solids),'stock_clearance_role':'full F0 positiveY17.5 +3.0 to upright; usefulload path via remaining7mm web/base/topbridge, no boughtcut or marginwaiver'},'root_and_commonmounts':'same intended functionalarchitecture; completing ordinary receiver/load interfaces, not accepting after firstfalsifier','fullFFC':{'unit':200,'flat':[16.8,1.8],'projectR':12.5,'ends_once':10,'new_relativepose_old_lengths_NOTINHERITED':True},'ToF4wire':{'OD':2.1,'sourceR':31.5},'physicalPASS':False})
 D.recompute();D.save()
 # Bounded finite head samples: same purchasedparts/angles, onlychangedPi.
 rows=[]
 for yaw,pitch in [(0,0),(-20,-10),(-20,0),(-20,10),(0,-10),(0,10),(20,-10),(20,0),(20,10)]:
  for hn,kind in [('MG92B_Head_pitch','yaw'),('HEAD_YAW_FORK_FIXED_PITCH_HOUSING','yaw'),('HEAD_MOVING_SENSOR_FRAME_AND_COVER_SPINE','pitch')]:
   q=D.getObject(hn).Shape.copy()
   if kind=='pitch':q.rotate(V(-135,0,121),V(0,1,0),pitch)
   q.rotate(V(-106,0,127),V(0,0,1),yaw)
   for pn in [x['n'] for x in moves]:
    s=D.getObject(pn).Shape;l=lower(s,q);r={'Pi':pn,'neighbor':hn,'yaw':yaw,'pitch':pitch,'bboxlower':l}
    if l>=1.25:r.update(gap_lower=l,clear_scoped=True)
    else:
     dist=s.distToShape(q)[0];r.update(actualgap=dist,valid=s.isValid() and q.isValid(),clear_scoped=dist>=1.25-1e-7)
     if not r['clear_scoped']:
      c=s.common(q);r.update(common=c.Volume,common_valid=c.isValid())
    rows.append(r)
 put('fixed-side-Pi-correlated-head-gate.json',{'rows':rows,'failures':[r for r in rows if not r['clear_scoped']],'all9_notcontinuousproof':True,'wholeacceptance':False})
 f0=D.getObject('F0_FHAC0002_30A').Shape
 put('tail-feed-functional-change-first-gate.json',{'actualgap':new.distToShape(f0)[0],'common':new.common(f0).Volume,'sourcebase_retained_missing':old.common(box(110,18,40,32,10,8.52)).cut(new).Volume,'remainingweb_8x7_actual_missing':box(133,20.5,49,8,7,31).cut(new).Volume,'all_other_parts':'unchanged; full F0/XA01 identity gap2.55 retained','valid':new.isValid(),'solids':len(new.Solids)})
 print(json.dumps({'Pi_head_failures':[r for r in rows if not r['clear_scoped']],'tailgap':new.distToShape(f0)[0],'objects':len(D.Objects)}))
run()
