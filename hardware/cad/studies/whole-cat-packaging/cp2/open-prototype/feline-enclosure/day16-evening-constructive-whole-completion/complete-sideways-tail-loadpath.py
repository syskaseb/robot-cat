import FreeCAD as A,FreeCADGui as G,Part,json
from pathlib import Path
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent
D.saveAs(str(P/'constructive-whole-completion.FCStd'))
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def shape(n):return D.getObject(n).Shape.copy()
def cyl(x,y,z,r,l,axis=V(0,0,1)):return Part.makeCylinder(r,l,V(x,y,z),axis)
def bb(s):
 b=s.BoundBox;return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def vol(s):return s.Volume if not s.isNull() else 0.0
# Derive from actual two source solids: retain original foundation seated base; replace only unfinished own support.
old=shape('P07_open_tail_root_U');base=[s for s in old.Solids if s.BoundBox.ZMax<100][0]
cartridge=shape('TAIL_FIXED_BEARING_CARTRIDGE')
members=[('retained_actual_base',base),('lower_common_beam',box(167,-50.6,85,46,42.6,6)),('bearing_spine',box(171,-16,85,27,8,49)),('MG_left_rear_web',box(167,-50.6,85,6,3.1,85)),('MG_right_rear_web',box(207,-50.6,85,6,3.1,85)),('MG_lower_saddle_seat',box(172,-50.6,138,36,3.1,8.75)),('MG_upper_saddle_seat',box(172,-50.6,161.25,36,3.1,8.75)),('integral_outer_race_cartridge',cartridge)]
frame=members[0][1]
for n,m in members[1:]:frame=frame.fuse(m)
# Same complete two M2 saddle sets; receiver is 3.1mm thick at their real axes, no shortening.
cutters=[cyl(185,-53,z,1.1,10,V(0,1,0)) for z in [144,164]]
for c in cutters:frame=frame.cut(c)
D.getObject('P07_open_tail_root_U').Shape=frame
D.getObject('TAIL_FIXED_BEARING_CARTRIDGE').ViewObject.Visibility=False
D.getObject('TAIL_FIXED_BEARING_CARTRIDGE').Label='RETIRED SEPARATE PRINT - exact cartridge integrated in P07 / cap stays separate'
for n in ['YTAIL_FIXED_RECEIVER_LINK_0','YTAIL_FIXED_RECEIVER_LINK_1']:
 D.getObject(n).ViewObject.Visibility=False;D.getObject(n).Label='RETIRED unfinished construction link; integrated P07 receiver replaces function'
# Actual cap plane maxY=-2, retained tube halfwidth7.133; derive useful side plane once, no pose grid.
oldrot=shape('TAIL_ROTATING_HOLLOW_REAL_ROOT');upper=max(oldrot.Solids,key=lambda s:s.BoundBox.ZMax).copy();upper.translate(V(0,10,0))
hub=cyl(185,0,154,7,6,V(0,1,0)).cut(cyl(185,0,154,4.05,6,V(0,1,0)))
poly=[V(x,0,z) for x,z in [(190,150),(197,152),(211,160),(214,168),(201,175),(190,160),(190,150)]]
neck=Part.Face(Part.makePolygon(poly)).extrude(V(0,16,0))
root=upper.fuse(neck).fuse(hub).cut(cyl(185,3,140,1.1,35))
o=D.getObject('TAIL_ROTATING_HOLLOW_REAL_ROOT');o.Shape=root;o.Label='Y TAIL integral hub+torque neck+retained curved tube / tube side plane Y10'
# Preserve true removable cap and existing 608, journal, all factory/source hardware poses.
planned=[]
for n,m in members:
 intended=m
 for c in cutters:intended=intended.cut(c)
 planned.append(dict(member=n,intended_mm3=vol(intended),missing_mm3=vol(intended.cut(frame)),bounds=bb(intended)))
joins=[]
for i,(n,a) in enumerate(members):
 for m,b in members[i+1:]:
  if a.BoundBox.intersect(b.BoundBox):
   q=vol(a.common(b))
   if q>1e-7:joins.append(dict(a=n,b=m,positive_join_mm3=q))
r={'fixed_frame':{'valid':frame.isValid(),'solids':len(frame.Solids),'bounds':bb(frame),'members':planned,'positive_connections':joins,'base_missing_mm3':vol(base.cut(frame))},'moving_root':{'valid':root.isValid(),'solids':len(root.Solids),'bounds':bb(root),'retained_curved_tube_transform':[0,10,0],'retained_tube_missing_mm3':vol(upper.cut(root)),'hub_neck_join_mm3':vol(hub.common(neck)),'neck_tube_join_mm3':vol(neck.common(upper)),'full_crosspin_source_unchanged':True},'effectivity':['P07 integrates fixed cartridge as ONE intended print; no fuse bought608 or removablecap','old separate cartridge and two unfinished links retained hidden as retired reference; no double material/BOM','original foundation seated base and all4 M3 roots preserved','same complete M2 saddle/cap/pin sets retained; no new actuator or hardware purchase'],'prototype_range':'chosen after local clearance gate; not inherited ±12 requirement','physicalPASS':False}
(P/'tail-constructive-material-and-effectivity.json').write_bytes((json.dumps(r,indent=2)+'\n').encode())
D.recompute();D.save();print(json.dumps({'frame':{k:v for k,v in r['fixed_frame'].items() if k not in ['members','positive_connections']},'root':r['moving_root'],'joins':len(joins)}))
