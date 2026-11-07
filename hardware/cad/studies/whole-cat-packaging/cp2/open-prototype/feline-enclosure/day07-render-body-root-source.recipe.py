from pathlib import Path
import json,html,math
from PIL import Image,ImageDraw,ImageFont
o=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure');d=json.loads((o/'day07-SOURCE-current-bankbed-material-and-approach-inputs.json').read_bytes());a=json.loads((o/'day07-SOURCE-front-spine-slung-landing-causal-alternative.json').read_bytes())
im=Image.new('RGB',(1440,1140),'#f5f6f8');p=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15);bold=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',24);sv=[]
p.text((25,15),'Whole SOURCE / BankBed: root falsifier and one causal load-interface alternative',font=bold,fill='#152238');p.text((25,51),'Measured source / proposed regions are distinct. No landing bracket built. N01 = 0/10.',font=font,fill='#b32030')
def xy(v):return(75+(v[0]+150)*4,580-(v[1]-20)*4)
def xz(v):return(55+(v[0]+150)*2.5,1015-(v[1]+85)*2.5)
def polyline(pts,c,w=2):
 if len(pts)>1:p.line(pts,fill=c,width=w);sv.append('<polyline fill="none" stroke="'+c+'" stroke-width="'+str(w)+'" points="'+' '.join(f'{x:.3f},{y:.3f}' for x,y in pts)+'"/>')
def box(bounds,project,c,w=2):
 lo,hi=bounds;q=[project((lo[0],lo[1])),project((hi[0],lo[1])),project((hi[0],hi[1])),project((lo[0],hi[1])),project((lo[0],lo[1]))];polyline(q,c,w)
def ordered(curves):
 todo=[list(q) for q in curves];pts=todo.pop(0)
 while todo:
  i,rev=min([(i,rev) for i in range(len(todo)) for rev in [False,True]],key=lambda z:math.dist(pts[-1],todo[z[0]][-1 if z[1] else 0]));q=todo.pop(i);q=list(reversed(q)) if rev else q;assert math.dist(pts[-1],q[0])<1e-4;pts+=q[1:]
 return pts
for w in sorted(d['actual_bottom_face']['contours'],key=lambda q:not q['outer']):
 pts=[xy(q) for q in ordered(w['curves'])];p.polygon(pts,fill='#c5cbd3' if w['outer'] else '#f5f6f8');polyline(pts,'#657183',2)
for q in d['new_moving_attachments']:
 lo,hi=q['world_bounds_mm'];c='#cc8b19' if 'PULL_TEMP' in q['name'] else '#2c6fae' if q['name'].endswith((':lower',':upper')) else '#9661ac';box([[lo[0],lo[1]],[hi[0],hi[1]]],xy,c,1)
box([[-53,68],[-45,76]],xy,'#c92335',4);box([[-54.5,39.25],[-35,46.25]],xy,'#16815c',4);box([[-50,40.25],[-38,45.25]],xy,'#b0359e',2);box([[-53.7,67],[-44.3,77]],xy,'#008e9b',2);polyline([xy(v) for v in [(-44,42.75),(-41,42.75),(-41,72),(-49,72)]],'#b0359e',3)
p.text((75,85),'XY: actual BankBed bottom boundary + proposed moving SOURCE bounds',font=font,fill='#152238')
for x in [-150,-100,-50,0,50,100]:
 xx,yy=xy((x,20));p.text((xx-10,yy+6),str(x),font=small,fill='#4b5362')
for y in [20,40,60,80,100,120,140]:
 xx,yy=xy((-150,y));p.text((xx-35,yy-6),str(y),font=small,fill='#4b5362')
legend=[('Grey','actual BankBed source','#657183'),('Red 8 x 8','rejected root: area0/embed0','#c92335'),('Green 19.5 x 7','actual material136.5mm2','#16815c'),('Blue','actual new SOURCE material','#2c6fae'),('Violet','full-stock proposed bounds','#9661ac'),('Orange','temporary25pull bounds','#cc8b19'),('Magenta','front-spine loadpath NOTBUILT','#b0359e'),('Cyan','open9guide PROPOSED','#008e9b')]
for i,(name,note,c) in enumerate(legend):p.text((1160,140+i*48),name,font=font,fill=c);p.text((1160,162+i*48),note,font=small,fill='#152238')
p.text((30,625),'XZ: actual BankBed section at Y72; moving SOURCE projected bounds are not a contact proof',font=font,fill='#152238')
for line in d['actual_bank_section_y72']['curves_xz']:polyline([xz(q) for q in line],'#657183',3)
for q in d['new_moving_attachments']:
 if not q['name'].endswith((':lower',':upper')):continue
 lo,hi=q['world_bounds_mm'];box([[lo[0],lo[2]],[hi[0],hi[2]]],xz,'#2c6fae',2)
box([[-53,51.5],[-45,52.25]],xz,'#c92335',3);box([[-53.7,38.75],[-44.3,49.25]],xz,'#008e9b',2)
for role,key in [('SOURCE entry','entry_world_mm'),('SOURCE exit','exit_world_mm')]:
 v=d['new_source_frame'][key];x,y=xz((v[0],v[2]));p.ellipse((x-4,y-4,x+4,y+4),fill='#2c6fae');p.text((x+8,y-12),role,font=small,fill='#152238')
for x in [-150,-100,-50,0,50,100]:
 xx,yy=xz((x,-85));p.text((xx-10,yy+7),str(x),font=small,fill='#4b5362')
text=['ACTUAL ROOT FALSIFIER','Foot [-53,-45] x [68,76], Z51.5..52.25:','common0 / contact0 / missing64mm2.','Nearest real material is Y67.75, gap0.25mm.','Current1292 BankBed isSame=true; no Actor0497.','','ONE NEXT LOAD INTERFACE (not built)','Actual front strip136.5mm2 -> 12x5 proposed root','-> 4x4 side drop/arm -> open9guide.','Root embed/full neighbors still REQUIRED.','','Whole coupled scope: 9IDs / 12portions / 4units','FL1: W004 / W020 / W019 continuousSOURCE','FL2: W005 / W022 / W021 continuousSOURCE','FL3: W006 / W024 / W023 SOURCE + DONOR','Knee6 9.4x7.2; Hip3 9.4x3.9; merge9 9.4x10.5','R35.1 / branch V3,D3,G3 / assembly OPEN.','All A/U/fit/slack NULL; no chord as routed length.','850project + MAX3 ceil5(min+20)<=900 preserved.','No physical cut / new splice / bracket / N01 PASS.']
for i,s in enumerate(text):p.text((785,660+i*22),s,font=font if i not in [0,6] else ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',18),fill='#152238' if i not in [0,6] else '#b32030')
im.save(o/'day07-SOURCE-bodylanding-source-and-causal-view.png')
labels=['SOURCEactualBankBedrootFAIL; front-spinealternativeNOTBUILT; N010/10','XY actualsourceboundary; movingattachmentbounds; proposedloadpath only','Redroot8x8 has0contact/embed, missing64; measuredgreenmaterialstrip136.5','Fullmovingcontext25=21operating+4temporary, allsourcepins preserved']
(o/'day07-SOURCE-bodylanding-source-and-causal-view.svg').write_bytes(('<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="1140"><rect width="1440" height="1140" fill="#f5f6f8"/>'+''.join(f'<text x="25" y="{30+25*i}" font-family="Arial" font-size="18">{html.escape(s)}</text>' for i,s in enumerate(labels))+''.join(sv)+'</svg>').encode());print('BODY_ROOT_SOURCE_VIEW_SAVED')
