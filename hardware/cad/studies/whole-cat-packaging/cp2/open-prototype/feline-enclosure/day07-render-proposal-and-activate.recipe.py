from pathlib import Path
import json,html,hashlib,os
from PIL import Image,ImageDraw,ImageFont
root=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical');out=root/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure';d=json.loads((out/'day07-whole-SOURCE-Knee-link-proposal-view.json').read_bytes());p=out/'day07-whole-physical-SOURCE-approach-Knee-link-proposal.json';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
im=Image.new('RGB',(1480,960),'#f7f8fa');dr=ImageDraw.Draw(im);font=lambda s:ImageFont.truetype('C:/Windows/Fonts/arial.ttf',s);svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1480" height="960"><rect width="1480" height="960" fill="#f7f8fa"/>']
def text(x,y,s,sz=19,col='#233448'):
 dr.text((x,y),s,font=font(sz),fill=col);svg.append(f'<text x="{x}" y="{y+sz}" font-family="Arial" font-size="{sz}" fill="{col}">{html.escape(s)}</text>')
def line(points,col,w=2):
 dr.line(points,fill=col,width=w);svg.append('<polyline points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in points)+f'" fill="none" stroke="{col}" stroke-width="{w}"/>')
def rect(box,col,w=2):
 x,y,x1,y1=box;dr.rectangle(box,outline=col,width=w);svg.append(f'<rect x="{x}" y="{y}" width="{x1-x}" height="{y1-y}" fill="none" stroke="{col}" stroke-width="{w}"/>')
text(28,18,'WHOLE PHYSICAL SOURCE — one Knee-owned holder / grouped moving approach',25);text(28,58,'PROPOSAL, NOT selected. Actual link face below; contact, tie access and whole regions remain gates.',19,'#a35c12')
point=lambda p:(740+p[0]*12,340-p[1]*8)
for c in d['actual_face_curves_axis_transverse_mm']:line([point(p) for p in c],'#60788d')
a=point([-43,7]);b=point([43,-7]);rect((a[0],a[1],b[0],b[1]),'#dd861a');text(90,115,'Actual Link117 outer face, in its own plane',19,'#60788d');text(90,145,'Orange: proposed 86 x 14 mm holder footprint',19,'#dd861a')
for v in [-15,15]:
 a=point([v-2,2]);b=point([v+2,-2]);rect((a[0],a[1],b[0],b[1]),'#b62a43',3)
text(90,505,'FIRST: 2 actual 4 x 4 mm contact pads + 2 selected T18I145 structural tie feed paths; no fusion to link.',19)
nodes=[(35,570,260,85,'FL1: SOURCE/FL1, 3 cores','Hip-owned factory plug intact'),(35,685,260,100,'FL2: SOURCE/FL2, 3 cores','Knee-owned continuous'),(35,815,260,105,'FL3 original + donor, 3+3','86 mm / 3 laps / 2 lands'),(365,685,265,100,'Knee6 + Hip3 merge','9.4 x 10.5 group / R35.1'),(700,685,270,100,'Fixed body landing9','BankBed1 underside; root OPEN'),(1060,570,370,85,'V3: W020 / W022 / W024','7.2 x 2.8 to existing full ends'),(1060,690,370,85,'D3: W004 / W005 / W006','10.5 x 3.9 to D_FL.2/.3/.4'),(1060,810,370,85,'G3: W019 / W021 / W023','10.5 x 3.9 to FL_G.2/.3/.4')]
for x,y,w,h,title,desc in nodes:rect((x,y,x+w,y+h),'#8fa2b4');text(x+10,y+10,title,18);text(x+10,y+43,desc,16)
for y in [612,735,865]:line([(295,y),(330,y),(330,735),(365,735)],'#748a9d')
line([(630,735),(700,735)],'#748a9d')
for y in [612,732,852]:line([(970,735),(1015,735),(1015,y),(1060,y)],'#748a9d')
text(350,900,'All 9 IDs / 4 physical MAX3 units. New lengths A/U NULL. 850 / ceil5(min+20)<=900 unchanged.',17,'#a12838')
svg.append('</svg>');(out/'day07-whole-SOURCE-Knee-link-proposal-view.svg').write_bytes(('\n'.join(svg)+'\n').encode());im.save(out/'day07-whole-SOURCE-Knee-link-proposal-view.png')
card=root/'hardware/HOBBY_COMPLETION_PLAN.md';raw=card.read_bytes();i=raw.index(b'## Historia poprzednich okien');pre=raw[:i].decode();tail=raw[i:];j=pre.index('\n',pre.index('## Bieżąca'))+1;fact='\nWHOLE_PHYSICAL_SOURCE_ACTIVE: '+p.name+' SHA'+sha(p)+'. ActualKneeLink117 outerface1187mm2; one86x14x8holder/10x4channel/3staggered8laps/20sleeves/2x9lands, 2T18I145structural+2T18R100jacketroles. ContactNOTfusion; first2actual4x4pads+tie-return/frame/fullholderneighbors. 9IDsallassigned4physicalSOURCE1/2/3+DONOR3MAX units; newA/U/minimumNULL. SixKnee+3Hipmerge toactualBankBed1undersidelandingproposal, thenV3/D3/G3localsplit; allfreecapacity/R/slack/transportunreceived, no oldPcredit. Savedsource-faceview+wholegraph beforetest. Sourcephysicalpartframe3/3REUSE, no oldscans/V3brackets. Target05:12UTC/native26064/46493.\n';assert card.read_bytes()==raw;q=card.with_suffix('.owner49start.tmp');q.write_bytes((pre[:j]+fact+pre[j:]).encode()+tail);os.replace(q,card)
rt=Path('C:/Users/Sysq/PycharmProjects/robot-cat/.codex/hooks/robot-cat-work-window.json');raw=rt.read_bytes();r=json.loads(raw);r['active_worker'].update(state='WHOLE_SOURCE_KNEE_LINK_PHYSICAL_MOUNT_FIRST_GATE',agent_turn_started_utc='2026-11-07T04:45:17Z',current_bounded_chunk_target_end_utc='2026-11-07T05:12:00Z',pending_operation='robot-cat49-Knee-holder-actual-mount-first-gate.py',pendingoperation='robot-cat49-Knee-holder-actual-mount-first-gate.py',latest_proposal=str(p),latest_proposal_sha256=sha(p),unsaved_geometry=False);assert rt.read_bytes()==raw;q=rt.with_suffix('.owner49start.tmp');q.write_bytes((json.dumps(r,ensure_ascii=False,indent=2)+'\n').encode());os.replace(q,rt)
print('PROPOSAL_VIEW_CARD_RUNTIME_SAVED',sha(out/'day07-whole-SOURCE-Knee-link-proposal-view.png'))
