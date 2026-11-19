"""Reassign negative shoulder to fixed outboard wall, yaw storage and open lid-side transfer."""
from pathlib import Path
P=Path(__file__).parent;E=P.parent/'day19-simple-box-common-core'
base=(P/'gallery.py').read_text();exec(base[:base.index('bp=transform')])
old=lay;lay=json.loads((P/'service-lay.json').read_bytes())
exec(base[base.index('pairnames='):base.index('for k,old')])
exec(base[base.index('def tube('):base.index("fore=sh('E19_ForeLid')")])
exec(base[base.index('def saddle('):base.index("fore=fore.multiFuse")])
def replace(n,v):D.getObject(n).Shape=v.removeSplitter()
p0=old['pairs']['yaw']['inlet'];p1=lay['pairs']['yaw']['inlet']
transform(['D19D_YawMatedPair'],p0,p1,0)
fore=sh('E19_ForeLid')
# Entire moving entrance is a side-loaded open bay. The microphone and touch are on its other side.
fore=fore.cut(box(-90,-100,170.5,71,49,3.25))
fore=fore.cut(box(-38,-69.2,172.99,31,18,13))
fore=fore.multiFuse(saddle('yaw'))
# A continuous gap around the full duplex USB project boot allows insertion from above.
rear=sh('E19_RearLid').cut(box(139.5,54,169,27.7,27,4.5))
# Local latch pocket follows the complete interlock. A small residual at the vent edge was real.
cap=sh('F19_RearCap')
for x in [28.15,195]:
    for y in [-100.8,98.75]:rear=rear.cut(box(x-.38,y-.83,169,6.76,3.24,4.04))
replace('E19_RearLid',rear)
replace('E19_ForeLid',fore)
# Remove the former fixed high cable wall. The low protected jaw below the gimbal and
# its entire positive-side attachment remain. A continuous external cheek replaces the removed wall.
n='E19_FrontShroud';orig=sh(n);body=orig.cut(box(-169,-120,118,114,131,107))
side=box(-154,-114,109,91.6,1.55,91.8)
low=box(-153,-113.8,109,90.3,17,1.65)
# Join the new cheek to the original fixed shroud wherever its lower rim actually crosses the bearing flange.
side=side.fuse(low).fuse(box(-154,-113.6,199.2,91.6,29,1.6)).fuse(box(-64.3,-113.7,109,1.65,12.1,91))
joined=body.fuse(side)
if len(joined.Solids)>1:
    # Anchor bridges at two separated stations on the original lower shell.
    for xx in [-137,-83]:
        region=body.common(box(xx,-106,88,6,86,29.7))
        if region.isNull() or not region.Solids:continue
        dist,ps,_=region.distToShape(low)
        a,b=ps[0];v=b-a
        if v.Length>.05:
            v.normalize();length=(a-b).Length
            bridge=Part.makeCylinder(2.9,length+3.4,a-1.7*v,v)
            joined=joined.fuse(bridge)
replace(n,joined)
# Aperture in the pitch-only skirt around the separately co-yawing factory exit, kept open to lay the lead.
n='D19D_PitchBack';s=sh(n).cut(box(-178,-96,109,43,43,48));replace(n,s)
# Co-yaw shelf supports the actual mate underneath. Its two lateral ribs stop below the housing.
n='E19_UpperYawCover';s=sh(n).cut(box(-113,-91,126.49,30.2,14.2,2.1))
sol=sorted(s.Solids,key=lambda a:-a.Volume)
detail=[dict(volume=v.Volume,bounds=bounds(v)) for v in sol[1:]]
# Small remnant of the previous negative-side lap ends below the new chamber; replaced by continuous outer side.
replace(n,sol[0])
# Open fore-cap front on negative side including extreme dynamic entry. Side closure goes on the stationary shroud.
n='F19_ForeCap';s=sh(n).cut(box(-65,-106,172.88,4,117,26.62))
s=s.cut(box(-65,-104,172.9,20,4.1,16.8));replace(n,s)
changed=['E19_UpperYawCover','D19D_PitchBack','E19_FrontShroud','E19_ForeLid','E19_RearLid','F19_ForeCap','F19_RearCap']
wr('retired-lower-hood-lap.json',dict(retired=detail,substitute='new full-height co-yaw plate and fixed outboard cheek; prior lower remnant contains no board / steel fastening or servo seat'))
wr('new-members.json',{n:dict(valid=sh(n).isValid(),members=[dict(mm3=v.Volume,bounds=bounds(v)) for v in sh(n).Solids]) for n in changed})
D.recompute();D.save()
exec(base[base.index('view=(E/'):])
