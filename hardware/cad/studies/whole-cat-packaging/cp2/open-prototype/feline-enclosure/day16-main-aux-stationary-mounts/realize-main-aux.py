import FreeCAD as A,FreeCADGui as G,Part,json,time,math
from pathlib import Path
from datetime import datetime,timezone
P=Path(__file__).parent;V=A.Vector
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def cyl(x,y,z,r,h):return Part.makeCylinder(r,h,V(x,y,z))
def fuse(ss):
 s=ss[0]
 for q in ss[1:]:s=s.fuse(q)
 return s
def gap(a,b):return sum(max(0,getattr(a,k+'Min')-getattr(b,k+'Max'),getattr(b,k+'Min')-getattr(a,k+'Max'))**2 for k in ['X','Y','Z'])**.5
def wr(n,d):(P/n).write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
def run():
 D=A.ActiveDocument;t=time.perf_counter();mount=D.getObject('PROPOSED_OPEN_MOUNT_PLANE_NOT_PRINT_PART');oldplane=mount.Shape.copy();p11=D.getObject('P11_rear_gate');oldp11=p11.Shape.copy();holes=[(89.321,24.159),(89.321,42.701),(122.241,70.241),(101.159,70.241),(122.241,49.159)];bosses=[];cages=[];rootbores=[];seatcuts=[]
 plan=dict(utc=datetime.now(timezone.utc).isoformat(),source='Frozenwhole4e567/82e8a5d4; actual MAIN/AUX primary2+3hole axes; fixed PCBbottom119, unchanged ports/full9.5AUX',one_common_print=True,actual_root=[(103,35),(103,49)],M2_axes=holes,realization='Two ordinary spacer4, local4mmrootbosses111..115, exact matchedISO10642headcones, actual2P11bores+Ucaptivenutseats/feed, five2.4planeholes+OD4L4spacers+M2x12fullsets',load='P11 actual top107 ->ordinaryspacer4 ->bossbottom111 ->commonplane115 ->five4mmspacers ->actualPCB119',safePCBcontact='Nominal annulus OD4/ID2.2 at supplier mount holes, not pressure on fullundersidefield; real annulus/components/revision FIT3',no_module_pose_change=True,unrelated_module_groups_planned_not_secured=True)
 wr('mount-realization-plan.json',plan)
 for i,y in enumerate([35,49]):
  x=103;bosses.append(cyl(x,y,111,5,4));rootbores.append(cyl(x,y,97,1.7,20));seatcuts.append(Part.makeCone(1.5,3.36,1.86,V(x,y,113.14)))
  D.getObject(f'ROOT_{i}_ordinary_spacer5').Shape=cyl(x,y,107,3,4).cut(cyl(x,y,107,1.6,4));D.getObject(f'ROOT_{i}_ordinary_spacer5').Label='ACTUAL ROOT ordinary spacer OD6 L4 / replaces proposed L5'
  cage=box(98,y-5,98.5,11,10,4.8)
  nutp=box(99.6,y-2.85,100.1,9.6,5.7,2.4)
  washp=cyl(x,y,102.5,3.7,.5).fuse(box(x,y-3.7,102.5,6.2,7.4,.5))
  cages.append(cage.cut(nutp.fuse(washp)).cut(rootbores[-1]))
 plane=fuse([oldplane]+bosses).cut(fuse(rootbores+seatcuts+[cyl(x,y,110,1.2,7) for x,y in holes]));mount.Shape=plane;mount.Label='P20 ACTUAL COMMON MAIN-AUX OPEN MOUNT / 2root seats +5M2bores'
 lower=fuse([oldp11.cut(fuse(rootbores))]+cages);p11.Shape=lower;p11.Label='P11 LOWER V16 rootbores+real captive nut feeds; upper removable unchanged'
 D.Label='DAY16 MAIN AUX REAL MOUNTS / ROOT-FIRST PCB-LATER CAP-LAST';D.recompute();D.saveAs(str(P/'main-aux-stationary-mounts.FCStd'))
 r=dict(utc=datetime.now(timezone.utc).isoformat(),checks=[],failures=[],realized_groups=['MAIN4853 primary2M2','AUX4092 full9.5 primary3M2','sharedP20actual2M3 root+P11Ucapture'],planned_groups=['BUSPCB onP13','PCA+wholeE1','BNO AMP speakerbasket','TTP MIC','S1 monitor','MTA WAGO FHAC'],physical_pass=False,whole_kit_ready=False,actual_fit_cut_slack=None)
 def ck(row,ok):
  r['checks'].append(row)
  if not ok:r['failures'].append(row)
 for n,s in [('P20',plane),('P11',lower)]:ck(dict(kind='real_print',part=n,valid=s.isValid(),solids=len(s.Solids)),s.isValid() and len(s.Solids)==1)
 for i,c in enumerate(cages):
  common=c.common(oldp11);ck(dict(kind='cage_actual_positive_root',i=i,common=common.Volume,valid=common.isValid()),common.isValid() and common.Volume>1e-5)
 for i,b in enumerate(bosses):ck(dict(kind='boss_positive_connection',i=i,common=b.common(oldplane).Volume),b.common(oldplane).Volume>1e-5)
 for n,s in [('P20',plane),('P11',lower)]:
  for o in D.Objects:
   if not (o.Name.startswith(('OPEN_ROOT','ROOT_','OPEN_M2')) and hasattr(o,'Shape')):continue
   q=o.Shape
   if gap(s.BoundBox,q.BoundBox)>.01:continue
   c=s.common(q);ck(dict(kind='whole_steel_or_spacer_ownprint_nonpenetration',part=n,other=o.Name,common=c.Volume,valid=c.isValid()),c.isValid() and c.Volume<1e-5)
 # True supplier bore/nominal safe annulus witnesses, no full AUXbox treated as solid at intended PCBmounts.
 for i,(x,y) in enumerate(holes):
  board=D.getObject('MAIN_Pololu4853' if i<2 else 'AUX_Pololu4092').Shape;probe=cyl(x,y,119,1.09,1.5748 if i<2 else 1.57);c=board.common(probe);ck(dict(kind='actual_primary_bore_binding',i=i,common=c.Volume,valid=c.isValid()),c.isValid() and c.Volume<1e-5)
  for tag in ['upperwasher','ordinary_spacer4']:
   q=D.getObject(f'OPEN_M2_{i}_{tag}').Shape;c=q.common(board);ck(dict(kind='actual_metal_support_vs_board_source',i=i,tag=tag,common=c.Volume,valid=c.isValid(),safe_real_component_annulus_FIT3=True),c.isValid() and c.Volume<1e-5)
 # Actual continuous sidefeed of full rootnut+washer, not just final position.
 for i,y in enumerate([35,49]):
  nutfeed=box(99.825,y-2.75,100.1,16.175,5.5,2.4);washerfeed=cyl(103,y,102.5,3.5,.5).fuse(box(103,y-3.5,102.5,13,7,.5))
  for tag,q in [('fullnut_feed',nutfeed),('fullwasher_feed',washerfeed)]:
   c=q.common(lower);ck(dict(kind=tag,i=i,common=c.Volume,valid=c.isValid()),c.isValid() and c.Volume<1e-5)
 # Only NEW positivebosses and cages against current retained rigid neighbor parts. Bodycovers/proxies not rigid components.
 changed=[('rootboss'+str(i),s) for i,s in enumerate(bosses)]+[('rootcage'+str(i),s) for i,s in enumerate(cages)]
 names=['S0_key','S1_NKK_S821_installed','Monitor_MOD05015','P13_BUS_bridge','P14_fixed_touch_rail','P15_removable_mic_rail','P11_REMOVABLE_UPPER_CROSSMEMBER','MAIN_Pololu4853','AUX_Pololu4092','FHAC0001_AUX4A','E2_Molex_and_inline_WAGO']
 for n,s in changed:
  for name in names:
   o=D.getObject(name)
   if not o or not hasattr(o,'Shape') or gap(s.BoundBox,o.Shape.BoundBox)>=1.25:continue
   q=o.Shape;g=s.distToShape(q)[0];c=s.common(q);ck(dict(kind='changed_positive_actual_neighbor',part=n,other=name,gap=g,common=c.Volume,valid=c.isValid(),classification='E2groupallocation_not_deliveredcontact' if name.startswith('E2') else 'retained actual/source'),c.isValid() and g>=1.25-1e-6 and c.Volume<1e-5)
 r['status']='MAIN_AUX_HOLD_FINITE_CAUSES' if r['failures'] else 'MAIN_AUX_REAL_MOUNT_LOCAL_SCOPED_ROOT_AND_5HOLE_JOINTS';r['seconds']=time.perf_counter()-t;wr('mount-function-result.json',r);D.save();G.getDocument(D.Name).Modified=False;print(json.dumps(dict(status=r['status'],checks=len(r['checks']),failures=r['failures'],seconds=r['seconds'],objects=len(D.Objects))))
run()
