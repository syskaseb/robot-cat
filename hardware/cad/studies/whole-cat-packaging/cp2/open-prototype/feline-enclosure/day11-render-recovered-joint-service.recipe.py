from pathlib import Path
import json,hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
O=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure')
expected={'day11-joint-bank-receiver-load-and-fore-neck-service-premise.json':'f830cd7647ca3b56ea809e7a860be8261b84ee3863dde28934707f965488ca4b','day11-joint-FPI-service-current-frame-relation.json':'381ff392e6b21a72b2a4ef77888fab65d96c12dd8c892e0a440f2368f715c7f7','day11-joint-service-current-limiting-material-sections.json':'4a96167d631114a24f0e27349cc2aa6555783602c5c8a67a8f889e609a2c7e65'}
for n,h in expected.items():assert hashlib.sha256((O/n).read_bytes()).hexdigest()==h
P=json.loads((O/list(expected)[0]).read_bytes());G=json.loads((O/list(expected)[1]).read_bytes());S=json.loads((O/list(expected)[2]).read_bytes())
fig,ax=plt.subplots(1,3,figsize=(19,7));fig.suptitle('Joint bank / fore-neck service — SAVED SOURCE READ, N01 0/10\nChosen SIDE FPI access allocation HOLD: valid common25.920 mm³ with retained P0 rail; no CAD rerun',fontsize=13)
for a in ax:a.grid(alpha=.15);a.set_aspect('equal',adjustable='box')
ax[0].set(title='Recorded XY site: all cases retained\nBounds locate parts; white space is NOT proof',xlabel='X mm',ylabel='Y mm')
bb=P['one_site_configuration']['FPI']['case']['bounds_mm'];op=P['one_site_configuration']['FPI']['case']['side_operation_box'];actual={q['actor']:q['bounds_mm'] for q in P['actual_context_bounds']}
for name,label,col in [('Station:D_FL:case','D5 all5','#2b6d91'),('CurrentFLG:case','G4 all4 / W025','#2b6d91'),('Ref_Material_S0_body_CP2_0_0','S0 BODY bounds','#7b7b7b')]:
 lo,hi=actual[name];ax[0].add_patch(Rectangle((lo[0],lo[1]),hi[0]-lo[0],hi[1]-lo[1],fill=False,edgecolor=col,ls='--'));ax[0].text((lo[0]+hi[0])/2,(lo[1]+hi[1])/2,label,fontsize=7,ha='center',color=col)
for name,lo,hi,col in [('FPI full51×22',bb[0],bb[1],'#c78b35'),('SIDE operation reserve',op[0],op[1],'#c43b36')]:
 ax[0].add_patch(Rectangle((lo[0],lo[1]),hi[0]-lo[0],hi[1]-lo[1],facecolor=col,edgecolor=col,alpha=.25));ax[0].text((lo[0]+hi[0])/2,(lo[1]+hi[1])/2,name,fontsize=7,ha='center')
for q in P['actual_context_bounds']:
 if 'F_L' in q['actor'] and '_Housing_' in q['actor']:
  lo,hi=q['bounds_mm'];ax[0].add_patch(Rectangle((lo[0],lo[1]),hi[0]-lo[0],hi[1]-lo[1],fill=False,ls=':',edgecolor='#526f47'));ax[0].text((lo[0]+hi[0])/2,hi[1]+2,q['actor'].replace('Ref_Material_','').split('_CP2')[0],fontsize=6,ha='center')
ax[0].set_xlim(-145,75);ax[0].set_ylim(-45,100)
ax[1].set(title='ACTUAL section X−42.8\nService field / P0 SideRight22',xlabel='Y mm',ylabel='Z mm')
cols={'CURRENT_P0_SIDERIGHT22':'#353e4b','SIDE_WHOLE_FHAC_CASE':'#ba812d','SIDE_ROUTINE_OPENING':'#d43b36'}
for q in G['section']:
 for i,curve in enumerate(q['curves_YZ']):
  if len(curve)>1:ax[1].plot([v[0] for v in curve],[v[1] for v in curve],color=cols[q['name']],lw=1.5 if q['name'].startswith('CURRENT') else 1.1,label=q['name'] if i==0 else None)
ax[1].annotate('Field lower edge38.25\nReal rail reaches38.52\nHOLD25.920 mm³ total\nnot delivered-lid contact',xy=(-29,38.4),xytext=(-13,63),arrowprops=dict(arrowstyle='->'),fontsize=8)
ax[1].set_xlim(-43,25);ax[1].set_ylim(33,75);ax[1].legend(loc='lower right',fontsize=6)
ax[2].set(title='Saved material section X−93.5036\nS0 panel roots / actual PWM washer',xlabel='Y mm',ylabel='Z mm')
sec=next(q for q in S['sections'] if q['x_mm']< -90)
colors={'Ref_Material_S0_body_CP2_0_0':'#6e747d','Ref_Material_PWM968517BottomWasher_0_0':'#b83638','CurrentFoundation:FoundationRail:-1':'#a8834f'}
for q in sec['rows']:
 for i,curve in enumerate(q['curves_YZ']):
  if len(curve)>1:ax[2].plot([v[0] for v in curve],[v[1] for v in curve],color=colors[q['actor']],lw=1.1,label=q['actor'].replace('Ref_Material_','').replace('_0_0','') if i==0 else None)
ax[2].scatter([-12,12],[99.1652708794]*2,c='#1b7653',s=18);ax[2].text(-10,102,'2 received root patches\n10 mm³ each, not new hood proof',fontsize=7)
ax[2].annotate('Real PWM metal\nold hood common.252442\nPRESERVED, NOT RETESTED',xy=(-43,100.394486),xytext=(-47,69),arrowprops=dict(arrowstyle='->'),fontsize=7)
ax[2].set_xlim(-51,28);ax[2].set_ylim(63,109);ax[2].legend(loc='lower right',fontsize=6)
fig.text(.02,.062,'No new case pose, trunk, support, print or service-path retry. Recorded SIDE site only: source service reserve is conservative/project geometry, not exact manufacturer lid/hand. Other service arrangements remain unproved.',fontsize=8)
fig.text(.02,.038,'DONOR D/V/G held exits received: F(43,5.65/8.5/11.35,4), +U; joint→exit65/43/21 INCLUDES9. SOURCEFL2 grip still OPEN; no Li/usable55/fit acceptance. All factory parts, four220 and both4MTA retained.',fontsize=8)
fig.text(.02,.014,'Rendered from pinned saved JSON sections after interrupted turn. Old PID26044/helper11476 absent; replacement GUI19584 restoration controlled by parent. No new geometry compute or continuous-overnight-progress claim.',fontsize=8)
fig.tight_layout(rect=[0,.095,1,.88]);base=O/'day11-joint-service-recovered-source-view';fig.savefig(str(base)+'.png',dpi=140);fig.savefig(str(base)+'.svg');plt.close(fig);print(str(base)+'.png')
