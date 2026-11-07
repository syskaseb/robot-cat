from pathlib import Path
import json,html
from PIL import Image,ImageDraw,ImageFont
o=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure')
d=json.loads((o/'day07-SOURCE-retention-window-and-input-quality-facts.json').read_bytes())
im=Image.new('RGB',(1280,820),'#f4f5f7');p=ImageDraw.Draw(im)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19);title=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',25)
p.text((28,20),'SOURCE: functional Ankle bay / retention HOLD',font=title,fill='#172238')
p.text((28,60),'Source-derived sections; no new fork or keeper material; N01 = 0/10',font=font,fill='#4b5362')
colors=['#737c88','#b32030','#df8d11'];svg=[]
def plot(q,box,xlim,ylim):
 x0,y0,x1,y1=box
 def xy(v):return (x0+(v[0]-xlim[0])/(xlim[1]-xlim[0])*(x1-x0),y1-(v[1]-ylim[0])/(ylim[1]-ylim[0])*(y1-y0))
 for i,s in enumerate(q):
  for line in s['curves_transverse_normal_mm']:
   a=[xy(v) for v in line]
   if len(a)>1:
    p.line(a,fill=colors[i],width=3);svg.append('<polyline fill="none" stroke="'+colors[i]+'" stroke-width="2" points="'+' '.join(f'{x:.3f},{y:.3f}' for x,y in a)+'"/>')
plot(d['sections'],(60,150,650,510),(-22,18),(-12,14))
p.text((40,110),'Actual section at axial -15 mm',font=font,fill='#172238')
p.text((40,525),'Grey: Link117 / red: purchased case089',font=font,fill='#172238')
p.text((40,553),'Orange: allocated flexible band return',font=font,fill='#a16a08')
p.text((40,581),'Common 20.020107 mm3 rejects THIS allocation.',font=font,fill='#b32030')
p.text((40,609),'Not proof that every manual band path collides.',font=font,fill='#172238')
# Exact rounded opening was tested by native Face.cut; this drawing is its bounds only.
x0,y0=830,175;scale=22
p.rectangle((x0,y0,x0+6*scale,y0+12*scale),outline='#737c88',width=3)
for cy in [4,8]:p.rectangle((x0+1.35*scale,y0+(cy-1)*scale,x0+4.65*scale,y0+(cy+1)*scale),outline='#087b58',width=4)
p.text((735,110),'Actual Link117 opening: bounds 6 x 12 mm',font=font,fill='#172238')
p.text((735,465),'2 full-capacity feeds: 3.3 x 2 mm each',font=font,fill='#087b58')
p.text((735,493),'Exact footprint outside opening: 0 / 0 mm2',font=font,fill='#087b58')
p.text((735,521),'4/4 actual nearby pairs; min gap 7.462685',font=font,fill='#087b58')
p.text((735,549),'Window feed only: whole loop/loadpath OPEN',font=font,fill='#b32030')
for y,t in [(665,'Continuous Ankle covers 0..74.2114 deg: 3 profiles min lower bound 3.117330 mm.'),(695,'4 heads + 4 pull fields + 2 tail fields separated; 12 loop-cover HOLD rows are NOT contacts.'),(725,'145 / 145 / 100 / 100 required incl. pull once: 118.757 / 113.400 / 72.300 / 74.700 mm.'),(755,'NEXT: slot-bearing whole retention; prove complete feeds/loops/heads/tails before fork material.')]:p.text((28,y),t,font=font,fill='#172238')
im.save(o/'day07-SOURCE-Ankle-bay-retention-received-view.png')
texts=['Source-derived actual section: axial -15 mm','Grey Link117; red case089; orange flexible band allocation','Common20.020107: allocation HOLD, not all handlay impossible','Full profiles continuous lower bound3.117330; 12 conservative loop rows OPEN','Actual native window6x12 / two3.3x2 feeds: exact outside area0/0','NEXT whole slot-bearing retention. No fork/keeper built. N010/10']
body=''.join(f'<text x="28" y="{40+i*28}" font-family="Arial" font-size="19">{html.escape(t)}</text>' for i,t in enumerate(texts))
(o/'day07-SOURCE-Ankle-bay-retention-received-view.svg').write_bytes(('<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="820" viewBox="0 0 1280 820"><rect width="1280" height="820" fill="#f4f5f7"/>'+body+''.join(svg)+'</svg>').encode())
print('RECEIVED_VIEW_SAVED')
