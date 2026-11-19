from pathlib import Path
import json,math
P=Path(__file__).parent;s=(P/'body-and-channel.py').read_text();exec(s[:s.index('# Start at F')])
# Rotate all five mouths together. The transverse tail-bearing saddle remains intact.
n='WAGO415_data__1_0';b=sh(n).BoundBox;c=b.Center;rot=A.Rotation(V(0,0,1),180);D.getObject(n).Placement=A.Placement(c-rot.multVec(c),rot).multiply(D.getObject(n).Placement)
# Lateral withdrawal at the battery door was rejected by the full motor-fuse bank.
# Bring the detachable pair to the open split; separate upward BEFORE moving the cell.
n='XT60H_mated_with_boots';o=D.getObject(n);r=None
# Original full allowance 50 X, 24 Y, 18 Z. Target 24 X,18 Y,50 Z.
r=A.Rotation(V(0,0,1),V(1,0,0),V(0,1,0),'ZXY')
tr=A.Placement(V(20,-30,127)-r.multVec(sh(n).BoundBox.Center),r);o.Placement=tr.multiply(o.Placement)
assert max(abs(a-b) for a,b in zip(bounds(sh(n)),[8,-39,102,32,-21,152]))<.002,bounds(sh(n))
for n in ['E19_ForeLid','E19_RearLid']:
 s0=sh(n).cut(box(4.6,-40,170.72,30.4,21.8,3.4));upd(n,s0)
# An open U cup supports the harness half; only the boot's two outside edges bear on
# the bottom lips. Both solder cups, wires and covers stay free through the centre.
s0=sh('E19_RearLid');pieces=[s0]
for y in [-38.6,-23.9]:
 pieces.extend([box(32.5,y,101.3,2.7,3.1,71),box(32.5,y,170.7,8.1,3.1,2.2),box(7.3,y,100.4,27.7,3.1,1.6),box(6.7,y,101,1,3.1,9)])
pieces.extend([box(32.6,-41,101.3,2.6,23.6,2.8),box(30.4,-40.45,101.5,3.8,1.12,12),box(30.4,-20.7,101.5,3.8,1.12,12)])
upd('E19_RearLid',join(pieces))
# Boot approaches occupy the open centre between these ledges, offset from both side rails.
wr('accessible-stations.json',dict(D_FL_rotated_at=list(c),source_case='WAGO415_data__1_0',XT60_project_bounds=bounds(sh('XT60H_mated_with_boots')),pull_Z=14,negative_bank_mouth_Y=-79,complete_source_tail_saddle=True,station_access='remove upper caps, hold lower boot at common window, lift battery half, then open RR door and extract isolated cell',physical_plug_profile=None))
changed=['H19_FrontFrame','E19_ForeLid','E19_RearLid'];wr('new-members.json',{n:dict(valid=sh(n).isValid(),members=[dict(volume=v.Volume,bounds=bounds(v)) for v in sh(n).Solids]) for n in changed})
D.recompute();D.save()
