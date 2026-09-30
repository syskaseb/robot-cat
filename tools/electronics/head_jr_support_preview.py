"""Small derived interface diagram; not a slicer or physical qualification."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/head-jr-support-r2'
checks=json.loads((OUT/'checks.json').read_text())
fig,axs=plt.subplots(1,2,figsize=(11,5))
ax=axs[0]
ax.add_patch(Rectangle((-170,62),40,18,color='#729eb8'))
ax.add_patch(Rectangle((-170,79),32,43,color='#729eb8'))
ax.add_patch(Rectangle((-158,82),12,30,color='#e7b456',alpha=.8))
for row in checks['slot_checks']:
    b=row['bbox_mm'];ax.add_patch(Rectangle((b[0],b[1]),b[3]-b[0],b[4]-b[1],color='white',ec='black'))
for y in checks['tie_stations_y_mm']:ax.text(-171,y,f'{y}',ha='right',va='center',fontsize=8)
ax.text(-152,97,'JR\nprovisional',ha='center',va='center',fontsize=9)
ax.set(xlim=(-181,-120),ylim=(55,129),title='XY: holder and eight through slots',xlabel='X mm',ylabel='Y mm')
ax=axs[1]
ax.add_patch(Rectangle((62,133),60,3,color='#729eb8'))
ax.add_patch(Rectangle((82,136),30,10,color='#e7b456',alpha=.8))
ax.add_patch(Rectangle((73,136),6,2.5,color='#45687c'))
ax.add_patch(Rectangle((115,136),6,3,color='#45687c'))
ax.annotate('independent insulation restraints',xy=(76,138.5),xytext=(61,154),arrowprops={'arrowstyle':'->'},fontsize=8)
ax.set(xlim=(57,129),ylim=(127,158),title='YZ: housing / insulation supports',xlabel='Y mm',ylabel='Z mm')
for ax in axs:ax.set_aspect('equal');ax.grid(alpha=.2)
fig.suptitle('JR holder candidate: two replacement prints, not complete head wiring')
fig.tight_layout();fig.savefig(OUT/'preview.png',dpi=150);plt.close(fig)
