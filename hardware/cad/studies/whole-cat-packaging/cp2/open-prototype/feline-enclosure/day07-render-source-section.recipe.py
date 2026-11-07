from pathlib import Path
import json,html
from PIL import Image,ImageDraw,ImageFont
o=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure');d=json.loads((o/'day07-S0-fixed-cowl-assembly-source-section.json').read_bytes())
im=Image.new('RGB',(1400,920),'#f7f8fa');draw=ImageDraw.Draw(im);font=lambda s:ImageFont.truetype('C:/Windows/Fonts/arial.ttf',s);svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="920" viewBox="0 0 1400 920"><rect width="1400" height="920" fill="#f7f8fa"/>']
def txt(x,y,text,size=20,color='#243242'):
 draw.text((x,y),text,font=font(size),fill=color);svg.append(f'<text x="{x}" y="{y+size}" font-family="Arial" font-size="{size}" fill="{color}">{html.escape(text)}</text>')
txt(32,20,'S0 — FIXED COWL / ASSEMBLY HOLD',28,'#aa202f');txt(32,62,'Actual source geometry, section Y = 0 mm. Candidate only; N01 remains 0/10.',20)
def panel(rect,bounds,title):
 x,y,w,h=rect;x0,x1,z0,z1=bounds;s=min((w-30)/(x1-x0),(h-50)/(z1-z0));ox=x+15;oy=y+h-15
 draw.rectangle([x,y,x+w,y+h],outline='#bac5d2',width=1);svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="#bac5d2"/>');txt(x+12,y+8,title,18)
 def pt(p):return (ox+(p[0]-x0)*s,oy-(p[1]-z0)*s)
 # Clip geometrically by sampling line segments; avoid false drawing outside ROI.
 for row in d['lines']:
  for curve in row['curves_xz_mm']:
   for a,b in zip(curve,curve[1:]):
    dx=b[0]-a[0];dz=b[1]-a[1];lo=0.;hi=1.
    for p,q in [(-dx,a[0]-x0),(dx,x1-a[0]),(-dz,a[1]-z0),(dz,z1-a[1])]:
     if p==0:
      if q<0:hi=-1;break
     elif p<0:lo=max(lo,q/p)
     else:hi=min(hi,q/p)
    if lo>hi:continue
    p1=pt([a[0]+lo*dx,a[1]+lo*dz]);p2=pt([a[0]+hi*dx,a[1]+hi*dz]);draw.line([p1,p2],fill=row['color'],width=2);svg.append(f'<path d="M {p1[0]:.2f} {p1[1]:.2f} L {p2[0]:.2f} {p2[1]:.2f}" stroke="{row["color"]}" fill="none" stroke-width="2"/>')
 wx,wz=d['witness_xz_mm']
 if x0<wx<x1 and z0<wz<z1:
  px,py=pt([wx,wz]);draw.ellipse([px-5,py-5,px+5,py+5],fill='#cc2936');svg.append(f'<circle cx="{px:.2f}" cy="{py:.2f}" r="5" fill="#cc2936"/>')
 txt(x+12,y+h+7,f'X [{x0}, {x1}] mm / Z [{z0}, {z1}] mm',16)
panel((30,105,1340,450),(-145,-5,45,116),'A. Current S0 panel / key, new cowl and preserved AF5 access')
panel((30,605,640,230),(-78,-58,101,110),'B. Same geometry: named AF5 / roof witness')
for i,row in enumerate(d['lines']):txt(710,607+i*29,row['name'].replace('_',' '),17,row['color'])
txt(32,867,'HOLD: allocated AF5 R3.2 x 35 region / new roof common = 0.676878 mm3. Actual tool contact not claimed.',18,'#aa202f')
txt(32,892,'Root patches Y = +/-12 are outside this section. Rear/lateral terminal shielding and skin anchors remain OPEN.',17)
svg.append('</svg>');(o/'day07-S0-fixed-cowl-assembly-source-section.svg').write_bytes(('\n'.join(svg)+'\n').encode());im.save(o/'day07-S0-fixed-cowl-assembly-source-section.png');print('SOURCE_SECTION_PNG_SVG_SAVED')
