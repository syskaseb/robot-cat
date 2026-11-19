from pathlib import Path
import json,math
P=Path(__file__).parent;E=P.parent/'day19-simple-box-common-core';F=P.parent/'day19-connected-servo-usb-and-closure'
exec((E/'core.py').read_text().split('# Each board/power cluster')[0].replace('19E.FCStd','19G.FCStd'))
def wr(n,q):(P/n).write_bytes((json.dumps(q,indent=1)+'\n').encode())
H=next(p for p in P.parents if (p/'electronics').is_dir());AUX=H/'electronics/full-cat'
q=json.loads((P/'connected-map.json').read_bytes());pop=json.loads((AUX/'pwm-carrier-r3/population.json').read_bytes())
origin=V(170,36,128.4);rot=A.Rotation(V(0,0,-1),V(1,0,0),V(0,-1,0),'ZXY');frame=A.Placement(origin,rot)
def mounted(s):s.Placement=frame.multiply(s.Placement);return s
pcb=box(-21.59,-25.4,-1.6002,43.18,50.8,1.6002)
pcb=pcb.makeFillet(2.54,[e for e in pcb.Edges if abs(e.Length-1.6002)<.0001])
tools=[cyl(r['x'],r['y'],-1.7,r['drill']/2,1.9) for r in pop['board']['holes']]
for row in pop['board']['groups']:
    for r in row['pads']:tools.append(cyl(r['x'],r['y'],-1.7,r['drill']/2,2))
pcb=pcb.cut(Part.makeCompound(tools))
add('G19_PermaProto1608',mounted(pcb),(.14,.45,.32),'43.18 x 50.8 supplier Eagle outline, copper pad drills and mounting holes; component face y36')
cc=[]
for c in pop['components']:
    xy=c.get('center');wh=c.get('xy_max');z=c.get('z_min',0);top=c.get('z_max')
    if xy and wh and top:cc.append(box(xy[0]-wh[0]/2,xy[1]-wh[1]/2,z,wh[0],wh[1],max(.25,top-z)))
add('G19_E1_population_limits',mounted(Part.makeCompound(cc)),(.41,.46,.48),'source maximum component profiles, distinct from actual PCB')
u=pop['u1_integration'];cx,cy=u['reserved_center'];w,h=u['reserved_xy']
add('G19_U1_adapter_region',mounted(box(cx-w/2,cy-h/2,3.5,w,h,6)),(.46,.40,.49),'Kamami575070 designated adapter area. Height and delivered pads need fit')
hide('E1_populated_prototype_board')
def pathfield(pts,r):
    ss=[]
    for a,b in zip(pts,pts[1:]):
        a,b=V(*a),V(*b);d=b-a
        if d.Length>.001:ss.append(Part.makeCylinder(r,d.Length,a,d))
    return ss
rows={r['wire']:r for r in q['wires']}
for name,ids,col in [('BUS',['W002','W003'],(.38,.72,.93)),('JRY',['XB12','XB13','XS13'],(.90,.49,.24)),('JRP',['XB22','XB23','XS23'],(.90,.64,.31)),('JRT',['XB32','XB33','XS33'],(.81,.43,.30)),('POWER',['W078','W079','W080'],(.70,.27,.28)),('I2S',['EXT020','EXT021','EXT022','EXT023','EXT024'],(.72,.44,.72))]:
    ss=[]
    for i in ids:ss+=pathfield(rows[i]['shared_approach'],1.05)
    add('G19_Group_'+name,Part.makeCompound(ss),col,'initial shared transport allocation, endpoints bound separately; overlapping illustrative spines are not independent wire solids')
# Source H3 plug orientation from original installed CAD placement, keep all supplier members.
cat=AUX/'pi-bus-primary-r1';hr=Part.Shape();hr.read(str(cat/'H3.brep'))
t0=A.Placement(V(66,46,132.6),A.Rotation(V(0,0,1),90));r=A.Rotation(V(0,0,1),180)
t=A.Placement(V(140,67.5,184)-r.multVec(V(92.804,78.11,133.77)),r).multiply(t0)
hr.Placement=t.multiply(hr.Placement)
wr('source-port-and-board.json',dict(H3=[dict(box=bounds(s),volume=s.Volume) for s in hr.Solids],H3_bounds=bounds(hr),PCB=bounds(sh('G19_PermaProto1608')),E1_old_field=bounds(sh('E1_populated_prototype_board')),register=dict(origin=list(origin),x=[0,0,-1],y=[1,0,0],z=[0,-1,0]),source_board_count=len(pop['board']['groups']),old_placeholder_removed_from_effectivity=True))
skins=['E19_FrontShroud','E19_ForeLid','E19_RearLid','F19_ForeCap','F19_RearCap','E19_BatteryDoor','E19_UpperYawCover','D19D_PitchBack']
view=G.activeDocument().activeView()
def camera(pos):
    z=V(*pos);z.normalize();x=V(0,0,1).cross(z);x.normalize();view.setCameraOrientation(A.Rotation(x,z.cross(x),z,'ZXY').Q);view.fitAll();view.redraw();G.updateGui()
for n in skins:hide(n)
for n in group('F19_Field_'):D.getObject(n).ViewObject.Visibility=True
camera((.27,-.57,1.35));view.saveImage(str(P/'initial-lay.png'),1440,960,'White')
for n in skins:D.getObject(n).ViewObject.Visibility=True
for n in group('G19_Group_','F19_Field_'):hide(n)
camera((-.62,-1,.39));view.saveImage(str(P/'three-quarter.png'),1440,960,'White');D.recompute();D.save()
