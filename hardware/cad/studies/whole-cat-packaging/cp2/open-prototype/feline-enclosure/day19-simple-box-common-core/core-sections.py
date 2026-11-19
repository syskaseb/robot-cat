"""Show the actual occupied levels on four cuts of the saved assembly."""
from pathlib import Path
import runpy,json,ast,numpy as np
P=Path(__file__).parent
src=(P.parent/'day19-closed-head-neck-and-module-interfaces/shoulder-sections.py').read_text()
exec(src[:src.index("lay=json.loads")].replace("whole-cat19C.FCStd","whole-cat19E.FCStd"))
hardware=[n for n in D.members if n.startswith(('Motor_ATO','S0_','OP_S1','TAIL_','CF17_BUS_CSK','CB_PCA_','PBAY_','NIGHT_INLINE','WAGO415_')) and n!='WAGO415_data_1_0' and n!='TAIL_ROTATING_HOLLOW_REAL_ROOT']
hardware+=['Pi4B_actual_PCB','PCA9685_Adafruit815_PCB','E1_populated_prototype_board','BNO085','MAX98357A_amp','E19_BUS_PCB','E19_BUS_population','MG92B_Head_yaw','MG92B_Tail','D19D_YawMatedPair','Speaker','ReSpeakerLite_on_REMOVABLE_back','Battery_GEA223S30X6GT','Monitor_MOD05015']
groups=[('nośnik i oparcia',['E19_ForeBase','E19_RearBase']+[n for n in D.members if n.startswith('E19_Wago')],'#166a61'),('osłony i ogon',['E19_FrontShroud','E19_UpperYawCover','E19_ForeLid','E19_RearLid','E19_KeyedTail','D19D_PitchBack'],'#374a69'),('obsada i osprzęt',hardware,'#9d4248'),('rezerwy i wiązki',['B19_TailJRUnderBank','C19_FFC190','D19D_ToF','D18C_DATA_BUS_FULL26_PROJECT_BOOT','B19_TailLaps']+[n for n in D.members if n.startswith('E19_Field')],'#cf8518')]
if 'E19_ReSpeakerSource' in D.members:
    hardware.remove('ReSpeakerLite_on_REMOVABLE_back');hardware.append('E19_ReSpeakerSource')
    groups[1][1].append('E19_BatteryDoor')
fig,axes=plt.subplots(2,2,figsize=(13,8))
for ax,x in zip(axes.flat,[-110,-60,48,140]):
    for title,names,color in groups:
        for n in names:
            b=D.bounds(n)
            if b[0]<x<b[3]:
                seg=sections(n,0,x)
                if seg:ax.add_collection(LineCollection(seg,colors=color,linewidths=1.05))
    ax.set_aspect('equal');ax.set(xlim=(-110,113),ylim=(33,225),title=f'X = {x} mm',xlabel='Y [mm]',ylabel='Z [mm]');ax.grid(lw=.28)
fig.legend([plt.Line2D([0],[0],color=g[2]) for g in groups],[g[0] for g in groups],loc='lower center',ncol=4)
fig.tight_layout(rect=(0,.06,1,1));fig.savefig(P/'critical-sections.png',dpi=135)
