from pathlib import Path
import json
P=Path(__file__).parent;s=(P/'body-and-channel.py').read_text();exec(s[:s.index('# Start at F')])
frame=sh('H19_FrontFrame');orig=frame.Volume
# The complete yaw servo's mounting flange crosses the thin skin inherited from the fixed chin.
# Seat both complete ears on their original printed land; keep the drive axis, fasteners and bearing bridge.
servo=sh('MG92B_Head_yaw');flange=servo.common(box(-153,-8,75.5,35,16,3))
clear=[flange]
for x in [-.25,.25]:
 for y in [-.25,.25]:
    p=flange.copy();p.translate(V(x,y,0));clear.append(p)
frame=frame.cut(join(clear))
# Actual straight driver is withdrawn upward after each anchor is seated; the load land is below this tool volume.
drivers=sh('B19_ToolEightAnchors');frame=frame.cut(drivers)
# Rear stop of the existing front transverse tab precedes the rear base. Other joint lips remain intact.
frame=frame.cut(box(19.87,96.95,47.95,2.6,2.73,31))
upd('H19_FrontFrame',frame)
wr('frame-access.json',dict(original_volume=orig,finished_volume=sh('H19_FrontFrame').Volume,flange_clearance_XY=.25,lower_face=bounds(flange),source_driver='B19_ToolEightAnchors r2.65 straight access above anchor heads',two_frame_parting_X=19.87))
wr('new-members.json',{n:dict(valid=sh(n).isValid(),members=[dict(volume=v.Volume,bounds=bounds(v)) for v in sh(n).Solids]) for n in ['H19_FrontFrame','E19_ForeLid','E19_RearLid']})
D.recompute();D.save()
