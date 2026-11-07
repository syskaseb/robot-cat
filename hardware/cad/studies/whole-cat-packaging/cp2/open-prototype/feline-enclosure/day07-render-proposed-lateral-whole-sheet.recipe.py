from pathlib import Path
import json,hashlib,html,math
from PIL import Image,ImageDraw
out=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure');p=out/'day07-SOURCE-lateral-mouth-receiver-layer-assembly-C1-proposal.json';r=json.loads(p.read_bytes());im=Image.new('RGB',(1400,1030),'white');d=ImageDraw.Draw(im);svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="1030"><rect width="1400" height="1030" fill="white"/>']
def txt(x,y,s,c='#222'):
 d.text((x,y),s,fill=c);svg.append(f'<text x="{x}" y="{y+13}" font-family="sans-serif" font-size="13" fill="{c}">{html.escape(s)}</text>')
def ln(pts,c,w=2):
 if len(pts)>1:d.line(pts,fill=c,width=w);svg.append('<polyline fill="none" stroke="'+c+'" stroke-width="'+str(w)+'" points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in pts)+'"/>')
txt(20,15,'SOURCE C1 whole lateral-mouth / receiver-layer / initial-lay hypothesis -- NOT SELECTED / N01 0/10')
txt(20,40,'Plan XY is projected allocation and endpoint graph, not contact proof. New rotation invalidates old48 spatial clearances.')
xy=lambda x,y:(55+(x+140)*4.2,520-(y+25)*3.7)
for n,bb in [('P_SYS_actual',[ [4.55,-1.5],[26.55,35.5]]),('FLG_actual_comb',[[16.125,57.7],[25.125,79.05]]),('BankBed_actual', [[-54.5,39.25],[109,80]])]:
 a,b=bb;ln([xy(a[0],a[1]),xy(b[0],a[1]),xy(b[0],b[1]),xy(a[0],b[1]),xy(a[0],a[1])],'#888');xx,yy=xy(*a);txt(xx,yy-14,n,'#666')
for b in r['six_full_reservoir_branch_plans']:
 x,y,z=b['mouth_upper'];lo=x-12.4650489295-35.1;col='#d67a13' if b['core']!='G' else '#9659bb';ln([xy(lo,y),xy(x,y)],col,4);xx,yy=xy(x,y);txt(xx-45,yy-14,b['wire']+' Y'+str(y),col)
 rc=b['receiver_chain']
 if b['core']!='G':
  P=rc['quarter_P'];R=35.1;pts=[xy(P[0]+R*math.sin(i*math.pi/180),P[1]-R+R*math.cos(i*math.pi/180)) for i in range(91)];ln(pts,'#c82e40' if b['wire']=='W005' else '#d8a36d',3)
 else:
  e=rc['source_actual_free_end'];ln([xy(x,y),xy(e[0],e[1])],'#ab8dbb',1)
for e in r['actual_all9_receiver_end_frames']:
 x,y,z=e['point_mm'];xx,yy=xy(x,y);d.ellipse((xx-3,yy-3,xx+3,yy+3),fill='#16844f');txt(xx+5,yy-12,e['wire']+'/'+e['receiver'],'#16844f')
txt(25,550,'Side: same E55..65 length algebra L_U=125.2..135.2; rotated horizontal mouths. NO new spatial or moving proof.')
xz=lambda x,z:(70+(x+80)*5.6,840-(z+35)*3.1)
for jj,n in enumerate(['W021','W005']):
 b=next(b for b in r['six_full_reservoir_branch_plans'] if b['wire']==n);x,y,zt=b['mouth_upper'];R=35.1;zm=zt-R
 for E,c in [(55,'#d67a13'),(65,'#9a4b08')]:
  dd=(E-(math.pi-2)*R)/2;xc=x-dd;pts=[(x,zt),(xc,zt)]+[(xc-R*math.sin(i*math.pi/180),zm+R*math.cos(i*math.pi/180)) for i in range(181)]+[(x,zt-2*R)];ln([xz(a,b) for a,b in pts],c,2)
 txt(490,615+jj*24,n+' Y'+str(y)+' mouth +X / lower -X')
txt(720,590,'Connected whole graph (OPEN links are explicit):')
for j,s in enumerate(['actual source14 + FL3 owned joints/lands','-> Knee6/Hip3 moving approach OPEN','-> received left9 passage (not terminal)','-> lateral lower inlets / lay-access OPEN','-> six independent E55..65 reservoirs','-> G2 source-defined S fans / D,V portal first gate','-> actual D3/G3/V3 full9 ends','Hip3 10each: independent bypass/stock OPEN','All9 IDs / 12 portions / 4 physical MAX3 retained','Actual deltaL / whole minima / fit / slack NULL']):txt(720,622+j*23,s)
txt(25,900,'FIRST local falsifier: full W005 R35.1 quarter near actual occupied G comb/stock + full current neighbors; no reservoir/print built first.')
txt(25,928,'Full factoryplug / source4ties / MODULEsolderkit / four220 / both4MTA retained; sourceclamps are not loose length-transfer seams.')
txt(25,956,'Current U1 rails/flange/understep/bores/foamC/metal/FHY/root remain. No carrier cut, foreign1.25 or outline3.25 waiver.')
txt(25,984,'No inherited old leg lengths / chord credits / length pooling / physical cut; installed budget remains pending whole connection.')
result=out/'day07-SOURCE-lateral-mouth-C1-current-portal-first-gate.json'
if result.exists():
 f=json.loads(result.read_bytes());q=f['first_falsifier'];txt(1035,350,'ACTUAL C1 PORTAL HOLD','#bc2437');txt(1035,375,'G comb common71.550619 mm3','#bc2437');txt(1035,400,'1/12 received; 11 unreceived','#bc2437');txt(1035,425,'Allocated region, not wire contact','#bc2437');px,py=xy(q['witnesses'][0][0][0],q['witnesses'][0][0][1]);d.ellipse((px-5,py-5,px+5,py+5),fill='#bc2437');svg.append(f'<circle cx="{px}" cy="{py}" r="5" fill="#bc2437"/>')
svg.append('</svg>');png=out/'day07-SOURCE-lateral-mouth-C1-whole-proposal-view.png';im.save(png);png.with_suffix('.svg').write_bytes(('\n'.join(svg)+'\n').encode());print(png)
