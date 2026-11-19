from pathlib import Path
P=Path(__file__).parent;O=P.parent;E=O/'day19-simple-box-common-core';H=O/'day19-shared-open-trunk-and-body-parting'
exec((E/'core.py').read_text().split('# Each board/power cluster')[0].replace('19E.FCStd','19I.FCStd'))
def read(p):return json.loads(p.read_bytes())
s=(H/'show-installed.py').read_text();exec(s[s.index('def displaytube'):s.index('for groupname')])
q=read(P/'lower-approaches.json');ss=[]
for w in ['W001','W025','W036','W060','W061']:ss+=displaytube(q[w]['points'],q[w]['diameter']/2)
add('I19_FiveGroundApproaches',Part.makeCompound(ss),(.22,.27,.33),'G1 five wire jackets at actual terminals; indicative hand lay')
ss=displaytube(read(H/'battery-leads.json')['input']['points'],2.4)
for sign in [-1,1]:
 ss+=displaytube(q['pack'+str(sign)]['points'],2.4)
 pts=[V(27,-30+sign*2.65,152),V(27,-30+sign*2.65,163)]
 for i in range(1,64):
    a=math.pi*i/63;pts.append(V(27+17*(1-math.cos(a)),-30+sign*2.65,163+17*math.sin(a)))
 pts.append(V(61,-30+sign*2.65,145));ss+=displaytube([list(p) for p in pts],2.4)
add('H19_Wires_battery',Part.makeCompound(ss),(.72,.33,.22),'two physically distinct pack jackets, forward fixed W075 and separate upper bight')
f=read(P/'shared-fuse-transfer.json');add('I19_HPInputFactory',Part.makeCompound(displaytube(f['routes'][0]['points'],2.1)),(.68,.37,.28),'one full 84.5 mm FHAC input, variable return before the prefuse extension')
skins=['E19_ForeLid','E19_RearLid','F19_ForeCap','F19_RearCap','E19_BatteryDoor','E19_UpperYawCover','D19D_PitchBack','D19D_Face']
fields=group('H19_Wires_','F19_Field_')+['G19_PitchFan','G19_H3_mate_allowance','G19_MIC_C_PlugAllow','H19_DATA_A_Boot','G19_PiAudioBoot','XT60H_mated_with_boots','C19_FFC190','D19D_ToF','I19_FiveGroundApproaches','I19_HPInputFactory']
v=G.activeDocument().activeView()
for name,pos,interior in [('interior',(.32,-.60,1.55),True),('front',(-1,0,.06),False),('opposite-side',(0,1,.08),False),('side',(0,-1,.06),False),('three-quarter',(-.62,-1,.39),False)]:
 for n in skins:D.getObject(n).ViewObject.Visibility=not interior
 for n in fields:D.getObject(n).ViewObject.Visibility=interior
 z=V(*pos);z.normalize();x=V(0,0,1).cross(z);x.normalize();v.setCameraOrientation(A.Rotation(x,z.cross(x),z,'ZXY').Q);v.fitAll();v.redraw();G.updateGui();v.saveImage(str(P/(name+'.png')),1440,960,'White')
D.recompute();D.save()
