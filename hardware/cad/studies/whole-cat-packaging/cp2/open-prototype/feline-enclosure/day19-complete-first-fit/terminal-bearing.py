from pathlib import Path
P=Path(__file__).parent;E=P.parent/'day19-simple-box-common-core'
exec((E/'core.py').read_text().split('# Each board/power cluster')[0].replace('19E.FCStd','19I.FCStd'))
updates={};result={}
n='H19_FrontFrame';s=sh(n).Solids[0]
# One side-open access across the three connected 221-615 mouths; under the two other intact inline seats.
tool=box(-53,-55.5,54.45,37.1,18.7,5.43)
# The interrupted 110.88 mm3 belongs to F_PWM. Keep its original top, both
# strap slots and complete actor. Carry the unloaded edge of the bed down to
# the original foot before opening the shared approach below its underside.
bridge=join([box(-40.7,-47.6,42.1,2.8,13.3,2.8),box(-40.7,-36.75,42.1,2.8,2.45,17.3),box(-41,-36.75,57.9,17,1.75,2.3)])
t=s.fuse(bridge,.00001).cut(tool,.00001).removeSplitter()
result[n]=dict(before=s.Volume,after=t.Volume,solids=[x.Volume for x in t.Solids],access=bounds(tool),valid=t.isValid())
wr('terminal-bearing.json',result)
assert t.isValid() and len(t.Solids)==1 and t.Volume>.995*s.Volume
updates[n]=t
for role,n in [('pitch','E19_UpperYawCover'),('yaw','E19_ForeLid'),('tail','E19_RearLid')]:
 rod=sh('G19_RemoteR_'+role);s=sh(n).Solids[0];t=s.cut(rod,.000001).removeSplitter()
 assert len(t.Solids)==1 and t.isValid()
 result[n]=dict(bearing_seat_mm3=s.Volume-t.Volume,solids=1,valid=True);updates[n]=t
for n,s in updates.items():D.getObject(n).Shape=s
wr('terminal-bearing.json',result);D.recompute();D.save()
