"""Open seats, board bearings, fuses and adjustable sample locations, one installed rack per level."""
from pathlib import Path
P=Path(__file__).parent
exec((P/'core.py').read_text().split('# Each board/power cluster')[0])
names=sorted(n for n in group('WAGO415_') if n!='WAGO415_data_1_0')
def obj(n):return D.getObject(n)
report={};adds={k:[] for k in ['ForeBase','RearBase','ForeLid','RearLid']}
def writepart(n,s):
    s=s.removeSplitter();obj(n).Shape=s
    report[n]=dict(pieces=[dict(volume=k.Volume,box=bounds(k)) for k in s.Solids],valid=s.isValid())
# The claws bear on the new rungs running over their full foot width. The only
# unsupported portions above the rungs are the four millimetre long clip springs.
for side,ids in [('Neg',names[:8]),('Pos',names[8:])]:
    for j,sub in enumerate([ids[:4],ids[4:]]):
        n='E19_Wago'+('Fore' if j==0 else 'Rear')+side
        blocks=[sh(n)]
        for q in sub:
            b=sh(q).BoundBox
            for x in [b.XMin-1.2,b.XMax-1.3]:
                blocks.append(box(x,b.YMin-1.15,111.35,2.51,b.YLength+2.3,2.55))
        rack=join(blocks)
        edge=24.98 if j==0 else 25.02
        rack=rack.common(box(-110 if j==0 else edge,-105,99,edge+110 if j==0 else 160-edge,210,33))
        writepart(n,rack)
# Remove only seam shards trapped below the plate; use a tongue through two
# existing wall windows at the adapter's rear edge, outside equipment.
q=sh('E19_FrontShroud');parts=sorted(q.Solids,key=lambda s:s.Volume,reverse=True)
report['chin_seam_shards']=[dict(volume=p.Volume,bounds=bounds(p)) for p in parts[1:]]
s=parts[0]
for sg in [-1,1]:
    tongue=box(-65.2,100.4 if sg==1 else -102.1,87,7.5,1.7,9)
    # Slip tongue on INSIDE wall. The lid prevents extraction in service.
    s=s.fuse(tongue)
    base=obj('E19_ForeBase');base.Shape=base.Shape.cut(box(-64.1,100.1 if sg==1 else -102.4,86.7,6.85,2.3,9.6))
writepart('E19_FrontShroud',s)
# Rear bottom edge allowance for the two projecting socket roots at X20.
rear=obj('E19_RearBase')
for yp in [-98,95]:rear.Shape=rear.Shape.cut(box(20.1,yp-2.8,39.7,2.35,7.4,2.3))
# Panels open individually. Put complete microphone with its USB and two steel
# sets below the fore cap. Speaker and monitor use rear cap, away from jaw loop.
move('ReSpeakerLite_on_REMOVABLE_back',group('HB_MIC_')+['D19_MIC_FULL_HEIGHT_RESERVE'],[-54,-14,156.5],90)
move('Speaker',[],[28,-24,150.4])
move('TTP223_touch',[],[-19,-40,163.1])
# PCB bearing tube reaches the REAL washer or board plane. All hardware stays separate.
def hanger(key,x,y,low,high,inner,outer,bridge=True):
    c=cyl(x,y,low,outer,high-low).cut(cyl(x,y,low-.1,inner,high-low+.2))
    adds[key].append(c)
def footbed(key,n,span,post=True):
    b=sh(n).BoundBox;x,y,z=b.XMin,b.YMin,b.ZMin;l,w=b.XLength,b.YLength
    # two narrow bottom support ribs, open ends for leads, no wall around fuse covers.
    for t in [.19,.76]:
        xx=x+l*t
        a=box(xx,y-.9,z-2.6,3.4,w+1.8,2.6)
        for yy in [y-1.1,y+w+.15]:a=a.fuse(box(xx,yy,z-2.5,3.4,.95,5))
        if post:
            for yy in [y+.5,y+w-3.25]:
                a=a.fuse(box(xx+.3,yy,41.1,2.8,2.8,z-41.1-1.5))
        adds[key].append(a)
# Independent supports below the open terminals of both short pairs, including all five full FHAC.
for n in ['PBAY_P_AUX','PBAY_P_REAR','PBAY_F_AUX','PBAY_F_HY','PBAY_F_TY','PBAY_F_HP','WAGO615_power_0_0','WAGO615_power_0_1','PBAY_P_SYS','PBAY_F_PI','PBAY_POST_F0','F0_FHAC0002_30A']:
    key='ForeBase' if sh(n).BoundBox.Center.x<20 else 'RearBase'
    footbed(key,n,None)
# Two accessible fuse straps per three-unit row can thread between factory ends.
# Inline stations used to coincide with the fuse lane; group all eight below the slats.
inline=sorted(group('NIGHT_INLINE_'))
for i,n in enumerate(inline):
    # Keep the 2+2 pairs at their leg stations. Identify actual corner by name.
    front='_F' in n;positive=('_FR_' in n or '_RR_' in n)
    x=-104 if front else 62
    same=[q for q in inline if q.split('_')[2]==n.split('_')[2]]
    y=(62 if positive else -88)+10*same.index(n)
    # Rear negative is the occupied JR tray; use the empty space at its anterior side below it.
    z=48.2 if not front else 51.2
    move(n,[],[x,y,z]);footbed('ForeBase' if front else 'RearBase',n,None)
# PCB bearing at every Pi fastening plane z95..98, on an open partial frame.
pi=[]
for x in [-104.5,-46.5]:
    for y in [-24.5,24.5]:
        pi.append(cyl(x,y,95,3.8,3).cut(cyl(x,y,94.9,1.38,3.2)))
    pi.append(box(x+1.6,-24.8,95,1.8,49.6,3))
for y in [-24.5,24.5]:
    pi.append(box(-103.3,y+1.45,95,56.8,1.8,3))
    pi.append(box(-105.5,min(y,math.copysign(33,y)),94.7,3.2,9.6,2.8))
    pi.append(box(-105.5,31 if y>0 else -33.6,41.1,3.2,3,55.8))
adds['ForeBase']+=pi
# MAIN/AUX/AMP use the source washer-to-board span. A pair of outboard legs
# joins the bearing bars to the base. BNO is hung from above, at its back washer.
for label,board in [('MAIN','MAIN_Pololu4853'),('AUX','AUX_Pololu4092'),('AMP','MAX98357A_amp')]:
    pts=[]
    for n in group('CB_'+label+'_'):
        if not n.endswith('_basewasher'):continue
        b=sh(n).BoundBox;x=b.Center.x;y=b.Center.y;z=b.ZMax;hi=sh(board).BoundBox.ZMin
        hanger('RearBase',x,y,z,hi,1.18,3.3)
        pts.append([x,y,z])
    for x,y,z in pts:
        # Leg displaced outward of the screw head and seated tangentially in its bearing.
        adds['RearBase'] += [box(x+1.7,y-.95,z+1,3.4,1.9,2.6),box(x+3.6,y-1.25,41,2.5,2.5,z-38.1)]
for n in group('CB_BNO_'):
    if n.endswith('backwasher'):
        b=sh(n).BoundBox;x=b.Center.x;y=b.Center.y
        hanger('RearLid',x,y,110.6,116.6,1.16,3.25)
        adds['RearLid'] += [box(x+1.7,y-.9,113,4,2,2.5),box(x+4.2,y-.9,113,2.6,2,59)]
# Microphone full steel lies below PCB; hang from the headwasher-side printed
# land without loading a connector. Bridge runs to the nearest wall of the top cap.
for n in group('HB_MIC_'):
    if n.endswith('headwasher'):
        b=sh(n).BoundBox;x=b.Center.x;y=b.Center.y;z=b.ZMax
        hanger('ForeLid',x,y,z,z+3.85,1.15,3.2)
        adds['ForeLid'] += [box(x+1.7,y-.8,z+1.35,4,1.8,2.2),box(x+4.2,y-.8,z+1.35,2.7,1.8,172-z)]
for n in group('OP_MONITOR_'):
    if n.endswith('nutwasher'):
        b=sh(n).BoundBox;x=b.Center.x;y=b.Center.y;z=b.ZMax
        hanger('RearLid',x,y,z,z+4.8,1.16,3.25)
        adds['RearLid'] += [box(x+1.7,y-.85,z+1,4.2,1.8,2.3),box(x+4.3,y-.85,z+1,2.6,1.8,172-z)]
# Speaker held by side clips; touch board rests against thin solid lid membrane.
for n,key in [('Speaker','RearLid'),('TTP223_touch','ForeLid')]:
    b=sh(n).BoundBox
    for x in [b.XMin+2,b.XMax-8]:
        for sg,y in [(-1,b.YMin),(1,b.YMax)]:
            adds[key].append(box(x,y-1.55 if sg<0 else y+.17,b.ZMin-1.45,6,1.38,173-b.ZMin))
            adds[key].append(box(x,y-1.55 if sg<0 else y-1.2,b.ZMin-1.45,6,2.75,1.35))
# Open adjustable two-slot lands for four unknown samples; dimensions describe
# adjustable travel only. The sample marker is not a fuse-body envelope.
for i,n in enumerate(sorted(group('NIGHT_MTA0100335_'))):
    key='ForeBase' if i<2 else 'RearBase';x=-47 if i<2 else 115;sg=-1 if i%2==0 else 1;y=-99.9 if sg<0 else 79.9
    move(n,[],[x+8,y+4,132.2])
    bed=box(x,y,129.5,28,20,2.6)
    for xx in [x+4,x+19]:bed=bed.cut(box(xx,y+2,129.3,3.4,16,3))
    bed=bed.fuse(box(x,(-102 if sg<0 else 98.6),129.5,28,3.4,2.6))
    adds[key].append(bed)
# Join by intended print. Log any material islands; an incomplete bracket cannot be exported as one part.
for key,items in adds.items():writepart('E19_'+key,join([sh('E19_'+key)]+items))
wr('module-bearings.json',dict(rows=report,additional_poses=moves));D.recompute();D.save()
