"""Plan native Assembly constraints from existing rigid leg hierarchy.

No invented axes: each leg pivot comes from a radius-9.6 cylindrical horn
surface in the saved model. Unresolved head/tail/electronics mounts are
explicit temporary kinematic locks, not physical design approval.
"""
from pathlib import Path
import ast,json
import FreeCAD as A
import Part
from probe21 import world,visible_names
from build22 import sha
ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'hardware/skorupa/v23/Kot_v23_AKUMULATOR_PETG.FCStd'
OUT=ROOT/'hardware/skorupa/v24'

def main():
    OUT.mkdir(exist_ok=True)
    d=A.openDocument(str(SOURCE)); vis=visible_names(SOURCE)
    leaves={o.Name:o for o in d.Objects if o.Name in vis and o.isDerivedFrom('Part::Feature') and not o.Shape.isNull() and not o.Name.startswith('Axis_')}
    tree=ast.parse((ROOT/'tools/freecad/WAVEGO_Motion.FCMacro').read_text(encoding='utf-8'))
    legs=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='LEGS' for t in n.targets))
    joints=[]; mapped={}; axes=[]
    def bylabel(label):
        xs=d.getObjectsByLabel(label); assert len(xs)==1,label
        return xs[0]
    def stage(obj):
        p=obj.getParentGeoFeatureGroup()
        while p:
            if p.Name.startswith('Motion_'): return p.Name
            p=p.getParentGeoFeatureGroup()
        return None
    for code,spec in legs.items():
        reps=[bylabel(spec['connector']),bylabel(spec['links'][0]),bylabel(spec['bracket'])]
        for i,(suffix,rep,servo) in enumerate(zip(['Hip','Knee','Ankle'],reps,spec['servos'])):
            group='Motion_'+code+'_'+suffix
            number=int(servo.rsplit('_',1)[1]); hn='HornDisc_Drive_v'+('2' if number==1 else '%03d'%(number-1))
            horn=bylabel(hn); s=world(horn)
            found=[(j,f.Surface) for j,f in enumerate(s.Faces,1) if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-9.6)<1e-5]
            assert len(found)==1,hn
            face,surf=found[0]; pos=list(surf.Center); axis=list(surf.Axis)
            # Historic FR/RR labels predate the cat head at negative X.
            physical=('Front' if pos[0]<21 else 'Rear')+('Left' if pos[1]>0 else 'Right')
            axisrow=dict(code=code,stage=suffix,physical_leg=physical,horn=horn.Name,face=face,pivot_mm=pos,axis=axis)
            axes.append(axisrow)
            parent=leaves['FrameFront20'] if i==0 else reps[i-1]
            joints.append(dict(name='Rev_'+code+'_'+suffix,type='Revolute',parent=parent.Name,child=rep.Name,
                pivot_mm=pos,axis=axis,status='measured horn axis',label=physical+' / '+suffix))
            mapped[rep.Name]=group
            for n,o in leaves.items():
                if stage(o)==group and n!=rep.Name:
                    assert n not in mapped,n
                    mapped[n]=group
                    joints.append(dict(name='Fix_'+n,type='Fixed',parent=rep.Name,child=n,status='rigid leg member from repaired source hierarchy'))
    # Tree topology avoids redundant bolt loops. All bolts/nuts still move
    # rigidly with their carriers; a second fixed edge adds no constraint.
    specific={'FrameRear20':'FrameFront20','SideLeft22':'FrameFront20','SideRight22':'FrameFront20',
        'Part__Feature005':'FrameFront20','Part__Feature038':'FrameFront20',
        'BatteryCarrier23':'Part__Feature005','Battery':'BatteryCarrier23','BatteryLiner23':'BatteryCarrier23',
        'BatteryStrap123':'BatteryCarrier23','BatteryStrap223':'BatteryCarrier23',
        'Belly22':'SideLeft22','ShellMounted20':'MountFrontL','PiTray18':'ShellMounted20','PiTray19':'ShellMounted20'}
    for n,o in leaves.items():
        if n in mapped or n=='FrameFront20': continue
        parent=specific.get(n,'FrameFront20')
        if n.startswith(('BatteryScrew','BatteryNut')): parent='BatteryCarrier23'
        elif n.startswith('BellyScrew'): parent='Belly22'
        elif n.startswith('BellyNut'): parent='SideLeft22' if n.endswith('L') else 'SideRight22'
        elif n.startswith(('Mount','NutShoe')): parent='FrameFront20' if 'Front' in n else 'FrameRear20'
        elif n.startswith(('ShellScrew','ShellNut')): parent='ShellMounted20'
        elif n.startswith(('FrameScrew','FrameNut')): parent='FrameFront20' if 'Front' in n else 'FrameRear20'
        assert parent in leaves,(n,parent)
        verified=n in specific or n.startswith(('BatteryScrew','BatteryNut','BellyScrew','BellyNut','Mount','NutShoe','ShellScrew','ShellNut','FrameScrew','FrameNut')) or n.startswith('Part__Feature')
        joints.append(dict(name='Fix_'+n,type='Fixed',parent=parent,child=n,
            status='rigid assembly retention' if verified else 'TEMPORARY LOCK: physical attachment/actuation not certified'))
        mapped[n]='Chassis'
    assert len(joints)==len(leaves)-1
    parents={j['child']:j['parent'] for j in joints}
    for n in leaves:
        chain=set()
        while n!='FrameFront20':
            assert n not in chain,n
            chain.add(n); n=parents[n]
    report=dict(source_sha256=sha(SOURCE),ground='FrameFront20',components=[dict(name=n,label=o.Label,stage=mapped.get(n,'Chassis')) for n,o in leaves.items()],
        joints=joints,axes=axes,revolute_count=sum(j['type']=='Revolute' for j in joints),
        fixed_count=sum(j['type']=='Fixed' for j in joints),
        temporary_locks=[j['child'] for j in joints if j['status'].startswith('TEMPORARY')],
        scope='12 leg DOF. Head/tail and unfinished physical mounts temporarily fixed. No load/contact dynamics or collision-free gait claim.')
    assert report['revolute_count']==12
    (OUT/'assembly-plan.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['revolute_count','fixed_count','temporary_locks']}),flush=True)
if __name__=='__main__': main()
