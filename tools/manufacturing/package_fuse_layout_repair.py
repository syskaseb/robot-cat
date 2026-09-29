"""Package only the working local replacement; do not select it in R5."""
import hashlib
import json
from pathlib import Path
import trimesh
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/fuse-layout-repair-r1'


def main():
    p=json.loads((OUT/'plan.json').read_text())
    checks=json.loads((OUT/'native-checks.json').read_text())
    stl=OUT/'DeckP10_relocated_f_pwm_DIAGNOSTIC_x1.stl'
    assert hashlib.sha256(stl.read_bytes()).hexdigest()==checks['stl_sha256']
    mesh=trimesh.load_mesh(stl)
    assert mesh.is_watertight and len(mesh.split())==1
    size=mesh.extents.tolist()
    assert max(size)+10<=256
    im=Image.new('RGB',(980,650),'#faf8f2'); d=ImageDraw.Draw(im)
    def pt(x,y):return (int(80+3.4*(x+94)),int(40+2.7*(95-y)))
    d.rectangle((*pt(-94,95),*pt(136,-95)),outline='black',width=2)
    d.rectangle((*pt(2.5,11),*pt(39.5,-11)),fill='#c8e1f1',outline='#24577a')
    d.text(pt(2.5,11),'P_REAR above',fill='black')
    for name,r in p['replacements'].items():
        b=r['bbox'];d.rectangle((*pt(b[0],b[4]),*pt(b[3],b[1])),outline='#b84a20',width=3)
        d.text(pt(b[0],b[4]+7),name+' below Deck',fill='#b84a20')
        for x,y in r['tie_slots']:
            d.rectangle((*pt(x-2,y+1),*pt(x+2,y-1)),fill='black')
    d.text((20,585),'Working replacement: 8 new slots; F_HP uses existing4. XY projection, not physical fit.',fill='black')
    d.text((20,612),'PETG / flat Deck / quantity1 replacement. Not selected in R5; wiring and underside fit OPEN.',fill='black')
    im.save(OUT/'preview.png')
    files=[OUT/n for n in ['plan.json','checks.json','native-checks.json','DeckP10RelocatedFPWM.FCStd',stl.name,'preview.png','README.md']]
    files += [ROOT/'tools/cad/fuse_layout_repair_r1.py',ROOT/'tools/cad/deck_f_pwm_relocated_r1.py',Path(__file__)]
    report={'status':'DIAGNOSTIC_REPLACEMENT_NOT_SELECTED', 'new_stl_count':1,'quantity':1,
            'mesh_watertight':True,'components':1,'extents_mm':size,
            'max_extent_plus_10mm_brim_mm':max(size)+10,'slicer_pass':False,'physical_pass':False,
            'files':[{'path':str(f.relative_to(ROOT)).replace('\\','/'),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in files]}
    (OUT/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'files':len(files),'size':size,'watertight':True}))


if __name__=='__main__':main()
