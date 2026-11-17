import FreeCAD as A,Part,json,math,time
from pathlib import Path
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent
def put(n,x):(P/n).write_bytes((json.dumps(x,indent=2,ensure_ascii=False)+'\n').encode())
def bb(s):
 if not s.Vertexes:return None
 b=s.optimalBoundingBox(False,True);return[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def run():
 t=time.perf_counter();D.save();f=D.getObject('A17_INTEGRAL_FRONT_DECK_AND_N1').Shape;tool=[]
 for x,y in [(x,y) for x in [-80,-70] for y in [-22.5,22.5]]:
  sy=1 if y>0 else -1;a=V(0,sy*math.sin(math.radians(20)),math.cos(math.radians(20)));p=V(x,y,48.52);field=Part.makeCylinder(1,4,p,a).fuse(Part.makeCylinder(1.5,80,p+a*4,a));c=f.common(field)
  tool.append({'axis':[x,y],'common':c.Volume,'bounds':bb(c),'actual_vertices':[list(v.Point) for v in c.Vertexes]})
 put('actual-driver-obstruction-source.json',{'rows':tool,'seconds':time.perf_counter()-t})
 # ONEchangedphysicalacousticinterface, currentfullfixture+completeactualstock.
 q=D.getObject('FC_F_POS').Shape;rows=[]
 names=['Speaker','SPEAKER_REMOVABLE_BASKET_RIM_TRIAL_KEEPER','FORE_MTA_FIXED_COMMON_POSTS_AND_LOWER']+[o.Name for o in D.Objects if o.Name.startswith('SPKR_M2') and hasattr(o,'Shape')]
 for n in names:
  s=D.getObject(n).Shape;valid=q.isValid() and s.isValid();g=q.distToShape(s)[0] if valid else None;c=q.common(s).Volume if valid and g<1.25 else 0
  rows.append({'neighbor':n,'valid':valid,'gap':g,'common':c,'required_foreign':1.25,'clear':valid and g>=1.25-1e-6});put('acoustic-full-unit-and-stock-gate.json',{'rows':rows,'cursor':len(rows),'all':len(names),'wholePASS':False})
 parting=[]
 for n in ['A17_INTEGRAL_FRONT_DECK_AND_N1','FC_F_NEG','FC_R_POS']:
  s=D.getObject(n).Shape;c=q.common(s);parting.append({'neighbor':n,'common':c.Volume,'valid':c.isValid(),'classification':'Distinctprints/sourcecowlparting needs0common; no OWNwaiver'})
 put('two-interface-coexistence-gate.json',{'acoustic':rows,'separate_prints':parting,'source_boughtparts_or_stock_moved':False,'worldoccupied_front_is_subset_old_sourceunion':True,'169_cursor':'FROZEN7; notreplayed','wholekit':False,'physicalPASS':False,'seconds':time.perf_counter()-t});D.save();print(json.dumps({'tool':tool,'acoustic':rows,'parting':parting,'seconds':time.perf_counter()-t}))
run()
