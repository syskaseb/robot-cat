from pathlib import Path
import json
P=Path(__file__).parent
s=(P/'show-installed.py').read_text();exec(s[:s.index('for groupname')]);exec(s[s.index("ss=displaytube(b['input']"):s.index("for n in group('G19_Lay_")]);D.recompute()
# Keep the final camera and actual physical visibility in the saved file; the interior uses the same updated runs.
v=G.activeDocument().activeView();rot=v.getCameraOrientation();skins=['E19_ForeLid','E19_RearLid','F19_ForeCap','F19_RearCap','E19_BatteryDoor','E19_UpperYawCover','D19D_PitchBack','D19D_Face'];fields=group('H19_Wires_','F19_Field_')+['G19_PitchFan','G19_MIC_C_PlugAllow','H19_DATA_A_Boot','G19_PiAudioBoot','XT60H_mated_with_boots','C19_FFC190','D19D_ToF']
for k in skins:hide(k)
for k in fields:D.getObject(k).ViewObject.Visibility=True
z=V(.32,-.60,1.55);z.normalize();x=V(0,0,1).cross(z);x.normalize();v.setCameraOrientation(A.Rotation(x,z.cross(x),z,'ZXY').Q);v.fitAll();v.redraw();G.updateGui();v.saveImage(str(P/'interior.png'),1440,960,'White')
for k in fields:hide(k)
for k in skins:D.getObject(k).ViewObject.Visibility=True
v.setCameraOrientation(rot);v.fitAll();D.recompute();D.save()
