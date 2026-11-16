import FreeCAD as A,FreeCADGui as G,Part,json,time
from pathlib import Path
D=A.ActiveDocument;P=Path(__file__).parent;V=A.Vector;t=time.perf_counter()
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
base=D.getObject('OLA_REAL_FRONT_MASK').Shape.copy();members=[];s=base
fovs=[D.getObject(n).Shape for n in ['CAM102x67_CONTINUOUS_FOV_NOT_MATERIAL','TOF_BOTH_TX_RX_FULLBOARD45_CONTINUOUS_FOV_NOT_MATERIAL']]
for y in [-31,31]:
 # Real recess orbitalwalls around unchanged fullgoldrim; no opaqueplug in opticalwindows.
 collar=Part.makeCylinder(21,13,V(-251,y,131),V(1,0,0)).cut(Part.makeCylinder(15.5,13.2,V(-251.1,y,131),V(1,0,0)))
 cheek=Part.makeSphere(24,V(-239,y*.84,111)).cut(Part.makeSphere(21.5,V(-239,y*.84,111))).common(box(-266,y-28,80,29,56,65))
 for q in fovs:collar=collar.cut(q);cheek=cheek.cut(q)
 s=s.fuse(collar).fuse(cheek);members.append({'role':'orbitalrecess+convexcheek','y':y,'collar_volume':collar.Volume,'cheek_volume':cheek.Volume})
# Actualskin functions have priority. If disconnected retain scopedproposal ratherthan fakeoneprint.
o=D.getObject('LC_ORBIT_CHEEK_FRONT_MASK') or D.addObject('PartDesign::Feature','LC_ORBIT_CHEEK_FRONT_MASK');o.Shape=s;o.ViewObject.ShapeColor=(.12,.14,.16)
D.getObject('OLA_REAL_FRONT_MASK').ViewObject.Visibility=False
r={'base':'OLA_REAL_FRONT_MASK unchanged pose','new':'LC_ORBIT_CHEEK_FRONT_MASK','valid':s.isValid(),'solids':len(s.Solids),'volume_mm3':s.Volume,'new_member_volumes':members,'camera_ToF_whole_primaryFOV_preserved':True,'goldrims_boughtposes_unchanged':True,'manufacturing_release':False,'physical_fit':None,'scoped_remaining':['positivejoin/retainer ifanydetachedfacefeature','ear/backcover root and actualmovingneckclosure','actualglyph/paint blackeyes no extraLED'],'seconds':time.perf_counter()-t}
(P/'physical-orbit-cheek-mask.json').write_bytes((json.dumps(r,indent=2)+'\n').encode());D.recompute();D.save();print(json.dumps(r))
