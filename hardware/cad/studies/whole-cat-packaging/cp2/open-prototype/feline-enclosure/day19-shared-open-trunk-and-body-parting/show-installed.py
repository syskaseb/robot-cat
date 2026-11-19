from pathlib import Path
import json,math
P=Path(__file__).parent;src=(P/'body-and-channel.py').read_text();exec(src[:src.index('# Start at F')])
def rd(n):return json.loads((P/n).read_bytes())
q=rd('named-approaches.json');b=rd('battery-leads.json')
def displaytube(points,r):
 pp=[V(*a) for a in points];short=[pp[0]]
 # Combine close collinear intervals. Draw continuous solids for the selected witnesses only.
 for p in pp[1:-1]:
    if (p-short[-1]).Length>=3:short.append(p)
 short.append(pp[-1]);ss=[]
 for a,b in zip(short,short[1:]):
    v=b-a
    if v.Length>.001:ss.append(Part.makeCylinder(r,v.Length,a,v))
 return ss
for groupname,names,col in [('bus',['W002','W003'],(.22,.51,.72)),('servo',['XB12','XB13','XS13','XB22','XB23','XS23','XB32','XB33','XS33'],(.79,.49,.23)),('supply',['W078','W079','W080'],(.77,.32,.28)),('speaker',['EXT023','EXT024'],(.50,.37,.70))]:
 ss=[]
 for name in names:ss.extend(displaytube(q[name]['points'],q[name]['diameter']/2))
 add('H19_Wires_'+groupname,Part.makeCompound(ss),col,'occupied hand-lay section at named common passage, not print material')
ss=displaytube(b['input']['points'],2.4)+displaytube(b['ground']['points'],2.4)
for sign in [-1,1]:
 pts=[[a[0]+sign*1.87,a[1]-sign*1.87,a[2]] for a in b['battery_return'][0]['points']]
 ss.extend(displaytube(pts,2.4))
add('H19_Wires_battery',Part.makeCompound(ss),(.73,.36,.23),'F0 stationary input and ground; loose battery-side bight before unplugging')
for n in group('G19_Lay_','G19_Group_','H19_MainTrunk','H19_TailSideTransfer','H19_PowerBranch'):hide(n)
hide('E19_ForeBase','E19_FrontShroud','Pi_USB_DATA_Delock_mating')
D.recompute();D.save()
v=G.activeDocument().activeView();skins=['E19_ForeLid','E19_RearLid','F19_ForeCap','F19_RearCap','E19_BatteryDoor','E19_UpperYawCover','D19D_PitchBack','D19D_Face']
fields=group('H19_Wires_','F19_Field_')+['G19_PitchFan','G19_H3_mate_allowance','G19_MIC_C_PlugAllow','H19_DATA_A_Boot','G19_PiAudioBoot','XT60H_mated_with_boots','C19_FFC190','D19D_ToF']
for name,pos,interior in [('interior',(.32,-.60,1.55),True),('front',(-1,0,.06),False),('side',(0,-1,.06),False),('three-quarter',(-.62,-1,.39),False)]:
 for n in skins:D.getObject(n).ViewObject.Visibility=not interior
 for n in fields:D.getObject(n).ViewObject.Visibility=interior
 z=V(*pos);z.normalize();x=V(0,0,1).cross(z);x.normalize();v.setCameraOrientation(A.Rotation(x,z.cross(x),z,'ZXY').Q);v.fitAll();v.redraw();G.updateGui();v.saveImage(str(P/(name+'.png')),1440,960,'White')
D.recompute();D.save()
