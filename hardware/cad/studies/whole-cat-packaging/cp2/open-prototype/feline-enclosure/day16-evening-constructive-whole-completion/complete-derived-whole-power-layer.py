import FreeCAD as A,Part,json,math
from pathlib import Path
D=A.ActiveDocument;P=Path(__file__).parent;V=A.Vector
# One shared height interval from whole occupied layer, not sequential bolt/head offsets.
# Under receiver shelf: full G_TAIL top59.52 + foreign1.25 + shelf2 + halfcase5.5 => H>=68.27.
# Above receiver+open lever: AUX underside117.2 -foreign1.25 -halfcase5.5 -lever20 => H<=90.45.
H=70.52;oldH=65.125;dh=H-oldH
for n,dz in [('PBAY_F_PI',dh),('PBAY_P_SYS',dh),('PBAY_F_AUX',6.02),('W043_FULL_UNCUT_ADAPTIVE_HANDLAY_COVER',dh),('W043_MIN84p5_NOMINAL_OCCUPIED_PROFILE',dh)]:
 D.getObject(n).Placement.Base+=V(0,0,dz)
# All bodies unchanged; only joint functional layer planned. No support print is released yet.
meta=json.loads((P/'power-face-full-uncut-stock-plan.json').read_text());meta['whole_shared_height_decision']={'allowed_center_H_mm':[68.27,90.45],'chosen_H_mm':H,'lower_constraint':'full G_TAIL body +1.25 foreign+shelf2+halfcase5.5','upper_constraint':'AUX full underside117.2 minus1.25, halfcase5.5 and20 open lever trial','authority':'ONE derived functional layer update before P11 material detail; not immutable supplier mouth','F_PI_changed_Z':[60.395,80.645],'P_SYS_changed_Z':[65.02,76.02],'F_AUX_changed_Z':[76.02,127.02]};meta['source_exit_assumption'][2]=H;meta['receiver_entry_assumption'][2]=H;meta['whole_entry_orientation']['cover_bounds']=[114,25.5,65.02,136,62.5,76.02]
(P/'power-face-full-uncut-stock-plan.json').write_bytes((json.dumps(meta,indent=2)+'\n').encode())
D.recompute();D.save()
# Finite affected list from actual visible nearpart cull, groups excluded; no world compound BOP.
checks=[];target=D.getObject('W043_FULL_UNCUT_ADAPTIVE_HANDLAY_COVER').Shape
names=['PBAY_F_AUX','PBAY_P_REAR','P11_rear_gate','P03_rear_deck_integrated_load_yoke','P19_shared_lower_carrier','ROW_POS_T18I1_NYLON','ROW_POS_REMOVABLE_END_KEEPER_RIGHT','REAR_PAIR_REMOVABLE_COMMON_KEEPER']
for n in names:
 o=D.getObject(n)
 if not o:continue
 s=o.Shape;b=target.BoundBox;c=s.BoundBox
 dx=max(0,b.XMin-c.XMax,c.XMin-b.XMax);dy=max(0,b.YMin-c.YMax,c.YMin-b.YMax);dz=max(0,b.ZMin-c.ZMax,c.ZMin-b.ZMax);lb=math.sqrt(dx*dx+dy*dy+dz*dz)
 if lb>=1.25:checks.append(dict(target='full_uncut_W043',other=n,bbox_lower_bound=lb,scope='qualified numeric whole-profile lower bound'));continue
 checks.append(dict(target='full_uncut_W043',other=n,common=target.common(s).Volume,gap=target.distToShape(s)[0],classification='plastic tie is OPEN assembly stock path not purchased rigid wire; keeper actual material'))
case=D.getObject('PBAY_P_SYS').Shape
for n in ['WAGO415_data_1_7','P19_shared_lower_carrier','P11_rear_gate','ROW_POS_REMOVABLE_END_KEEPER_RIGHT','REAR_PAIR_REMOVABLE_COMMON_KEEPER']:
 o=D.getObject(n)
 if o:checks.append(dict(target='whole_P_SYS',other=n,common=case.common(o.Shape).Volume,gap=case.distToShape(o.Shape)[0]))
(P/'whole-power-affected-layer-gates.json').write_bytes((json.dumps(checks,indent=2)+'\n').encode());print(json.dumps(checks))
