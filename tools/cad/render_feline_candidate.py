"""Honest coordinated candidate views, not the selected or fully mounted cat."""
import json
import pickle
import time
import sys
import numpy as np
import FreeCAD as A
import Part
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import BASE,OUT,STAGES,transforms,apply
from build_feline_layout_envelope import STATIONS,section_coefficients


def main():
    tick=time.monotonic();plan=json.loads((OUT/'module-layout.json').read_text());scenario=None
    if '--receiver-scenario' in sys.argv:
        scenario=json.loads((OUT/'motion-receivers-checks.json').read_text())
        assert scenario['native_built'] and sha(ROOT/scenario['native'])==scenario['native_sha256']
        plan=json.loads((ROOT/scenario['module_plan']).read_text())
    show_skin='--with-current-skin' in sys.argv;iso='--isometric-only' in sys.argv
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
            if n in plan.get('part_pose_overrides',{}):
                ov=plan['part_pose_overrides'][n]
                v=v@np.array(ov['rotation_rows']).T+ov['translation_mm']
            # Dropping triangles is not mesh simplification: it creates
            # misleading holes in heads and plates. Render the whole mesh.
            placed[n]=(v@np.array(g['rotation_rows']).T+g['translation_mm'],c,kind)
    for n,r in inventory.items():
        if n in placed or r['kind']!='surface':continue
        if n.startswith('BatteryFrameHardware'):continue
        if r['label'].startswith(('P0_','tail/')) or n.startswith(('Print_P0_','Print_CP2_TailRiser','Battery')):
            v,c,kind=cache[n];placed[n]=(v,c,kind)
    feet=json.loads((OUT/'belly-feet-native.json').read_text())
    assert feet['external_fit_complete']
    for row in feet['parts']+feet['hardware']:
        s=reader.shape(ROOT/feet['native'],row['object']);p,f=s.tessellate(.5)
        v=np.array([list(x) for x in p])[np.array(f)]
        placed[row['object']]=(v,np.array([.4,.53,.61]),'surface')
    if show_skin:
        receipt=json.loads((OUT/'shared-skin-exact.json').read_text());access=json.loads((OUT/'skin-access-native.json').read_text())
        assert receipt['status']=='SAMPLED_SHARED_SKIN_CLEAR_COWLS_MOUNTS_WIRING_OPEN'
        assert receipt['native_sha256']==access['native_sha256']==sha(ROOT/access['native'])
        for row in access['parts']:
            s=reader.shape(ROOT/access['native'],row['object']);p,f=s.tessellate(.3)
            v=np.array([list(x) for x in p])[np.array(f)]
            placed[row['object']]=(v,np.array([.22,.24,.26]),'surface')
        # Proposed black PETG appearance only. Exact head-shell geometry is
        # retained, and all unresolved headref hardware remains visible.
        for n,(v,c,kind) in list(placed.items()):
            if n in ('Ref_Material_head_0_0_FrontLeft_0_0','Ref_Material_head_0_0_FrontRightPorted_0_0',
                'Ref_Material_head_0_0_Rear_0_0','Ref_Material_head_0_0_Nose_0_0',
                'Ref_Material_head_0_0_EarL_0_0','Ref_Material_head_0_0_EarR_0_0'):
                placed[n]=(v,np.array([.22,.24,.26]),kind)
    axes=json.loads((ROOT/'hardware/simulation/p0/e6-leg-compatibility.json').read_text())['axes']
    suffix=('-skin' if show_skin else '')+('-receivers' if scenario else '')
    views=[(0,('candidate-isometric' if iso else 'candidate-standing')+suffix+'.png')]
    if '--standing-only' not in sys.argv and not iso:views.append((envelope['planning_pose_index'],'candidate-lying'+suffix+'.png'))
    factory=json.loads((OUT/'factory-routes.json').read_text())
    current_factory=factory['source_sha256'][(OUT/'module-layout.json').relative_to(ROOT).as_posix()]==__import__('hashlib').sha256((OUT/'module-layout.json').read_bytes()).hexdigest()
    if scenario:factory={'routes':scenario['factory_routes']};current_factory=True
    curves=[]
    if current_factory:
        for row in factory['routes']:
            edges=[]
            for p in row['parts']:
                a,b=A.Vector(*p['start']),A.Vector(*p['end'])
                edges.append(Part.makeLine(a,b) if p['kind']=='line' else Part.Arc(a,A.Vector(*p['mid']),b).toShape())
            curves.append(np.array([list(v) for v in Part.Wire(edges).discretize(Deflection=.2)]))
    prefixes=json.loads((OUT/'prefix-allocation.json').read_text());approaches=[]
    specs={r['id']:r for r in prefixes['specifications']}
    assert prefixes['source_sha256'][(OUT/'module-layout.json').relative_to(ROOT).as_posix()]==__import__('hashlib').sha256((OUT/'module-layout.json').read_bytes()).hexdigest()
    for key,k in prefixes['allocation'].items():
        r=specs[key]
        if scenario and r['role'] in plan['motion_receiving_changes']:continue
        bend=next(c['bend'] for c in prefixes['domains'][key] if c['option']==k)
        p=A.Vector(*r['point']);d=A.Vector(*r['direction']);d.normalize()
        b=A.Vector(*bend);b=b-d*b.dot(d);b.normalize();q=p+d*9;R=12.4
        w=Part.Wire([Part.makeLine(p,q),Part.Arc(q,q+d*(R/2**.5)+b*(R*(1-1/2**.5)),q+d*R+b*R).toShape()])
        approaches.append(np.array([list(v) for v in w.discretize(Deflection=.2)]))
    for index,filename in views:
        pose=motion['poses'][index];drop=pose['body_drop_mm'];members={}
        for code,groups in motion['membership'].items():
            aa=[next(a for a in axes if a['code']==code and a['stage']==stage) for stage in STAGES]
            tf=transforms(aa,pose['legs'][code]['angles_delta_degrees'])
            for stage,t in zip(STAGES,tf):
                for n in groups[stage]:members[n]=t
        camera_views=[('PRZÓD',np.array([[0,0,-1],[1,0,0],[0,1,0]])),
            ('BOK',np.array([[-1,0,0],[0,0,1],[0,1,0]])),
            ('GÓRA',np.array([[-1,0,0],[0,1,0],[0,0,-1]]))]
        if iso:
            eye=np.array([-4.,-6.,3.]);eye/=np.linalg.norm(eye)
            right=np.cross(eye,[0,0,1]);right/=np.linalg.norm(right)
            up=np.array([0.,0.,1.])-eye*eye[2];up/=np.linalg.norm(up)
            camera_views=[('GEOMETRIA CAD | proponowany czarny PETG',np.column_stack((right,up,eye)))]
        fig,axs=plt.subplots(1,len(camera_views),figsize=(12,9) if iso else (18,7),dpi=135 if iso else 120)
        axs=np.atleast_1d(axs)
        for ax,(title,basis) in zip(axs,camera_views):
            polygons=[];colors=[];depth=[]
            for n,(v,c,kind) in placed.items():
                if n in members:v=apply(v.reshape(-1,3),members[n]).reshape(v.shape)
                v=v.copy();v[:,:,2]-=drop;p=v@basis
                polygons.append(p[:,:,:2]);depth.append(p[:,:,2].mean(1))
                normals=np.cross(v[:,1]-v[:,0],v[:,2]-v[:,0]);length=np.linalg.norm(normals,axis=1)
                normals/=np.maximum(length,1e-12)[:,None]
                light=np.array([-.3,-.5,1.]);light/=np.linalg.norm(light)
                shade=.55+.45*abs(normals@light)
                colors.append(shade[:,None]*np.array(c)[None,:])
            v=np.concatenate(polygons);d=np.concatenate(depth);c=np.concatenate(colors);order=np.argsort(d)
            ax.add_collection(PolyCollection(v[order],facecolors=c[order],edgecolors='none',rasterized=True))
            for x,w,h in ([] if show_skin else STATIONS):
                co,si=section_coefficients(w,h);co=np.r_[co,co[0]];si=np.r_[si,si[0]]
                v=np.column_stack((np.full(len(co),x),co*w/2,envelope['native']['center_z_mm']+si*h/2-drop))@basis
                ax.plot(v[:,0],v[:,1],color='#1680b3',lw=.75)
            for curve in curves:
                q=curve.copy();q[:,2]-=drop;q=q@basis
                ax.plot(q[:,0],q[:,1],color='#d97928',lw=1.3)
            for curve in approaches:
                q=curve.copy();q[:,2]-=drop;q=q@basis
                ax.plot(q[:,0],q[:,1],color='#d97928',lw=.65)
            if title!='GÓRA' and not iso:ax.axhline(motion['ground_rest_z_mm'],color='#333333',lw=1)
            ax.autoscale_view();ax.set_aspect('equal');ax.grid(alpha=.15);ax.set_title(title);ax.set_xlabel('mm')
        fig.suptitle(('4 PANELE CAD | OSŁONY PRZEJŚCIOWE I MOCOWANIA OPEN' if show_skin else 'WSPÓLNY PLAN, NIE WYBRANY')+f' | opuszczenie {drop:.2f} mm',fontsize=13 if iso else 15)
        fig.text(.5,.045,'Aktualne moduły, P0/ogon i4natywne podpory na8osiachM2. Mocowania przeniesionych modułów i pełne przewody OPEN.',ha='center',fontsize=9)
        fig.text(.5,.017,('Czarny:4rzeczywiste panele CAD i planowany kolor zachowanej głowy. ' if show_skin else 'Niebieski: rezerwacja, nie ścianka. ')+
            f'Pomarańczowe:{len(curves)}odcinkówMTA i{len(approaches)}niezmienionych podejść, NIE pełna wiązka.',ha='center',fontsize=8 if iso else 9)
        fig.tight_layout(rect=(0,.07,1,.94));fig.savefig(OUT/filename,facecolor='white');plt.close(fig)
    result=dict(views=[f for i,f in views],parts=len(placed),factory_curves=len(curves),unchanged_approaches=len(approaches),
        omitted_stale_relocated_approaches=len(prefixes['allocation'])-len(approaches),full_wiring_complete=False,
        receiver_scenario=bool(scenario),physical_pass=False,seconds=round(time.monotonic()-tick,3))
    if scenario:result['native_sha256']=scenario['native_sha256']
    (OUT/('render-receivers-skin.json' if scenario else 'render-candidate-current.json')).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)


if __name__=='__main__':main()
