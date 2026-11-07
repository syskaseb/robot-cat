from pathlib import Path
import json,html
from PIL import Image,ImageDraw,ImageFont
o=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure');d=json.loads((o/'day07-SOURCE-open-ladder-C1-received-sections-and-next-interface.json').read_bytes());im=Image.new('RGB',(1480,980),'#f7f8fa');dr=ImageDraw.Draw(im);font=lambda s:ImageFont.truetype('C:/Windows/Fonts/arial.ttf',s);svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1480" height="980"><rect width="1480" height="980" fill="#f7f8fa"/>']
def txt(x,y,t,s=18,c='#25384a'):
 dr.text((x,y),t,font=font(s),fill=c);svg.append(f'<text x="{x}" y="{y+s}" font-family="Arial" font-size="{s}" fill="{c}">{html.escape(t)}</text>')
txt(30,16,'SOURCE open ladder C1 — casing cleared / Ankle end-interface HOLD',27,'#ad263c');txt(30,58,'Actual BRep sections. SAME source frame / joints / profiles. Candidate not added to current 1311.',19)
def panel(rect,b,title,rows):
 x,y,w,h=rect;x0,x1,z0,z1=b;scale=min((w-28)/(x1-x0),(h-48)/(z1-z0));ox=x+14;oy=y+h-14;dr.rectangle((x,y,x+w,y+h),outline='#bcc8d3');svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="#bcc8d3"/>');txt(x+10,y+8,title)
 def pt(p):return ox+(p[0]-x0)*scale,oy-(p[1]-z0)*scale
 for row in rows:
  for curve in row['curves']:
   for a,c in zip(curve,curve[1:]):
    dx=c[0]-a[0];dz=c[1]-a[1];lo=0.;hi=1.
    for p,q in [(-dx,a[0]-x0),(dx,x1-a[0]),(-dz,a[1]-z0),(dz,z1-a[1])]:
     if p==0:
      if q<0:hi=-1;break
     elif p<0:lo=max(lo,q/p)
     else:hi=min(hi,q/p)
    if lo>hi:continue
    aa=pt([a[0]+lo*dx,a[1]+lo*dz]);cc=pt([a[0]+hi*dx,a[1]+hi*dz]);dr.line([aa,cc],fill=row['color'],width=2);svg.append(f'<path d="M{aa[0]:.2f},{aa[1]:.2f} L{cc[0]:.2f},{cc[1]:.2f}" fill="none" stroke="{row["color"]}" stroke-width="2"/>')
 txt(x+10,y+h+5,f'Local axial [{x0}, {x1}] / other axis [{z0}, {z1}] mm',15)
panel((30,100,1420,255),(-47,45,-3,10),'A. Transverse = 0: actual supported lower beds and removable pressure fingers',d['sections'][0]['rows'])
panel((30,400,1420,260),(-48,44,-14,10),'B. Normal = 4: continuous side beams, full nominal profiles and current Ankle part',d['sections'][1]['rows'])
panel((30,710,650,180),(-46.5,-37,-11,-2),'C. Same normal = 4, Ankle-facing end enlarged',d['sections'][1]['rows'])
txt(720,716,'Orange: lower printed ladder / green: full profiles',18);txt(720,746,'Purple: real removable pressure half',18,'#8755b5');txt(720,776,'Red: current Ankle part123',18,'#ca293b');txt(720,816,'3D print-corner gap = 1.084631 < 1.25 mm',19,'#ad263c');txt(720,847,'3D witness normal = 6; not inferred from this section.',16)
txt(30,922,'17 members retained; 21 positive junctions. Case058 gap 1.35. 9/10 neighbours separated, 1 clearance HOLD.',18)
txt(30,950,'Full profiles clear neutral + ground END only; continuous motion / selected tie stock / body landing / A,U remain OPEN.',17,'#ad263c');svg.append('</svg>');(o/'day07-SOURCE-open-ladder-C1-received-view.svg').write_bytes(('\n'.join(svg)+'\n').encode());im.save(o/'day07-SOURCE-open-ladder-C1-received-view.png');print('LADDER_SOURCE_VIEW_SAVED')
