from pathlib import Path
P=Path(__file__).parent;E=P.parent/'day19-simple-box-common-core'
exec((E/'core.py').read_text().split('# Each board/power cluster')[0].replace('19E.FCStd','19I.FCStd'))
# One removable transverse spring band, installed over either of the case's two physical rungs.
# The hooks catch the outboard undersides of the rung; terminal exits stay open.
def band():
 def block(x,y,z,dx,dy,dz):return box(x,y,z,dx,dy,dz)
 a=box(0,-2.55,20.47,3.4,27.1,1.22)
 for y in [-2.55,23.25]:a=a.fuse(box(0,y,-3.85,3.4,1.3,25.3))
 a=a.fuse(box(0,-2.55,-3.85,3.4,2.95,1.15)).fuse(box(0,21.60,-3.85,3.4,2.95,1.15))
 return a.removeSplitter()
proto=band();assert len(proto.Solids)==1 and proto.isValid()
frame=sh('H19_FrontFrame')
# At the upper crossed case the short-axis rung bridges both central bearers,
# leaving the lower fuse and all of its factory ends accessible.
cross=box(-74.6,19.76,73.4,24.2,3.4,2.6);a=frame.Solids[0].fuse(cross,.00001).removeSplitter()
assert a.isValid() and len(a.Solids)==1
D.getObject('H19_FrontFrame').Shape=a
r={};racks=['H19_FrontFrame','E19_RearBase','Pi4B_actual_PCB','AUX_Pololu4092','MAIN_Pololu4853','F0_FHAC0002_30A','E19_ForeLid','E19_RearLid']+group('PBAY_','WAGO615_','CB_AUX_','CB_MAIN_','NIGHT_INLINE_')
for code in ['AUX','TY','PI','HY','HP']:
 n='PBAY_F_'+code;b=sh(n).BoundBox;opts=[]
 for frac in ([.76] if code=='HY' else [.19,.76]):
    q=proto.copy()
    if code=='HY':q.Placement=A.Placement(V(b.XMax,b.YMin+51*frac,b.ZMin),A.Rotation(V(0,0,1),90))
    else:q.Placement=A.Placement(V(b.XMin+51*frac,b.YMin,b.ZMin),A.Rotation())
    hits={}
    for m in racks:
        s=sh(m)
        if not q.BoundBox.intersect(s.BoundBox):continue
        val=q.common(s).Volume
        if val>.001:hits[m]=val
    opts.append(dict(rung=frac,hits=hits,xyz=bounds(q)))
    if not hits:
        add('I19_FuseBand_'+code,q,(.32,.45,.52),'removable spring keeper on transverse rung, releases from both outer hooks before withdrawing isolated holder')
        break
 r[code]=opts
wr('band-seat.json',r);D.recompute();D.save()
