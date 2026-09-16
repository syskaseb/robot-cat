"""Build the verified computer-tray increment using FreeCAD's bundled Python.

Does not overwrite v17. Generated BReps are imported by Apply18.FCMacro.
All geometry is in WORLD coordinates (head -X). No hardware dimensions are
inferred from generic servo/PCB envelopes.
"""
from pathlib import Path
import json, math, time
import FreeCAD as App
import Part
from brep_inventory import ROOT, OUT, read_shapes

V = App.Vector
OUT.mkdir(exist_ok=True)
S = read_shapes()
FLIP = App.Placement(V(42,0,0),App.Rotation(V(0,0,1),180))

def global_shape(name):
    s=S[name][0].copy()
    s.Placement=FLIP.multiply(s.Placement)
    return s

def box(x0,x1,y0,y1,z0,z1):
    return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))

def cyl(r,z0,z1,x,y):
    return Part.makeCylinder(r,z1-z0,V(x,y,z0))

def hex_prism(af,z0,z1,x,y):
    r=af/math.sqrt(3)
    points=[V(x+r*math.cos(i*math.pi/3),y+r*math.sin(i*math.pi/3),z0) for i in range(6)]
    return Part.Face(Part.makePolygon(points+[points[0]])).extrude(V(0,0,z1-z0))

def union(items):
    return items[0].multiFuse(items[1:]).removeSplitter() if len(items)>1 else items[0]

def save(name,shape):
    print('validate',name,flush=True)
    assert not shape.isNull() and shape.isValid() and len(shape.Solids)==1, name
    shape.exportBrep(str(OUT/(name+'.brep')))
    b=shape.BoundBox
    return dict(name=name,valid=True,solids=1,volume_mm3=shape.Volume,
                bbox_mm=[b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax])

def main():
    report={'stage':'computer-tray increment; NOT complete print release',
            'source':'25f4a32d966aa4772e87a36725425d4d7b5f60f2',
            'material':'PETG', 'parts':[], 'checks':{},
            'pi_drawing':'https://pip-assets.raspberrypi.com/categories/545-raspberry-pi-4-model-b/documents/RP-008343-DS-1-raspberry-pi-4-mechanical-drawing.pdf'}
    pi_holes=[(x,y) for x in (-15.5,42.5) for y in (-24.5,24.5)]
    mounts=[(x,y) for x in (-12,61) for y in (-36,36)]
    # Original Pi datum and electronics placement are retained.
    ears=[]
    for x,y in mounts:
        # Raised flanges leave room for the receiver above WAVEGO's z=38.52
        # top cover without raising the computer or consuming its HAT reserve.
        ya,yb=(28.5,31.5) if y>0 else (-31.5,-28.5)
        ea,eb=(28.5,41.5) if y>0 else (-41.5,-28.5)
        ears.extend([box(x-5.5,x+5.5,ya,yb,40,47),box(x-5.5,x+5.5,ea,eb,45,47)])
    tray=union([box(-22,69,-31,31,40,42)] +
               [cyl(3.5,40,45,x,y) for x,y in pi_holes] + ears)
    cutters=[cyl(1.45,39,46,x,y) for x,y in pi_holes]
    cutters += [hex_prism(5.3,39.9,42.2,x,y) for x,y in pi_holes]
    cutters += [cyl(1.7,39,48,x,y) for x,y in mounts]
    # Ventilation in the tray; keep the four fixing bosses and perimeter intact.
    cutters += [box(x,x+7,-16,16,39,43) for x in (-6,6,18,30,48)]
    tray=tray.cut(Part.makeCompound(cutters)).removeSplitter()
    report['parts'].append(save('PiTray18',tray))
    # A separate ring carries the removable tray, rather than welding it into
    # the existing shell. Its fixing bosses contain captive M3 hex nuts.
    outer=box(-25,72,-42.5,42.5,39,43)
    inner=box(-19,66,-28,28,38,44)
    frame=union([outer.cut(inner)]+[cyl(5.5,39,45,x,y) for x,y in mounts])
    recess=box(-22.35,69.35,-31.85,31.85,40,48)
    frame=frame.cut(recess)
    nut_slots=[box(x-3.45,x+3.45,30 if y>0 else -36,36 if y>0 else -30,40,42.6) for x,y in mounts]
    frame_cutters=Part.makeCompound([cyl(1.7,38,46,x,y) for x,y in mounts] +
                                   [hex_prism(5.8,40,42.6,x,y) for x,y in mounts] + nut_slots)
    frame=frame.cut(frame_cutters)
    # Preserve only a modest rim; support ring attaches to the existing floor.
    shell=global_shape('BackCover')
    print('fuse receiver with shell',flush=True)
    ear_reliefs=[box(x-5.85,x+5.85,28.15 if y>0 else -41.85,41.85 if y>0 else -28.15,45,47.35) for x,y in mounts]
    modified=shell.fuse(frame).cut(recess).cut(inner).cut(frame_cutters).cut(Part.makeCompound(ear_reliefs)).removeSplitter()
    report['parts'].append(save('BackCover18',modified))
    report['checks']['tray_shell_overlap_mm3']=tray.common(modified).Volume
    report['checks']['tray_pi_overlap_mm3']=tray.common(global_shape('Pi')).Volume
    report['checks']['tray_cooling_overlap_mm3']=tray.common(global_shape('PiHatCooling')).Volume
    # Through-bores checked against complete solids, not only against their bboxes.
    report['checks']['pi_bore_obstructions_mm3']=[tray.common(cyl(1.44,39.9,45.1,x,y)).Volume for x,y in pi_holes]
    report['checks']['tray_bore_obstructions_mm3']=[tray.common(cyl(1.69,39,48,x,y)).Volume for x,y in mounts]
    report['checks']['receiver_bore_obstructions_mm3']=[modified.common(cyl(1.69,38.9,45.1,x,y)).Volume for x,y in mounts]
    report['pi_hole_centres_mm']=pi_holes
    report['tray_fixing_centres_mm']=mounts
    report['fasteners']={'pi':'4 x M2.5, captive hex nuts AF5.3 pockets; choose screw length against actual PCB',
                         'tray':'4 x M3x8 with M3 hex nuts; verify physical engagement before assembly'}
    report['pending']=['microservo model and horn interface', 'printer build volume',
                       'shell segmentation and lid joints', 'remaining electronics mounts and wiring',
                       'chassis/leg dynamic clearances', 'tail 3-vs-4-servo reconciliation',
                       'thermal and physical fit tests']
    (OUT/'tray-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report['checks']),flush=True)
    for name,value in report['checks'].items():
        values=value if isinstance(value,list) else [value]
        assert all(abs(v)<0.001 for v in values), (name,value)

if __name__=='__main__':
    main()
