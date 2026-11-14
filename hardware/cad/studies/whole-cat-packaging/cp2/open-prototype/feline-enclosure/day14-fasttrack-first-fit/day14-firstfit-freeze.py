import FreeCAD as A, FreeCADGui as G, Part,json,time
from pathlib import Path
from PySide import QtCore
P=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day14-fasttrack-first-fit')
D=A.getDocument('DAY14_WAVEGO_FIRST_FIT_UNRELEASED');A.setActiveDocument(D.Name)
d=json.loads((P/'layout.json').read_bytes());r={a['id']:a for a in d['rows']}
for n,p,dim in [('Upper_frame_end_105',[108,-49,90],[3,96,3]),('Upper_frame_rail_-49',[-104,-49,90],[215,3,3]),('Upper_frame_rail_44',[-104,44,90],[215,3,3])]:
 o=D.getObject(r[n]['object']);o.Shape=Part.makeBox(*dim,A.Vector(*p));b=o.Shape.BoundBox;r[n]['bounds_mm']=[[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]];r[n]['volume_mm3']=o.Shape.Volume
battery_column=Part.makeBox(106.5,35,115,A.Vector(-2,-17.5,65))
fixed=['Rear_S0_shared_panel_BLANK','Upper_frame_end_105','MAIN_Pololu4853','AUX_Pololu4092','Monitor_MOD05015']
s0=Part.makeCompound([D.getObject(r[n]['object']).Shape for n in r if n.startswith('S0_') and r[n]['evidence']=='selected_source'])
out=[]
for n in fixed+['S0_complete11']:
 s=s0 if n=='S0_complete11' else D.getObject(r[n]['object']).Shape
 out.append(dict(fixed=n,distance_mm=battery_column.distToShape(s)[0]))
d['checks'].append(dict(hazard='BATTERY_VERTICAL_EXTRACTION_AFTER_MIC_BACK_REMOVAL_UNPLUG',method='One vertical occupied prism from selectednominal battery65..180 vs six named actual or proposed fixed bottlenecks; no wholemotion scan',pairs=out,min_gap_mm=min(x['distance_mm'] for x in out),status='NAMED_NOMINAL_SWEEP_BOUND_ONLY_FACTORYLEAD_UNPLUG_AND_STRAPS_FIT2'))
d['first_fit_wall_start_utc']='2026-11-14T20:55:50Z'
d['final_geometry_utc']=__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()
d['native_object_count']=len(D.Objects)
(P/'layout.json').write_bytes((json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode())
D.Label='DAY14 WAVEGO FIRST FIT — UNRELEASED / one arrangement';D.recompute()
G.activeDocument().activeView().viewAxonometric();G.activeDocument().activeView().fitAll()
# Save after the MCP transaction completes, so modified=false is actually observable.
QtCore.QTimer.singleShot(1200,lambda doc=D:doc.save())
print(json.dumps({'battery_extraction':out,'geometry_saved_after_transaction':True,'doc':D.Name}))
