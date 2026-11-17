import FreeCAD as A,Part,json,time
from pathlib import Path
D=A.ActiveDocument;P=Path(__file__).parent
def bb(s):
 b=s.BoundBox;return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def low(a,b):
 a=bb(a);b=bb(b);return sum(max(0,a[i]-b[i+3],b[i]-a[i+3])**2 for i in range(3))**.5
def put(n,x):(P/n).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def run():
 t=time.perf_counter();previous=P/'current-body-delta-checks.json';rows=json.loads(previous.read_text(encoding='utf-8'))['rows'] if previous.exists() else []
 names=['Pi_GPIO1992_factory_female','Pi_USB_DATA_Delock_mating','Pi_components_and_cooling','Speaker','Monitor_MOD05015','ReSpeakerLite_on_REMOVABLE_back','BUS25514_installed','RG_FRONT_GRID_WITH_INTEGRAL_HEAD_RECEIVER','RG_REAR_GRID_WITH_STEPPED_RECEIVING_CROSSMEMBER','FORE_MTA_FIXED_COMMON_POSTS_AND_LOWER','FORE_MTA_REMOVABLE_UPPER_RECEIVER','P02_front_deck','P03_rear_deck_integrated_load_yoke']
 names += [o.Name for o in D.Objects if hasattr(o,'Shape') and o.ViewObject.Visibility and o.Name.startswith(('Motor_ATO4A','S0_'))]
 # Separate source solids only at the NEW belly hazard, not a whole126 compound BOP.
 source=D.getObject('WAVEGO_complete_126_source_solids')
 sourcecandidates=[]
 if source:
  for i,s in enumerate(source.Shape.Solids):
   b=s.BoundBox
   if b.ZMax>=31.1 and b.XMax>=-168 and b.XMin<=197 and b.YMax>=-125 and b.YMin<=125:sourcecandidates.append((i,s))
 put('new-belly-source-cull.json',{'hazard':'NEW32..44mm belly vs actual retained source chassis/hip parts. Individual current source operands, no globalcompound.','source_total126':len(source.Shape.Solids) if source else None,'new_near_candidates':[{'i':i,'b':bb(s)} for i,s in sourcecandidates]})
 for n in globals().get('PART_NAMES',['HB_F_NEG','HB_F_POS','HB_R_NEG','HB_R_POS']):
  rows=[r for r in rows if r['part']!=n]
  s=D.getObject(n).Shape
  # Fixed named current equipment/receiver interfaces, only the newly created wall.
  for qn in names:
   q=D.getObject(qn)
   if not q:continue
   l=low(s,q.Shape)
   if l>=1.25:continue
   valid=s.isValid() and q.Shape.isValid()
   r={'part':n,'neighbor':qn,'valid':valid,'scope':'new_wall_only','matched_existing_deck_bearing':qn.startswith(('P02_','P03_'))}
   if valid:
    r['common']=s.common(q.Shape).Volume;r['gap']=s.distToShape(q.Shape)[0]
    r['clear_scoped']=r['common']<1e-7 if r['matched_existing_deck_bearing'] else r['gap']>=1.25-1e-7
   else:r['clear_scoped']=None
   rows.append(r)
   put('current-body-delta-checks.json',{'rows':rows,'cursor':len(rows),'failures':[r for r in rows if r['clear_scoped'] is False],'wholePASS':False,'seconds':time.perf_counter()-t})
  # The source bodies mostly lie BELOW the new wall; BBoxcull each local floor piece.
  floor=s.common(Part.makeBox(400,280,14,A.Vector(-180,-140,30)))
  for i,q in sourcecandidates:
   l=low(floor,q)
   if l>=1.25:continue
   r={'part':n,'neighbor':'WAVEGO_source_solid_'+str(i),'valid':floor.isValid() and q.isValid(),'scope':'new_belly_only','common':floor.common(q).Volume,'gap':floor.distToShape(q)[0]}
   r['clear_scoped']=r['gap']>=1.25-1e-7;rows.append(r)
   put('current-body-delta-checks.json',{'rows':rows,'cursor':len(rows),'failures':[r for r in rows if r['clear_scoped'] is False],'wholePASS':False,'seconds':time.perf_counter()-t})
 print(json.dumps({'rows':len(rows),'failures':[r for r in rows if r['clear_scoped'] is False],'seconds':time.perf_counter()-t}))
run()
