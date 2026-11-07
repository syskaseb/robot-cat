from pathlib import Path
import json,hashlib,html
from PIL import Image,ImageDraw
out=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure');p=out/'day07-SOURCE-under-bank-side-bay-actual-input-read.json';r=json.loads(p.read_bytes());im=Image.new('RGB',(1450,920),'white');d=ImageDraw.Draw(im);svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1450" height="920"><rect width="1450" height="920" fill="white"/>']
def txt(x,y,s,color='#222'):
 d.text((x,y),s,fill=color);svg.append(f'<text x="{x}" y="{y+13}" font-family="sans-serif" font-size="13" fill="{color}">{html.escape(s)}</text>')
txt(20,12,'SOURCE under-bank side bay / actual current fixed-source sections / NOT SELECTED / N01 0/10')
txt(20,35,'All intersecting valid source operands retained. Wire/stock drawings are context, not automatically rigid obstacles.')
colors={}
for j,yy in enumerate([40,55,75]):
 ox=50;oy=292+j*282;scale=4.8;txt(20,70+j*282,'Y='+str(yy)+' mm; X horizontal, Z vertical')
 for q in r['sections']:
  if q['Y_mm']!=yy:continue
  n=q['name'];col='#cc273a' if 'Ref_Material_P0_' in n else '#2758c8' if any(w in n for w in ['Foundation','U1','Support','BankPad']) else '#1a9253' if 'case' in n.lower() else '#aa65b7'
  colors[n]=col
  for line in q['curves_xz']:
   pts=[(ox+(x+138)*scale,oy-(z+45)*1.95) for x,z in line]
   if len(pts)>1:d.line(pts,fill=col,width=2);svg.append('<polyline fill="none" stroke="'+col+'" points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in pts)+'"/>')
 for x in [-130,-100,-50,0,50,100]:txt(ox+(x+138)*scale,oy+8,str(x))
txt(20,895,'Red actual P0 source; blue supports; green case actors; violet remaining source/stock. Moving parts and group capacity NOT yet qualified.')
svg.append('</svg>');p=out/'day07-SOURCE-under-bank-side-bay-current-sections.png';im.save(p);p.with_suffix('.svg').write_bytes(('\n'.join(svg)+'\n').encode());print(p)
