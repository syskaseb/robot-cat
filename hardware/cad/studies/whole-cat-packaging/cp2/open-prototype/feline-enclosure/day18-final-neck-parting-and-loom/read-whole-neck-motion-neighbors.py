import FreeCAD as A,Part,json,time,datetime
from pathlib import Path
D=A.ActiveDocument;P=Path(D.FileName).parent;V=A.Vector
def bg(a,b):return sum(max(0,getattr(a,k+'Min')-getattr(b,k+'Max'),getattr(b,k+'Min')-getattr(a,k+'Max'))**2 for k in ['X','Y','Z'])**.5
def wr(n,x):(P/n).write_bytes((json.dumps(x,indent=2)+'\n').encode())
targets=['Motor_ATO4A__1_0','Motor_ATO4A__1_3','Motor_ATO4A_1_0','Motor_ATO4A_1_3','WAGO415_data__1_0','WAGO415_data__1_4','WAGO415_data_1_1','WAGO415_data_1_4','Pi4B_actual_PCB','Pi_components_and_cooling']
heads=[D.getObject(n).Shape for n in ['F3_HEAD_FRONT','F3_HEAD_BACK']]
poses=[(0,0),(-20,-10),(-20,10),(20,-10),(20,10)]
rows=[]
wr('selected-neck-interface-plan.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'one_hypothesis':'Retain full current moving skull and actual current roots; reconstruct the fixed fore-cowl shoulder receiving edge around a conservatively covered moving rear head, with an inboard overlapping fixed dark baffle instead of the old rectangular neck void. Fixed vs moving prints remain disjoint and fastened, not fused. No electronics move or head translation.','decision_gate':'Before this material cut, check actual moving skull against current FRONT rigid MTA/TE/ATO and terminal/required Pi layers: a shell cut cannot qualify purchased-part/moving-shell interference. Operands retain source installation-vs-material classification.','fixed_source':'98e254116c1128f13a94742449beddf451461fd5','motion':{'yaw':[-20,20],'pitch':[-10,10]},'do_not_claim':'five poses are witnesses, not continuous certification or all-path impossibility','physical_PASS':False})
for yaw,pitch in poses:
 ry=A.Rotation(V(0,1,0),pitch);rz=A.Rotation(V(0,0,1),yaw)
 T=A.Placement(V(-106,0,127)-rz.multVec(V(-106,0,127)),rz).multiply(A.Placement(V(-135,0,121)-ry.multVec(V(-135,0,121)),ry))
 for i,h0 in enumerate(heads):
  h=h0.copy();h.transformShape(T.toMatrix())
  for n in targets:
   o=D.getObject(n)
   if not o or bg(h.BoundBox,o.Shape.BoundBox)>1.25:continue
   c=h.common(o.Shape);b=c.BoundBox
   rows.append({'yaw':yaw,'pitch':pitch,'head':['front','back'][i],'fixed':n,'common':c.Volume,'valid':c.isValid(),'common_bounds':[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax] if c.Volume>1e-6 else None,'classification':'full retained MTA/TE/ATO assembly or source installed PCB case field; conservative purchased assembly capacity not an invented empty wire obstacle'})
  wr('current-moving-neck-near-unit-witnesses.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':rows,'cursor':[yaw,pitch,i],'scope':'only current neck/head interface neighbors; no old global matrix'})
print('NECK_WITNESSES_COMPLETE',len(rows),[r for r in rows if r['common']>1e-5])
