from pathlib import Path
P=Path(__file__).parent;E=P.parent/'day19-simple-box-common-core'
exec((E/'core.py').read_text().split('# Each board/power cluster')[0].replace('19E.FCStd','19I.FCStd'))
n='PBAY_P_AUX';b=sh(n).BoundBox;c=b.Center;r=A.Rotation(V(0,0,1),180)
o=D.getObject(n);o.Placement=A.Placement(V(-2,81,131.5)-r.multVec(c),r).multiply(o.Placement)
rack=[box(-21.92,92.26,142.7,35.5,2.61,2.57),box(-18.6,78.2,124.6,33.24,7.8,2.4)]
for x in [-15.6,9.0]:
 rack.extend([box(x,71.35,124.55,3.4,22.13,2.45),box(x,90.70,124.59,3.4,2.8,19.6)])
for x,tip in [(-18.65,-18.65),(13.16,12.4)]:
 rack.extend([box(x,78.2,125.1,1.48,7.8,11.8),box(tip,78.2,136.18,2.24,7.8,1.15)])
deck=sh('E19_ForeLid').Solids[0];rack=join(rack);out=deck
for a in rack.Solids:out=out.fuse(a,.00001)
out=out.removeSplitter();assert out.isValid() and len(out.Solids)==1
D.getObject('E19_ForeLid').Shape=out
# Only the two retired dedicated shelf rungs are removed; the original floor stays continuous.
frame=sh('H19_FrontFrame').Solids[0]
for x in [-100+30*.19,-100+30*.76]:
 frame=frame.cut(box(x-.008,-56.11,45.6,3.416,21.24,7.01),.00001)
frame=frame.removeSplitter();assert frame.isValid() and len(frame.Solids)==1;D.getObject('H19_FrontFrame').Shape=frame
wr('distribution-shelf.json',dict(bank=bounds(sh(n)),four_active={'1':'XB11','2':'XA03','3':'XB21','4':'XB31'},fifth='unoccupied',entry='-Y',paired_station='G1 on independent upper bearing; integral once in removable deck',support_overlap=deck.Volume+rack.Volume-out.Volume))
D.recompute();D.save()
