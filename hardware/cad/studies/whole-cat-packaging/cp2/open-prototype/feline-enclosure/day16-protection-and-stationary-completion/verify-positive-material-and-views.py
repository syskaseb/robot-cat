import FreeCAD as A,FreeCADGui as G,Part,json,time,zipfile,xml.etree.ElementTree as E
from pathlib import Path
from datetime import datetime,timezone
P=Path(__file__).parent;O=P.parent;D=A.ActiveDocument;V=A.Vector
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def gap(a,b):return sum(max(0,getattr(a,k+'Min')-getattr(b,k+'Max'),getattr(b,k+'Min')-getattr(a,k+'Max'))**2 for k in ['X','Y','Z'])**.5
def wr(n,d):(P/n).write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
def run():
 t=time.perf_counter();removed=[]
 for o in list(D.Objects):
  if o.Name.startswith('BUS_PASSIVE_SPACER_') and o.Shape.BoundBox.YMin>0:removed.append(o.Name);D.removeObject(o.Name)
 D.Label='DAY16 STATIONARY PARTIAL / NOMINAL PRIMARY MOUNTS / NAMED HOLDS';D.recompute();D.save();G.getDocument(D.Name).Modified=False
 r=dict(utc=datetime.now(timezone.utc).isoformat(),checks=[],failures=[],duplicate_positiveY_passive_reference_removed=removed,only_four_actualBUS_spacers=True,complete=False)
 z=zipfile.ZipFile(O/'day16-common-protection-retention/shared-protection-retention.FCStd');xml=E.fromstring(z.read('Document.xml'));index={q.get('name'):q for q in xml.findall('.//ObjectData/Object')}
 positive=[]
 for n in ['P12_common_deck_speaker','P13_BUS_bridge','P14_fixed_touch_rail','P15_removable_mic_rail']:
  f=index[n].find("./Properties/Property[@name='Shape']/Part").get('file');old=Part.Shape();old.importBrepFromString(z.read(f).decode());s=D.getObject(n).Shape.cut(old)
  if s.isNull() or s.Volume<1e-8:r['checks'].append(dict(kind='actual_positive_material',part=n,volume=0,scope='only intendedbore removals / no positive material'));continue
  positive.append((n,s));r['checks'].append(dict(kind='actual_positive_material',part=n,valid=s.isValid(),volume=s.Volume,bounds=[s.BoundBox.XMin,s.BoundBox.YMin,s.BoundBox.ZMin,s.BoundBox.XMax,s.BoundBox.YMax,s.BoundBox.ZMax]))
 names=['Pi4B_actual_PCB','Pi_components_and_cooling','Pi_USB_DATA_Delock_mating','Pi_GPIO1992_factory_female','P19_shared_lower_carrier','S1_NKK_S821_installed','Monitor_MOD05015','MAIN_Pololu4853','AUX_Pololu4092','BNO_FULL_SOURCE_INSTALLATION_COVER','MAX98357A_amp','PCA9685_Adafruit815_PCB','BUS25514_installed','E1_populated_prototype_board','TTP223_touch','RS_USB_FULL_SOURCE_COVER']
 names += [o.Name for o in D.Objects if o.Name.startswith(('S0_','Motor_ATO','Leg_protected','COVER_'))]
 for part,s in positive:
  for n in names:
   o=D.getObject(n)
   if not o or not hasattr(o,'Shape') or gap(s.BoundBox,o.Shape.BoundBox)>=1.25:continue
   if (part=='P12_common_deck_speaker' and n in ['MAX98357A_amp','E1_populated_prototype_board']) or(part=='P14_fixed_touch_rail' and n=='TTP223_touch') or(part=='P15_removable_mic_rail' and n=='RS_USB_FULL_SOURCE_COVER'):continue # only declaredprimary/edgefixture scope; NOT globalnameOwn
   for i,q in enumerate(s.Solids):
    if gap(q.BoundBox,o.Shape.BoundBox)>=1.25:continue
    c=q.common(o.Shape);g=q.distToShape(o.Shape)[0];row=dict(kind='newpositive_foreign',part=part,solid=i,other=n,common=c.Volume,gap=g,valid=c.isValid());r['checks'].append(row)
    if not c.isValid() or c.Volume>1e-6 or g<1.25-1e-6:r['failures'].append(row)
   if time.perf_counter()-t>43:r['cursor']=[part,n];break
  if r.get('cursor'):break
 # Primaryaudiofeed intact after samefamilycommonPCA/E1root realization.
 feed=box(-75,23,89.99,12,20,4.02);c=D.getObject('P12_common_deck_speaker').Shape.common(feed);r['checks'].append(dict(kind='preserved_source_audio_openfeed',common=c.Volume,valid=c.isValid()))
 for o in D.Objects:
  if not o.Name.startswith('BANK_') or o.Name in ['BANK_PANEL_NEG','BANK_PANEL_POS'] or not hasattr(o,'Shape'):continue
  for n in ['P10_front_gate','P11_rear_gate','BANK_PANEL_NEG','BANK_PANEL_POS']:
   s=D.getObject(n).Shape
   if gap(s.BoundBox,o.Shape.BoundBox)>.01:continue
   c=s.common(o.Shape);row=dict(kind='bank_fullsteel_matchedprint_nonpenetration',part=o.Name,print=n,common=c.Volume,valid=c.isValid());r['checks'].append(row)
   if not c.isValid() or c.Volume>1e-5:r['failures'].append(row)
 # Nominal matched pad/edge contacts do not authorize pressure on hidden ICs.
 r['exclusions']=['AMP actualPCBdatum26.1 insideinstallationcover: primaryannulus/revisionFIT3','E1 nominalfreeedgecontact; no hiddenICpressure accepted','TTP unknownsafecontactlands/perimeter oneFIT3','MIC primaryholepads/underside2.585, no broadundersidepress','BODYcovers and head/tail/wholewirebudgets remain separate'];r['complete']=not bool(r.get('cursor'));r['seconds']=time.perf_counter()-t;wr('positive-material-result.json',r)
 # Three actual localsections with explicitplane corners: no empty makePlane.
 rows=[]
 definitions=[('PCA_X',-35.945,['P12_common_deck_speaker','PCA9685_Adafruit815_PCB']+[o.Name for o in D.Objects if o.Name.startswith('PCA__35_945')]),('MIC_X',-.52,['P15_removable_mic_rail']+[o.Name for o in D.Objects if o.Name.startswith('MIC_1_')]),('AMP_X',-42.15,['P12_common_deck_speaker']+[o.Name for o in D.Objects if o.Name.startswith('AMP_1_')])]
 for tag,x,ns in definitions:
  plane=Part.Face(Part.makePolygon([V(x,-60,60),V(x,90,60),V(x,90,170),V(x,-60,170),V(x,-60,60)]))
  for n in ns:
   o=D.getObject(n)
   if not o or not hasattr(o,'Shape'):continue
   q=o.Shape.section(plane);lines=[[[p.y,p.z] for p in e.discretize(Number=16)] for e in q.Edges]
   if lines:rows.append(dict(section=tag,x=x,name=n,lines=lines))
 wr('actual-stationary-sections.json',rows)
 vis=[];hidden=[]
 for o in D.Objects:
  if not hasattr(o,'Shape') or o.Shape.isNull():continue
  vis.append(dict(name=o.Name,visible=o.ViewObject.Visibility))
  if o.Name.startswith(('CLOSED_BODY','CLOSED_HEAD','UNSELECTED')) or o in D.getObject('UNSELECTED_TRIALS_NOT_OPERATING').Group:o.ViewObject.Visibility=False;hidden.append(o.Name)
 wr('view-source.json',dict(document=D.Name,objects=len(D.Objects),engineering_cutaway_only=True,hidden=hidden,restore_visibility=vis))
 D.recompute();G.activeDocument().activeView().viewAxonometric();G.activeDocument().activeView().fitAll();G.updateGui();D.save();G.getDocument(D.Name).Modified=False
 print(json.dumps(dict(checks=len(r['checks']),failures=r['failures'],complete=r['complete'],seconds=r['seconds'],section_lines=sum(len(x['lines']) for x in rows),objects=len(D.Objects))))
run()
