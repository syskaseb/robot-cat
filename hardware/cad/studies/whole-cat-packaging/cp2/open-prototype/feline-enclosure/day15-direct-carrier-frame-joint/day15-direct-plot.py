from pathlib import Path
import json,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
P=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day15-direct-carrier-frame-joint');r=json.loads((P/'actual-joint-and-HOLD-section-curves.json').read_bytes())
fig,axs=plt.subplots(1,2,figsize=(13,7))
cols={'P12_common_deck_speaker':'#1554ab','P19_shared_lower_carrier':'#d77b09','S0_body':'#c22b28','Battery_GEA223S30X6GT':'#329345','MAIN_Pololu4853':'#329345'}
for ax,sec in zip(axs,r):
 for row in sec['curves']:
  pts=row['points'];ax.plot([p[0] for p in pts],[p[1] for p in pts],c=cols.get(row['name'],'#444444'),lw=1.7)
 ax.set_aspect('equal');ax.grid(alpha=.2)
axs[0].set_xlim(66,87);axs[0].set_ylim(77,103);axs[0].set_xlabel('X [mm]');axs[0].set_ylabel('Z [mm]');axs[0].set_title('Actual vertical joint section Y30')
axs[0].annotate('MAIN gap 1.48',xy=(76,93.2),xytext=(66.5,99),fontsize=9,arrowprops=dict(arrowstyle='->'))
axs[0].annotate('M3x12 includes head',xy=(76,91.5),xytext=(66.5,96),fontsize=8,arrowprops=dict(arrowstyle='->'))
axs[0].annotate('full nut / washer\ntip beyond nut 1.1',xy=(76,82),xytext=(66.5,78),fontsize=8,arrowprops=dict(arrowstyle='->'))
axs[1].set_xlim(98,115);axs[1].set_ylim(-29,-13);axs[1].set_xlabel('X [mm]');axs[1].set_ylabel('Y [mm]');axs[1].set_title('Actual rear tray / S0 section Z65 — HOLD')
axs[1].plot([108,108.223588907],[ -21,-21.067718304],c='black',marker='o',ms=3)
axs[1].annotate('gap 0.233619 < 1.25\ncommon 0, no contact',xy=(108,-21),xytext=(98.4,-15),fontsize=9,arrowprops=dict(arrowstyle='->'))
fig.legend(handles=[Line2D([0],[0],c=c,label=l) for l,c in [('P12 fixedreceiver','#1554ab'),('P19 carrier','#d77b09'),('Whole standardsteel','#444444'),('Actual S0','#c22b28'),('Retained board / battery','#329345')]],loc='lower center',ncol=3,fontsize=9)
fig.suptitle('One direct loadjoint: local material/steel clear; WHOLE carrier clearance HOLD',fontsize=12);fig.tight_layout(rect=[0,.11,1,.94]);fig.savefig(P/'actual-joint-and-HOLD-sections.png',dpi=170)
