import FreeCAD as A,FreeCADGui as G,Part,json,math,time
from pathlib import Path
from datetime import datetime,timezone
D=A.ActiveDocument;P=Path(__file__).parent;V=A.Vector

def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def cy(x,y,z,r,h,a=V(0,0,1)):return Part.makeCylinder(r,h,V(x,y,z),a)
def fuse(ss):
 s=ss[0]
 for q in ss[1:]:s=s.fuse(q)
 return s
def vol(s):return 0.0 if s.isNull() else s.Volume
def ringxy(x0,y0,x1,y1,z,w,t):return box(x0-t,y0-t,z,x1-x0+2*t,y1-y0+2*t,w).cut(box(x0,y0,z-.01,x1-x0,y1-y0,w+.02))
def nutY(x,y,z,af,h):
 rr=af/math.sqrt(3);ps=[V(x+rr*math.cos(k*math.pi/3),y,z+rr*math.sin(k*math.pi/3)) for k in range(6)];return Part.Face(Part.makePolygon(ps+[ps[0]])).extrude(V(0,h,0)).cut(cy(x,y-.01,z,1.1,h+.02,V(0,1,0)))
def run():
 t=time.perf_counter();r=dict(utc=datetime.now(timezone.utc).isoformat(),source_commit='d0757ee5',same_nine_case_allocation=True,parts=[],joints=[],protected=[],ties=[],old_retire_functions=[])
 gr=D.addObject('App::DocumentObjectGroup','P11_FUNCTIONAL_POWER_RETENTION_V16');added=[]
 def add(n,s,show=True,color=(.20,.63,.65)):
  o=D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.Visibility=show;o.ViewObject.ShapeColor=color;gr.addObject(o);return o
 old=D.getObject('P11_rear_gate').Shape.copy();bank=D.getObject('BANK_PANEL_NEG').Shape.copy();p10=D.getObject('P10_front_gate').Shape.copy()
 # Material ownership is by actual constructionfunction, not caseairBBox/floor.
 obsolete=[box(55,78,55,120,4.4,29),box(55,54,52.6,120,5,2.4),box(169,54,52.6,6,28.4,54.4),box(55,51.75,103,120,3.25,5.65)]
 obsolete += [box(55+23*i,54.25,106.25,20.25,4.75,2.4) for i in range(5)]
 obsolete += [box(95,-97,98.63,12,13,10)] # oldnegativerearbankear becomesREALlowerdoglegjoint.
 keep=[('root35',old.common(cy(103,35,100,7,11))),('root49',old.common(cy(103,49,100,7,11))),('baseNEG',old.common(box(85,-89,48,26,10,14))),('basePOS',old.common(box(85,79,48,26,10,14))),('keyNEG',old.common(box(94,-87,124,14,8,10))),('keyPOS',old.common(box(94,79,124,14,8,10))),('P12lapNEG',old.common(box(82,-21,87,25,5,10))),('P12lapPOS',old.common(box(82,15,87,25,5,10)))]
 lower=old.cut(fuse(obsolete));clear=[]
 for n in ['PBAY_P_SYS','PBAY_P_REAR','PBAY_F_PI','PBAY_F_AUX','PBAY_F_HY','PBAY_F_HP','PBAY_F_TY','PBAY_P_AUX']:
  b=D.getObject(n).Shape.BoundBox;clear.append(box(b.XMin-1.25,b.YMin-1.25,b.ZMin-1.25,b.XLength+2.5,b.YLength+2.5,b.ZLength+2.5))
 lower=lower.cut(fuse(clear));lower=fuse([lower]+[s for _,s in keep])
 # Fixed load route around the SAME negativebay, realbase->outerpost->upperframe.
 members=[('NEG_BASE_DOGLEG',box(95,-99,54,12,19,6)),('NEG_OUTER_LOAD_POST',box(95,-99,56,6,4,66)),('NEG_UPPER_RETURN',box(95,-99,118,12,19,5)),('POS_615_BACKWALL',box(94,93.3,57.6,61,2.4,46.4)),('POS_UPPER_RETURN',box(98,79.25,100,57,16.45,4)),('TWO_FUSE_SHARED_BACKING',box(53,78.3,52.6,134,3.4,28)),('NEG_FHAC_SHARED_BACKING',box(53,-94.8,62,71,2.5,45)),('NEG_CASE_ROOT_LOW',box(95,-99,58,12,7,6)),('NEG_CASE_ROOT_HIGH',box(95,-99,102,12,7,5)),('BANK_LOWER_FIXED_RECEIVER',box(95,-96,52,12,16,11.7))]
 for x in [55,134]:
  members += [('FUSE_BASE_FRONT_'+str(x),box(x,56,50.5,51,4,4.5)),('FUSE_BASE_REAR_'+str(x),box(x,74,50.5,51,7.7,4.5))]
 for x in [100,125]:
  members += [('615_FLOOR_'+str(x),box(x,81.7,57.6,22,14,2.4)),('615_LEFT_STOP_'+str(x),box(x-.3-2.4,82,60,2.4,11,3)),('615_BACK_STOP_'+str(x),box(x,93.3,60,22,2.4,37))]
 for x in [55,78,101]:members.append(('MG_BASE_'+str(x),box(x,-94.8,61.6,20.25,6.8,2.4)))
 # P_AUX safe two-strips support: no inventedpressure on MTA or wholecell.
 members += [('PAUX_BEARING_A',box(65,-65,76.6,21,3,2.4)),('PAUX_BEARING_B',box(65,-38,76.6,21,3,2.4)),('PAUX_JOIN_EDGE',box(84,-65,76.6,2,30,2.4)),('PAUX_RISING_WEB',box(86,-65,76.6,4,4,30.4)),('PAUX_TOP_LOAD_RETURN',box(86,-65,103,15,4,4))]
 lower=fuse([lower]+[s for _,s in members])
 # Complete SAMEbankjoint moved only aswholeloadinterface tobelowFHAC. Realprinttab, not headslide.
 bclear=box(88,-97,97.63,9,16,13);newbank=bank.cut(bclear)
 bankmembers=[('BANK_DROP_WEB',box(48,-86,54,4,6,52.63)),('BANK_LOWER_DOGLEG',box(48,-96,52,47,10,11.7)),('BANK_DROP_END_RETURN',box(48,-96,54,4,16,6))]
 newbank=fuse([newbank]+[s for _,s in bankmembers]);newbore=cy(82,-92,58.5,1.7,32,V(1,0,0));newbank=newbank.cut(newbore).cut(box(85.8,-104,54.8,3.2,12.5,7.4));lower=lower.cut(newbore)
 for o in D.Objects:
  if o.Name.startswith('BANK__1_REAR_'):
   s=o.Shape.copy();s.translate(V(0,0,58.5-103.63));o.Shape=s;o.Label='SamefullbankrearM3set / WHOLE lowerdoglegaxisZ58.5'
 r['joints'].append(dict(role='BANK_NEG_WHOLE_REAR_JOINT',same_full_M3x25_nut2washers=True,axis=[1,0,0],new_y=-92,new_z=58.5,old_z=103.63,actual_lower_receiver_root=vol(members[0][1].common(old)),actual_bank_drop_root=vol(bankmembers[0][1].common(bank)),side_nut_feed='-Y/openbeforebanks, fullnut+washer',no_purchased_frame_cut=True))
 # Actual removable TWO615 upperkeeper; complete2xM2x8+L1spacers/head+2washers/fullnuts.
 keepermembers=[box(96,88,97.3,56,5.3,2.4),box(93,91.9,93,6,1.4,6.7),box(148,91.9,93,6,1.4,6.7)];keeper=fuse(keepermembers)
 for i,x in enumerate([96,151]):
  hole=cy(x,90,96.5,1.1,10,V(0,1,0));keeper=keeper.cut(hole);lower=lower.cut(hole)
  ss=[('fullM2x8',cy(x,90.6,96.5,1,8,V(0,1,0)).fuse(cy(x,88.6,96.5,1.9,2,V(0,1,0)))),('headwasher',cy(x,90.6,96.5,2.5,.3,V(0,1,0)).cut(cy(x,90.59,96.5,1.1,.32,V(0,1,0)))),('spacerL1',cy(x,90.9,96.5,2,1,V(0,1,0)).cut(cy(x,90.89,96.5,1.1,1.02,V(0,1,0)))),('nutwasher',cy(x,95.7,96.5,2.5,.3,V(0,1,0)).cut(cy(x,95.69,96.5,1.1,.32,V(0,1,0)))),('fullnut',nutY(x,96,96.5,4,1.6))]
  for tag,s in ss:add('PB_KEEP_'+str(i)+'_'+tag,s,color=(.7,.71,.75))
  r['joints'].append(dict(role='615KEEPER'+str(i),M2x8=True,ordinaryspacerL1=True,fullnut=True,washers2=True,tip_beyond_fullnut=1.0,stock='NEEDED_UNCONFIRMED'))
 # FiveWHOLEselectedT18I roles. Fullnylon/ring/head; freeend/tensionOPENbeforecovers, humantrimonlyunusedplasticafterlock.
 loops=[]
 for role,x in [('F_HY',55),('F_HP',78),('F_TY',101)]:
  n=ringxy(x,-94.8,x+20.25,-70,90.75,2.5,1.2);head=box(x+7.725,-68.8,91,4.8,4.5,3.5);loops.append(n);add('PB_TIE_'+role+'_NYLON',n,color=(.2,.2,.23));add('PB_TIE_'+role+'_HEAD',head,color=(.2,.2,.23));r['ties'].append(dict(role=role,selected145=True,loop=2*(20.25+24.8+2.4),head_full=[4.8,4.5,3.5],unusedtail_open_then_humantrim=True))
 for role,x in [('F_PI',80.5),('F_AUX',159.5)]:
  n=box(x-1.25,54.8,53.8,2.5,28.1,22.65).cut(box(x-1.26,56,55,2.52,25.7,20.25));loops.append(n);add('PB_TIE_'+role+'_NYLON',n,color=(.2,.2,.23));add('PB_TIE_'+role+'_HEAD',box(x-2.4,64.75,76.45,4.8,4.5,3.5),color=(.2,.2,.23));r['ties'].append(dict(role=role,selected145=True,loop=2*(25.7+20.25+2.4),head_full=[4.8,4.5,3.5],unusedtail_open_then_humantrim=True))
 n=box(81.25,-66.2,75.4,2.5,32.4,13.8).cut(box(81.24,-65,76.6,2.52,30,11.4));loops.append(n);add('PB_TIE_PAUX_NYLON',n,color=(.2,.2,.23));add('PB_TIE_PAUX_HEAD',box(80.1,-70.7,84,4.8,4.5,3.5),color=(.2,.2,.23));r['ties'].append(dict(role='PAUXnew',selected145=True,loop=2*(30+11.4+2.4),qty_new_demand_unconfirmed=1,unusedtail_open_then_humantrim=True))
 lower=lower.cut(fuse(loops))
 # New POST412 fullcase root onactualP10crossbeam, no imaginary root over speaker.
 postmembers=[box(-132,10,61.6,18,3,2.4),box(-132,27,61.6,18,3,2.4),box(-118,6,61.6,4,24,2.4),box(-118,6,61.6,4,4,45.4),box(-118,6,103,18.5,4,4)]
 newp10=fuse([p10]+postmembers);n=box(-126.25,8.8,60.4,2.5,22.4,14.8).cut(box(-126.26,10,61.6,2.52,20,12.4));newp10=newp10.cut(n);add('PB_TIE_POST_NYLON',n,color=(.2,.2,.23));add('PB_TIE_POST_HEAD',box(-127.4,4.3,69,4.8,4.5,3.5),color=(.2,.2,.23));r['ties'].append(dict(role='POSTnew',selected145=True,loop=2*(20+12.4+2.4),qty_new_demand_unconfirmed=1,unusedtail_open_then_humantrim=True))
 D.getObject('P11_rear_gate').Shape=lower;D.getObject('BANK_PANEL_NEG').Shape=newbank;D.getObject('P10_front_gate').Shape=newp10;add('PB_TWO_615_REMOVABLE_KEEPER',keeper)
 for nm,s in [('P11_rear_gate',lower),('BANK_PANEL_NEG',newbank),('P10_front_gate',newp10),('PB_TWO_615_REMOVABLE_KEEPER',keeper)]:
  b=s.BoundBox;r['parts'].append(dict(name=nm,valid=s.isValid(),solids=len(s.Solids),bounds=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax],volume=vol(s)))
 for nm,s in keep:r['protected'].append(dict(name=nm,source_volume=vol(s),missing=vol(s.cut(lower))))
 r['intended_members']=[dict(name=nm,missing_after_designed_functional_bores_and_stockchannels=vol(s.cut(lower)),connection_to_source=vol(s.common(old))) for nm,s in members]
 r['bank_members']=[dict(name=nm,covered_volume=vol(s.common(newbank)),planned_volume=vol(s)) for nm,s in bankmembers]
 r['old_retire_functions']=['fiveoldverticalFHACrack andupperfingers replaced by2horizontal+3sidecapturedgroups','oldBANK_NEGrearupperear/fullM3pose replacedbyWHOLElowerdoglegjoint','oldfront615uppercapture no longercurrent forP_SYS/P_REAR; newkeeper/fullM2','oldPAUX/POSTmountroles replacedbyactualcommonroots; no boughtcase deletion']
 r['original_shape_changes_explicit']=['P11','P10','BANK_PANEL_NEG','BANK_NEG_REARfullM3set'];r['physical_pass']=False;r['wholekit_ready']=False;r['actual_fit_cut_slack']=None;r['seconds']=time.perf_counter()-t
 D.Label='DAY16 FUNCTIONAL P11 POWER RETENTION - NOMINAL CHECKPOINT';D.recompute();D.saveAs(str(P/'power-retention-realized.FCStd'));(P/'construction-checkpoint.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(saved=True,objects=len(D.Objects),parts=r['parts'],protected=r['protected'],seconds=r['seconds'])))
run()
