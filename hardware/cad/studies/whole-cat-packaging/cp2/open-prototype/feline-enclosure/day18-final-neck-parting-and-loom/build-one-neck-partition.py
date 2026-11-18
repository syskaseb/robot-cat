import FreeCAD as A,Part,json,math,datetime
from pathlib import Path
D=A.ActiveDocument;P=Path(D.FileName).parent;V=A.Vector
def box(x,y,z,a,b,c):return Part.makeBox(a,b,c,V(x,y,z))
def cy(x,y,z,r,h):return Part.makeCylinder(r,h,V(x,y,z))
def ell(c,r):
 s=Part.makeSphere(1);m=A.Matrix();m.A11,m.A22,m.A33=r;s=s.transformGeometry(m);s.translate(V(*c));return s
def wr(n,x):(P/n).write_bytes((json.dumps(x,indent=2)+'\n').encode())
def run():
 cap=D.getObject('YAW_FIXED_OUTER_RACE_CAP');oldcap=cap.Shape.copy()
 columns=[box(-95,y,124,4,3,34.5) for y in [-5,2]]
 baffle=cy(-106,0,157.5,16,27.5).cut(cy(-106,0,157.5,14.4,25.9))
 for y in [6,-25]:baffle=baffle.cut(box(-126,y,158,40,19,21))
 for y in [-14.5,14.5]:baffle=baffle.cut(cy(-106,y,120,4.25,70))
 root=oldcap.copy()
 for q in columns+[baffle]:root=root.fuse(q).removeSplitter()
 missing=[q.cut(root).Volume for q in [oldcap]+columns+[baffle]]
 gate={'valid':root.isValid(),'solids':len(root.Solids),'all_intended_missing':missing,'actual_column_cap_positive_common':[oldcap.common(s).Volume for s in columns],'actual_column_baffle_positive_common':[s.common(baffle).Volume for s in columns],'old_failed_face_only_union_source_loss':'raw1062.7764 retained in selected-inset-neck-root-cheap-gate; repaired by ONE actual1mm positive overlap at baffle, not another root location','complete_source_cap_retained':max(missing)<1e-5}
 wr('real-fixed-baffle-root-coverage.json',gate)
 if not root.isValid() or len(root.Solids)!=1 or max(missing)>1e-5:
  wr('implementation-HOLD.json',{'cause':'fixed cap+baffle intended coverage not achieved; no skin changed','gate':gate});print('NORMAL_RETURN_ROOT_HOLD',gate);return
 cap.Shape=root
 front=D.getObject('F3_HEAD_FRONT');back=D.getObject('F3_HEAD_BACK');oldfront=front.Shape.copy();oldback=back.Shape.copy()
 upper=oldback.common(box(-220,-110,172,200,220,150))
 # The lower OLD moving back becomes a real FIXED shoulder guard, not a virtual detached integral beam.
 lower=oldback.common(box(-220,-110,60,200,220,97.5))
 ho=ell((-134,0,150),(64,77,64));f=oldfront.copy();b=upper.copy();joint_rows=[]
 for side in [-1,1]:
  y=side*53;z=190;boss=box(-145,y-4,z-6,8,8,12).common(ho)
  f=f.fuse(boss)
  b=b.cut(box(-140,y-4.25,z-6.25,3.25,8.5,12.5)).fuse(box(-136.75,y-4,z-6,3.5,8,12).common(ho))
  bore=Part.makeCylinder(1.1,22,V(-150,y,z),V(1,0,0));f=f.cut(bore);b=b.cut(bore);b=b.cut(Part.makeCylinder(2.75,34,V(-132.7,y,z),V(1,0,0)))
  prefix='F3_HEAD_BACK_'+('m1' if side<0 else '1')+'_'
  for o in D.Objects:
   if o.Name.startswith(prefix):
    vol=o.Shape.Volume;o.Placement.Base+=V(0,-side*20,45);joint_rows.append({'name':o.Name,'full_source_volume_before':vol,'after':o.Shape.Volume})
 front.Shape=f.removeSplitter();back.Shape=b.removeSplitter()
 data=json.loads((P/'front-skin-continuous-motion-cover.json').read_text());vs=[V(*q) for q in data['vertices']]
 faces=[Part.Face(Part.makePolygon([vs[i] for i in q]+[vs[q[0]]])) for q in data['faces']]
 tool=Part.makeSolid(Part.makeShell(faces)).removeSplitter()
 if tool.Volume<0:tool.reverse()
 if not tool.isValid():wr('implementation-HOLD.json',{'cause':'local front motion cover invalid, root/head state saved but cowls untouched'});D.recompute();D.save();return
 tool=tool.common(box(-260,-180,90,320,360,190))
 # Actual current fixed module capacities retained; relief applies only to NEW upper skin, never foundation/floor.
 names=['Motor_ATO4A__1_0','Motor_ATO4A__1_3','Motor_ATO4A_1_0','Motor_ATO4A_1_3','WAGO415_data__1_0','WAGO415_data__1_4','WAGO415_data_1_1','WAGO415_data_1_4','Pi_components_and_cooling']
 relief=[]
 for n in names:
  o=D.getObject(n)
  if not o:continue
  q=o.Shape.BoundBox;relief.append(box(q.XMin-1.25,q.YMin-1.25,max(90,q.ZMin-1.25),q.XLength+2.5,q.YLength+2.5,max(.01,q.ZMax+1.25-max(90,q.ZMin-1.25))))
 # Low closed roof follows BOTH actual head lower guard and body cross-section footprint. DATA and ToF/JR get internal ports, not wire cuts.
 bodyroof=box(-140,-90,155.9,115,180,1.6)
 headroof=ell((-134,0,150),(64,77,64)).common(box(-140,-100,155.9,115,200,1.6))
 roof=bodyroof.fuse(headroof).removeSplitter()
 shoulder_rows=[]
 for tag,side in [('NEG',-1),('POS',1)]:
  o=D.getObject('F3_BODY_FORE_'+tag);old=o.Shape.copy();reg=box(-220,-115 if side<0 else 0,40,240,115,250)
  keep=old.cut(box(-220,-115,157.5,195,230,180))
  # Source floor/receiving roots remain exactly; only above157.5 and X<-25 is the planned retired old shoulder.
  pieces=[keep,lower.common(reg),roof.common(reg)]
  s=pieces[0]
  for q in pieces[1:]:s=s.fuse(q).removeSplitter()
  s=s.cut(tool)
  for q in relief:s=s.cut(q)
  s=s.removeSplitter();o.Shape=s
  shoulder_rows.append({'name':o.Name,'valid':s.isValid(),'solids':len(s.Solids),'source_below90_missing':old.common(box(-220,-115,40,240,230,50)).cut(s).Volume,'volume':s.Volume})
 wr('one-real-neck-partition-material.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'fixed_baffle_root':gate,'moving_head_parts':{'front_valid':front.Shape.isValid(),'front_solids':len(front.Shape.Solids),'back_valid':back.Shape.isValid(),'back_solids':len(back.Shape.Solids),'front_back_common':front.Shape.common(back.Shape).Volume},'reused_full_M2x16_sets':joint_rows,'fixed_shoulders':shoulder_rows,'withdrawn_unbuilt_roles':['old lower rear head as pitch-moving shell','old back fastener seats atZ145 replaced by full same sets atZ190','old front cowl upper roof X<-25 above157.5; source floors/6receiver joints untouched'],'planned_replacement':'fixed lower neck/body roof and upper moving cap with inset protected C-baffle. Real guard source cap retained0missing; body/module poses and all optics unchanged.','must_gate':['neutral/four extreme moving material versus new fixed guard and current full cases','full actual currentFFC200/ToF4 profiles through protected lateral windows, no shorterR/profile/range','actual source cap driver/head/factory screw/bearing installation','new shoulder useful connection/closed-floor and silhouette; no automatic acceptance from valid1solid'],'whole_closed_accepted':False,'physical_PASS':False})
 D.recompute();D.save();print('ONE_NECK_PARTITION_REALIZED',shoulder_rows)
run()
