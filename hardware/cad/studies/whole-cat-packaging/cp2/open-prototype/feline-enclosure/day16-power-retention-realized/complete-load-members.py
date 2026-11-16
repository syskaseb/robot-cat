import FreeCAD as A,FreeCADGui as G,Part,json,time,math
from pathlib import Path
from datetime import datetime,timezone
D=A.ActiveDocument;P=Path(__file__).parent;V=A.Vector
B=lambda x,y,z,l,w,h:Part.makeBox(l,w,h,V(x,y,z))
C=lambda x,y,z,r,h,a=V(0,0,1):Part.makeCylinder(r,h,V(x,y,z),a)
vol=lambda s:0.0 if s.isNull() else s.Volume
t=time.perf_counter();rows=[]
old=D.getObject('P11_rear_gate').Shape.copy();bridge=B(95,50,100,6,31.7,4)
for y in [35,49]:
 bridge=bridge.cut(B(99.6,y-2.85,100.1,9.6,5.7,2.4)).cut(C(103,y,102.5,3.7,.5).fuse(B(103,y-3.7,102.5,6.2,7.4,.5))).cut(C(103,y,97,1.7,20))
ss=[('LOAD_ROOT_TO_POSITIVE_RECEIVER',bridge),('FPI_FLOOR_JOIN',B(75,56,50.5,4,25.7,2.5)),('FAUX_FLOOR_JOIN',B(154,56,50.5,4,25.7,2.5)),('P_REAR_ENDSTOP_BASE_JOIN',B(122.3,82,57.6,4.7,13.7,2.4))]
s=old
for n,q in ss:
 s=s.fuse(q);rows.append(dict(name=n,connection_previous=vol(q.common(s)),volume=q.Volume))
D.getObject('P11_rear_gate').Shape=s
# A REALnominalreceivingparting againstfixedP11, notvirtualfusion/airBBoxcut.
bank=D.getObject('BANK_PANEL_NEG');before=bank.Shape.copy();bank.Shape=before.cut(s)
post=D.getObject('P10_front_gate');join=B(-118,6,61.6,7,4,4.4);source_main=max(post.Shape.Solids,key=lambda q:q.Volume);source_join=vol(join.common(source_main));post.Shape=post.Shape.fuse(join)
r=dict(utc=datetime.now(timezone.utc).isoformat(),P11valid=s.isValid(),P11solids=len(s.Solids),joins=rows,bankpartition=dict(valid=bank.Shape.isValid(),solids=len(bank.Shape.Solids),explicit_interface_material_partition=vol(before)-vol(bank.Shape),fixed_common=vol(bank.Shape.common(s)),contact_area=bank.Shape.common(s).Area),POST_actual_source_join=source_join,POSTvalid=post.Shape.isValid(),POSTsolids=len(post.Shape.Solids),seconds=time.perf_counter()-t)
(P/'functional-member-completion.json').write_text(json.dumps(r,indent=2)+'\n');D.recompute();D.save();G.getDocument(D.Name).Modified=False;print(json.dumps(r))
