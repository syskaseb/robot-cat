from pathlib import Path
import json,hashlib,zipfile,html,math,csv
from PIL import Image,ImageDraw
root=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical');out=root/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure';temp=Path('C:/Users/Sysq/AppData/Local/Temp');rd=lambda n:json.loads((out/n).read_bytes());a=rd('day07-WHOLE_SOURCE-receiver-anchored-returns-and-concentric-underbody-entry-proposal.json');b=rd('day07-WHOLE_SOURCE-ninecore-connected-entry-first-gate.json');c=rd('day07-WHOLE_SOURCE-current-context-and-first-gap-view-data.json');names=[]
src=(temp/'robot-cat92-package-whole-source-outcome.py').read_text(encoding='utf-8-sig');code=src[src.index('im=Image.new'):src.index('for src in [')];code=code.replace('(1600,1160)','(1600,1400)').replace('height="1160"','height="1400"').replace('945+i*24','1160+i*24').replace('assert not png.exists();','')
code=code.replace("for i in range(0,len(pts)-1,2):dr.line(pts[i:i+2],fill=col,width=width)","\n  for p0,p1 in zip(pts,pts[1:]):\n   N=max(2,int(math.dist(p0,p1)/5))\n   for j in range(0,N,2):dr.line([(p0[0]+(p1[0]-p0[0])*k/N,p0[1]+(p1[1]-p0[1])*k/N) for k in [j,min(j+1,N)]],fill=col,width=width)")
insert="""
leg=rd('day07-whole-physical-SOURCE-approach-Knee-link-proposal.json');holder=a['current_moving_holder']
for row in a['rows']:
 i=row['row'];P=leg['source_origins'][i]['source_outer_reservation_world_mm'] if i<2 else holder['current_EXIT'];Q=[row['source_passage_P'][0],77,row['source_passage_P'][2]];col={'D':'#1764bc','V':'#cf8119','G':'#18864c'}[row['core']]
 for proj in [projectXY,projectXZ]:line([proj(P),proj(Q)],col,1,True);px,py=proj(P);dr.ellipse((px-3,py-3,px+3,py+3),outline=col)
for proj in [projectXY,projectXZ]:
 P=leg['source_origins'][2]['source_outer_reservation_world_mm'];Q=holder['current_ENTRY'];line([proj(P),proj(Q)],'#8d5ca6',1,True);line([proj(holder['current_ENTRY']),proj(holder['current_EXIT'])],'#8d5ca6',2)
txt(1010,914,'Dashed LEG links = unresolved actualmovingregions, NOT chordlength.')
txt(1010,936,'Hollow source14 datums are bundle refs, NOT guessed cavities.')
txt(1010,958,'Purple sidecaraxis +8.5: originalFL3 -> owned3joints -> DONOR.')
"""
code=code.replace("png=out/",insert+"\npng=out/");exec(code);print(png.name,hashlib.sha256(png.read_bytes()).hexdigest())
