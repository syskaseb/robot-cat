import FreeCAD as A, FreeCADGui as G,Part,json,time,math,hashlib
from pathlib import Path
from datetime import datetime,timezone
P=Path(__file__).parent;V=A.Vector
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def fuse(ss):
 s=ss[0]
 for q in ss[1:]:s=s.fuse(q)
 return s
def run():
 D=A.ActiveDocument;t=time.perf_counter();old={o.Name:o.Shape.copy() for o in D.Objects if o.Name.startswith('CLOSED_BODY_')}
 decks=[D.getObject(n).Shape for n in ['P02_front_deck','P03_rear_deck_integrated_load_yoke']];fs=[]
 for s in decks:
  for f in s.Faces:
   b=f.BoundBox
   if b.ZLength<1e-6 and f.Area>20:
    w=f.OuterWire.copy();w.translate(V(0,0,-b.ZMin));flat=Part.Face(w)
    if flat.normalAt(0,0).z<0:flat.reverse()
    fs.append(flat)
 # Normalize coplanar projection via a 1mm prism union; original oppositely oriented/nested faces yielded mixed Compound, no model edit.
 prism=fuse([f.extrude(V(0,0,1)) for f in fs]).removeSplitter()
 bottom=[f for f in prism.Faces if f.BoundBox.ZLength<1e-6 and abs(f.BoundBox.ZMin)<1e-6]
 footprint=Part.Face(max(bottom,key=lambda f:f.Area).OuterWire)
 outer=footprint.makeOffset2D(3.65);guard=footprint.makeOffset2D(1.25);inner=footprint.makeOffset2D(-3)
 # Real foundation deck replaces redundant middle skin floor. Perimeter skirt and upper bearing lip close its outer edge.
 skirt=outer.cut(guard).extrude(V(0,0,9.42));skirt.translate(V(0,0,41.5))
 lip=outer.cut(inner).extrude(V(0,0,2.4));lip.translate(V(0,0,48.52))
 deck=fuse(decks);receiver=fuse([skirt,lip]).cut(deck)
 remove=guard.extrude(V(0,0,22));remove.translate(V(0,0,30))
 # Tail slot crosses BOTH separately installed rear skins. No tail/servo/bearing relocation.
 throat=box(174,-28,135,72,56,88)
 partition={'front_negative':box(-150,-120,20,175,120,200),'front_positive':box(-150,0,20,175,120,200),'rear_negative':box(25,-120,20,190,130,200),'rear_positive':box(25,10,20,190,110,200)}
 for n,s in old.items():
  tag=n.replace('CLOSED_BODY_','');region=partition[tag];new=s.cut(remove).fuse(receiver.common(region)).cut(throat)
  D.getObject(n).Shape=new
 for o in D.Objects:
  if o.Name.startswith(('P01','P02','P03','P04','P05','P06','P07','H04')):o.ViewObject.Visibility=True
 D.Label='DAY16 BOTTOM + TAIL / ONE FUNCTIONAL CORRECTION / NOT PRINT RELEASE';D.recompute();D.saveAs(str(P/'bottom-tail-closure.FCStd'))
 result=dict(utc=datetime.now(timezone.utc).isoformat(),source_commit='4e567a69bb81228a4c1fb15f7114396387def3b3',source_foundation_unchanged=True,closure='Actual P02/P03 deck is central bottom closure; new skin outer skirt and top bearing lip form perimeter, source rails unchanged',tail='Actual rear split with 56mm wide open throat; install skins from opposite Y sides around retained tail, not thread tail through a closed hole',checks=[],first_falsifier=None,whole_feasible=False,physical_pass=False,actual_fit_cut_slack=None)
 for n in old:
  s=D.getObject(n).Shape;result['checks'].append(dict(part=n,valid=s.isValid(),solids=len(s.Solids),volume=s.Volume))
  if not s.isValid() or len(s.Solids)!=1:result['first_falsifier']=dict(kind='New skin material realization invalid/disconnected',part=n,solids=len(s.Solids));break
 if not result['first_falsifier']:
  for n in old:
   s=D.getObject(n).Shape
   for qn in ['P01_load_rail','P01_load_rail_instance2','P02_front_deck','P03_rear_deck_integrated_load_yoke','P04_deck_splice','P04_deck_splice_instance2','Ola_tail_ENVELOPE']:
    q=D.getObject(qn).Shape;c=s.common(q);gap=s.distToShape(q)[0];row=dict(part=n,other=qn,common=c.Volume,valid=c.isValid(),gap=gap,interface='matched actual deck bearing' if qn.startswith(('P02','P03')) else 'foreign retained shape')
    result['checks'].append(row)
    if not c.isValid() or c.Volume>1e-5 or (qn.startswith(('P01','P04','Ola_tail')) and gap<1.25-1e-6):result['first_falsifier']=row;break
   if result['first_falsifier']:break
 result['tail_motion_basis']=dict(native_bearing_axis='Actual Tail608 axis worldZ through185,0',native_bearing_Z=[137,144],simulator_tail_axis='Old URDF localY; not current WAVEGO mechanical axis/range binding',required_range_UNKNOWN=True,horn_output_axis_and_coupling_FIT3=True,opening_bounds=[174,-28,135,246,28,223],neutral_tail_unmodified=True,no_continuous_required_motion_PASS=True)
 # Analytic continuous azimuth bound for full unmodified tail bounding prism, not a matrix of poses.
 b=D.getObject('Ola_tail_ENVELOPE').Shape.BoundBox;xmin=b.XMin-185;xmax=b.XMax-185;ymax=max(abs(b.YMin),abs(b.YMax));allowY=28-1.25
 theta=math.asin(allowY/math.hypot(xmax,ymax))-math.atan2(ymax,xmax)
 result['tail_motion_basis'].update(dict(analytic_admissible_symmetric_Zyaw_degrees=math.degrees(theta),method='For every angle in interval, maxabsY <= xmax*sin(theta)+ymax*cos(theta); full source tail BBox conservatively contained. This interval is capacity, NOT accepted required range.',minX_at_bound=185+xmin*math.cos(theta)-ymax*math.sin(theta),maxX_at_bound=185+xmax*math.cos(theta)+ymax*math.sin(theta)))
 result['scope']='HOLD_NO_SECOND_GEOMETRY' if result['first_falsifier'] else 'BOTTOM_AND_NEUTRAL_TAIL_SCOPED_REQUIRED_MOTION_UNQUALIFIED'
 result['seconds']=time.perf_counter()-t
 (P/'closure-result.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
 rows=[]
 for z in [42.7,46.5,49.0,167.0]:
  for n in list(old)+['P01_load_rail','P01_load_rail_instance2','P02_front_deck','P03_rear_deck_integrated_load_yoke','Ola_tail_ENVELOPE']:
   s=D.getObject(n).Shape;b=s.BoundBox
   if b.ZMin>z or b.ZMax<z:continue
   sec=s.section(Part.makePlane(500,250,V(-270,-120,z)))
   rows.append(dict(z=z,name=n,lines=[[[v.x,v.y] for v in e.discretize(Deflection=.7)] for e in sec.Edges]))
 (P/'closure-sections.json').write_text(json.dumps(rows)+'\n')
 D.save();G.getDocument(D.Name).Modified=False
 print(json.dumps(dict(scope=result['scope'],first=result['first_falsifier'],tail=result['tail_motion_basis'],checks=len(result['checks']),seconds=result['seconds'])))
run()
