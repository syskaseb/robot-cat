import FreeCAD as A,FreeCADGui as G,Part,json,math,time
from pathlib import Path
from datetime import datetime,timezone
P=Path(__file__).parent;V=A.Vector
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def cylx(x,y,z,r,l):return Part.makeCylinder(r,l,V(x,y,z),V(1,0,0))
def fuse(ss):
 s=ss[0]
 for q in ss[1:]:s=s.fuse(q)
 return s
def hx(x,y,z,af,h):
 r=af/math.sqrt(3);p=[V(x,y+r*math.cos(k*math.pi/3),z+r*math.sin(k*math.pi/3)) for k in range(6)];return Part.Face(Part.makePolygon(p+[p[0]])).extrude(V(h,0,0))
def gap(a,b):return sum(max(0,getattr(a,k+'Min')-getattr(b,k+'Max'),getattr(b,k+'Min')-getattr(a,k+'Max'))**2 for k in ['X','Y','Z'])**.5
def wr(n,d):(P/n).write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
def ringxy(x0,y0,x1,y1,z,w,t):return box(x0-t,y0-t,z,x1-x0+2*t,y1-y0+2*t,w).cut(box(x0,y0,z-.01,x1-x0,y1-y0,w+.02))
def run():
 D=A.ActiveDocument;P.mkdir(exist_ok=True);t=time.perf_counter();gr=D.addObject('App::DocumentObjectGroup','COMMON_PROTECTION_RETENTION_NOMINAL_FIT3')
 def add(n,s,col=(.25,.58,.65),show=True):
  o=D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=col;o.ViewObject.Visibility=show;gr.addObject(o);return o
 old10=D.getObject('P10_front_gate').Shape.copy();old11=D.getObject('P11_rear_gate').Shape.copy();olddeck={n:D.getObject(n).Shape.copy() for n in ['P02_front_deck','P03_rear_deck_integrated_load_yoke']};parts=[];steel=[];read=[]
 # Actual all-group height/material dependency first, no posegrid: one 5mm lifted whole FHAC bank + full P11 bypass.
 for o in D.Objects:
  if o.Name.startswith(('FHAC0001','WAGO','Motor_ATO','Leg_protected','F0_FHAC','POST_F0')) and hasattr(o,'Shape'):
   b=o.Shape.BoundBox;read.append(dict(name=o.Name,b=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax],classification='MTA four source boxes/fullends; WAGO/FHAC nominal case allocations, NOT exact flange/clip/plastic'))
 wr('whole-group-interface-read.json',dict(utc=datetime.now(timezone.utc).isoformat(),groups=read,bank_case_reference_panel=[100.63,102.63],whole_FHAC_height_interval=dict(min_bottom=54.97,max_bottom_if_old_P11beam=50.75,empty=True,cause='Source fullcase allocation vs retained cover captive-root to53.72, original beam bottom103. Keep fullcase, change WHOLE rear retaining load route.'),one_choice='FHAC five WHOLE units lift5 to55..106; P11 load U around frontY51.75..54.75/back79.25..82.25/farX169..175, ROOT35/49 and capkeys retained',all10factoryleads_opposite_ends_unchanged_sourceunits=True,changed_reach_is_FIT2_NO_LENGTHCREDIT=True))
 # Receiving ears are integral OWN print additions at actual uprights; nominal mating faces x-98 and95.
 ears10=[];ears11=[];bores10=[];bores11=[]
 for sy in [-1,1]:
  yc=92*sy;y0=84 if sy>0 else -97
  ears10.append(box(-104,y0,98.63,6,13,10));ears11.append(box(95,y0,98.63,12,13,10));bores10.append(cylx(-110,yc,103.63,1.7,28));bores11.append(cylx(80,yc,103.63,1.7,36))
  yy=47.6 if sy>0 else -80.4;panel=box(-96,yy,100.63,148,32.8,2)
  for i in range(6):
   cx=-81.8819+24*i;panel=panel.cut(box(cx-5.65,64*sy-11.1,99.63,11.3,22.2,4))
  rail=box(-98,80 if sy>0 else -86,100.63,193,6,6);front=box(-98,82 if sy>0 else -96,98.63,6,14,10);rear=box(89,82 if sy>0 else -96,98.63,6,14,10)
  s=fuse([panel,rail,front,rear]).cut(fuse(bores10+bores11));parts.append(add('BANK_PANEL_'+('POS' if sy>0 else 'NEG'),s))
  for tag,x0,L,headx,wx,nx,nh in [('FRONT',-104.5,20,-107.5,-92,-91.5,2.4),('REAR',82.5,25,107.5,88.5,86.1,2.4)]:
   # Rear screw points -X: fullshaft82.5..107.5; front points +X.
   shaft=cylx(x0,yc,103.63,1.5,L);head=cylx(headx,yc,103.63,2.75,3);steel.append(add(f'BANK_{sy}_{tag}_M3x{L}_FULL',shaft.fuse(head),(.7,.7,.73)))
   washers=[(-104.5,-104),(-92,-91.5)] if tag=='FRONT' else [(107,107.5),(88.5,89)]
   for j,(a,b) in enumerate(washers):steel.append(add(f'BANK_{sy}_{tag}_washer{j}',cylx(a,yc,103.63,3.5,b-a).cut(cylx(a-.01,yc,103.63,1.6,b-a+.02)),(.7,.7,.73)))
   steel.append(add(f'BANK_{sy}_{tag}_fullnut',hx(nx,yc,103.63,5.5,nh).cut(cylx(nx-.01,yc,103.63,1.525,nh+.02)),(.7,.7,.73)))
 # Shared rear FIVE-case ladder: real source P11 bypass rather than case/head micromoves.
 bypass=[box(98,51.75,103,77,3,4),box(98,79.25,103,77,3,4),box(169,51.75,103,6,30.5,4)]
 p11=old11.cut(box(94,54.75,102.99,14,24.5,4.02));p11=fuse([p11]+ears11+bypass)
 ladder=[box(55,78,55,120,4.4,29),box(55,54,52.6,120,5,2.4),box(169,54,52.6,6,28.4,54.4),box(55,51.75,103,120,3.25,5.65).cut(Part.makeCylinder(4.25,5,V(103,49,107)))]
 tieparts=[];tie_meta=[]
 for i,role in enumerate(['Pi3A','AUX4A','Yaw1A','Pitch1A','Tail1A']):
  o=D.getObject('FHAC0001_'+role);s=o.Shape.copy();s.translate(V(0,0,5));o.Shape=s;o.Label='WHOLE FHAC '+role+' / shared ladder55..106 / bothfactoryleads FIT2'
  x=55+23*i;ladder.append(box(x,54.25,106.25,20.25,4.75,2.4));band=ringxy(x,56,x+20.25,82.4,77.75,2.5,1.2);tieparts.append(band);tie_meta.append(dict(role='FHAC_'+role,sku='111-02370_T18I',unit145=True,section=[2.5,1.2],loop_nominal=2*(20.25+26.4+2.4),physical_fullstock_tension_FIT=True,unused_tail_open_assembly_then_human_trim=True))
  add('TIE_FHAC_'+role+'_NYLON_REFERENCE',band,(.25,.25,.28));add('TIE_FHAC_'+role+'_FULL_HEAD',box(x+7.725,51.5,77.75,4.8,4.5,3.5),(.25,.25,.28))
 p11=fuse([p11]+ladder);p11=p11.cut(fuse(bores11+tieparts));D.getObject('P11_rear_gate').Shape=p11;D.getObject('P11_rear_gate').Label='P11 V16 protection ladder + around-bank load bypass / roots cap retained'
 # Common front F0 saddle rooted at actual top P10, independent of wirepull; bottom stops in OWN P02.
 hanger=box(-106,46.5,85,6,6,49.5);top=[box(-133,y,119.25,33,2,2.4) for y in [32,65]]+[box(-106,32,119.25,6,35,2.4)];tieF=[]
 for z in [74,103]:
  b=ringxy(-132,32,-100,67,z,3.5,1.2);tieF.append(b);add(f'T30L_F0_{z}_NYLON_REFERENCE',b,(.2,.2,.23));add(f'T30L_F0_{z}_FULL_HEAD',box(-138,46.5,z,6,6,4),(.2,.2,.23));tie_meta.append(dict(role='F0_'+str(z),sku='111-03410_T30L',unit190min_nom198=True,section=[3.5,1.2],head_project_reservation=[6,6,4],loop_nominal=2*(32+35+2.4),unused_tail_open_assembly_then_human_trim=True))
 p10=fuse([old10,hanger]+top+ears10).cut(fuse(bores10+tieF));D.getObject('P10_front_gate').Shape=p10;D.getObject('P10_front_gate').Label='P10 V16 front F0 independent case capture + bank ears'
 # One lower organizer across actual deck parting. No purchased body cut; guides and source covers provide positive capture.
 added=[];cases=[o for o in D.Objects if o.Name.startswith(('WAGO415','WAGO615'))]
 for o in cases:
  b=o.Shape.BoundBox;added.append(box(b.XMin-2,b.YMin-2,48.22,b.XLength+4,b.YLength+4,b.ZMin-48.22))
  for x in [b.XMin-2,b.XMax+.25]:added.append(box(x,b.YMin,50.52,1.75,b.YLength,4))
  for x in [b.XMin,b.XMax-2]:
   for y in [b.YMin-2,b.YMax+.25]:added.append(box(x,y,50.52,2,1.75,2))
 # Rear two WAGOs need one removable common keeper; long row keepers are also one each, with T18I-held real slotted posts.
 caps=[]
 def keeper(tag,xc,yc,span,xcase0,xcase1,ybar):
  nonlocal added
  cap=[box(xcase0,ybar,60.02,xcase1-xcase0,2,2.4)]
  for j,x in enumerate(xc):
   post=box(x-4,yc-4,48.22,8,8,11.8);slot=box(x-4.1,yc-1.45,50.12,8.2,2.9,1.6);post=post.cut(slot);added.append(post)
   cap.append(box(min(x-4,xcase0 if j==0 else xcase1-2),min(yc-4,ybar),60.02,abs((xcase0+2 if j==0 else xcase1+2)-(x-4)),abs(ybar-yc)+6,2.4))
   # Actual rectangular ring material through the post tunnel, not its airBBox.
   ring=box(x-5.2,yc-1.25,50.12,10.4,2.5,13.5).cut(box(x-4,yc-1.26,51.32,8,2.52,11.1));tieparts.append(ring);add(tag+f'_T18I{j}_NYLON',ring,(.2,.2,.23));add(tag+f'_T18I{j}_HEAD',box(x-8,yc-2.25,55,4.8,4.5,3.5),(.2,.2,.23));tie_meta.append(dict(role=tag+str(j),sku='111-02370_T18I',unit145=True,section=[2.5,1.2],loop_nominal47p8=True,unused_tail_open_assembly_then_human_trim=True))
  # Middle main-row bodies are positively captured by actual P19/P12 above; split the new endkeepers around retained carrier crossarms.
  shape=fuse(cap)
  if tag.startswith('ROW_'):
   sy=1 if yc>0 else -1;bar=box(-49.5,37 if sy>0 else -39,60.02,156,2,2.4);left=fuse([bar.common(box(-70,-60,59,73.75,120,6)),box(-59.75,40.5 if sy>0 else -49,60.02,14.75,8.5,2.4),box(-49.5,37 if sy>0 else -49,60.02,2.5,12,2.4)]);right=fuse([bar.common(box(101.25,-60,59,20,120,6)),box(103.75,40.5 if sy>0 else -49,60.02,8,8.5,2.4),box(104.5,37 if sy>0 else -49,60.02,3.25,12,2.4)]);caps.append(add(tag+'_REMOVABLE_END_KEEPER_LEFT',left));caps.append(add(tag+'_REMOVABLE_END_KEEPER_RIGHT',right))
  else:caps.append(add(tag+'_REMOVABLE_COMMON_KEEPER',shape))
 keeper('ROW_POS',[-55.75,107.75],45,0,-49.5,106.5,37)
 keeper('ROW_NEG',[-55.75,107.75],-45,0,-49.5,106.5,-39)
 keeper('REAR_PAIR',[126.5,180.5],35,0,131.5,175.5,48)
 # WAGO615 positive upper restraint is ACTUAL P12 above, not a guessed newlid under the speaker.
 capture=[]
 for o in cases:
  if not o.Name.startswith('WAGO615'):continue
  b=o.Shape.BoundBox;c=box(b.XMin,b.YMin,b.ZMax,b.XLength,b.YLength,5).common(D.getObject('P12_common_deck_speaker').Shape);capture.append(dict(name=o.Name,actual_upper_capture_volume=c.Volume,gap_to_underside=1.48,lowerguides_height=4,remove_actualP12_before_levers=True))
 # Four actual separate MTA0100335 on one common open lower edge rail, factory exits kept open alongX.
 leg=[];legspine=box(-98,-51.4,61.8,175,2.9,5.2);added.append(legspine)
 for x in [-94,-49,-4,41]:added.append(box(x,-51.4,48.22,6,2.9,16.38))
 for i in range(4):
  o=D.getObject('Leg_protected_MTA0100335_'+str(i));b=o.Shape.BoundBox;added.append(box(b.XMin,-51.4,64.6,b.XLength,11,2.4))
  for x in [b.XMin-2,b.XMax+.25]:added.append(box(x,-48.5,67,1.75,8.1,2))
  # One selected whole T18I encloses case AND connected saddle; no wire pull/leg-E2 stock confusion.
  x=(b.XMin+b.XMax)/2;ring=box(x-1.25,-52.6,63.4,2.5,13.4,13.7).cut(box(x-1.26,-51.4,64.6,2.52,11,11.3));tieparts.append(ring);add(f'LEG{i}_T18I_NYLON',ring,(.2,.2,.23));tie_meta.append(dict(role='LEG'+str(i),sku='111-02370_T18I',unit145=True,section=[2.5,1.2],loop_nominal44p6=True,both_actual_MTA_factoryends_kept=True))
 # Front POST412 case and F0 lower corner floor, not electrically pressure-loaded ends.
 added += [box(-134,30,46.6,34,5,2.4),box(-134,64,46.6,34,5,2.4),box(-139,-62,47.6,35,26,2.4)]
 q=D.getObject('POST_F0_WAGO412').Shape.BoundBox
 for x in [-132,-116.75]:added.append(box(x,-60,50,1.75,22,10.5))
 postcap=add('POST412_REMOVABLE_KEEPER',box(-133,-61,60.5,19,24,2.4));caps.append(postcap)
 postring=box(-140.2,-50.25,46.4,37.4,2.5,17.7).cut(box(-139,-50.26,47.6,35,2.52,15.3));tieparts.append(postring);add('POST412_T18I_NYLON',postring,(.2,.2,.23));tie_meta.append(dict(role='POST412',sku='111-02370_T18I',unit145=True,loop_nominal110p2=True))
 organizer=fuse(added).cut(fuse([o.Shape for o in D.Objects if o.Name.startswith('LEG') and o.Name.endswith('_T18I_NYLON')]))
 # Root lower additions in BOTH actual deck parts without fictional fusion across X30.
 for n,reg in [('P02_front_deck',box(-160,-110,30,190,220,70)),('P03_rear_deck_integrated_load_yoke',box(30,-110,30,180,220,70))]:
  s=olddeck[n].fuse(organizer.common(reg));D.getObject(n).Shape=s;D.getObject(n).Label='V16 integral shared WAGO/protection organizer / '+n
 # Eight SELECTED inline junctions get one shared source-rooted strain rail, no8customcases or inventedbody dimensions.
 p6=D.getObject('P06_S0_shared_panel');old6=p6.Shape.copy();anchor=box(120,20.25,92.22,36,6,6.3)
 for i in range(8):anchor=anchor.cut(box(120.4+4.4*i,20.15,94.52,3.1,6.2,1.8))
 add('INLINE8_SOURCE_STRAIN_RAIL_UNSELECTED_ROOT_OPEN',anchor,show=False);p6.Label='P06 unchanged / inline8 candidate root NOT received'
 wr('retention-and-stock-plan.json',dict(ties=tie_meta,T18I_implemented_demand=16,T30L_implemented_demand=2,extra8_T18I_inline_strains_PLANNED_demand_unconfirmed=True,no_inventory_claim=True,unused_plastic_tail_trim_human_AFTER_lock_only=True,no_actual_cuts=True,wire_JR_Molex_4E2units_textile200_full=True,MTA_primary_nominal=dict(window=[11.3,22.2],panel2=True,flange_contact_nominal_each169p14=True,fullsourceBOX_not_clipgeometry=True,one_unit_FIT3=True),WAGO615_actual_uppercapture=capture,inline8=dict(actual_selected_refs=['W026','W037','W041','W042','W044','W045','W052','W053'],one_actual8slot_source_P06rail=True,actualbodypositions_and_case_fit_NOTqualified=True,no8newcases=True),FHAC_relocation=dict(deltaZ5=True,case55to106=True,all10factoryleads_full=True,affectedgrips_and_reach_FIT2_no_credit=True),assembly=['root frame/nuts before bank','two strips to actualfourreceiver ears, completefourM3sets','housingwithinternalcontacts first then wholeexternalfemaleTEfromopenbelow thenATOlast','loadWAGO guides/openlevers/fullwire ends then removable keeperbars; P12 removal for615 service','prethreadfullselectedplasticstock/caseclips thenlock; ONLYhumanmaytrimunusedplastictails later','all FHAC fullfactorypigtails openhandlay beforeclosure; no fakeE1disconnect']))
 D.Label='DAY16 SHARED PROTECTION NOMINAL RETENTION / CHECKPOINT';D.recompute();D.saveAs(str(P/'shared-protection-retention.FCStd'))
 r=dict(utc=datetime.now(timezone.utc).isoformat(),checks=[],failures=[],physical_pass=False,whole_kit_ready=False,actual_fit_cut_slack=None,group_scope='nominal actualprintmaterial, primaryclip/physicalsafeplastic FIT3; inlinebodies not yet secured')
 changed=[D.getObject(n) for n in ['P10_front_gate','P11_rear_gate','P02_front_deck','P03_rear_deck_integrated_load_yoke']]+parts+caps
 for o in dict((o.Name,o) for o in changed).values():
  s=o.Shape;row=dict(kind='print_realization',part=o.Name,valid=s.isValid(),solids=len(s.Solids));r['checks'].append(row)
  if not s.isValid() or len(s.Solids)!=1:r['failures'].append(row)
 # Actual ears roots/useful positive material; removablemates checked by nominalface contracts, not fused volumes.
 for owner,old,es in [('P10',old10,ears10),('P11',old11,ears11)]:
  for i,s in enumerate(es):r['checks'].append(dict(kind='actual_integral_ear_root',owner=owner,i=i,common=s.common(old).Volume))
 # Full selected TE/ATO avoid panel while boxhousing expected flange allocation overlap is NOT physicalplasticcollision.
 for panel in [o for o in parts if o.Name.startswith('BANK_PANEL')]:
  for o in D.Objects:
   if not o.Name.startswith('Motor_ATO'):continue
   for i in [1,2,3]:
    q=o.Shape.Solids[i]
    if gap(panel.Shape.BoundBox,q.BoundBox)>1.25:continue
    c=panel.Shape.common(q);g=panel.Shape.distToShape(q)[0];row=dict(kind='panel_vs_full_TE_ATO',panel=panel.Name,unit=o.Name,member=i,gap=g,common=c.Volume,valid=c.isValid());r['checks'].append(row)
    if not c.isValid() or c.Volume>1e-5 or g<1.25-1e-6:r['failures'].append(row)
 # One finite actual near-neighbor screen for all sharedparts; case contact and primaryflange interfaces are explicit, not blanketOWN.
 for o in parts+caps:
  if o.Name=='P06_S0_shared_panel':continue
  for n in ['P10_front_gate','P11_rear_gate','P12_common_deck_speaker','P19_shared_lower_carrier','P06_S0_shared_panel','S0_key','S1_NKK_S821_installed','MAIN_Pololu4853','AUX_Pololu4092']:
   q=D.getObject(n)
   if not q or gap(o.Shape.BoundBox,q.Shape.BoundBox)>1.25:continue
   c=o.Shape.common(q.Shape);g=o.Shape.distToShape(q.Shape)[0];row=dict(kind='sharedpart_actual_neighbor',part=o.Name,other=n,gap=g,common=c.Volume,valid=c.isValid());r['checks'].append(row)
   if not c.isValid() or c.Volume>1e-5:r['failures'].append(row)
 r['seconds']=time.perf_counter()-t;r['status']='NOMINAL_RETENTION_FINITE_BLOCKERS' if r['failures'] else 'NOMINAL_SHARED_RETENTION_REALIZED_LOCAL_GATES_PHYSICAL_COUPONS_OPEN';wr('retention-result.json',r);D.save();G.getDocument(D.Name).Modified=False;print(json.dumps(dict(status=r['status'],failures=r['failures'],checks=len(r['checks']),seconds=r['seconds'],objects=len(D.Objects))))
run()
