from pathlib import Path
import zipfile
from xml.etree import ElementTree as ET
P=Path(__file__).parent;E=P.parent/'day19-simple-box-common-core';H=P.parent/'day19-shared-open-trunk-and-body-parting'
exec((E/'core.py').read_text().split('# Each board/power cluster')[0].replace('19E.FCStd','19I.FCStd'))
def frozen(name):
 with zipfile.ZipFile(H/'whole-cat19H.FCStd') as z:
    prop=ET.fromstring(z.read('Document.xml')).find("./ObjectData/Object[@name='%s']/Properties/Property[@name='Shape']/Part"%name);s=Part.Shape();s.importBrepFromString(z.read(prop.get('file')).decode());return s
# Restore the former negative-wall G1 installation area to its received frame.
# All other changes (diagonal, HY cradle, Pi return, fixed jaw guard) are outside this region.
vol=box(-40.5,-102.4,40.98,40.9,44.35,35.3);frame=sh('H19_FrontFrame').Solids[0];orig=frozen('H19_FrontFrame');rest=orig.common(box(-40.64,-102.55,40.85,41.2,44.65,35.57))
# The former G1's four source feet originally protruded past its back. Those
# obsolete feet belong to neither the restored side wall nor the new upper bank.
for xx in [-40+22*.19,-40+22*.76]:
 rest=rest.cut(box(xx-.02,-59.12,45.5,3.44,2.25,9.1))
frame=frame.cut(vol,.00001).fuse(rest,.00001).removeSplitter()
wr('wall-restore.json',dict(solids=[dict(volume=v.Volume,box=bounds(v)) for v in frame.Solids],valid=frame.isValid()))
assert len(frame.Solids)==1 and frame.isValid()
D.getObject('H19_FrontFrame').Shape=frame
# The entire terminal station hangs under the removable foredeck, above leg and fuse heights.
n='WAGO615_power_0_0';o=D.getObject(n);rot=A.Rotation(V(1,0,0),90);centre=V(-7,81,151)
o.Placement=A.Placement(centre-rot.multVec(sh(n).BoundBox.Center),rot).multiply(o.Placement)
deck=sh('E19_ForeLid').Solids[0];arms=[]
for x in [-22.1,3.8]:
 arms.extend([box(x,69.85,142.6,3.5,25.2,2.9),box(x,92.25,143.35,3.5,2.7,29.8),box(x,92.15,170.4,3.5,6.1,2.7)])
# Common transverse rung and two elastic end fingers capture the complete field.
arms.append(box(-27.15,78.1,143.2,40.3,7.6,2.3))
for x,tip in [(-27.15,-27.15),(11.66,10.88)]:
 arms.extend([box(x,78.1,144.3,1.47,7.6,13.15),box(tip,78.1,156.7,2.26,7.6,1.19)])
for x in [-22.1,3.8]:arms.append(box(x,92.14,143.5,3.5,1.25,5.15))
rack=join(arms);s=deck.fuse(rack,.00001).removeSplitter()
assert len(s.Solids)==1 and s.isValid(),[(v.Volume,bounds(v)) for v in s.Solids]
D.getObject('E19_ForeLid').Shape=s
# XPWM shelf's outboard drop and service loop were competing for one column.
# Keep both original shelf slots. Move the entire aft suspension web to its opposite edge.
n='E19_RearLid';s=sh(n).Solids[0];pre=s.Volume
newweb=box(59.7,-20.9,117.63,2.7,2.55,55.35);s=s.fuse(newweb,.00001).cut(box(59.64,-34.57,120.01,2.82,2.64,52.0),.00001).removeSplitter()
assert len(s.Solids)==1 and s.isValid();D.getObject(n).Shape=s
wr('gallery-installation.json',dict(source='19E service-bays.py paired XPWM shelf hangers, both slot spans retained',revised_hanger=bounds(newweb),deck_seated_G1=bounds(sh('WAGO615_power_0_0')),G1_rack=bounds(rack),deck_rack_overlap=rack.Volume+deck.Volume-D.getObject('E19_ForeLid').Shape.Volume,negative_wall_restored_H=bounds(vol),new_steel=0,physical_sample=None))
D.recompute();D.save()
