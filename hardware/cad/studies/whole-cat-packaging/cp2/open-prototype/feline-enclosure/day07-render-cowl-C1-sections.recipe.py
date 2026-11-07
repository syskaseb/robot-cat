from pathlib import Path
import json,html
from PIL import Image,ImageDraw,ImageFont
out=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure');data=json.loads((out/'day07-S0-cowl-C1-actual-washer-witness-and-sections.json').read_bytes());im=Image.new('RGB',(1480,1060),'#f7f8fa');draw=ImageDraw.Draw(im);font=lambda s:ImageFont.truetype('C:/Windows/Fonts/arial.ttf',s);svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1480" height="1060"><rect width="1480" height="1060" fill="#f7f8fa"/>']
def txt(x,y,t,size=19,col='#26384a'):
 draw.text((x,y),t,font=font(size),fill=col);svg.append(f'<text x="{x}" y="{y+size}" font-size="{size}" font-family="Arial" fill="{col}">{html.escape(t)}</text>')
txt(30,18,'S0 fixed cowl C1 — AF5 port received / rear support HOLD',27,'#ad2431');txt(30,58,'Actual BRep sections. Same case/key/frame. Full AF5 R3.2 x 35 retained. New cowl NOT selected.',20)
def panel(rect,bounds,title,view,witness=False):
 x,y,w,h=rect;x0,x1,z0,z1=bounds;s=min((w-28)/(x1-x0),(h-48)/(z1-z0));ox=x+14;oy=y+h-14
 draw.rectangle([x,y,x+w,y+h],outline='#bdc8d4');svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="#bdc8d4"/>');txt(x+12,y+7,title,18)
 def point(p):return ox+(p[0]-x0)*s,oy-(p[1]-z0)*s
 for row in view['lines']:
  for curve in row['curves_xz_mm']:
   for a,b in zip(curve,curve[1:]):
    dx=b[0]-a[0];dz=b[1]-a[1];lo=0.;hi=1.
    for p,q in [(-dx,a[0]-x0),(dx,x1-a[0]),(-dz,a[1]-z0),(dz,z1-a[1])]:
     if p==0:
      if q<0:hi=-1;break
     elif p<0:lo=max(lo,q/p)
     else:hi=min(hi,q/p)
    if lo>hi:continue
    a1=point([a[0]+lo*dx,a[1]+lo*dz]);b1=point([a[0]+hi*dx,a[1]+hi*dz]);draw.line([a1,b1],fill=row['color'],width=2);svg.append(f'<path d="M{a1[0]:.2f},{a1[1]:.2f} L{b1[0]:.2f},{b1[1]:.2f}" stroke="{row["color"]}" stroke-width="2" fill="none"/>')
 txt(x+12,y+h+6,f'X [{x0}, {x1}] / Z [{z0}, {z1}] mm',15)
panel((30,105,1420,325),(-145,-5,45,116),'A. Y = 0: dedicated AF5 tool port, unchanged operator R15',data['views'][0])
panel((30,480,1420,275),(-145,-75,52,105),'B. Y = -42: actual new rear support and retained PWM washer',data['views'][1])
panel((30,805,640,185),(-99,-90,98.5,101.5),'C. Same Y = -42 section, enlarged',data['views'][1])
txt(710,810,'Orange: new fixed cowl / rear return',18,'#df8219');txt(710,840,'Red: actual retained PWM metal washer',18,'#cb263a');txt(710,870,'Purple: full source AF5 access region',18,'#7c4abb');txt(710,900,'Green: unchanged source operator R15',18,'#1c9981');txt(710,940,'C1 new material / actual washer common = 0.252442 mm3',18,'#ad2431')
txt(30,1020,'C0/C1 preserved. No third offset. Unreceived: 19/32 static, remaining 10 assembly, changed motion. N01 = 0/10.',18,'#ad2431');svg.append('</svg>');(out/'day07-S0-cowl-C1-source-sections.svg').write_bytes(('\n'.join(svg)+'\n').encode());im.save(out/'day07-S0-cowl-C1-source-sections.png');print('C1_SOURCE_SECTIONS_SAVED')
