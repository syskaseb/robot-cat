from pathlib import Path
import json,html
from PIL import Image,ImageDraw
o=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure');d=json.loads((o/'day07-D15-current-binding-and-receiver-context-sections.json').read_bytes())
im=Image.new('RGB',(1500,1240),'white');dr=ImageDraw.Draw(im);svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="1240"><rect width="1500" height="1240" fill="white"/>']
def txt(x,y,s,c='#222'):
 dr.text((x,y),s,fill=c);svg.append(f'<text x="{x}" y="{y+13}" font-family="sans-serif" font-size="14" fill="{c}">{html.escape(s)}</text>')
def col(n,k):
 if n.startswith('G4C1capacity:'):return '#d8a151'
 if n.startswith('G4C1:'):return '#d47f00'
 if n=='Station:D_FL:case' or n.startswith('CurrentDFL:'):return '#176430'
 if n=='Station:D_FR:case' or n.startswith('D_FR:first9:'):return '#325d98'
 if 'S0_' in n or n.startswith('S0:'):return '#7c3d86'
 if n=='Station:P_SYS:case':return '#9b3916'
 if k=='moving_neutral_only':return '#dbc0c7'
 return '#b1b7bd'
txt(20,10,'CURRENT RECEIVER-SIDE NATIVE SECTIONS / D1-D5 PROJECT FRAME BINDING / G4 PROPOSED / N01 0/10')
panels=[('G4_XY_Z45p52',40,570,3.0,[-145,-62]),('D3_XZ_Yminus16p25',40,1090,2.5,[-145,-35]),('V2_YZ_Xminus16',870,1090,2.5,[-62,-35])]
for vn,ox,oy,s,lo in panels:
 v=next(q for q in d['sections'] if q['name']==vn);txt(ox,45 if vn.startswith('G4') else 700,vn+' actual section; no projection contact inference')
 curves=sorted(v['actor_curves'],key=lambda q:col(q['actor'],q['kind'])!='#b1b7bd')
 for a in curves:
  c=col(a['actor'],a['kind']);width=1 if c in ['#b1b7bd','#dbc0c7'] else 2
  for line in a['curves']:
   pts=[(ox+(p[0]-lo[0])*s,oy-(p[1]-lo[1])*s) for p in line]
   if len(pts)>1:dr.line(pts,fill=c,width=width);svg.append('<polyline fill="none" stroke="'+c+'" stroke-width="'+str(width)+'" points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in pts)+'"/>')
 if vn.startswith('G4'):
  for n,p in [('D1/W002',[57.5,-25.75]),('D5/W007',[57.5,-6.75]),('P_SYS',[15,14]),('newG4',[32.5,68]),('S0',[-110,0]),('LEFT9passage',[-132.75,58])]:
   x=ox+(p[0]-lo[0])*s;y=oy-(p[1]-lo[1])*s;dr.ellipse((x-3,y-3,x+3,y+3),fill='#d02020');txt(x+5,y,n,'#a51010')
txt(1135,90,'COLORS:')
for i,(s,c) in enumerate([('green: D_FL actual5clamp','#176430'),('orange: exactG4C1/newstock','#d47f00'),('blue: current D_FR','#325d98'),('purple: S0 body/key','#7c3d86'),('brown: P_SYS case','#9b3916'),('grey: retained actual context','#999999'),('pink: moving neutral ONLY','#c090a0')]):txt(1135,120+i*35,s,c)
for i,s in enumerate(['D1port [57.5,-25.75,48.5], D5port [57.5,-6.75,48.5]; both held9+.25 endX65.980362/Z51.625242.', 'D_FR currentcase [19,-.5,-13]..[49,18.5,-4]; first9 currentports Y-.5/Z-8.5. OldW007D_FR worlddatum is stale.', 'Sections show actual occupied material only at three planes; apparent white regions are NOT proven connected free space.', 'SourceKnee6/Hip3/leftpassage and separate D3/G3/V3 freefan need full R35.1/stock/assembly proof; no new wire geometry built.']):txt(20,1140+i*21,s)
svg.append('</svg>');p=o/'day07-D15-actual-receiver-layer-sections.png';im.save(p);p.with_suffix('.svg').write_bytes(('\n'.join(svg)+'\n').encode());print(p)
