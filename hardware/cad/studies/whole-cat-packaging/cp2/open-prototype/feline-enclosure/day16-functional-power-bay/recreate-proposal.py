# Run ONLY in an explicitly loaded sole-owner SOURCE99007document, never currentproposal.
import json
from pathlib import Path
import FreeCAD as A

def add_unselected_wholecase_copies(D,folder):
 p=Path(folder);data=json.loads((p/'whole-functional-hypothesis.json').read_text());mapping=json.loads((p/'proposal-geometry-map.json').read_text())
 if D.getObject('PBAY_P_SYS'):raise RuntimeError('Proposalalreadyexists; doNOTduplicatephysicalreferences')
 group=D.addObject('App::DocumentObjectGroup','POWER_BAY_ONE_UNSELECTED_FUNCTIONAL_PLAN')
 for q,m in zip(data['relocations'],mapping):
  source=D.getObject(q['name']);s=source.Shape.copy()
  if 'rotate' in q:s.rotate(A.Vector(),A.Vector(*q['rotate'][0]),q['rotate'][1])
  b=s.BoundBox;s.translate(A.Vector(*[q['min'][i]-[b.XMin,b.YMin,b.ZMin][i] for i in range(3)]))
  o=D.addObject('PartDesign::Feature',m['name']);o.Shape=s;group.addObject(o);o.addProperty('App::PropertyString','ProposedReplacementOf').ProposedReplacementOf=source.Name
 D.recompute()
 # SourcegeometryUNCHANGED; explicit9copyoverrides/UNSELECTED, noextraBOM/no tests.
