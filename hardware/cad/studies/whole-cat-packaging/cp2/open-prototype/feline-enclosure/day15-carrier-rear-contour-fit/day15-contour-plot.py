from pathlib import Path
import json,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
P=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day15-carrier-rear-contour-fit');r=json.loads((P/'actual-rear-section-Z65.json').read_bytes());fig,axs=plt.subplots(1,2,figsize=(12,7));colors={'P19_shared_lower_carrier':'#d17b12','S0_body':'#bd2828','Battery_GEA223S30X6GT':'#218c55','P05_spacer_instance2':'#1755b3','H03_panel_M3x55_1':'#444444'}
for ax in axs:
 for row in r:
  xy=row['xy'];ax.plot([p[0] for p in xy],[p[1] for p in xy],c=colors[row['name']],lw=1.8)
 ax.set_xlim(98,115);ax.set_aspect('equal');ax.grid(alpha=.2);ax.set_xlabel('X [mm]');ax.set_ylabel('Y [mm]')
axs[0].set_ylim(-26,-10);axs[0].set_title('Negative-Y / actual S0: gap 1.627 >= 1.25')
axs[1].set_ylim(8,24);axs[1].set_title('Positive-Y / current P05 + M3x50: HOLD')
axs[1].annotate('actual P05 face X107\nwall band only 0.75',xy=(107,15),xytext=(98.3,21.5),fontsize=9,arrowprops=dict(arrowstyle='->'))
axs[1].annotate('actual M3x50 shaft\ngap 0.5 < 1.25',xy=(108.5,15),xytext=(98.3,9),fontsize=9,arrowprops=dict(arrowstyle='->'))
fig.suptitle('One functional R5 contour — full rear band is NOT qualified',fontsize=13)
fig.legend(handles=[Line2D([0],[0],c=c,label=l) for l,c in [('P19 coupon/currentcontour','#d17b12'),('Actual S0','#bd2828'),('Nominalbatteryfullbox','#218c55'),('RetainedP05sourceprint','#1755b3'),('WholeM3x50steel','#444444')]],loc='lower center',ncol=3,fontsize=8);fig.tight_layout(rect=[0,.12,1,.94]);fig.savefig(P/'actual-rear-two-sided-section.png',dpi=170)
