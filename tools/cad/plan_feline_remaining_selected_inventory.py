"""Close the selected-material universe before more detailed/pose qualification.

Retain ALL60tail mechanism pieces, three omitted FHAC bodies, F_PWM sleeve
and the selected-stage monitor reference. Old neck replacement stays explicit.
Also replace the USB branch's connection face as one bounded coherent change.
"""
import hashlib
import json
import sys
import time
import zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import OUT,BASE,MODEL


def main():
    tick=time.monotonic();dest=OUT/'n01-remaining-selected-inventory.json';bundle=dest.with_suffix('.zip')
    resume='--resume-monitor-source' in sys.argv
    if resume:
        old=json.loads(dest.read_text());assert old['status']=='SELECTED_INVENTORY_PARTIAL' and old['errors']==["KeyError('Monitor_CP2')"]
        assert len(old['parts'])==64 and sha(bundle)==old['bundle_sha256']
    else:assert not dest.exists() and not bundle.exists()
    files={k:OUT/n for k,n in dict(scene='n01-full-material-scene.json',lower='n01-lower-bay-world-probe.json',
        common='n01-common-restraint-world-probe.json',motion='motion-layout.json').items()}
    p={k:json.loads(f.read_text()) for k,f in files.items()};reader=SavedShapes();shapes={};rows=[]
    report=dict(status='READING_SELECTED_INVENTORY_AND_USB_FACE_CHANGE',selected=False,N01_complete=False,
        physical_pass=False,parts=rows,missing_before=[],old_neck_replacement_pending=[],
        placed_tail_source_unchanged=True,three_FHAC_and_monitor_placement_open=True,
        USB_contacts=[],USB_root_mating=[],errors=[],USB_pairs=0,
        source_sha256={f.relative_to(ROOT).as_posix():sha(f) for f in (*files.values(),Path(__file__))})
    if resume:
        with zipfile.ZipFile(bundle) as zz:
            for r in old['parts']:
                raw=zz.read(r['entry']);assert hashlib.sha256(raw).hexdigest()==r['sha256']
                s=Part.Shape();s.importBrepFromString(raw.decode('utf-8'));shapes[r['name']]=s;rows.append(r)
        report['old_neck_replacement_pending']=old['old_neck_replacement_pending']
        report['missing_before']=[r['name'] for r in rows];report['saved64_source_shapes_reused']=True
        for n,h in old['source_sha256'].items():
            if n.endswith('.FCStd'):assert sha(ROOT/n)==h;report['source_sha256'][n]=h
    def save():
        report['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    def gate():
        if time.monotonic()-tick>240:raise TimeoutError('240s selected-universe budget')
    def add(n,s,role,source,obj,placed):
        assert s.isValid() and s.Solids,n
        shapes[n]=s;b=s.BoundBox
        rows.append(dict(name=n,role=role,source=source.relative_to(ROOT).as_posix(),object=obj,placed_current=placed,
            bounds_mm=[[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]],volume_mm3=s.Volume))
    save()
    try:
        represented={r['name'] for r in p['scene']['parts']}
        for r in p['motion']['inventory']:
            gate();n=r['object'];label=r['label']
            if r['kind']!='surface' or n in represented or n in shapes:continue
            if label.startswith('tail/'):
                add(n,reader.shape(MODEL,n),'RetainedTailMechanism',MODEL,n,True);report['missing_before'].append(n)
            elif n in ('Ref_Material_W3Ref_F_HY_case_0_0','Ref_Material_W3Ref_F_HP_case_0_0','Ref_Material_W4_F_TY_case_0_0','Ref_Material_F_PWM_sleeve_0_0'):
                role='F_PWM' if 'PWM' in n else 'F_HY' if 'F_HY' in n else 'F_HP' if 'F_HP' in n else 'F_TY'
                add(n,reader.shape(MODEL,n),role,MODEL,n,False);report['missing_before'].append(n)
            elif label.startswith('neck/'):
                if resume:continue
                report['old_neck_replacement_pending'].append(dict(name=n,label=label,
                    reason='New4M3head root/triangular webs proposed; original neck tower is not silently reselected or absent as clearance'))
        # Current mounting document contains the seats/slots, not a monitor
        # component. The inherited nominal reference is in its source plan.
        monitor=BASE/'OpenPrototypePlan.FCStd'
        add('SelectedMonitor5015Reference',reader.shape(monitor,'Monitor_CP2'),'Monitor5015',monitor,'Monitor_CP2',False)
        report['missing_before'].append('SelectedMonitor5015Reference')
        assert sum(r['role']=='RetainedTailMechanism' for r in rows)==60
        assert {r['role'] for r in rows if r['role']!='RetainedTailMechanism'}=={'F_HY','F_HP','F_TY','F_PWM','Monitor5015'}
        # Inboard-Y coupling avoids shrinking rear corner; whole cable and
        # after-bend clamp stay fixed, no another X offset of the old knuckle.
        x=128.5304752678421;y=-71.90814337545011;z=51.60996202870123
        points=[np.array(q) for q in ([105,-36,64],[105,-60,58],[x,-60,58],[x,y+3.9,z])]
        def beam(a,b,w):
            d=b-a;v=np.array([-d[1],d[0],0]);v=v/np.linalg.norm(v);profiles=[]
            for q in (a,b):
                vv=[A.Vector(*(q+v*u+[0,0,h])) for u,h in ((-w/2,-1.5),(w/2,-1.5),(w/2,1.5),(-w/2,1.5))]
                profiles.append(Part.makePolygon(vv+[vv[0]]))
            return Part.makeLoft(profiles,True,True)
        arm=beam(points[0],points[1],6)
        for a,b in zip(points[1:],points[2:]):arm=arm.fuse(beam(a,b,4))
        for q in points[1:-1]:arm=arm.fuse(Part.makeBox(4,4,3,A.Vector(*(q-[2,2,1.5]))))
        arm=arm.removeSplitter();assert arm.isValid() and len(arm.Solids)==1
        add('CurrentBUS:USB_DiagonalArm',arm,'USB_current_inboard_face_root',Path(__file__),'planned_root',True)
        report['USB_whole_path_mm']=[q.tolist() for q in points]
        scene={};meta={}
        retired={'StructureReserve:NineWire'+kind+code for kind in ('Cuff','Arm') for code in ('FL','FR','RL','RR')}
        for key in ('scene','lower','common'):
            probe=p[key];path=ROOT/probe['bundle'];assert sha(path)==probe['bundle_sha256']
            with zipfile.ZipFile(path) as zz:
                for r in probe['parts']:
                    n=r['name']
                    if r.get('role')=='CurrentCassette' or n in retired or n=='CurrentBUS:USB_DiagonalArm':continue
                    s=Part.Shape();s.importBrepFromString(zz.read(r['entry']).decode('utf-8'));scene[n]=s;meta[n]=r
        for r in rows:
            if r['role']=='RetainedTailMechanism':scene[r['name']]=shapes[r['name']];meta[r['name']]=r
        for n,s in scene.items():
            gate()
            if not arm.BoundBox.intersect(s.BoundBox):continue
            report['USB_pairs']+=1
            assert s.isValid() and s.Solids,(n,'Invalid candidate')
            c=arm.common(s);assert c.isNull() or c.isValid(),n
            if c.Volume>1e-5:
                row=dict(part=n,volume_mm3=c.Volume)
                if n in ('CurrentBUS:USB_AfterBendRelief','BundleCuff:RR'):report['USB_root_mating'].append(row)
                else:report['USB_contacts'].append(row)
        assert {r['part'] for r in report['USB_root_mating']}=={'CurrentBUS:USB_AfterBendRelief','BundleCuff:RR'}
        cable=scene['CurrentBUS:USB_CableFirst'];report['USB_full_cable_gap_mm']=arm.distToShape(cable)[0]
        outer=reader.shape(OUT/'central-cassette-envelope/FelineLayoutEnvelope.FCStd','TorsoEnvelope')
        diff=arm.cut(outer);assert diff.isNull() or diff.isValid()
        report['USB_outside_mm3']=diff.Volume;report['USB_boundary_gap_mm']=arm.distToShape(Part.makeCompound(outer.Shells))[0]
        report['USB_root_scoped_clear']=not report['USB_contacts'] and diff.Volume<1e-5 and report['USB_boundary_gap_mm']>=3.65-1e-5 and report['USB_full_cable_gap_mm']>=1.25-1e-5
        report['status']='SELECTED_INVENTORY_RECEIVED_USB_ROOT_SCOPED_CLEAR_LAYOUT_OPEN' if report['USB_root_scoped_clear'] else 'SELECTED_INVENTORY_RECEIVED_USB_ROOT_REJECTED'
    except Exception as exc:report['errors'].append(repr(exc));report['status']='SELECTED_INVENTORY_PARTIAL'
    with zipfile.ZipFile(bundle,'a' if resume else 'x',compression=zipfile.ZIP_DEFLATED) as zz:
        existing=set(zz.namelist())
        for i,r in enumerate(rows):
            entry=f'{i:03d}.brep'
            if entry in existing:
                raw=zz.read(entry);assert hashlib.sha256(raw).hexdigest()==r['sha256']
            else:
                raw=shapes[r['name']].exportBrepToString().encode('utf-8');zz.writestr(entry,raw)
            r.update(entry=entry,sha256=hashlib.sha256(raw).hexdigest())
    report.update(bundle=bundle.relative_to(ROOT).as_posix(),bundle_sha256=sha(bundle))
    report['source_sha256'].update(reader.hashes)
    report['next']='Allocate3FHAC and monitor WITH all20WAGO/46additionalECAD wire segments, retained60tail and head truss/33oldneck replacements; do not claim805scene complete or run more isolated mounts.'
    save();print(json.dumps({k:report[k] for k in ('status','worker_seconds','USB_pairs','errors')})+' parts='+str(len(rows)),flush=True)


if __name__=='__main__':main()
