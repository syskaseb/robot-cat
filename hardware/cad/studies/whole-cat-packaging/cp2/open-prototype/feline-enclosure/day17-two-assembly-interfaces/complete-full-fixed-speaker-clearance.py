import FreeCAD as A,Part,json,math,time
from pathlib import Path
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent
def put(n,x):(P/n).write_bytes((json.dumps(x,indent=2,ensure_ascii=False)+'\n').encode())
def box(x,y,z,a,b,c):return Part.makeBox(a,b,c,V(x,y,z))
def rr(x1,x2,z1,z2,r,y):
 def v(x,z):return V(x,y,z)
 rt=math.sqrt(.5);e=[]
 a=v(x1+r,z1);b=v(x2-r,z1);e.append(Part.makeLine(a,b));c=v(x2,z1+r);e.append(Part.Arc(b,v(x2-r+r*rt,z1+r-r*rt),c).toShape())
 a=c;b=v(x2,z2-r);e.append(Part.makeLine(a,b));c=v(x2-r,z2);e.append(Part.Arc(b,v(x2-r+r*rt,z2-r+r*rt),c).toShape())
 a=c;b=v(x1+r,z2);e.append(Part.makeLine(a,b));c=v(x1,z2-r);e.append(Part.Arc(b,v(x1+r-r*rt,z2-r+r*rt),c).toShape())
 a=c;b=v(x1,z1+r);e.append(Part.makeLine(a,b));c=v(x1+r,z1);e.append(Part.Arc(b,v(x1+r-r*rt,z1+r-r*rt),c).toShape())
 return Part.Face(Part.Wire(e))
def run():
 t=time.perf_counter();D.save();o=D.getObject('FC_F_POS');old=Part.Shape();old.read(str(P/'source-FC_F_POS.brep'));inner=rr(-108,10,96,153,8,95.5);outer=rr(-109.6,11.6,94.4,154.6,9.6,95.5);port=inner.extrude(V(0,45,0));ring=outer.cut(inner).extrude(V(0,25.5,0))
 source=P.parent/'day17-night-whole-floor-cowl-head-tail/build-floor-based-cowl.py';ns={'__file__':str(source)};exec(source.read_text(encoding='utf-8').split('def run():')[0],ns)
 bodyouter=Part.makeLoft([ns['profile'](s,1,True) for s in ns['stations'] if s[0]<=80],True,True)
 limit=bodyouter.fuse(box(-110,95.5,94,123,15.6,61));ring=ring.common(limit)
 plate=outer.copy();plate.translate(V(0,14,0));plate=plate.extrude(V(0,1.6,0))
 protected=old.cut(port);q=protected.fuse(ring).fuse(plate)
 for x in [-76,-24]:q=q.cut(Part.makeCylinder(20,45,V(x,90,122.5),V(0,1,0)))
 q=q.removeSplitter();o.Shape=q;o.Label='CURRENT integral rounded acoustic grille / fullspeaker+keeper retained';D.recompute();D.save();q.exportBrep(str(P/'FC_F_POS_acoustic_world.brep'))
 out={'sourceold_volume':old.Volume,'new_volume':q.Volume,'PETG_delta_g':(q.Volume-old.Volume)*.00127,'valid':q.isValid(),'solids':len(q.Solids),'actual_planned_port_bounds_XZ':[-108,10,96,153],'inner_cornerR':8,'front_innerY':109.5,'front_outerY':111.1,'returnbackY':95.5,'declared_reasons':'Keeperfullfront107.75 ->1.75frontgap; lowerfixedpostY94 ->1.5backgap; ringroundedXZ protectswholeSpeaker100x45+fullkeeper, no shrink/move. ForebodymaxY117notincreased.','source_same_ruled_bodyouter_used_only_to_limit_returnrim':str(source),'acoustic_openings':'2realR20holes centredX-76/-24 Z122.5, existinglocations retained, no giantrectangularwindow','ring_old_positive_overlap':ring.common(protected).Volume,'plate_ring_positive_overlap':plate.common(ring).Volume,'outside_planned_port_source_missing':protected.cut(q).Volume,'planned_old_material_removed':old.common(port).Volume,'no_new_hardware':True,'retained_source_bodykeys_and_M2laps':'OutsidepatchX-109.6..9.6/Y>=95.5/Z94.4..154.6; unchanged sourcepositions/parting','local_assembly':'Offerforepositivecowl from+Y afterwholeSpeakerandkeeper fixed; sourcepartprojection+frontplane clearance allowslocalmonotoneclosure. Wholeexistinghead/othercowlsequence notpromoted.','wholekit':False,'physicalPASS':False,'seconds':time.perf_counter()-t}
 out['actual_fixed_corner_binding']={'witness':[7.75,95,147.25],'required_right_inner_bound':7.75+8-math.sqrt((8-1.25)**2-(147.25-145)**2),'chosen_right_inner':10,'basis':'FULLactualfixednutreceiver, notonlyremovablekeeper. Onealgebraicroundedcornerbound; no offsetgrid or smallerprofile.'};put('acoustic-interface-final.json',out);D.save();print(json.dumps(out))
run()
