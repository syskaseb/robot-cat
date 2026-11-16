import FreeCAD as A,FreeCADGui as G,json,math
from pathlib import Path
from PySide import QtCore
D=A.ActiveDocument;P=Path(__file__).parent;V=A.Vector
j=json.loads((P/'whole-low-layout-effectivity.json').read_text())
def bbox(o):
 b=o.Shape.BoundBox;return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def move(n,target,rot=None):
 o=D.getObject(n)
 if rot:o.Placement=A.Placement(V(),rot).multiply(o.Placement)
 b=o.Shape.BoundBox;o.Placement.Base+=V(*target)-V(b.XMin,b.YMin,b.ZMin)
move('F0_FHAC0002_30A',[-41.5,-67,52],A.Rotation(V(1,0,0),-90))
move('XT60H_mated_with_boots',[-6,-72,84])
for n,delta in [('MAIN_all_terminal_field_FIT2',(9,-32,-31.5)),('AUX_all_terminal_field_FIT2',(3,-57,-31.5))]:
 o=D.getObject(n)
 if o:o.Placement.Base+=V(*delta)
# Hide only analytical fields/retired demands, not real purchased protrusions.
for o in D.Objects:
 n=o.Name
 if ('FOV' in n or n.startswith(('CAM102','TOF_BOTH','LOW_REGION_')) or 'INSTALLATION' in n or 'terminal_field_FIT2' in n):o.ViewObject.Visibility=False
D.Label='LOWER LIGHTER WHOLE CONCEPT - UNSELECTED'
selected=list(dict.fromkeys(j['new_prints']+j['retained_print_names']))
rows=[]
for n in selected:
 o=D.getObject(n);s=o.Shape;vol=s.Volume
 solids=s.Solids;c=sum((q.CenterOfMass*q.Volume for q in solids),V())/vol if vol else V()
 rows.append({'name':n,'volume_mm3':vol,'PETG_full_g':vol*.00127,'COM_mm':list(c),'bounds':bbox(o),'solids':len(solids),'valid':s.isValid()})
total=sum(r['PETG_full_g'] for r in rows)
com=[sum(r['COM_mm'][i]*r['PETG_full_g'] for r in rows)/total for i in range(3)]
m={'density_g_cm3':1.27,'method':'cached actual print solid volume; no electronics density; complete before-after scope explicit','baseline70_fullPETG_g':1778.501,'current_selected_print_count':len(rows),'current_fullPETG_g':total,'delta_fullPETG_g':1778.501-total,'percent_reduction_same_scope':100*(1778.501-total)/1778.501,'current_print_COM_mm':com,'rows':rows,'not_counted_as_proven_saving':'required future complete fixings/anchors/retention/coverjoints allowance not yet modeled','future_material_planning_allowance_g':[50,120],'original_legs_unchanged_solidPETG_g':118.210,'baseline_body_roof185p201_new145_mm_drop':40.2009939496,'head_lowered_mm':20,'tail_axis_lowered_mm':42,'physical_mass_not_certificate':True}
(P/'same-density-mass-and-height.json').write_bytes((json.dumps(m,indent=2)+'\n').encode())
# Entire source modules/end references, not just visible source boxes.
mods=[]
for r in j['moves']:
 o=D.getObject(r['name'])
 if o and not hasattr(o,'Group'):mods.append({'name':o.Name,'bounds':bbox(o),'volume_mm3':o.Shape.Volume})
(P/'current-whole-module-bounds.json').write_bytes((json.dumps(mods,indent=2)+'\n').encode())
# Named cheap real source risk: speaker versus Pi GPIO female. Exact source fields, no whole-world replay.
pairs=[]
for a,b in [('Speaker','Pi_GPIO1992_factory_female'),('F0_FHAC0002_30A','Pi4B_actual_PCB'),('XT60H_mated_with_boots','S0_key')]:
 x=D.getObject(a).Shape;y=D.getObject(b).Shape
 pairs.append({'a':a,'b':b,'gap_mm':x.distToShape(y)[0],'risk':'actual source case/connector or allocated complete mating profile; gap not all-path result'})
(P/'first-finite-whole-gate.json').write_bytes((json.dumps({'checks':pairs,'whole_result':'PROPOSAL_ONLY not whole fit PASS','unreceived':['complete mounting hardware and positive load connections','all physical-group adjacency and stock-space','source MTA0100335 full unit','CSI continuous occupied space and motion reserve','full textile capture and covers real keyed fasteners'],'technical_notes':['two loft endplanes initially open; real end closures not yet realized','253mm WAGO rails need real split for brim below256','source uncertainty cover can intersect speaker; one real MINIVAL sample required']},indent=2)+'\n').encode())
D.recompute();D.save()
v=G.activeDocument().activeView();v.viewAxonometric();v.fitAll();v.redraw()
def finish():
 D.Label='LOWER LIGHTER WHOLE CONCEPT - UNSELECTED';D.save();G.activeDocument().Modified=False
 (P/'actual-native-final-save.json').write_bytes((json.dumps({'path':D.FileName,'objects':len(D.Objects),'saved':True,'unsaved':False,'pending':None,'GUI_PID':17796,'scope':'ONE WHOLE LOWER LIGHTER CONCEPT NOT WHOLEFIT','UTC':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()},indent=2)+'\n').encode())
QtCore.QTimer.singleShot(1500,finish)
print(json.dumps({'mass_full_g':total,'reduction_g':1778.501-total,'named_gate':pairs}))
