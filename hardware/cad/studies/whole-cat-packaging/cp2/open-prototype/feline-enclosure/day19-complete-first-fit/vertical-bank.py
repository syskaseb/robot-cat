from pathlib import Path
P=Path(__file__).parent;E=P.parent/'day19-simple-box-common-core'
exec((E/'core.py').read_text().split('# Each board/power cluster')[0].replace('19E.FCStd','19I.FCStd'))
n='WAGO615_power_0_0';o=D.getObject(n);c=sh(n).BoundBox.Center;rot=A.Rotation(V(1,0,0),-90)
tr=A.Placement(V(-20,-70.5,63)-rot.multVec(c),rot);o.Placement=tr.multiply(o.Placement)
frame=sh('H19_FrontFrame').Solids[0]
# Remove the two earlier shallow snap ears above the common base crossmember only.
for x in [-40.18,-2.14]:
 frame=frame.cut(box(x,-72.29,52.01,2.32,8.29,13.1),.00001)
ss=[]
# Narrow cheek arms catch only the two ends of the bank. All five vertical mouths
# and the levers remain between them. Slip off the ears manually with both lids removed.
for x,tip in [(-40.15,-40.15),(-1.34,-2.12)]:
 ss+=[box(x,-72.25,50.8,1.47,6.2,23.6),box(tip,-72.25,74.18,2.26,6.2,1.25)]
for x in [-35.4,-7.8]:
 for y in [-77.35,-64.85]:ss.append(box(x,y,50.9,3.5,1.15,5.2))
frame=frame.fuse(join(ss),.00001).removeSplitter()
assert len(frame.Solids)==1 and frame.isValid();D.getObject('H19_FrontFrame').Shape=frame
wr('vertical-bank.json',dict(terminal_bounds=bounds(sh(n)),fixture_extent=bounds(frame),five_entry_plane_z=74,route_reason='three TKD 4 mm2 fixed branches require radius 21 mm; vertical mouths accept a common overhead elbow within the negative-side bay'))
