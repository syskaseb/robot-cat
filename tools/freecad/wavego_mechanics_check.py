"""FreeCAD MCP inspection of the mechanical prototype, not print certification."""
import json
import math
from pathlib import Path
import FreeCAD as App
import Part

try:
    import FreeCADGui as Gui
except ImportError:  # headless: presentation() is unavailable, check() is not
    Gui = None

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'hardware/wavego/mechanics'
LAYOUT = ROOT / 'hardware/wavego/layout'
helper = ROOT / 'tools/freecad/wavego_layout_analysis.py'
ns = {'__file__': str(helper), '__name__': 'measurement_helpers'}
exec(compile(helper.read_text(encoding='utf-8'), str(helper), 'exec'), ns)
world_shape, bounds, overlap = (ns[k] for k in ('world_shape','bounds','overlap'))

def inputs(doc):
    assert doc.Name == 'WAVEGO_cat_mechanical', 'Use the mechanical copy only'
    data = json.loads((OUT/'components.json').read_text(encoding='utf-8'))
    mapping = json.loads((LAYOUT/'object-map.json').read_text(encoding='utf-8'))
    parts = {o.Name:o for o in doc.Objects
             if o.TypeId in ('PartDesign::Body','Part::Feature') and o.Name.startswith('CAT_')}
    comp = {c['id']:doc.getObject(mapping[c['id']]) for c in data['components']}
    missing = [k for k,v in comp.items() if v is None]
    if not parts or missing:
        raise RuntimeError('Run tools/freecad/wavego_cat_shell.py first; '
                           'the document is missing generated parts or envelopes: '
                           + str(missing))
    return data, parts, comp

def presentation(doc, mode='closed'):
    data, parts, comp = inputs(doc)
    group = doc.getObject('CatMechanicalParts') or doc.addObject('App::DocumentObjectGroup','CatMechanicalParts')
    group.Label = 'CAT - mechanical prototype / NOT released for printing'
    for name,o in parts.items():
        group.addObject(o)
        color = (0.23,0.27,0.30)
        if name=='CAT_Face_Mask': color=(0.82,0.79,0.70)
        if name in ('CAT_Neck_Load_Frame','CAT_Tail_Mount','CAT_Camera_Carrier'):color=(0.38,0.41,0.44)
        for view in [v for v in (o.ViewObject, getattr(o,'Tip',None) and o.Tip.ViewObject) if v]:
            view.ShapeColor=color
            view.LineColor=(0.10,0.12,0.13)
            view.Transparency=0
            view.DisplayMode='Flat Lines'
        for prop,value in [('Material','PETG - proposed colour; slicer settings not validated'),
                           ('ReleaseStatus','PROTOTYPE: fixed head/tail; actuator adapters and DFM pending')]:
            if prop not in o.PropertiesList:o.addProperty('App::PropertyString',prop,'Mechanical design')
            setattr(o,prop,value)
        o.Visibility = not (mode=='open' and name in ('CAT_Spine_Front','CAT_Spine_Rear','CAT_Face_Mask'))
    for cid,o in comp.items():
        o.Visibility = mode=='open' or cid in ('Camera','IR','ToF')
        if cid in ('Camera','IR','ToF'):
            for v in [v for v in (o.ViewObject, getattr(o,'Tip',None) and o.Tip.ViewObject) if v]:
                v.ShapeColor=(0.055,0.07,0.08)
                v.Transparency=0
    for o in doc.Objects:
        if o.TypeId=='Sketcher::SketchObject' or o.Name.startswith(('X_Axis','Y_Axis','Z_Axis','XY_Plane','XZ_Plane','YZ_Plane','Origin','Axis_')):
            o.Visibility=False
        if o.Name in ('Backpack_envelope___NOT_a_printable_shell','Head_envelope___NOT_a_printable_shell','CameraFOV','CameraMountPattern','StudyMountingAxes'):
            o.Visibility=False
    for label in ('TopCover','Part9','Part001'):
        for o in doc.getObjectsByLabel(label):o.Visibility=False
    if hasattr(Gui,'Snapper') and getattr(Gui.Snapper,'grid',None):Gui.Snapper.grid.off()
    doc.Label='WAVEGO CAT - mechanical prototype - front minus X'
    doc.recompute()

def check(doc, gait=False):
    data, parts, comp = inputs(doc)
    source_count=ns['verify_source'](doc)
    shapes={k:world_shape(o) for k,o in parts.items()}
    cs={k:world_shape(o) for k,o in comp.items()}
    base=json.loads((LAYOUT/'measurements.json').read_text(encoding='utf-8'))
    original=[(doc.getObject(p['name']),world_shape(doc.getObject(p['name']))) for p in base['parts']]
    original=[(o,s) for o,s in original if o.Label not in ('TopCover','Part9','Part001')]
    geometry={k:{'valid':s.isValid(),'solids':len(s.Solids),'bbox':bounds(s),'volume_mm3':round(s.Volume,2)} for k,s in shapes.items()}
    pairs=[]
    contact=[]
    for i,(a,sa) in enumerate(shapes.items()):
        for b,sb in list(shapes.items())[i+1:]:
            vol=overlap(sa,sb)
            if vol>0.001:pairs.append([a,b,round(vol,3)])
            gap=sa.distToShape(sb)[0]
            if gap<0.01:contact.append([a,b,round(gap,4)])
    source_hits=[]
    component_hits=[]
    for name,s in shapes.items():
        for o,t in original:
            v=overlap(s,t)
            if v>0.001:source_hits.append([name,o.Label,round(v,3)])
        for cid,t in cs.items():
            v=overlap(s,t)
            if v>0.001:component_hits.append([name,cid,round(v,3)])
    mismatch=[]
    for c in data['components']:
        expected=c['min']+[a+b for a,b in zip(c['min'],c['size'])]
        if any(abs(a-b)>0.01 for a,b in zip(expected,bounds(cs[c['id']]))):mismatch.append(c['id'])
    joints=[]
    shell = ROOT/'tools/freecad/wavego_cat_shell.py'
    gen = {'__file__': str(shell), '__name__': 'cat_shell_probes'}
    exec(compile(shell.read_text(encoding='utf-8'), str(shell), 'exec'), gen)
    for probe in gen['bore_probes']():
        hits=[]
        for p in probe['points']:
            cyl=Part.makeCylinder(probe['diameter']/2.0, probe['length'],
                                  App.Vector(*p), App.Vector(*probe['axis']))
            for target in probe['parts']:
                v=overlap(cyl,shapes[target])
                if v>0.001:hits.append([target,p,round(v,3)])
        joints.append(dict(name=probe['name'],parts=probe['parts'],
                           axes=probe['points'],axis_direction=list(probe['axis']),
                           bore_probe_length=probe['length'],
                           shaft_diameter=probe['diameter'],blocked_bores=hits))
    gait_hits=[]
    if gait:
        path=ROOT/'tools/freecad/WAVEGO_Motion.FCMacro'
        definitions=path.read_text(encoding='utf-8').rsplit('\ndoc = App.ActiveDocument',1)[0]
        motion={}
        exec(compile(definitions,str(path),'exec'),motion)
        for i in range(25):
            angles=motion['trot_angles'](i/25)
            for o,s in original:
                parents=ns['parents'](o)
                for leg,spec in motion['LEGS'].items():
                    chain=[j for j in ('Hip','Knee','Ankle') if f'Motion_{leg}_{j}' in parents]
                    if not chain:continue
                    t=App.Placement()
                    for j in chain:
                        idx=('Hip','Knee','Ankle').index(j)
                        t=t.multiply(ns['rotation'](spec['pivots'][idx],spec['axes'][idx],angles[leg][idx]))
                    moved=s.copy();moved.Placement=t.multiply(s.Placement)
                    for name,shape in shapes.items():
                        v=overlap(moved,shape)
                        if v>0.001:gait_hits.append([i/25,o.Label,name,round(v,3)])
    result=dict(source_parts_unchanged=source_count,geometry=geometry,part_intersections=pairs,
                contact_pairs=contact,source_hits=source_hits,component_envelope_hits=component_hits,
                manifest_mismatch=mismatch,joints=joints,gait_phases=25 if gait else 0,gait_hits=gait_hits,
                limits=['Head is carried on a pan-servo reserve and the tail is tendon driven; neither actuator is a purchased-part model.',
                        'PCB envelopes are not purchased-part CAD; unspecified module mounts remain pending.',
                        'Bore probes test void continuity, not thread engagement, strength or tool access.',
                        'Ventilation openings are geometry only: no airflow, CFD or thermal measurement was made.',
                        'No load, mass distribution, thermal, cable fatigue or slicer certification.'])
    (OUT/'validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result))
    return result
