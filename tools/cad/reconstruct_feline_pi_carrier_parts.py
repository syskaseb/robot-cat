"""Reconstruct known carrier features without fragile sequential global fusions.

Planning components only. No native replacement or unchanged-geometry claim.
The fixed PWM root and split joint are deliberately outside this reconstruction.
"""
import json,math,time,zipfile,hashlib
import numpy as np
import FreeCAD as A
import Part
from feline_shared_pi_carrier import saddle,placement,circle_arc,pipe
from receive_feline_pi_split_service_space import independent
from feline_solid_distance import bbox_lower_bound
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from check_main_p0_placement import ROOT,sha
from pathlib import Path


def build(scene,recipe):
    tick=time.monotonic();parts={};cuts=[];errors={}
    def put(name,s):
        assert s.isValid() and s.Solids
        parts[name]=s
    def rod(name,a,b,r=1.5):
        a=np.array(a);b=np.array(b);v=b-a
        put(name,Part.makeCylinder(r,float(np.linalg.norm(v)),A.Vector(*a),A.Vector(*v)))
        put(name+':round',Part.makeSphere(r,A.Vector(*b)))
    def bar(name,a,b):
        a=np.array(a);b=np.array(b);t=(b-a)/np.linalg.norm(b-a);u=np.array([-t[1],t[0],0])
        s=Part.makeBox(float(np.linalg.norm(b-a)),4,1.6,A.Vector(0,-2,0))
        s.Placement=placement(np.column_stack([t,u,[0,0,1]]),a)*s.Placement;put(name,s)
    stem=np.array(recipe['Pi_actual_root']['stem_mm']);anchor=recipe['Pi_actual_root']['point_mm']
    put('root_ball',Part.makeSphere(2,A.Vector(*anchor)));rod('common_root',anchor,stem)
    axes=recipe['Pi_top_actual_axes_mm'];fore=min(y for x,y in axes);rear=max(y for x,y in axes)
    rod('fore_left_entry',stem,[-.5,fore,105.6])
    bar('top_fore_rail',[-.5,fore,104.8],[57.5,fore,104.8])
    bar('right_U_rail',[57.5,fore,104.8],[57.5,rear,104.8])
    bar('top_rear_rail',[-.5,rear,104.8],[57.5,rear,104.8])
    for i,(x,y) in enumerate(axes):put('M2_pad'+str(i),Part.makeCylinder(3.5,1.6,A.Vector(x,y,104.8)))
    ends={e['name']:e for e in recipe['new_Pi_full_ends']}
    four=[ends['PiGPIO:'+n] for n in ('PI.H3','PI.H5','PI.H6','PI.H11')]
    h1=ends['PiGPIO:PI.H1'];t1=(np.array(h1['full9_mm'][1])-h1['full9_mm'][0])/9
    t=np.array([math.sqrt(.5),math.sqrt(.5),0]);entry=np.array(h1['full9_mm'][1])+.75*t1
    end4=np.mean([e['full9_mm'][0] for e in four],axis=0)+9.75*t
    rod('outside_PCB_column',stem,[-6,stem[1],87.3])
    rod('H1_after_strap_entry',[-6,stem[1],87.3],[entry[0],entry[1],87.3])
    rod('H1_after_strap_post',[entry[0],entry[1],87.3],[entry[0],entry[1],77.55])
    rod('GPIO_above_whole_head',[-6,stem[1],87.3],[end4[0],end4[1],87.3])
    rod('GPIO_after_strap_post',[end4[0],end4[1],87.3],[end4[0],end4[1],77.55])
    rod('upper_USB_beam',[59.5,29,107.1],[118.5,28.8581096347,107.1])
    rod('USB_pad_post',[118.5,28.8581096347,107.1],[118.5,28.8581096347,102.9])
    rod('upper_power_beam',[91,29,106.38],[110.65,72.2681096347,107.1])
    rod('power_pad_post',[110.65,72.2681096347,107.1],[110.65,72.2681096347,105.6])
    groups=[('GPIO4',[(e['full9_mm'][0],t) for e in four],.7),
            ('H1',[(h1['full9_mm'][0],t1)],.7),
            ('Power2',[(ends['PiPower:'+w]['full9_mm'][0],[0,1,0]) for w in ('W079','W080')],1.55)]
    for name,lands,r in groups:put(name+':pad',saddle(lands,r)[0])
    b=scene['PiBudget:UnlabelledTopComponentsBudget'].BoundBox
    cuts.append(('PCB_keepout',Part.makeBox(b.XLength+2.5,b.YLength+2.5,104.8-(b.ZMin-1.25),A.Vector(b.XMin-1.25,b.YMin-1.25,b.ZMin-1.25))))
    for e in [*four,h1]:
        q=np.array(e['point_mm']);d=np.array(e['axis']);b=np.array(e.get('independent_bend',[math.sqrt(.5),math.sqrt(.5),0]))
        first=q+1.5*d;arcend=first+10*(d+b);tip=np.array(e['full9_mm'][1])+3*b
        tool,_=pipe([Part.makeLine(A.Vector(*q),A.Vector(*first)),circle_arc(first,d,b,10,math.pi/2),Part.makeLine(A.Vector(*arcend),A.Vector(*tip))],.85)
        cuts.append((e['name'],tool))
    cuts.extend((n,s) for n,s in scene.items() if n.startswith(('PiGrip:','USBGrip:Pi:')))
    for n,s in scene.items():
        if n.startswith('Ref_Material_Pi4') and 'Screw' in n:
            b=s.BoundBox;c=b.Center;cuts.append((n+':tool',Part.makeCylinder(2.5,30,A.Vector(c.x,c.y,b.ZMax-2))))
    cuts.extend(('M2_hole'+str(i),Part.makeCylinder(1.2,15,A.Vector(x,y,100))) for i,(x,y) in enumerate(axes))
    for name in list(parts):
        s=parts[name]
        try:
            assert not s.check(True)
            for label,tool in cuts:
                if bbox_lower_bound(s.BoundBox,tool.BoundBox)>1e-6:continue
                s=s.cut(independent(tool))
                if s.isNull() or not s.Solids:break
                assert not s.check(True),label
            if s.isNull() or not s.Solids:del parts[name]
            else:parts[name]=s
        except Exception as exc:errors[name]=str(exc)
        print('COMPONENT',name,'HOLD' if name in errors else 'valid',flush=True)
    report=dict(status='UNFUSED_COMPONENT_RECONSTRUCTION_ONLY',strict_errors=errors,
                component_count=len(parts),worker_seconds=round(time.monotonic()-tick,3),
                omitted=['Fixed PWM root','USB pad: load exact received source before complete assembly',
                         'Split joint and updated removable USB detail'],
                equivalent_union_proven=False,load_path_proven=False,N01_complete=False,physical_pass=False)
    save_json(OUT/'n01-Pi-component-reconstruction-20261024.json',report)
    return parts,report


def save_parts(parts,report):
    assert not report['strict_errors']
    archive=OUT/'n01-Pi-component-reconstruction-20261024.breps.zip';rows=[]
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
        for name,s in parts.items():
            assert s.isValid() and s.Solids and not s.check(True)
            data=s.exportBrepToString().encode();entry=str(len(rows))+'.brep'
            z.writestr(entry,data)
            reopened=Part.Shape();reopened.importBrepFromString(data.decode())
            assert not reopened.check(True)
            rows.append(dict(name=name,entry=entry,sha256=hashlib.sha256(data).hexdigest(),strict_reopen=True))
    report.update(geometry=rows,bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),
                  source_sha256={str(Path(__file__).relative_to(ROOT)).replace('\\','/'):sha(Path(__file__)),
                                 'n01-shared-Pi-carrier-r3-core-received.json':sha(OUT/'n01-shared-Pi-carrier-r3-core-received.json')})
    save_json(OUT/'n01-Pi-component-reconstruction-20261024.json',report)
    return report
