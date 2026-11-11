from pathlib import Path
import json,hashlib,math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
O=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure');r=json.loads((O/'day11-WHOLE-end-to-end-underbank-first-gate.json').read_bytes());f=json.loads((O/'day11-WHOLE-end-to-end-frozen-length-and-load-premises.json').read_bytes());b=json.loads((O/'day06-recovery-current1292-data-receipt.json').read_bytes());bounds={q['name']:q['bounds_mm'] for q in b['rows']}
fig,ax=plt.subplots(1,3,figsize=(19,7));fig.suptitle('ONE whole SOURCE-side / open-underbank architecture — HOLD, N01 0/10\nActual endpoints + candidate components; dashed links UNKNOWN, not accepted wire routes',fontsize=14)
for a in ax:a.grid(alpha=.15);a.set_aspect('equal',adjustable='box')
ax[0].set(title='Whole XY: 9 IDs / 12 portions / 4 MAX3',xlabel='X mm',ylabel='Y mm');ax[1].set(title='Whole XZ: load / service layers remain unproved',xlabel='X mm',ylabel='Z mm')
styles=[('Ref_Material_S0_body_CP2_0_0','S0 body bounds','#777777'),('Station:P_SYS:case','P_SYS case','#315c82'),('F_PI:registered_casing_reservation','FULL FPI variable home','#298352')]
for n,label,col in styles:
 lo,hi=bounds[n]
 for a,j in [(ax[0],1),(ax[1],2)]:
  a.add_patch(Rectangle((lo[0],lo[j]),hi[0]-lo[0],hi[j]-lo[j],fill=False,edgecolor=col,ls='--',lw=1));a.text((lo[0]+hi[0])/2,(lo[j]+hi[j])/2,label,ha='center',fontsize=7,color=col)
for q in r['rows']:
 start,end=q['start'],q['end'];rad=q['nominal_r_mm']+.4
 for a,j in [(ax[0],1),(ax[1],2)]:a.add_patch(Rectangle((start[0],start[j]-rad),end[0]-start[0],2*rad,color='#db5a49',alpha=.17,lw=.5))
 qf=next(t for t in f['nine_ID_twelve_portions'] if t['wire']==q['wire'] and t['physical_unit']==q['unit']);E=qf['receiver_held9_frame']['end']
 for a,j in [(ax[0],1),(ax[1],2)]:
  a.plot([end[0],E[0]],[end[j],E[j]],'--',color='#a060a0',lw=.7);a.plot(E[0],E[j],'o',color='#21426b',ms=3);a.text(E[0]+1,E[j]+1,q['wire'],fontsize=6)
entry=[-126,52,32];p0=f['source_motion_ports36'][0]
for name,P in [('Hip3 / 10',p0['source_origins'][0]['nominal_source14_outer_world_mm']),('Knee6 / 55 each',p0['Knee_exit_world_mm'])]:
 for a,j in [(ax[0],1),(ax[1],2)]:
  a.plot(P[0],P[j],'o',color='#195a40',ms=5);a.text(P[0]-4,P[j]+4,name,fontsize=8);a.plot([P[0],entry[0]],[P[j],entry[j]],'--',color='#195a40',lw=1)
for a,j in [(ax[0],1),(ax[1],2)]:
 a.plot(entry[0],entry[j],'s',color='#be3024',ms=5);a.text(entry[0],entry[j]-8,'Accounting entry\nNOT a terminal',fontsize=7)
 a.set_xlim(-151,100)
ax[0].set_ylim(-45,108);ax[1].set_ylim(-75,115)
ax[1].axhline(46.52,color='#6b8669',lw=.7,ls=':');ax[1].text(85,48,'MAIN46.52',fontsize=7,ha='right')
ax[0].text(80,-40,'D1 BUS.D / W003 mate, D5 W007 both ends\nG4 includes W025; whole bought cases retained',ha='right',fontsize=8)
ax[1].text(90,-64,'Knee Source21 + actual 3 owned joints retained.\n55 transfer only through loose guides, before true fixed caps.\nU(55..65): length125.2..135.2 is conditional, not +55 again.',ha='right',fontsize=8)
ax[2].set(title='ACTUAL P0 / occupied-field section\nX = %.3f mm; no bbox-as-material'%r['section_plane_x_mm'],xlabel='Y mm',ylabel='Z mm')
cols={'CURRENT_P0_SIDELEFT22':'#434b55','ACTUAL_ALLOCATED_BRANCH_FIELD':'#d84432','NOMINAL_BRANCH_FIELD':'#258dba'}
for sec in r['section']:
 for i,curve in enumerate(sec['curves_YZ']):
  if len(curve)>1:ax[2].plot([p[0] for p in curve],[p[1] for p in curve],color=cols[sec['name']],lw=1.3 if sec['name'].startswith('CURRENT') else .9,label=sec['name'] if i==0 else None)
W=r['witnesses'][0]
ax[2].plot([p[1] for p in W],[p[2] for p in W],'k-',lw=2)
ax[2].annotate('allocated gap %.6f < 1.25\nnominal %.6f; common0\nHOLD, not delivered contact'%(r['allocated_gap_mm'],r['nominal_gap_mm']),xy=(W[0][1],W[0][2]),xytext=(52,23),arrowprops=dict(arrowstyle='->'),fontsize=8)
ax[2].set_xlim(40,65);ax[2].set_ylim(20,44);ax[2].legend(loc='upper right',fontsize=6)
fig.text(.02,.025,'RED = full unchanged profiles +0.4 margin. Candidate trunk branches 9→8→7→6→3; no all9 at one port.  R35.1 transitions / source-ground / actual Li, ΔLi, usable55 / perunit850–900 / FPI–S0–V3 simultaneous service: UNKNOWN.  No new support built.',fontsize=9)
fig.tight_layout(rect=[0,.055,1,.89]);base=O/'day11-WHOLE-end-to-end-layout-and-critical-section';fig.savefig(str(base)+'.png',dpi=140);fig.savefig(str(base)+'.svg');plt.close(fig)
print(str(base)+'.png')
