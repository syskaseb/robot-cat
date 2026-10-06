"""Diagnostic sections of ONE rejected proposal, not another CAD variant."""
from pathlib import Path
import hashlib
import json
import math
import sys

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2'
DATA=BASE/'service-zone-sections.json'


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def extract():
    import FreeCAD as A
    import Part
    native=BASE/'BoardDatumCandidate.FCStd'
    assert not DATA.exists(), 'Receive existing sections instead'
    gate=json.loads((BASE/'service-zone-gate.json').read_text(encoding='utf-8'))
    assert digest(native)==gate['source_sha256'][native.relative_to(ROOT).as_posix()]
    d=A.openDocument(str(native));sections=[]
    try:
        for x in [-24,11,43]:
            points=[A.Vector(x,y,z) for y,z in [(-130,-20),(130,-20),(130,200),(-130,200),(-130,-20)]]
            plane=Part.Face(Part.makePolygon(points));curves={}
            for name in ['TorsoEnvelope','W076_EXTENSION_CP2']:
                shape=d.getObject(name).Shape
                assert shape.isValid()
                cut=shape.section(plane);assert cut.isValid()
                curves[name]=[[[p.y,p.z] for p in e.discretize(Deflection=.1)] for e in cut.Edges]
            sections.append(dict(x_mm=x,curves=curves))
        DATA.write_text(json.dumps(dict(source_native_sha256=digest(native),
            selected=False,physical_pass=False,sections=sections,
            projection_is_not_collision_proof=True),indent=2)+'\n',encoding='utf-8')
        print('3 native cross-sections extracted; no source save',flush=True)
    finally:A.closeDocument(d.Name)


def render():
    from PIL import Image,ImageDraw,ImageFont
    output=BASE/'service-zone-sections.png'
    assert not output.exists() or '--refresh-render' in sys.argv
    data=json.loads(DATA.read_text(encoding='utf-8'))
    gate=json.loads((BASE/'service-zone-gate.json').read_text(encoding='utf-8'))
    rows=json.loads((BASE/'service-zone-inventory.json').read_text(encoding='utf-8'))['components']
    image=Image.new('RGB',(1590,1030),'#fafafa');draw=ImageDraw.Draw(image)
    fonts=[ImageFont.truetype('C:/Windows/Fonts/arial.ttf',s) for s in [14,19,26]]
    draw.text((32,22),'CP2: wspólna kontrola strefy obsługi — wariant ODRZUCONY',fill='#222222',font=fonts[2])
    draw.text((32,62),'Bez zmiany wybranego R53. Kontury: przekrój BRep; prostokąty: rezerwacje; łuki: tylko początki przewodów.',fill='#444444',font=fonts[1])
    for index,section in enumerate(data['sections']):
        left=35+index*520;top=165;scale=1.9;x=section['x_mm']
        def p(y,z):return (left+(y+125)*scale,top+(200-z)*scale)
        draw.text((left,120),f'Przekrój X = {x} mm',fill='#222222',font=fonts[1])
        for y in range(-100,101,50):
            draw.line([p(y,-10),p(y,190)],fill='#dddddd');draw.text(p(y,-18),str(y),fill='#555555',font=fonts[0])
        for z in range(0,181,30):
            draw.line([p(-120,z),p(120,z)],fill='#dddddd');draw.text((left,p(0,z)[1]-17),str(z),fill='#555555',font=fonts[0])
        draw.text((left+205,590),'Y [mm]',fill='#444444',font=fonts[1])
        for row in rows:
            name=row['name'];b=list(row['bounds_mm'])
            if '_CP2' not in name or name.startswith(('Access_','W','XA','XT','Splice','Post','S0','S1')):continue
            if not b[0]<=x<=b[3]:continue
            revised=name in gate['changed_names']
            if revised:
                draw.rectangle([p(b[1],b[5]),p(b[4],b[2])],outline='#b9b9b9',width=1)
                if name.startswith('F_L'):b[1]+=2.5;b[4]+=2.5
                elif name.startswith('F_R'):b[2]+=12;b[5]+=12
                else:
                    delta=21 if name.startswith(('FL_','RL_','D_FL')) else 10
                    b[2]-=delta;b[5]-=delta
            if name in {r['name'] for r in gate['outside']}:color='#cf3535'
            else:color='#c9792b' if revised else '#587c99'
            draw.rectangle([p(b[1],b[5]),p(b[4],b[2])],outline=color,width=2)
            label=name.replace('_CP2','').replace('_Housing','').replace('_ATO',' ATO')
            draw.text(p(b[1],b[5]),label,fill=color,font=fonts[0])
        for name,curves in section['curves'].items():
            for curve in curves:
                draw.line([p(*q) for q in curve],fill='#242424' if name=='TorsoEnvelope' else '#bf3b32',width=3)
        for end in gate['terminal_escapes']:
            if abs(end['mouth_mm'][0]-x)>1e-5:continue
            points=[]
            for seg in end['segments']:
                if seg['kind']=='line':points.extend([seg['start_mm'],seg['end_mm']])
                else:
                    a=seg['start_mm'];u=seg['start_tangent'];v=seg['end_tangent'];r=seg['radius_mm']
                    points.extend([[a[k]+r*u[k]*math.sin(t)+r*v[k]*(1-math.cos(t)) for k in range(3)] for t in [i*math.pi/80 for i in range(41)]])
            draw.line([p(q[1],q[2]) for q in points],fill='#8c458b',width=5)
            draw.text(p(points[-1][1],points[-1][2]-9),end['wire_id'],fill='#8c458b',font=fonts[0])
    notes=['Czerwony kontur: źródłowy W076; czerwone prostokąty: części wychodzące poza tułów.',
        'W035 i W054: przecięcia z W076 potwierdzone przez BRep, nie przez ten rysunek.',
        'Podnoszenie prawego banku narusza zakrzywiony dach; obniżanie lewych WAGO narusza dolny bok.',
        'Nie tworzyć mocowań tej propozycji. Następny plan musi zmienić orientację banku lub strefę źródła jako całość.',
        'Tułów 325×200×160 mm pozostaje. Każdy docelowy wydruk: 256³ mm wraz z potrzebnym zapasem.',
        'Brak pełnych tras, odciążeń i dowodu ruchu pokrywy FHAC; to nie ukończenie W1/W5 ani fizyczny PASS.']
    for i,note in enumerate(notes):draw.text((35,690+i*44),note,fill='#444444',font=fonts[1])
    image.save(output);print(output,flush=True)


if __name__=='__main__':
    render() if '--render' in sys.argv else extract()
