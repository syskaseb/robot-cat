from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
P=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day15-strapped-carrier-first-fit')
r=json.loads((P/'closed-load-path-first-gate.json').read_bytes())
fig,axs=plt.subplots(1,2,figsize=(13,7),sharex=True,sharey=True)
colors={'P12_common_deck_speaker':'#1554ab','P19_shared_lower_carrier':'#0b8958','Battery_GEA223S30X6GT':'#444444'}
for ax,sec in zip(axs,r['sections']):
 for row in sec['curves']:
  xy=row['yz'];color=colors.get(row['name'],'#e07700');ls='--' if 'tail' in row['name'] or 'closure' in row['name'] else '-'
  ax.plot([p[0] for p in xy],[p[1] for p in xy],color=color,lw=1.6,ls=ls)
 ax.axhline(62.8,c='#0b8958',lw=.6,alpha=.4);ax.axhline(91.3,c='#1554ab',lw=.6,alpha=.4)
 ax.text(-36,58.0,'P19 floor 60.8–62.8\nOUTSIDE closed band',fontsize=9,color='#0b8958')
 ax.text(-36,99.5,'P12 roof 91.3–96\nOUTSIDE closed band',fontsize=9,color='#1554ab')
 ax.annotate('nominal roof gap 2.6',xy=(0,90),xytext=(5,101),arrowprops=dict(arrowstyle='->'),fontsize=8)
 ax.set_title(f'Actual BRep section X={sec["stationX"]} mm');ax.set_xlim(-38,38);ax.set_ylim(54,108);ax.set_aspect('equal');ax.grid(alpha=.2);ax.set_xlabel('Y [mm]')
axs[0].set_ylabel('Z [mm]')
fig.legend(handles=[Line2D([0],[0],c=c,label=l) for l,c in [('P12 fixed print','#1554ab'),('P19 carrier','#0b8958'),('Battery full box','#444444'),('Full 2.2 strap / tail / closure fields','#e07700')]],loc='lower center',ncol=2,fontsize=9)
fig.suptitle('Current two loops: no enclosed P12/P19 member — proposed common clamp NOT QUALIFIED',fontsize=12)
fig.tight_layout(rect=[0,.10,1,.95]);fig.savefig(P/'actual-two-load-sections.png',dpi=170);plt.close(fig)
print(str(P/'actual-two-load-sections.png'))
