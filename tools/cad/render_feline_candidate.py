"""Honest coordinated candidate views, not the selected or fully mounted cat."""
import json
import pickle
import time
import numpy as np
import FreeCAD as A
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from check_main_p0_placement import ROOT,SavedShapes
from plan_feline_layout import BASE,OUT,STAGES,transforms,apply
from build_feline_layout_envelope import STATIONS,section_coefficients


def main():
    tick=time.monotonic();plan=json.loads((OUT/'module-layout.json').read_text())
    motion=json.loads((OUT/'motion-layout.json').read_text())
    envelope=json.loads((OUT/'layout-checkpoint.json').read_text())
    inventory={r['object']:r for r in motion['inventory']};cache={}
    with (BASE/'phase1-prototype-final/preview/triangulation-cache.pkl').open('rb') as f:
        pickle.load(f)
        while True:
            try:n,m=pickle.load(f)
            except EOFError:break
            cache[n]=m
    reader=SavedShapes();placed={}
    for g in plan['groups']:
        for n in g['objects']:
            v,c,kind=cache[n]
            if n in plan['reference_substitutions']:
                r=plan['reference_substitutions'][n];s=reader.shape(ROOT/r['source'],r['object'])
                s.translate(A.Vector(*r['world_shift_before_head_drop_mm']))
                p,f=s.tessellate(.8);v=np.array([list(x) for x in p])[np.array(f)]
            # Dropping triangles is not mesh simplification: it creates
            # misleading holes in heads and plates. Render the whole mesh.
            placed[n]=(v@np.array(g['rotation_rows']).T+g['translation_mm'],c,kind)
    for n,r in inventory.items():
        if n in placed or r['kind']!='surface':continue
        if r['label'].startswith(('P0_','tail/')) or n.startswith(('Print_P0_','Print_CP2_TailRiser','Battery')):
            v,c,kind=cache[n];placed[n]=(v,c,kind)
    axes=json.loads((ROOT/'hardware/simulation/p0/e6-leg-compatibility.json').read_text())['axes']
    for index,filename in [(0,'candidate-standing.png'),(envelope['planning_pose_index'],'candidate-lying.png')]:
        pose=motion['poses'][index];drop=pose['body_drop_mm'];members={}
        for code,groups in motion['membership'].items():
            aa=[next(a for a in axes if a['code']==code and a['stage']==stage) for stage in STAGES]
            tf=transforms(aa,pose['legs'][code]['angles_delta_degrees'])
            for stage,t in zip(STAGES,tf):
                for n in groups[stage]:members[n]=t
        fig,axs=plt.subplots(1,3,figsize=(18,7),dpi=120)
        views=[('PRZÓD',np.array([[0,0,-1],[1,0,0],[0,1,0]])),
            ('BOK',np.array([[-1,0,0],[0,0,1],[0,1,0]])),
            ('GÓRA',np.array([[-1,0,0],[0,1,0],[0,0,-1]]))]
        for ax,(title,basis) in zip(axs,views):
            polygons=[];colors=[];depth=[]
            for n,(v,c,kind) in placed.items():
                if n in members:v=apply(v.reshape(-1,3),members[n]).reshape(v.shape)
                v=v.copy();v[:,:,2]-=drop;p=v@basis
                polygons.append(p[:,:,:2]);depth.append(p[:,:,2].mean(1));colors.append(np.tile(c*.85,(len(p),1)))
            v=np.concatenate(polygons);d=np.concatenate(depth);c=np.concatenate(colors);order=np.argsort(d)
            ax.add_collection(PolyCollection(v[order],facecolors=c[order],edgecolors='none',rasterized=True))
            co,si=section_coefficients();co=np.r_[co,co[0]];si=np.r_[si,si[0]]
            for x,w,h in STATIONS:
                v=np.column_stack((np.full(17,x),co*w/2,envelope['native']['center_z_mm']+si*h/2-drop))@basis
                ax.plot(v[:,0],v[:,1],color='#1680b3',lw=.75)
            if title!='GÓRA':ax.axhline(motion['ground_rest_z_mm'],color='#333333',lw=1)
            ax.autoscale_view();ax.set_aspect('equal');ax.grid(alpha=.15);ax.set_title(title);ax.set_xlabel('mm')
        fig.suptitle(f'WSPÓLNY KANDYDAT, ODRZUCONY | opuszczenie {drop:.2f} mm',fontsize=15)
        fig.text(.5,.045,'Pokazane aktualne moduły kandydata i P0/ogon; nie wybrany projekt. Nowe mocowania i pełne przewody jeszcze NIE zbudowane.',ha='center',fontsize=9)
        fig.text(.5,.017,'Niebieski: rezerwacja obudowy, nie ścianka. Stare galerie jawnie zastępowane; nie są ukrytymi gotowymi mocowaniami.',ha='center',fontsize=9)
        fig.tight_layout(rect=(0,.07,1,.94));fig.savefig(OUT/filename,facecolor='white');plt.close(fig)
    print(json.dumps(dict(views=['candidate-standing.png','candidate-lying.png'],parts=len(placed),seconds=round(time.monotonic()-tick,3))),flush=True)


if __name__=='__main__':main()
