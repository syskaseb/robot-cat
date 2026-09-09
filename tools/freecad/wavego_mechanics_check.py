"""FreeCAD MCP inspection of the mechanical prototype, not print certification."""
import json
import math
from pathlib import Path
import FreeCAD as App
import FreeCADGui as Gui
import Part

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
    parts = {o.Name:o for o in doc.Objects if o.TypeId=='PartDesign::Body' and o.Name.startswith('CAT_')}
    comp = {c['id']:doc.getObject(mapping[c['id']]) for c in data['components']}
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
        for view in (o.ViewObject,o.Tip.ViewObject):
            view.ShapeColor=color
            view.LineColor=(0.10,0.12,0.13)
            view.Transparency=0
            view.DisplayMode='Flat Lines'
        for prop,value in [('Material','PETG - proposed colour; slicer settings not validated'),
                           ('ReleaseStatus','PROTOTYPE: fixed head/tail; actuator adapters and DFM pending')]:
            if prop not in o.PropertiesList:o.addProperty('App::PropertyString',prop,'Mechanical design')
            setattr(o,prop,value)
        o.Visibility = not (mode=='open' and name in ('CAT_Back_Lid','CAT_Face_Mask'))
    for cid,o in comp.items():
        o.Visibility = mode=='open' or cid in ('Camera','IR','ToF')
        if cid in ('Camera','IR','ToF'):
            for v in (o.ViewObject,o.Tip.ViewObject):
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
    def joint(name,targets,points,axis,length,shaft_radius):
        hits=[]
        for p in points:
            probe=Part.makeCylinder(shaft_radius,length,App.Vector(*p),App.Vector(*axis))
            for target in targets:
                v=overlap(probe,shapes[target])
                if v>0.001:hits.append([target,p,round(v,3)])
        joints.append(dict(name=name,parts=targets,axes=points,axis_direction=axis,
                           bore_probe_length=length,shaft_diameter=2*shaft_radius,blocked_bores=hits))
    joint('lid to body',['CAT_Base_Chassis_Tray','CAT_Back_Lid'],[[x,y,122] for x in (-102,134) for y in (-66,66)],(0,0,1),10,1.5)
    joint('neck to front chassis',['CAT_Base_Chassis_Tray','CAT_Neck_Load_Frame'],[[x,y,37.02] for x in (-80,-70) for y in (-22.5,22.5)],(0,0,1),6.4,1.25)
    joint('tail bracket to rear chassis',['CAT_Base_Chassis_Tray','CAT_Tail_Mount'],[[x,y,37.02] for x in (112,122) for y in (-22.5,22.5)],(0,0,1),6.4,1.25)
    joint('head to neck',['CAT_Head_Shell','CAT_Neck_Load_Frame'],[[-107,y,z] for y in (-23,23) for z in (154,207)],(1,0,0),17,1.5)
    joint('face to head',['CAT_Face_Mask','CAT_Head_Shell'],[[-188.4,y,z] for y in (-47,47) for z in (166,194)],(1,0,0),14.4,1.5)
    joint('camera carrier to head floor',['CAT_Camera_Carrier','CAT_Head_Shell'],[[x,25,139] for x in (-158,-119)],(0,0,1),5.4,1.5)
    joint('tail to bracket',['CAT_Tail','CAT_Tail_Mount'],[[169,y,109] for y in (-9,9)],(1,0,0),15,1.5)
    joint('camera PCB pattern',['CAT_Camera_Carrier'],[[-168,y,z] for y in (7.5,28.5) for z in (174.6,187.1)],(1,0,0),5.2,1.0)
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
                limits=['Fixed mechanical prototype: neck/tail not actuated.',
                        'PCB envelopes are not purchased-part CAD; unspecified module mounts remain pending.',
                        'Bore probes test void continuity, not thread engagement, strength or tool access.',
                        'No load, mass distribution, thermal, cable fatigue or slicer certification.'])
    (OUT/'validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result))
    return result
