"""Select three changed wire interfaces, without approving an unfinished harness."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
CAD=ROOT/'hardware/cad/studies/head-external-wire-support-r1'
PARENT=ROOT/'hardware/manufacturing/one-batch-prototype-r20'
OUT=ROOT/'hardware/manufacturing/one-batch-prototype-r21'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def main():
    OUT.mkdir(exist_ok=True);c=read(CAD/'checks.json');assert c['status']=='SAMPLED_CHANGED_INTERFACES_CLEAR' and not c['hits'] and c['bolt_land_removed_mm3']==0
    if 'script_sha256' in c:c['initial_repair_script_sha256']=c.pop('script_sha256')
    c['finalizer_script_sha256']=sha(ROOT/'tools/cad/head_wire_support_finish_r1.py');c['builder_script_sha256']=sha(ROOT/'tools/cad/head_external_wire_support_r1.py');dump(CAD/'checks.json',c)
    s=read(PARENT/'selection.json');q=read(PARENT/'one-order-quantities.json')
    changes={'head:UpperFork':('UpperForkWireArmSlotted','broad side flat, transformed Y+90,5mm brim; inspect overhang/slot in phase2'),
      'head:FrontRightPorted':('FrontRightWirePassage','inherited worldZ up; broad inherited cut support,5mm brim; slicer/supports in phase2'),
      'body:raised-upper-cover-mount':('CoverHeadWirePassage','open skirt down;5mm brim; roof supports in phase2')}
    for identity,(name,orientation) in changes.items():
        row=next(p for p in s['prints'] if p['identity']==identity);file=CAD/(name+'_candidate_x1.stl')
        row.update(stl=file.relative_to(ROOT).as_posix(),sha256=sha(file),recipe=(CAD/'plan.json').relative_to(ROOT).as_posix(),orientation=orientation,status='selected_head_wire_interface_candidate')
    s.update(parent_selection_sha256=sha(PARENT/'selection.json'),head_wire_interface_checks_sha256=sha(CAD/'checks.json'),phase1_complete=False)
    s['conditions'].append('R21 replaces3 existing prints: fork wire outrigger, round front-right passage, cover exit preserving3.3mm bolt land. Sampled nominal loop clear/Rmin32.588. JR/factory lead storage, end transitions/restraints, fixed yaw feed and whole wiring still unfinished. Not phase1 completion or physical PASS.')
    q.update(selected_prints='hardware/manufacturing/one-batch-prototype-r21/selection.json',phase1_complete=False)
    dump(OUT/'selection.json',s);dump(OUT/'one-order-quantities.json',q)
    interface=dict(status='SELECTED_CHANGED_HEAD_INTERFACES_ONLY',new_stls=3,replacement_parts=3,new_fasteners=0,new_skus=0,
      loop={'bundle_design_OD_mm':5,'length_mm':180,'plane_z_mm':124,'yaw_sample_deg':[-15,0,15],'pitch_sample_deg':[-10,0,5],'radius_sample_mm':[x['radius_mm'] for x in c['loop_poses']],
        'continuous_sweep':False,'end_tangents_and_storage_complete':False},
      wires=['XB22 F_HP.out->C_HP.V+ redHELU23302 0.5mm2','XB23 G_AUX.4->C_HP.GND blackHELU23301 0.5mm2','XS23 R2.2->C_HP.PWM yellowKamami1178401 supplier0.12mm2'],
      PWM='Verified candidate SKU; no cyclic-life certification, no WAGO minimum0.14mm2 termination. Staggered local JR adapter joints still to construct; factory250mm servo lead unchanged.',
      assembly=['Use only three replacement parts, not old prints alongside them.','Bare fork/front relief first, servo factory lead exits its Carrier before shell closure.','Cover exit clears retained M2 screw land; retain all existing brackets/bolts.','JR location/extra lead restraint/end support still open: do not pretend this is complete wiring.'],
      phase2=['Spline/shaft and central screw fit','PETG fit/edge deburring0.5mm','Unpowered head/loop hand sweep and pinout','No power before full electrical checks'],
      next_step='Complete factory JR lead storage, stationary-to-moving transitions and two end restraints as one useful head harness. Then fixed yaw feed and remainder/source protection.',physical_pass=False,phase1_complete=False)
    dump(OUT/'head-wire-interface.json',interface)
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle,Circle
    old=read(ROOT/'hardware/electronics/full-cat/head-external-yaw-loop-r2/checks.json')
    fig,axes=plt.subplots(1,2,figsize=(12,5))
    for pose in old['loop_poses']:
        vs=pose['samples'];axes[0].plot([v[0] for v in vs],[v[1] for v in vs],label=f"yaw {pose['yaw']:+} / R{pose['radius_mm']:.2f}")
    axes[0].add_patch(Rectangle((-136,8),6,55,color='#3679a0',alpha=.3));axes[0].add_patch(Rectangle((-94,92),38,12,color='#e6a34c',alpha=.5));axes[0].plot(-84,91,'ko');axes[0].set_title('XY: loop at Z124 / fork arm / cover passage')
    axes[1].add_patch(Circle((-134,123),12,color='#3679a0',alpha=.3));axes[1].add_patch(Rectangle((-136,122),6,4,color='#234e68'));axes[1].set_xlim(-153,-116);axes[1].set_ylim(108,140);axes[1].set_title('XZ: round front relief / fork arm, nominal REST')
    for ax in axes:ax.set_aspect('equal');ax.grid(alpha=.2);ax.set_xlabel('X mm')
    axes[0].legend(fontsize=8);fig.suptitle('R21 changed interfaces only / full head harness still OPEN / no physical PASS');fig.tight_layout();fig.savefig(OUT/'preview.png',dpi=150);plt.close(fig)
    (OUT/'README.md').write_text('# R21: changed head wire interfaces\n\nThree replacement PETG prints, unchanged66 jobs/100installed parts/4samples. Nominal sampled interfaces clear; not whole head wiring or phase1 completion. JR storage, end transitions/restraints and fixed yaw feed are next. Slicer/prints/purchases/physical tests remain phase2. No new fasteners or purchased SKU.\n',encoding='utf-8')
    files=[Path(__file__),ROOT/'tools/cad/head_external_wire_support_r1.py',ROOT/'tools/cad/head_wire_support_finish_r1.py',PARENT/'selection.json',PARENT/'one-order-quantities.json',PARENT/'manifest.json',ROOT/'hardware/electronics/full-cat/head-external-yaw-loop-r1/checks.json',ROOT/'hardware/electronics/full-cat/head-external-yaw-loop-r2/checks.json']
    for folder in (CAD,OUT):files.extend(p for p in folder.iterdir() if p.is_file() and p.suffix!='.FCBak' and p.name!='manifest.json')
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in files}
    pins.update(read(ROOT/'hardware/electronics/full-cat/head-external-yaw-loop-r1/checks.json')['source_sha256'])
    pins.update(read(CAD/'plan.json')['parents_sha256'])
    for n,h in list(pins.items()):
        # plan keys are cached owner names, not path strings.
        if '/' not in n:del pins[n];pins[f'hardware/electronics/full-cat/head-external-yaw-loop-r1/{n}_REST.brep']=h
    assert all(sha(ROOT/p['stl'])==p['sha256'] for p in s['prints']) and len(s['prints'])==66 and s['installed_petg_parts']==100
    assert all(sha(ROOT/n)==h for n,h in pins.items())
    dump(OUT/'manifest.json',dict(files_sha256=pins,new_stls=3,selected_jobs=66,installed_petg_parts=100,phase1_complete=False,physical_pass=False))
    print(json.dumps(dict(jobs=66,installed_parts=100,pins=len(pins),new_stls=3)))
if __name__=='__main__':main()
