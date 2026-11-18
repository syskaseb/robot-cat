import FreeCAD as A,Part,json,datetime
from pathlib import Path
D=A.ActiveDocument;P=Path(D.FileName).parent;V=A.Vector;guard=D.getObject('YAW_FIXED_OUTER_RACE_CAP').Shape
def wr(n,x):(P/n).write_bytes((json.dumps(x,indent=2)+'\n').encode())
steel=[o for o in D.Objects if 'YAW_SHAFT_FORK_POSITIVE_CROSSPIN' in o.Name and hasattr(o,'Shape')];rows=[]
for yaw in [-20,0,20]:
 R=A.Rotation(V(0,0,1),yaw);T=A.Placement(V(-106,0,127)-R.multVec(V(-106,0,127)),R)
 for o in steel:
  s=o.Shape.copy();s.transformShape(T.toMatrix());c=s.common(guard);rows.append({'yaw':yaw,'actual_whole_stock':o.Name,'common':c.Volume,'valid':c.isValid(),'gap':s.distToShape(guard)[0]})
wr('full-yaw-crosspin-new-fixed-guard-gate.json',{'checks':rows,'source_steel_units':len(steel),'scope':'only new fixed neck cap/columns versus FULL retained yaw crosspin/screw/nut/washers, not printed fork alone','physical_PASS':False})
family=json.loads((P.parent/'day18-connected-storage-pitch-frame/occupied-FFC200-family.json').read_text());hits=[];tested=0
for q in family:
 for i,cc in enumerate(q['corners']):
  for k,c in enumerate(cc):
   x,y,z=c
   if not(-123<=x<=-89 and -19<=y<=19 and 123<=z<=186):continue
   tested+=1
   if guard.isInside(V(*c),1e-6,True):hits.append({'yaw':q['yaw'],'pitch':q['pitch'],'station':i,'corner':k,'point':c,'classification':'FULL current16.8x1.8 FFC occupied profile witness in ACTUAL new print; fails this mapped family/guard interface, not all flexible routes'})
wr('FFC200-current-neck-local-profile-witness.json',{'tested_critical_corner_points':tested,'inside_material_witnesses':hits,'scope':'cheap named new fixed collar/column pinch screen; absence of vertex hits would NOT prove whole ribbon clearance','physical_PASS':False})
t=json.loads((P.parent/'day18-closed-whole-common-assembly/ToF4-full-connected-family-and-unit-plan.json').read_text());tofhits=[];near=[]
for q in t['fixed_fans']:
 for i,c in enumerate(q['centreline']):
  x,y,z=c
  if not(-124<=x<=-88 and -20<=y<=20 and 123<=z<=187):continue
  if guard.isInside(V(*c),1e-6,True):tofhits.append({'wire':q['wire'],'station':i,'point':c})
  else:
   d=guard.distToShape(Part.Vertex(V(*c)))[0]-1.45
   if d<1.25:near.append({'wire':q['wire'],'station':i,'occupied_lower_gap':d,'point':c})
wr('ToF4-current-neck-port-local-witness.json',{'source':'same4actual HELU cores; primary JP3.2/6/3/4; full planned510/core with properend/loss; no Pololu600','inside_wire_centres':tofhits,'near_full_individual_OD2p1_plus_project_margin':near,'scope':'only source current stationary fan branches near new cap/strut/lateral inlet; moving family and source grips remain separate OPEN','physical_PASS':False})
wr('current-combined-neck-decision-gate.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'material_neutral_and4extremes':'30 head/front-fixed-neck witness BOPs common0, stored separately; not allpose manufacturing approval','full_steel_hard_failures':[r for r in rows if r['common']>1e-6],'full_steel_clearance_failures':[r for r in rows if r['gap']<1.25-1e-6],'FFC_actual_print_profile_hits':len(hits),'ToF_actual_print_wire_centre_hits':len(tofhits),'ToF_small_clearance_candidates':len(near),'JR':'three separate full physicalunits250+250+300 retained; positive side capacity may take4ToF+JR300flat3.5x1.8, fixed yaw250 staysbody, pitchfactory250 staysyaw-case-to-mate; actual grips/full unit handlay still ENGINEERING OPEN, not physical-pass','whole_closed_accepted':False,'physical_PASS':False})
print('COMBINED_NECK_GATE',{'steel_positive':[r for r in rows if r['common']>1e-6],'FFC_hits':len(hits),'ToF_hits':len(tofhits),'ToF_near':len(near)})
