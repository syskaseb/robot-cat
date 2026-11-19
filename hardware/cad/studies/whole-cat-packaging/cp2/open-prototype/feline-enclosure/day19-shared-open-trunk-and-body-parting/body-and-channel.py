"""The front floor and fixed shroud share one anchored material body; the decks stay lift-off."""
from pathlib import Path
import json,zipfile,math
from xml.etree import ElementTree as ET
P=Path(__file__).parent;O=P.parent;F=O/'day19-connected-servo-usb-and-closure';E=O/'day19-simple-box-common-core';G0=O/'day19-real-terminations-and-assembly'
exec((E/'core.py').read_text().split('# Each board/power cluster')[0].replace('19E.FCStd','19H.FCStd'))
def original(path,n):
 with zipfile.ZipFile(path) as z:
    o=ET.fromstring(z.read('Document.xml')).find("./ObjectData/Object[@name='%s']/Properties/Property[@name='Shape']/Part"%n)
    s=Part.Shape();s.importBrepFromString(z.read(o.get('file')).decode('ascii'));return s
def upd(n,s):D.getObject(n).Shape=s.removeSplitter()
# Start at F's unextended wall. G's three added low walls contained no anchor or mechanism.
nose=original(F/'whole-cat19F.FCStd','E19_FrontShroud');floor=sh('E19_ForeBase')
assert nose.BoundBox.XMin < -166
# Rearward extension lies OUTSIDE both lift-off walls. The return at its back descends
# below their join, preserving an opaque stepped seam while leaving the lift vertical.
before=nose.Volume
nose=nose.cut(box(-64.75,-104.05,142.1,51,212,79))
# The mounting frame at positive Y remains immediately forward of the deck and load bridge.
front=join([floor,nose])
merged=add('H19_FrontFrame',front,(.24,.31,.32),'single front floor, fixed shroud and bearing load frame; four existing front anchor stacks; install gimbal from open top before cover')
hide('E19_FrontShroud','E19_ForeBase')
# Both roof decks now break at the same accessible spine. The upper caps still close it.
# The two ends of the U-shaped decks remain tied through the untouched perimeter.
cut=box(-60,-54,170.72,252,24,3.38)
for n in ['E19_ForeLid','E19_RearLid']:
 s=sh(n).cut(cut)
 if n=='E19_ForeLid':
    # Supplier USB1-adjacent population at one of the two existing screw shoulders.
    # Relieve the supplier component side without reducing the actual screw bore/land.
    s=s.cut(box(-66.55,47.75,158.65,2.85,3.7,2.45))
 upd(n,s)
# Full data plug boot is distinct from the legacy installation field at the same mouth.
add('H19_DATA_A_Boot',box(-20,-8.16,99.6,26,15,9),(.50,.42,.66),'Lanberg DATA_A project overmould 26x15x9; lower port of rear stack')
hide('H19_DATA_A_Boot')
# Occupied cross-sections allocated collectively before individual branch assignments.
def bundle(n,pts,w,h):
 ss=[]
 for a,b in zip(pts,pts[1:]):
    a,b=V(*a),V(*b);dr=b-a
    ar=box(-w/2,-h/2,0,w,h,dr.Length);ar.Placement=A.Placement(a,A.Rotation(V(0,0,1),dr));ss.append(ar)
 add(n,Part.makeCompound(ss),(.88,.56,.17),'shared occupied station region; open for lay before two caps; field only')
bundle('H19_MainTrunk',[[-49,-43,183],[10,-43,183],[48,-43,156],[156,-43,156],[186,-40,150]],12,6)
bundle('H19_TailSideTransfer',[[177,-40,151],[190,-30,153],[190,25,153],[178,27,138]],8,5)
bundle('H19_PowerBranch',[[-55,-40,101],[-24,-40,111],[49,-40,110],[91,-25,107],[112,-8,101]],7,4)
wr('new-members.json',{n:dict(valid=sh(n).isValid(),members=[dict(volume=v.Volume,bounds=bounds(v)) for v in sh(n).Solids]) for n in ['H19_FrontFrame','E19_ForeLid','E19_RearLid']})
wr('frame-parting.json',dict(shroud_source='19F before cosmetic lower extension',trimmed_aft_return_mm3=before-nose.Volume,front_floor_volume=floor.Volume,retained_shroud=nose.Volume,fused_volume=front.Volume,united_common_mm3=floor.Volume+nose.Volume-front.Volume,extent=bounds(front),stock_actors_moved=[],deck_access=[-60,-54,170.72,192,-30,174.1],known_mic_witness=[-66.03,48.21,159.09,-64.23,50.91,160.6]))
D.recompute();D.save()
v=G.activeDocument().activeView()
for n in ['E19_ForeLid','E19_RearLid','F19_ForeCap','F19_RearCap']:hide(n)
v.viewAxonometric();v.fitAll();v.redraw();G.updateGui();v.saveImage(str(P/'initial-open-trunk.png'),1440,960,'White')
for n in ['E19_ForeLid','E19_RearLid','F19_ForeCap','F19_RearCap']:D.getObject(n).ViewObject.Visibility=True
for n in group('H19_MainTrunk','H19_TailSideTransfer','H19_PowerBranch'):hide(n)
D.recompute();D.save()
