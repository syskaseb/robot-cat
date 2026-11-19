"""Place service bays in the open box, with servo pairs and complete board connections."""
from pathlib import Path
P=Path(__file__).parent
exec((P/'core.py').read_text().split('# Each board/power cluster')[0])
# Move the fore acoustic station to the opposite side of the fore lid. Its
# whole group, bearing ears and screw datums travel together. Free up the
# central neck volume. A bottom-face cut is bounded below the lid so the panel stays continuous.
mic=obj=D.getObject('ReSpeakerLite_on_REMOVABLE_back')
mb=mic.Shape.BoundBox;lid=D.E19_ForeLid.Shape
supports=[]
for n in group('HB_MIC_'):
    if not n.endswith('headwasher'):continue
    b=sh(n).BoundBox;x=b.Center.x;y=b.Center.y;z=b.ZMax
    w=box(x-3.5,y-3.5,z-.2,11.1,7,171.48-z)
    supports.append(lid.common(w));lid=lid.cut(w)
# Rotate the complete horizontal 86x35 field to fit across the short-sided front cover length
# by using a rearward +Y face alongside the lifting cover, with full hand access when open.
delta=V(0,25,0)
for n in ['ReSpeakerLite_on_REMOVABLE_back','D19_MIC_FULL_HEIGHT_RESERVE']+group('HB_MIC_'):D.getObject(n).Placement.Base+=delta
for s in supports:s.translate(delta)
lid=join([lid]+supports)
for x in [-49,-27]:
    for y in [23,70,85]:
        lid=lid.cut(cyl(x,y,170.9,2,3))
D.E19_ForeLid.Shape=lid.removeSplitter()
# Open aft, split service window in the fixed jaw for the factory exit. Yaw
# steel and diagonal load members are lateral. The case remains removable.
# The arc turns upward before reaching either short FHAC case.
for n in ['E19_FrontShroud','E19_ForeBase']:
    o=D.getObject(n);s=o.Shape.cut(box(-119.55,-4,50.7,30.5,8.0,47.3))
    o.Shape=s.removeSplitter()
move('D19D_YawMatedPair',[],[-79,-53,110])
# Both open cable lands join the existing outer rails behind the pair. Both
# flat strap slots can be threaded from above before installing the power banks.
base=D.E19_ForeBase.Shape
for x in [-76.8,-54]:
    r=box(x,-55.6,107.2,4.8,19.6,2.8)
    r=r.fuse(box(x,-56.7,107.2,4.8,1.1,5.7)).fuse(box(x,-36,107.2,4.8,1.1,5.7))
    # support from the WAGO bank side corridor without crossing the fuse solids.
    r=r.fuse(box(x,-58.4,107.5,4.8,3,2))
    # Do not drive a pillar through the fuse below. A horizontal rail attaches
    # to the nose/side at the outboard edge, above the highest seated fuse.
    r=r.fuse(box(x,-99.2,108.52,4.8,44.5,2.0))
    # free-standing at x<-64 meets a new post at the outer frame.
    r=r.fuse(box(x,-99.6,41.1,4.8,2.8,68.5))
    base=base.fuse(r)
D.E19_ForeBase.Shape=base.removeSplitter()
# Four e-fuse samples placed only after their lids/outriggers are known. Physical
# coupon is the slotted open adjustable land replicated at the two ends.
land=box(0,0,0,28,20,2.6)
for x in [4,19]:land=land.cut(box(x,2,-.2,3.4,16,3))
# A separate off-robot coupon carries the same slot pitch. It is excluded from robot mass.
co=add('E19_MTA_sample_land',land,(.3,.49,.42),'off-robot sample coupon for four unmeasured holders, not a fifth installed MTA');co.ViewObject.Visibility=False
# E2 and axial fuse are complete assembly fields in a shared, open insulated bay.
# Mated housing allowance from the established JR/JPWM regional design, not a cuttable connector.
e=add('E19_FieldJPWM',box(35,-32,120,26,12,12),(.88,.62,.15),'JPWM 2 full mated housings, known 26x12x12 project space; both latches accessible with lid removed');e.ViewObject.Visibility=False
shelf=box(33,-34,117.4,30,16,2.6)
for x in [37,55]:shelf=shelf.cut(box(x,-32,117.1,3.2,12,3.3))
# Carry the module from above on one pair of outside webs, with open mating along X.
rear=D.E19_RearLid.Shape
for x in [33.3,59.7]:
    shelf=shelf.fuse(box(x,-34.5,117.6,2.7,2.5,54.4))
D.E19_RearLid.Shape=rear.fuse(shelf).removeSplitter()
# All moved source actors and revised bearing sections remain individually retrievable.
wr('service-bays.json',dict(moves=moves,mic_delta=list(delta),fuse_coupon='28x20 is adjustable slotted land, unknown delivered fuse profile/cover and both leads',parts={n:dict(solid_count=len(sh(n).Solids),valid=sh(n).isValid(),bounds=bounds(sh(n))) for n in ['E19_ForeBase','E19_RearLid','E19_FrontShroud','E19_ForeLid']}))
D.recompute();D.save()
