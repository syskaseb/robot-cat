from pathlib import Path
import json,html
from PIL import Image,ImageDraw,ImageFont
o=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure');d=json.loads((o/'day07-SOURCE-slot-carrier-first-material.json').read_bytes());final=json.loads((o/'day07-SOURCE-slot-crosshead-functional-grooves.json').read_bytes());d['sections']=final['sections'];d['status']=final['status'];f=json.loads((o/'day07-SOURCE-slot-full-stock-completion.json').read_bytes());b=json.loads((o/'day07-SOURCE-slot-whole-tail-bearing-gate.json').read_bytes())
im=Image.new('RGB',(1440,900),'#f5f6f8');p=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15);title=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',24)
p.text((25,15),'SOURCE native-window clamp + sidecar tray: actual received sections',font=title,fill='#152238');p.text((25,53),d['status']+' / NOT SELECTED / N01 0/10',font=font,fill='#b32030')
names=['actual_Link117','new_lower_sidecar','new_pressure_roof','full3_source_profiles','full4_selected_loops'];colors=['#7d8591','#2470ba','#16816b','#d57a00','#8e37ac'];sv=[]
for i,u in enumerate(sorted({s['axial_mm'] for s in d['sections']})):
 x0=45+i*475;y0=145;x1=x0+420;y1=650
 def xy(v):return(x0+(v[0]+8)/34*(x1-x0),y1-(v[1]+6)/36*(y1-y0))
 p.text((x0,105),'Axial u = '+str(round(u,6))+' mm',font=font,fill='#152238');p.rectangle((x0,y0,x1,y1),outline='#c7cdd7')
 for s in d['sections']:
  if s['axial_mm']!=u:continue
  c=colors[names.index(s['name'])]
  for line in s['curves']:
   pts=[xy(v) for v in line]
   if len(pts)>1:p.line(pts,fill=c,width=3);sv.append('<polyline fill="none" stroke="'+c+'" stroke-width="2" points="'+' '.join(f'{x:.3f},{y:.3f}' for x,y in pts)+'"/>')
 for v in [-5,0,5,10,15,20,25]:
  x,y=xy([v,-6]);p.text((x-5,y+6),str(v),font=small,fill='#3f4c60')
 for n in [0,5,10,15,20,25]:
  x,y=xy([-8,n]);p.text((x-25,y-8),str(n),font=small,fill='#3f4c60')
for i,(n,c) in enumerate(zip(['Actual Link117','New lower sidecar','New pressure roof','Full 3 source profiles','Full 4 selected loops'],colors)):
 x=25+i*280;p.rectangle((x,700,x+15,715),fill=c);p.text((x+21,696),n,font=font,fill='#152238')
lines=['Band / real Link bearing areas: '+', '.join(f"{q['projected_common_area_mm2']:.6f}" for q in b['actual_bearing'])+' mm2; bought link never fused.',
       'Complete stock foreign matrix: '+str(f['complete_matrix_count'])+' received, 0 missing; conservative Ankle cover scope only, not whole N09.',
       '145 / 145 / 100 / 100 required (loop +25 once): '+ ' / '.join(f"{q['required_mm']:.3f}" for q in b['all4_units'])+' mm.',
       'Material: '+str(len(d['intended_member_coverage']))+' intended members / '+str(sum(q['positive'] for q in d['positive_junctions']))+'/'+str(len(d['positive_junctions']))+' positive joints; '+('member gate received' if d['material_ok'] else 'material gate HOLD')+'.',
       'Remaining: material/stock gate as named above; bodylanding + all9 SOURCE transports/physical budgets + initial assembly/motion/outline OPEN.']
for i,line in enumerate(lines):p.text((25,735+i*29),line,font=font,fill='#152238')
im.save(o/'day07-SOURCE-slot-retention-received-view.png');text=''.join(f'<text x="25" y="{35+i*28}" font-family="Arial" font-size="18">{html.escape(s)}</text>' for i,s in enumerate([d['status'],'Actualsections; greyLink/blueLower/greenRoof/orangeProfiles/violetLoops; NOTselected']));(o/'day07-SOURCE-slot-retention-received-view.svg').write_bytes(('<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="900"><rect width="1440" height="900" fill="#f5f6f8"/>'+text+''.join(sv)+'</svg>').encode());print('SLOT_RECEIVED_VIEW_SAVED')
