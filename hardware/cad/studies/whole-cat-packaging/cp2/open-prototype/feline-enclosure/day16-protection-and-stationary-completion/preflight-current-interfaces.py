import FreeCAD as A,Part,json,zipfile,xml.etree.ElementTree as E,time
from pathlib import Path
from datetime import datetime,timezone
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent;O=P.parent
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def bb(s):
 b=s.BoundBox;return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def gap(a,b):return sum(max(0,getattr(a,k+'Min')-getattr(b,k+'Max'),getattr(b,k+'Min')-getattr(a,k+'Max'))**2 for k in ['X','Y','Z'])**.5
def run():
 t=time.perf_counter();r=dict(utc=datetime.now(timezone.utc).isoformat(),module_frames=[],roots=[],inline=[],root_protection=[],striptools=[],finite_stock=[],failures=[],physical_pass=False)
 for n in ['BUS25514_installed','PCA9685_Adafruit815_PCB','E1_populated_prototype_board','BNO085','MAX98357A_amp','ReSpeakerLite_on_REMOVABLE_back','TTP223_touch','Speaker','S1_NKK_S821_installed','Monitor_MOD05015']:
  o=D.getObject(n);r['module_frames'].append(dict(name=n,b=bb(o.Shape),placement=o.Placement.toMatrix().A,classification='actualPCB_source' if n=='PCA9685_Adafruit815_PCB' else 'nominalfullinstallation_or_sourcecase_not_PCBdatum'))
 for n,q,owner in [('PCA_E1_lower_commonroot',box(-98,34,90,126,4,4),'P12_common_deck_speaker'),('BNO_underroot',box(-101,-49,76,29,25,3),'P10_front_gate'),('AMP_lowerroot',box(-58,16,93,20,4,3),'P12_common_deck_speaker'),('inline_footfront',box(117,6,48.22,3,4,2),'P03_rear_deck_integrated_load_yoke'),('inline_footrear',box(195,6,48.22,3,4,2),'P03_rear_deck_integrated_load_yoke')]:
  c=q.common(D.getObject(owner).Shape);r['roots'].append(dict(name=n,owner=owner,actualcommon=c.Volume,valid=c.isValid()))
 rigid=[o for o in D.Objects if hasattr(o,'Shape') and not o.Shape.isNull() and (o.Name.startswith(('S0_','FHAC0001','Motor_ATO','WAGO415','WAGO615','P19_')) or o.Name in ['P06_S0_shared_panel','MAIN_Pololu4853','AUX_Pololu4092','S1_NKK_S821_installed','Monitor_MOD05015','E2_Molex_and_inline_WAGO'])]
 for i in range(8):
  s=box(120+9.35*i,8,65,8.1,35.5,8.9)
  for o in rigid:
   if gap(s.BoundBox,o.Shape.BoundBox)>=1.25:continue
   c=s.common(o.Shape);g=s.distToShape(o.Shape)[0];q=dict(i=i,other=o.Name,gap=g,common=c.Volume,valid=c.isValid());r['inline'].append(q)
   if not c.isValid() or c.Volume>1e-6 or g<1.25-1e-6:r['failures'].append(dict(kind='inline_candidate_wholelayer',**q))
 # Only missing MAIN/AUX root preservation, not their alreadyaccepted matrix.
 z=zipfile.ZipFile(O/'day16-main-aux-stationary-mounts/main-aux-stationary-mounts.FCStd');e=E.fromstring(z.read('Document.xml'));node=next(o for o in e.findall('.//ObjectData/Object') if o.get('name')=='P11_rear_gate');f=node.find("./Properties/Property[@name='Shape']/Part").get('file');s=Part.Shape();s.importBrepFromString(z.read(f).decode());cur=D.getObject('P11_rear_gate').Shape
 for i,y in enumerate([35,49]):
  roi=box(97,y-5,98.5,13,10,18);protected=s.common(roi);missing=protected.cut(cur);r['root_protection'].append(dict(role='MAIN_AUX_actualroot'+str(i),missing=missing.Volume,valid=missing.isValid()))
  for tag,q in [('fullnut_feed',box(99.825,y-2.75,100.1,16.175,5.5,2.4)),('fullwasher_feed',Part.makeCylinder(3.5,.5,V(103,y,102.5)).fuse(box(103,y-3.5,102.5,13,7,.5)))]:
   c=q.common(cur);r['root_protection'].append(dict(role=tag+str(i),common=c.Volume,valid=c.isValid()))
 for sy in [-1,1]:
  for side,q in [('FRONT',Part.makeCylinder(4.25,20.5,V(-128,92*sy,103.63),V(1,0,0))),('REAR',Part.makeCylinder(4.25,20,V(110.5,92*sy,103.63),V(1,0,0)))]:
   for o in rigid:
    if gap(q.BoundBox,o.Shape.BoundBox)>=1.25:continue
    c=q.common(o.Shape);r['striptools'].append(dict(side=side,sy=sy,other=o.Name,common=c.Volume,gap=q.distToShape(o.Shape)[0],valid=c.isValid()))
 for o in D.Objects:
  if not hasattr(o,'Shape') or not ('T18I' in o.Name or o.Name.startswith(('TIE_FHAC','T30L_F0'))):continue
  for other in rigid:
   if gap(o.Shape.BoundBox,other.Shape.BoundBox)>=1.25:continue
   # Fullband vs OWNretainedcase is intentional; record only actual separate motorbank/S0 interference candidates.
   if not other.Name.startswith(('S0_','Motor_ATO')):continue
   c=o.Shape.common(other.Shape);r['finite_stock'].append(dict(part=o.Name,other=other.Name,common=c.Volume,gap=o.Shape.distToShape(other.Shape)[0],valid=c.isValid(),classification='Motor housing/ATO/TE sourcecompound; allocation caseBOX is not deliveredclipplastic'))
 r['seconds']=time.perf_counter()-t;(P/'preflight-current-interfaces.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(seconds=r['seconds'],roots=r['roots'],inline_failures=r['failures'],root_protection=r['root_protection'],tools=len(r['striptools']),stock_candidates=len(r['finite_stock']),module_frames=r['module_frames'])))
run()
