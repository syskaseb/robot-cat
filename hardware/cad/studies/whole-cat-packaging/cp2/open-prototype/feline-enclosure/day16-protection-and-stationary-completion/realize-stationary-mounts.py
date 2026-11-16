import FreeCAD as A,FreeCADGui as G,Part,json,math,time
from pathlib import Path
from datetime import datetime,timezone
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def fu(ss):
 s=ss[0]
 for q in ss[1:]:s=s.fuse(q)
 return s
def cyl(p,r,h,axis=(0,0,1)):return Part.makeCylinder(r,h,V(*p),V(*axis))
def hx(p,af,h,axis):
 u=V(1,0,0);a=V(*axis);v=a.cross(u);pts=[V(*p)+(u*math.cos(k*math.pi/3)+v*math.sin(k*math.pi/3))*(af/math.sqrt(3)) for k in range(6)];return Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(a*h)
def gap(a,b):return sum(max(0,getattr(a,k+'Min')-getattr(b,k+'Max'),getattr(b,k+'Min')-getattr(a,k+'Max'))**2 for k in ['X','Y','Z'])**.5
def wr(n,d):(P/n).write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
def run():
 if D.getObject('STATIONARY_REAL_MOUNTS_NOMINAL'):return print('already realized; use saved result')
 t=time.perf_counter();gr=D.addObject('App::DocumentObjectGroup','STATIONARY_REAL_MOUNTS_NOMINAL');new=[];steel=[];proof=[];holes=[];actual=[]
 old={n:D.getObject(n).Shape.copy() for n in ['P10_front_gate','P12_common_deck_speaker','P13_BUS_bridge','P14_fixed_touch_rail','P15_removable_mic_rail']}
 def add(n,s,kind='steel',visible=True):
  o=D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=(.7,.71,.75) if kind=='steel' else (.22,.6,.65);o.ViewObject.Visibility=visible;gr.addObject(o);new.append(o)
  if kind=='steel':steel.append(o)
  return o
 def integrate(n,ss,cuts=[]):
  initial=D.getObject(n).Shape.copy();joined=fu([initial]+ss)
  for c in cuts:joined=joined.cut(c)
  D.getObject(n).Shape=joined
  proof.append(dict(owner=n,retained_initial_missing_except_explicit_cuts=initial.cut(fu(cuts)).cut(joined).Volume if cuts else initial.cut(joined).Volume,new_members_missing=[s.cut(fu(cuts)).cut(joined).Volume if cuts else s.cut(joined).Volume for s in ss],positive_roots=[s.common(initial).Volume for s in ss],valid=joined.isValid(),solids=len(joined.Solids)))
 def setZ(tag,x,y,pcb,th,base,thbase,stand,L,m2=True):
  # Full M2, head/upperwasher/whole shaft/fullnut/lowerwasher; +Z head.
  under=pcb+th+.3;nb=base-.3-1.6
  for name,s in [('fullscrew',cyl((x,y,under-L),1,L).fuse(cyl((x,y,under),1.9,2))),('upperwasher',cyl((x,y,pcb+th),2.5,.3).cut(cyl((x,y,pcb+th-.01),1.1,.32))),('lowerwasher',cyl((x,y,base-.3),2.5,.3).cut(cyl((x,y,base-.31),1.1,.32))),('fullnut',hx((x,y,nb),4,1.6,(0,0,1)).cut(cyl((x,y,nb-.01),1,1.62))),('ordinaryspacer',cyl((x,y,base+thbase),2,stand).cut(cyl((x,y,base+thbase-.01),1.1,stand+.02)))]:add(tag+'_'+name,s)
  holes.append(dict(role=tag,M2_length=L,washer2=True,nutAF4_h1p6=True,PCBbottom=pcb,standoff=stand,fulltip=under-L,nutbottom=nb))
 # Whole plan: fixed source cases/ports remain; primary-defined PCBs sit on
 # dimensioned nominal datums inside existing allocations, not boxcorner claims.
 wr('whole-mount-datum-plan.json',dict(utc=datetime.now(timezone.utc).isoformat(),BUS=dict(primary42x33=True,PCBbottom110_from_actual_P13top107_plus3=True,axes=[[x,y] for x in [20.5,57.5] for y in [-14,14]],two_positiveY_M2sets_plus_fourpads=True,reason='negativeY extra screws would conflict with existing BUS frame joint; four supports/two full clamps retain board'),PCA=dict(actual_source_board_Y38to39p6=True,primary_axes=[[x,z] for x in [-91.825,-35.945] for z in [97.175,116.225]],rear_supportY41p6to44_standoff2=True,whole_tip47p7_below_bankY50=True),BNO=dict(primary25p4x22p86_centered_inside_oldcover=True,PCBbottom80_nominal=True,two_positiveY_holes_only=True,lower2unused_for_legcase_clearance=True,hook_root_actualP10_above_fullcover90=True),AMP=dict(primary17p78x19p05=True,PCBplaneY26p1_nominal_inside_existingcover=True,component_side_plusY_headerFIT=True,inside_captiveM2x8_no_lowerwasher_roof2=True,all_hardwareYmin20_above_PiCooling18plus1p25=True),MIC=dict(STEP_measurements_local_bound=True,PCBbottom144_equals_P15boss140_plus4=True,underside2p585_bottom141p415=True,whole_sourcecover_retained=True,actualrevision_FIT3=True),TTP='unknownmountpattern -> adjustablecommonperimeter; fixedP14, no fake E1 disconnect',speaker='adjustableperimeter trial only, basket/flange actualcontact and magnet gap FIT3, no membrane pressure claim',S1_monitor='NOT REALIZED in this batch; sharedroot/access still OPEN',no_bought_pose_move=True,no_wire_length_credit=True))
 # BUS: four actual support pads, TWO full throughsets on +Y; four sourceholes stay available.
 pads=[];bores=[]
 for x in [20.5,57.5]:
  for y in [-14,14]:
   pads.append(cyl((x,y,104),3.3,3));bores.append(cyl((x,y,102),1.1,12));add('BUS_PASSIVE_SPACER_'+str(x)+'_'+str(y),cyl((x,y,107),2,3).cut(cyl((x,y,107),1.1,3)))
   if y>0:setZ('BUS_'+str(x),x,y,110,1.6,104,3,3,12)
 integrate('P13_BUS_bridge',pads,bores);actual.append('BUS:4pads+2completeM2x12 throughsets; nominalPCBdatum/revisionFIT3')
 # PCA+whole E1: same common actualP12 root; open sidewalls, preserved audio feed.
 feed=box(-75,23,89.99,12,20,4.02);base=box(-98,34,90,126,4,4).cut(feed)
 members=[base];cuts=[]
 for x in [-91.825,-35.945]:
  members.extend([box(x-3,34,91,6,10,3),box(x-3,41.6,94,6,2.4,25.3)])
  for z in [97.175,116.225]:
   cuts.append(cyl((x,35,z),1.1,14,(0,1,0)));under=37.7
   add('PCA_'+str(x)+'_'+str(z)+'_fullscrew',cyl((x,under,z),1,10,(0,1,0)).fuse(cyl((x,under-2,z),1.9,2,(0,1,0))))
   for tag,y in [('front',37.7),('rear',44)]:add('PCA_'+str(x)+'_'+str(z)+'_'+tag+'washer',cyl((x,y,z),2.5,.3,(0,1,0)).cut(cyl((x,y-.01,z),1.1,.32,(0,1,0))))
   add('PCA_'+str(x)+'_'+str(z)+'_nut',hx((x,44.3,z),4,1.6,(0,1,0)).cut(cyl((x,44.29,z),1,1.62,(0,1,0))))
   add('PCA_'+str(x)+'_'+str(z)+'_spacer2',cyl((x,39.6,z),2,2,(0,1,0)).cut(cyl((x,39.59,z),1.1,2.02,(0,1,0))))
   holes.append(dict(role='PCA',axis=[x,z],M2_length10=True,spacer2=True,fullnut2washers=True,shaft_tip47p7=True))
   probe=cyl((x,37.99,z),1.25,1.62,(0,1,0));c=probe.common(D.getObject('PCA9685_Adafruit815_PCB').Shape);proof.append(dict(primary_PCA_bore=[x,z],common=c.Volume,valid=c.isValid(),if_positive_representation_missing_not_bought_drill=True))
 for x in [-28,25.25]:members.extend([box(x,34,91,2.75,14,3),box(x,38,94,2.75,10,30.5)])
 for x in [-25,22]:members.append(box(x,38,91.6,3,10,2.4))
 integrate('P12_common_deck_speaker',members,cuts)
 ecap=fu([box(-28,38,124.5,5.5,10,2.4),box(22.5,38,124.5,5.5,10,2.4),box(-28,46.75,124.5,56,2,2.4)])
 add('E1_SHARED_OPEN_EDGE_KEEPER',ecap,'print');actual.append('PCA:actual4primarybores/full4M2x10; E1sharededgecage+removablekeeper nominal safeedgeFIT3')
 for i,x in enumerate([-26.6,26.6]):
  outer=box(x-1.25,36.8,90.4,2.5,13.6,37.7);inner=box(x-1.26,38,91.6,2.52,11.2,35.3);q=outer.cut(inner);add('E1_T18I_'+str(i)+'_nylon',q);add('E1_T18I_'+str(i)+'_head',box(x+1.25,42,119,4.8,4.5,3.5))
 # BNO: two upper-row primary holes avoid four actual lower MTAunits.
 hook=[box(-107,-31,74.6,32.6,7.5,2.4),box(-107,-31,74.6,3.55,7.5,19.3),box(-107,-31,91.5,9,7.5,2.4)]
 bc=[]
 for x in [-97.36,-77.04]:bc.append(cyl((x,-27.76,70),1.1,15));setZ('BNO_'+str(x),x,-27.76,80,1.6,74.6,2.4,3,10)
 integrate('P10_front_gate',hook,bc);actual.append('BNO:2primaryholes/full2M2x10+actualhooktoP10; 2lowerholes unused')
 # AMP: whole captive architecture fits BETWEEN cooling18 and actualPCB26.1.
 am=[box(-58,16,93,20,8.1,3)];ac=[]
 for i,x in enumerate([-54.85,-42.15]):
  z=114.985;am.append(box(x-3,19.5,94,6,4.6,24));ac.extend([cyl((x,19.4,z),1.1,8,(0,1,0)),box(x-2.1,20.4,z-2.1,9.5,1.8,4.2)])
  add('AMP_'+str(i)+'_M2x8_full',cyl((x,20,z),1,8,(0,1,0)).fuse(cyl((x,28,z),1.9,2,(0,1,0))))
  add('AMP_'+str(i)+'_upperwasher',cyl((x,27.7,z),2.5,.3,(0,1,0)).cut(cyl((x,27.69,z),1.1,.32,(0,1,0))))
  add('AMP_'+str(i)+'_fullnut',hx((x,20.5,z),4,1.6,(0,1,0)).cut(cyl((x,20.49,z),1,1.62,(0,1,0))))
  add('AMP_'+str(i)+'_spacer2',cyl((x,24.1,z),2,2,(0,1,0)).cut(cyl((x,24.09,z),1.1,2.02,(0,1,0))))
 integrate('P12_common_deck_speaker',am,ac);actual.append('AMP:2primaryM2x8/captivenuts/2mmroof, no lowerwashers by whole bearing design')
 # MIC: true two diagonal STEP holeframes, underside2.585 kept above localboss140.
 data=json.loads((P.parents[7]/'reference/head-electronics-2026-09-22/measurements.json').read_text()) if False else json.loads(Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/reference/head-electronics-2026-09-22/measurements.json').read_text())
 pcb=data['pcb'];cx=(pcb['min_mm'][0]+pcb['max_mm'][0])/2;cy=(pcb['min_mm'][1]+pcb['max_mm'][1])/2;mm=[];mc=[];axes=[]
 for i,q in enumerate(data['mounting_holes']):
  x,y,_=q['centre_on_bottom_mm'];x=x-cx+38;y-=cy;axes.append([x,y]);mm.append(cyl((x,y,137.5),4,2.5));mc.extend([cyl((x,y,134),1.1,8),box(x-2.1,min(y,-25 if y<0 else 25),136.35,4.2,abs(y-( -25 if y<0 else 25))+2,1.75)])
  add('MIC_'+str(i)+'_fullM2x10',cyl((x,y,135.81),1,10).fuse(cyl((x,y,145.81),1.9,2)))
  add('MIC_'+str(i)+'_washer',cyl((x,y,145.51),2.5,.3).cut(cyl((x,y,145.5),1.1,.32)))
  add('MIC_'+str(i)+'_fullnut',hx((x,y,136.4),4,1.6,(0,0,1)).cut(cyl((x,y,136.39),1,1.62)))
  add('MIC_'+str(i)+'_spacer4',cyl((x,y,140),2,4).cut(cyl((x,y,139.99),1.1,4.02)))
 integrate('P15_removable_mic_rail',mm,mc);actual.append('MIC:2actualSTEPdiagonalM2x10 captivefeeds/4mmspacers, undersideclearance1.415, no4cornerfiction')
 # Fixed touch: sourcepattern unknown -> one shared openperimeter, twofullM2sets.
 tm=[];tc=[]
 for x in [2,32]:
  tm.extend([box(x-3.5,51,135.5,7,6,5.5),box(x-2,51,141,4,6,8.5)]);tc.append(cyl((x,54,131),1.1,24));setZ('TTP_'+str(x),x,54,149.5,2.4,135.5,14,0,20)
 cap=fu([box(0,43,149.5,5,24,2.4),box(30,43,149.5,5,24,2.4),box(0,43,149.5,35,2,2.4),box(0,65,149.5,35,2,2.4)])
 integrate('P14_fixed_touch_rail',tm,tc);cap=cap.cut(fu(tc));add('TTP_FIXED_COMMON_PERIMETER_KEEPER',cap,'print');actual.append('TTP:realsharedperimeter+2fullM2x20; contactlands/revisionFIT3, touchwindowopen')
 D.Label='DAY16 STATIONARY NOMINAL REAL MOUNTS / FINITE DELTA OPEN';D.recompute();D.saveAs(str(P/'stationary-completion.FCStd'));G.getDocument(D.Name).Modified=False
 wr('realization-checkpoint.json',dict(utc=datetime.now(timezone.utc).isoformat(),realized=actual,proof=proof,whole_hardware=holes,mic_axes=axes,root_first_then_modules_then_realcap=True,source_module_positions_unchanged=True,source_integral_parting_preserved=True,unsecured=['inline8 rejected S0metalgap0.596503','negative415rightfullstock S0body common35.5368+head75.2666 remainsHOLD','speakerbasket actualsafecontact/retention','S1/monitor','head/tailhorns','covers/wirebudgets'],physical_pass=False,wholekit_ready=False,actual_cut_fit_slack=None,newobjects=len(new),objects=len(D.Objects),seconds=time.perf_counter()-t))
 print(json.dumps(dict(saved=D.FileName,objects=len(D.Objects),realized=actual,seconds=time.perf_counter()-t,connection_defects=[q for q in proof if 'solids' in q and(q['solids']!=1 or not q['valid'])])))
run()
