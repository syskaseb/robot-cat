"""Allocate complete independent insulation/case restraints before native CAD.

Replaceable ordinary bands, no adhesive carrying a wire load. Shared jaw at
the intact yaw tails is separate from their solder sleeves and JR cases.
"""
import plan_current_head_supply as S
from plan_current_tail_complete import tie_x
A,Part,H,OUT=S.A,S.Part,S.H,S.OUT
box=H.T.box

def plan():
 parts=S.layout();pads=[];cuts=[];bands={};grips=[]
 parts['FHYFloor']=box([-168,-97,106,-108,-73.5,110])
 def add(n,b):
  parts[n]=box(b);pads.append(dict(name=n,bounds_mm=b))
 def cut(n,b):
  cuts.append(dict(name=n,bounds_mm=b))
 def grip(n,x,y,z,r,base,postwidth=7,headnorth=True):
  # Bearing plane is below intact insulation by0.05. The band silhouette
  # also has0.05 clearance; tension/creep/realOD remain delivery gates.
  top=z-r-.05;y0,y1=y-r-1.3,y+r+1.3;z0,z1=top-2.7,z+r+1.25
  add(n+'Post',[x-postwidth/2,y-r-1.25,base,x+postwidth/2,y+r+1.25,top])
  band,head=tie_x(x,y0,y1,z0,z1,headnorth);bands[n+'_Band']=band;bands[n+'_Head']=head
  cut(n+'Return',[x-1.5,y0-.2,z0-.1,x+1.5,y1+.2,z0+1.4])
  for label,aa,bb in [('S',y0-.2,y0+1.25),('N',y1-1.25,y1+.2)]:
   cut(n+'Side'+label,[x-1.5,aa,z0-.1,x+1.5,bb,z1+.2])
  grips.append(dict(name=n,axis='X',centre_mm=[x,y,z],intact_insulation_only=True,T18I=1))
 # Same complete two fuse bodies; factory exits independently supported.
 add('FHYWestWing',[-178,-89,107,-166,-81,110])
 add('FHYEastWing',[-115,-89,107,-106,-81,110])
 add('FHPWestWing',[-49,84,66.99,-38.05,93,69.99])
 add('FHPEastWing',[12.95,84,66.99,24,93,69.99])
 for n,x,y,z,base in [('FHYOut',-171.5,-85.125,120,110),('FHYIn',-110.5,-85.125,120,110),
  ('FHPOut',-42.55,88.625,79.99,69.99),('FHPIn',17.45,88.625,79.99,69.99)]:grip(n,x,y,z,2,base,headnorth=not n.startswith('FHP'))
 # One group jaw OUTSIDE the fuse body, on all three intact straight
 # source tails. A tall post under the red wire inside the fuse would be
 # a false load path and would also obstruct its ATO lid.
 x=-100.5;bottom=138.3224451363255-1.1
 # Bridge ABOVE the whole120mm downleg, rooted SOUTH of the factory
 # input. A continuous tall post fromZ110 would cut its own earlier wire.
 add('YawSourceBridgeRoot',[-114,-95,107,-108,-90,126.4])
 add('YawSourceBridge',[-114,-95,123.4,-97.5,-81,126.4])
 add('YawSourcePost',[-103.5,-87.2,126.4,-97.5,-82.9,bottom])
 band,head=tie_x(x,-88.446025219201,-81.653048041315,bottom-2.7,140.220816502359+2.3)
 bands['YawSource_Band']=band;bands['YawSource_Head']=head
 cut('YawSourceReturn',[x-1.5,-88.65,bottom-2.8,x+1.5,-81.45,bottom-1.3])
 for aa,bb in [(-88.65,-87.2),(-82.9,-81.45)]:cut('YawSourceSide'+str(aa),[x-1.5,aa,bottom-2.8,x+1.5,bb,143])
 grips.append(dict(name='YawSource',centre_mm=[x,-85,139.0124355653],intact_insulation_only=True,T18I=1,wires=['XB12','XB13','XS13']))
 # Paired source stub; the top-facing head clears ALL five ports. Side
 # heads here would block the neighbouring port1/2 or5 approach.
 x=-111.5;z=123.39378221735;top=z-1.1
 add('GroundSourcePost',[-115,-31.65,116.40378221735,-108,-24.7,top])
 band,unused=tie_x(x,-33,-23.35,top-2.7,z+2.3)
 bands['GroundSource_Band']=band
 bands['GroundSource_Head']=box([x-2.4,-29.925,z+2.3,x+2.4,-26.425,z+6.8])
 cut('GroundSourceReturn',[x-1.5,-33.2,top-2.8,x+1.5,-23.15,top-1.3])
 for aa,bb in [(-33.2,-31.75),(-24.6,-23.15)]:cut('GroundSourceSide'+str(aa),[x-1.5,aa,top-2.8,x+1.5,bb,z+2.5])
 grips.append(dict(name='GroundSource',centre_mm=[x,-28.175,z],intact_insulation_only=True,T18I=1,ports=[3,4]))
 # Retain the already qualified W2 yaw carrier/joints. Its sleeves are
 # staggered and followed by a taper, not another straight insulation seat.
 # YawSource independently anchors the three fixed feeds upstream.
 yaw_pads=[];yaw_cuts=[]
 # Both known PCB feeds are gripped at their straight fanouts, not bare
 # copper, pads or the first formed1mm bare arc. Carrier changes separately.
 carrier_pads=[];carrier_cuts=[]
 for n,y,headnorth in [('B1',27.57,True),('B2',-27.6,False)]:
  before=len(pads);beforecuts=len(cuts)
  add(n+'Root',[60,y-3.5,74.72,68,y+3.5,77.72]);grip(n,64,y,79.2,1.05,77.72,8,headnorth)
  bands[n+'_Head']=box([61.6,y-1.75,81.5,66.4,y+1.75,86.0])
  carrier_pads.extend(pads[before:]);del pads[before:]
  carrier_cuts.extend(cuts[beforecuts:]);del cuts[beforecuts:]
  for row in carrier_pads:
   parts.pop(row['name'],None)
 # Two replaceable body bands each; ATO service cuts these only, supports
 # the holder and opens it on the bench. No routine WAGO disconnect bank.
 for label,bounds,xs in [('FHY',H.bb(parts['F_HY_case']),[-150,-130]),('FHP',H.bb(parts['F_HP_case']),[-28,-8])]:
  for i,x in enumerate(xs):
   gap=1.35 if label=='FHY' else 1.2
   y0,y1=bounds[1]-gap,bounds[4]+gap;z0=bounds[2]-2.7;z1=bounds[5]+1.25
   band,head=tie_x(x,y0,y1,z0,z1,label!='FHP')
   if label=='FHY':head=box([x-2.4,-79,z1,x+2.4,-75.5,z1+4.5])
   else:head=box([x-2.4,79,z1,x+2.4,82.5,z1+4.5])
   bands[label+'Case'+str(i)+'_Band']=band;bands[label+'Case'+str(i)+'_Head']=head
   cut(label+'CaseReturn'+str(i),[x-1.5,y0-.2,z0-.1,x+1.5,y1+.2,z0+1.4])
   for side,aa,bb in [('S',y0-.2,y0+1.25),('N',y1-1.25,y1+.2)]:
    cut(label+'CaseSide'+str(i)+side,[x-1.5,aa,bounds[2]-2.8,x+1.5,bb,bounds[2]+.1])
 # Keep SJ4570's actual2.49 envelope beneath G_AUX. It retains the case,
 # never a substitute for the independent port3/4 source insulation grip.
 parts['G_AUX_SJ4570']=box([-135,-39.8,116.40378221735,-117,-29.8,118.89378221735])
 return dict(pads=pads,cuts=cuts,carrier_pads=carrier_pads,carrier_cuts=carrier_cuts,yaw_pads=yaw_pads,yaw_cuts=yaw_cuts,
  bands=bands,parts=parts,grips=grips,T18I_new=len(grips)+4,SJ4570_reused_pairs=1,SJ4570_trimmed_pair_mm=[18,10],
  service='Energy absent. Support each FHAC and cut its two body bands; open the delivered lid on the supported bench if its provisional in-place lid envelope fails. Do not pull wires. Source/G_AUX and known PCB ends are released only for whole head removal, not routine fuse replacement.',
  phase2_gates=['Delivered FHAC100mm per-side/OD4/R6/usable length and lid/tool fit','T18I head3.5x4.8x4.5 actual orientation, tension, liner, creep and support edges','SJ4570 PETG adhesion and mated thickness; not wire restraint','No source energizing before global E3/E4 tests'])
if __name__=='__main__':
 p=plan();S.save('grip-plan.json',{k:v for k,v in p.items() if k not in ('parts','bands')})
 print('Planned',len(p['grips']),'independent insulation grips,',p['T18I_new'],'new bands')
