"""Complete the SAME cowl: actual-source conformal penetrations, no bought cuts."""
import FreeCAD as A,Part,json,time
from pathlib import Path
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent
def box(x,y,z,a,b,c):return Part.makeBox(a,b,c,V(x,y,z))
def bb(s):
 b=s.BoundBox;return[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def low(a,b):
 a=bb(a);b=bb(b);return sum(max(0,a[i]-b[i+3],b[i]-a[i+3])**2 for i in range(3))**.5
def put(n,x):(P/n).write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
def run():
 t=time.perf_counter();D.save();raw=json.loads((P/'current-body-delta-checks.json').read_text());put('raw-before-functional-cowl-clearances.json',raw)
 # Full Pi + factory mating ends/cooling space; actual parts remain untouched.
 # A rounded integrated service fairing, not a rectangular open device window.
 outer=box(-155.25,-101.17,37.75,117.5,36.02,71.5);outer=outer.makeFillet(3,outer.Edges)
 inner=box(-153.25,-99.17,39.75,113.5,50,67.5)
 front=D.getObject('HB_F_NEG');front.Shape=front.Shape.fuse(outer).cut(inner)
 holes=Part.makeCompound([Part.makeCylinder(2.5,60,V(x,-145,z),V(0,1,0)) for x in [-119,-109,-99,-89,-79,-69,-59,-49] for z in [66,78,90]])
 front.Shape=front.Shape.cut(holes)
 source=D.getObject('WAVEGO_complete_126_source_solids').Shape.Solids
 ids=sorted(set(int(r['neighbor'].split('_')[-1]) for r in raw['failures'] if r['neighbor'].startswith('WAVEGO_source_solid_')))
 guards=[];grows=[]
 # Only the finite NEW belly/source candidates already implicated, not all126.
 for i in ids:
  s=source[i]
  try:
   g=s.makeOffsetShape(1.35,.001,fill=True);good=g.isValid() and bool(g.Solids)
   grows.append({'source_solid':i,'valid_guard':good,'source':bb(s),'guard':bb(g),'method':'actual shape rounded offset1.35, required1.25'})
   if good:guards.append(('source_'+str(i),g))
  except Exception as e:grows.append({'source_solid':i,'valid_guard':False,'error':str(e)})
 # Local LOW source support material, not a BBox cut through an unspecified floor.
 for n in ['RG_FRONT_GRID_WITH_INTEGRAL_HEAD_RECEIVER','RG_REAR_GRID_WITH_STEPPED_RECEIVING_CROSSMEMBER','FORE_MTA_FIXED_COMMON_POSTS_AND_LOWER']:
  s=D.getObject(n).Shape.common(box(-180,-140,30,400,280,42))
  try:
   g=s.makeOffsetShape(1.35,.001,fill=True);good=g.isValid() and bool(g.Solids);grows.append({'owner':n,'valid_guard':good,'method':'actual material belowZ72 offset1.35','source_local_volume':s.Volume})
   if good:guards.append((n,g))
  except Exception as e:grows.append({'owner':n,'valid_guard':False,'error':str(e)})
 put('functional-conformal-guard-sources.json',{'guards':grows,'bought_parts_changed':False,'global_scans_replayed':False})
 rows=[]
 for n in ['HB_F_NEG','HB_F_POS','HB_R_NEG','HB_R_POS']:
  o=D.getObject(n);s=o.Shape;s.exportBrep(str(P/(n+'.before-conformal-relief.brep')))
  for gn,g in guards:
   if low(s,g)<.01:s=s.cut(g)
  # Exact matched removable deck surface, not a foreign-clearance waiver.
  for dn in ['P02_front_deck','P03_rear_deck_integrated_load_yoke']:
   q=D.getObject(dn).Shape
   if low(s,q)<.01:s=s.cut(q)
  o.Shape=s.removeSplitter();D.recompute();D.save()
  rows.append({'name':n,'valid':o.Shape.isValid(),'solids':len(o.Shape.Solids),'volume':o.Shape.Volume,'bounds':bb(o.Shape)})
  put('functional-cowl-completion-checkpoint.json',{'rows':rows,'guard_errors':[g for g in grows if not g['valid_guard']],'cursor':len(rows),'physicalPASS':False,'wholePASS':False,'seconds':time.perf_counter()-t})
 print(json.dumps({'rows':rows,'guard_errors':[g for g in grows if not g['valid_guard']],'seconds':time.perf_counter()-t}))
run()
