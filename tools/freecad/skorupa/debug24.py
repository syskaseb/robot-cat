"""Headless isolation of native solver issue; never alters user documents."""
from pathlib import Path
import json,sys
import FreeCAD as A,Part
sys.path.insert(0,A.getHomePath()+'Mod/Assembly')
import JointObject
from probe21 import world
ROOT=Path(__file__).resolve().parents[3]; OUT=ROOT/'hardware/skorupa/v24'
plan=json.loads((OUT/'assembly-plan.json').read_text(encoding='utf-8'))
if len(sys.argv)>1:
    if sys.argv[1]=='FR':
        selected={r['name'] for r in plan['components'] if r['stage'].startswith('Motion_FR_')}|{plan['ground']}
        plan['components']=[r for r in plan['components'] if r['name'] in selected]
        plan['joints']=[r for r in plan['joints'] if r['child'] in selected]
source=A.openDocument(str(ROOT/'hardware/skorupa/v23/Kot_v23_AKUMULATOR_PETG.FCStd'))
d=A.newDocument('DebugNative24'); asm=d.addObject('Assembly::AssemblyObject','Assembly')
g=asm.newObject('Assembly::JointGroup','Joints')
for row in plan['components']:
    container=asm.newObject('App::Part','Rigid_'+row['name']) if 'wrappers' in sys.argv else asm
    o=container.newObject('Part::Feature',row['name']); o.Shape=world(source.getObject(row['name']))
    if 'boxes' in sys.argv: o.Shape=Part.makeBox(1,1,1); o.Placement=A.Placement()
def component(n): return d.getObject(('Rigid_' if 'wrappers' in sys.argv else '')+n)
ground=g.newObject('App::FeaturePython','Ground'); JointObject.GroundedJoint(ground,component(plan['ground']))
for row in plan['joints']:
    p=component(row['parent']); q=component(row['child'])
    j=g.newObject('App::FeaturePython',row['name']); JointObject.Joint(j,1 if row['type']=='Revolute' else 0)
    j.Detach1=True; j.Detach2=True
    j.Reference1=(p,['','']); j.Reference2=(q,['',''])
    datum=A.Placement()
    if row['type']=='Revolute': datum=A.Placement(A.Vector(*row['pivot_mm']),A.Rotation(A.Vector(0,0,1),A.Vector(*row['axis'])))
    j.Placement1=p.Placement.inverse()*datum; j.Placement2=q.Placement.inverse()*datum
print('created',len(d.Objects),flush=True)
d.recompute()
print('recomputed',flush=True)
for row in plan['joints']:
    j=d.getObject(row['name']); p=component(row['parent']); q=component(row['child'])
    a=p.Placement*j.Placement1; b=q.Placement*j.Placement2
    assert a.isSame(b,1e-6),(row['name'],str(a),str(b))
print('initial all JCS coincide; limits',[(p,getattr(d.getObject('Rev_FR_Hip'),p)) for p in d.getObject('Rev_FR_Hip').PropertiesList if 'Limit' in p],flush=True)
print('solve',asm.solve(),flush=True)
