from pathlib import Path
import json,math
P=Path(__file__).parent;E=P.parent/'day19-simple-box-common-core';F=P.parent/'day19-connected-servo-usb-and-closure'
exec((E/'core.py').read_text().split('# Each board/power cluster')[0].replace('19E.FCStd','19G.FCStd'))
def wr(n,q):(P/n).write_bytes((json.dumps(q,indent=1)+'\n').encode())
def setpart(n,s):D.getObject(n).Shape=s.removeSplitter()
m=json.loads((P/'mic-port.json').read_bytes());c=V(*m['pivot_xy'],0)
# Reuse both mounting axes. The whole mic turns 180; the identical fastener sets stay in the same holes.
r=A.Rotation(V(0,0,1),180);tr=A.Placement(c-r.multVec(c),r)
for n in ['E19_ReSpeakerSource','ReSpeakerLite_on_REMOVABLE_back','D19_MIC_FULL_HEIGHT_RESERVE']:
    o=D.getObject(n);o.Placement=tr.multiply(o.Placement)
mouth=V(*m['mouth'])
add('G19_MIC_C_PlugAllow',box(mouth.x-5.2,mouth.y-19,mouth.z-3.5,10.4,19,7),(.72,.58,.35),'project allowance behind actual STEP USB1 face, full delivered USB_AUDIO connector unknown')
# Approach from a second upper stack on the official physical Pi footprint. Retain project-size plug.
o=D.getObject('INSERT_AUDIO_USB_A_FULL_MATE_FIELD')
if o:o.Placement.Base+=V(0,0,7)
# True E1 board requires a supported edge 6.59 mm below the prior receiver. The wall stays anchored to the floor.
base=sh('E19_RearBase');seat=box(143.8,35.75,106.55,52.4,2.1,44)
base=base.cut(seat)
rail=box(159.5,34.5,104.9,36.7,5.6,1.91)
for xx in [160,191]:
    rail=rail.fuse(box(xx,37.75,105.4,3.2,1.5,6.3)).fuse(box(xx,34.55,105.4,3.2,1.25,4.7))
# Backing reaches rear body wall above the switch. Laminate is captured at two edges;
# the negative-Y component face and the positive-Y solder face remain accessible before installation.
rail=rail.fuse(box(191.2,37.9,105.1,17.2,2.15,3.2)).fuse(box(193.9,37.8,106.4,2.4,2,44.4))
rail=rail.fuse(box(193.9,35.1,150.12,2.4,4.8,1.3)).fuse(box(195.45,35.2,147.5,1.1,3.7,3.3))
setpart('E19_RearBase',base.fuse(rail))
# H3 real mounted connector projects upward at the outer rear corner. Reserve insertion and a rolling exit
# under one closed local cover. The rest of the accepted roof, rear switch and tail opening stay in place.
cap=sh('F19_RearCap');hood=box(185.8,34.8,199.45,21.7,52,23).cut(box(187.2,36.2,199.2,18.9,49.2,21.8))
cap=cap.fuse(hood).cut(box(187.2,36.2,198.8,18.9,49.2,2.7));setpart('F19_RearCap',cap)
add('G19_H3_mate_allowance',box(194,71.8,188.73,6.5,10.7,8),(.82,.78,.62),'separate project exposed header plug/strain relief after mating; H3.1 D H3.3 G, V contact withdrawn')
lid=sh('E19_RearLid').cut(box(192.7,38.7,170.9,17.5,7.4,3.45))
# Hand-lay window from open split for the two separated body trunk groups.
lid=lid.cut(box(19.9,-46,170.8,14.3,10,3.6))
setpart('E19_RearLid',lid)
# Current acoustic station, not its historical bounding box. Direct perforations through both lids.
for n in ['E19_ForeLid','F19_ForeCap']:
    s=sh(n);z=170.9 if n=='E19_ForeLid' else 198.7
    for xx in [-48,-27]:
        for yy in [18,35,59,83]:
            x=2*c.x-xx;y=2*c.y-yy
            s=s.cut(cyl(x,y,z,1.8,3.4))
    if n=='E19_ForeLid':s=s.cut(box(8,-46,170.8,12.4,10,3.6))
    setpart(n,s)
# Extend the existing fixed side wall downwards. The front return is installed with the same removable shroud.
shroud=sh('E19_FrontShroud');side=box(-161.5,-113.95,82,98.8,1.65,28.6)
side=side.fuse(box(-161.6,-113.95,82,1.65,12,29)).fuse(box(-161.3,-113.75,82,98.5,7.6,1.65))
setpart('E19_FrontShroud',shroud.fuse(side))
for n in group('G19_Group_'):hide(n)
t=json.loads((P/'named-approaches.json').read_bytes());plan=json.loads((P/'whole-termination-plan.json').read_bytes())
def tube(pts,r):
    vv=[V(*a) for a in pts];ss=[]
    for a,b in zip(vv,vv[1:]):
        d=b-a
        if d.Length>.001:ss.append(Part.makeCylinder(r,d.Length,a,d))
    return ss
for k,ids,col in [('BUS',['W002','W003'],(.36,.69,.87)),('ServoPower',['XB12','XB22','XB32'],(.89,.48,.30)),('ServoGround',['XB13','XB23','XB33'],(.30,.31,.32)),('ServoPWM',['XS13','XS23','XS33'],(.90,.72,.32)),('Power',['W078','W079','W080'],(.80,.40,.40)),('Audio',['EXT023','EXT024','EXT025'],(.54,.47,.75))]:
    ss=[]
    for w in ids:
        pts=t[w]['points'];pp=pts[::3]+([pts[-1]] if (len(pts)-1)%3 else [])
        ss+=tube(pp,t[w]['diameter']/2)
    add('G19_Lay_'+k,Part.makeCompound(ss),col,'occupied physical unit profiles, not printed material')
pp=[]
for b in plan['JR']['pitch']['branches']:pp+=tube(b['points'],.9)
add('G19_PitchFan',Part.makeCompound(pp),(.83,.62,.23),'three individual 25/9/8 ends after retained JR246')
# Display 19F pitch stock prior to branching; its old terminal fan has been retired.
q=json.loads((F/'service-lay.json').read_bytes());p=next(z['points'] for z in q['pitch_transfer'] if z['yaw']==0)
D.F19_Field_JR_pitch.Shape=Part.makeCompound(tube(p[::3]+[p[-1]],1.98))
# The remote resistor belongs at the actual connector. Individual suspended ends are fit to delivered JR housing,
# before any heatshrink. Keep independent pockets for the local return and PWM ends.
for key,n,host in [('yaw','D19D_YawMatedPair','E19_ForeLid'),('tail','B19_TailMatedPair','E19_RearLid'),('pitch','BR_FLANK_HP_PAIR','E19_UpperYawCover')]:
    b=sh(n).BoundBox;x=b.XMax-9;y=b.YMax+3.3;z=b.ZMin+1.0
    rack=box(x-2.2,b.YMax+.5,z-1.5,6.4,5.4,1.5)
    rack=rack.fuse(box(x-2.2,y-1.35,z-.2,6.4,.8,1.8)).fuse(box(x-2.2,y+1.55,z-.2,6.4,.8,1.8))
    setpart(host,sh(host).fuse(rack))
    add('G19_RemoteR_'+key,cyl(x,y+.45,z+.9,.8,3.6,(1,0,0)),(.64,.54,.35),'selected 10k Vishay component body at actual local PWM/ground station; lead dressing/delivered tap remain to fit')
changed=['E19_RearBase','E19_RearLid','E19_ForeLid','E19_UpperYawCover','E19_FrontShroud','F19_ForeCap','F19_RearCap']
wr('new-members.json',{n:dict(valid=sh(n).isValid(),members=[dict(volume=s.Volume,bounds=bounds(s)) for s in sh(n).Solids]) for n in changed})
D.recompute();D.save()
v=G.activeDocument().activeView();skins=['E19_FrontShroud','E19_ForeLid','E19_RearLid','F19_ForeCap','F19_RearCap','E19_BatteryDoor','E19_UpperYawCover','D19D_PitchBack','D19D_Face']
fields=group('G19_Lay_','F19_Field_')+['G19_PitchFan','G19_H3_mate_allowance','G19_MIC_C_PlugAllow','D19D_ToF','C19_FFC190']
for name,pos,inside in [('interior',(.28,-.65,1.45),True),('side',(0,-1,.06),False),('front',(-1,0,.06),False),('three-quarter',(-.62,-1,.39),False)]:
    for n in skins:D.getObject(n).ViewObject.Visibility=not inside
    for n in fields:D.getObject(n).ViewObject.Visibility=inside
    z=V(*pos);z.normalize();x=V(0,0,1).cross(z);x.normalize();v.setCameraOrientation(A.Rotation(x,z.cross(x),z,'ZXY').Q);v.fitAll();v.redraw();G.updateGui();v.saveImage(str(P/(name+'.png')),1440,960,'White')
D.recompute();D.save()
