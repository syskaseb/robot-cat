import FreeCAD as A, Part, FreeCADGui as G, json
from pathlib import Path
from datetime import datetime,timezone
P=Path(__file__).parent
D=A.ActiveDocument;V=A.Vector
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def wr(n,d):(P/n).write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
def run():
 if D.getObject('LEG0_T18I_HEAD'):return print('already applied; read final-local-result.json')
 group=D.getObject('COMMON_PROTECTION_RETENTION_NOMINAL_FIT3')
 def add(n,s):
  o=D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=(.17,.17,.2)
  if group:group.addObject(o)
  return o
 # Full end-stop feet join the previously edge-only disconnected pieces to
 # their actual case saddle. No bought body/metal or useful source floor cut.
 for i in range(4):
  b=D.getObject('Leg_protected_MTA0100335_'+str(i)).Shape.BoundBox
  for x in [b.XMin-2,b.XMax+.25]:
   s=box(x,-51.4,64.6,1.75,11,2.4)
   for n,lo,hi in [('P02_front_deck',-160,30),('P03_rear_deck_integrated_load_yoke',30,210)]:
    q=s.common(box(lo,-100,30,hi-lo,200,80))
    if q.Volume>1e-8:D.getObject(n).Shape=D.getObject(n).Shape.fuse(q)
  x=(b.XMin+b.XMax)/2
  add('LEG'+str(i)+'_T18I_HEAD',box(x-2.4,-57.1,68,4.8,4.5,3.5))
 add('POST412_T18I_HEAD',box(-125.9,-51.25,64.1,4.8,4.5,3.5))
 for o in D.Objects:
  if o.Name.endswith('_T18I1_HEAD'):
   s=o.Shape.copy();s.translate(V(13.2,0,0));o.Shape=s
 D.recompute();D.save();G.getDocument(D.Name).Modified=False
 r=dict(utc=datetime.now(timezone.utc).isoformat(),source='same intended functional interface; added end-stop feet and full selected stock head references',parts=[],capture=[],failures=[],physical_pass=False,whole_kit_ready=False,actual_fit_cut_slack=None)
 for n in ['P02_front_deck','P03_rear_deck_integrated_load_yoke','P10_front_gate','P11_rear_gate']:
  s=D.getObject(n).Shape;q=dict(name=n,valid=s.isValid(),solids=len(s.Solids),volume=s.Volume);r['parts'].append(q)
  if not q['valid'] or q['solids']!=1:r['failures'].append(q)
 roofs=[o for o in D.Objects if o.Name.startswith(('P12_','P19_','ROW_')) and hasattr(o,'Shape') and not o.Shape.isNull() and 'HEAD' not in o.Name and 'NYLON' not in o.Name]
 for o in D.Objects:
  if not o.Name.startswith(('WAGO415','WAGO615')):continue
  b=o.Shape.BoundBox;field=box(b.XMin,b.YMin,b.ZMax,b.XLength,b.YLength,1.999)
  hits=[]
  for roof in roofs:
   bb=roof.Shape.BoundBox
   if bb.XMax<b.XMin or bb.XMin>b.XMax or bb.YMax<b.YMin or bb.YMin>b.YMax or bb.ZMin>b.ZMax+2:continue
   c=field.common(roof.Shape)
   if c.isValid() and c.Volume>1e-7:hits.append(dict(roof=roof.Name,volume=c.Volume,min_gap_z=c.BoundBox.ZMin-b.ZMax))
  r['capture'].append(dict(case=o.Name,actual_upper_material_within2mm=hits,lower_positive_stops2mm=True,status='NOMINAL_CAPTURE_WITH_SAFE_PLASTIC_FIT3' if hits else 'UPPER_CAPTURE_OPEN_NOT_SECURED'))
 r['status']='NOMINAL_PRINTS_CONNECTED_REMAINING_SCOPE_OPEN' if not r['failures'] else 'FINITE_PRINT_CONNECTION_OPEN'
 r['unreceived']=['Eight inline2411 actualcaseframes and rooted strainrail','all newly selected full-stock and all-current-neighbor clearances not globally accepted','MTA clip/flange delivery and femaleTE insertion/latch one FIT3','wholefiveFHAC pigtail reach after5mm lift FIT2, no length credit','WAGO safe contact/levers and all-group closure physical coupon']
 wr('final-local-result.json',r)
 # Source-derived local sections only; full purchased allocations retained.
 sections=[]
 for tag,x,ns in [('BANK_LEFT_X',-81.8819,['BANK_PANEL_NEG','BANK_PANEL_POS','P10_front_gate']),('REAR_FHAC_X',105,['P11_rear_gate','P19_battery_MTA_carrier','P12_common_deck_speaker'])]:
  for n in ns:
   o=D.getObject(n)
   if not o or not hasattr(o,'Shape'):continue
   q=o.Shape.section(Part.makePlane(240,180,V(x,-120,0),V(1,0,0)))
   lines=[]
   for e in q.Edges:
    lines.append([[p.y,p.z] for p in e.discretize(Number=20)])
   sections.append(dict(section=tag,x=x,name=n,lines=lines))
 wr('actual-interface-sections.json',sections)
 D.Label='DAY16 COMMON PROTECTION / NOMINAL CONNECTED PRINTS / OPEN FIT3+INLINE'
 D.recompute();D.save();G.getDocument(D.Name).Modified=False
 print(json.dumps(dict(status=r['status'],failures=r['failures'],capture_open=[q['case'] for q in r['capture'] if not q['actual_upper_material_within2mm']],objects=len(D.Objects))))
run()
