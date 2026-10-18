"""Canonical read-only planning scene, ordered overlays and current port pose.

Not a selected assembly or complete wiring. Keeps unknown/invalid suppliers
explicit; world-posed saved BReps are never placed a second time.
"""
import hashlib
import json
import zipfile
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT


def box(lo,hi):
    return Part.makeBox(*(b-a for a,b in zip(lo,hi)),A.Vector(*lo))


def load(negative_row=False,upper_rows=False):
    files={k:OUT/n for k,n in dict(scene='n01-full-material-scene.json',
        lower='n01-lower-bay-world-probe.json',common='n01-common-restraint-world-probe.json',
        extra='n01-remaining-selected-inventory.json',packet='n01-current-endpoint-packet-r3.json',
        ports='n01-twenty-wago-port-contract.json').items()}
    data={k:json.loads(f.read_text()) for k,f in files.items()};scene={};meta={};templates={}
    pins={f.relative_to(ROOT).as_posix():sha(f) for f in files.values()}
    retired={'StructureReserve:NineWire'+k+c for k in ('Cuff','Arm') for c in ('FL','FR','RL','RR')}
    for key in ('scene','lower','common','extra'):
        p=data[key];bundle=ROOT/p['bundle'];assert sha(bundle)==p['bundle_sha256']
        pins[bundle.relative_to(ROOT).as_posix()]=p['bundle_sha256']
        with zipfile.ZipFile(bundle) as z:
            for r in p['parts']:
                n=r['name']
                if r.get('role')=='CurrentCassette' or n in retired:continue
                raw=z.read(r['entry']);assert hashlib.sha256(raw).hexdigest()==r['sha256'],n
                s=Part.Shape();s.importBrepFromString(raw.decode('utf-8'))
                if key=='extra' and not r['placed_current']:
                    templates[r['role']]=(n,s,r);continue
                scene[n]=s;meta[n]=r
    pose=data['packet']['changed_scene_groups']['POST_F0'];m=A.Matrix()
    for i in range(3):
        for j in range(3):setattr(m,f'A{i+1}{j+1}',pose['relative_rotation_rows'][i][j])
    c=A.Vector(*pose['centre_mm']);rot=A.Rotation(m);tf=A.Placement(c-rot.multVec(c),rot)
    for n,s in scene.items():
        if meta[n].get('role')=='POST_F0':s.Placement=tf*s.Placement
    scene['NominalPiUSBCPowerMould']=box(*data['packet']['nominal_Pi_USB_C_mould']['bounds_mm'])
    meta['NominalPiUSBCPowerMould']=dict(role='Pi4',kind='project_mating_reservation')
    changes=[]
    if negative_row or upper_rows:
        for st in data['ports']['stations']:
            ref=st['ref']
            negative=ref in ('G_TAIL','G_AUX','P_AUX','G2','FL_P')
            positive=ref in ('D_FL','FL_G','FR_P','D_FR','FR_G')
            if not negative and not (upper_rows and positive):continue
            matches=[n for n,r in meta.items() if r.get('role')==st['current_group']]
            assert len(matches)==1,(ref,matches)
            n=matches[0];s=scene[n];centre=s.BoundBox.Center
            flip=ref in ('G_TAIL','G_AUX','P_AUX');rot=A.Rotation(A.Vector(0,0,1),180 if flip else 0)
            tf=A.Placement(centre+A.Vector(5 if upper_rows else 0,0,6.1)-rot.multVec(centre),rot)
            s.Placement=tf*s.Placement
            for p in st['occupied_ports']:
                p['point_mm']=list(tf.multVec(A.Vector(*p['point_mm'])))
                p['departure_axis']=list(rot.multVec(A.Vector(*p['departure_axis'])))
                assert abs(p['point_mm'][2]-46.1)<2e-5
                assert p['departure_axis'][1]*(1 if negative else -1)>.99
            changes.append(dict(ref=ref,name=n,flip_Z180=flip,mouth_Z_mm=46.1,
                occupied_ports=len(st['occupied_ports']),relative_placement=str(tf)))
        assert len(changes)==(10 if upper_rows else 5)
        if not upper_rows:assert sum(r['occupied_ports'] for r in changes)==22
    return scene,meta,templates,data,pins,changes
