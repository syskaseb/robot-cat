"""One complete current material scene BEFORE further routing/native detail.

Reconcile retained R5 modules, bank48, Pi shared probe, received70part
cassette, actual BUS, frame/feet and current leg-rest material. A previous
P0-only cassette screen is explicitly NOT clearance against lower U1/F0/WAGO.
No scene/geometry changed to suppress a failure; no unchanged motion rerun.
"""
import hashlib
import json
import time
import zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import OUT,MODEL
from plan_feline_n01_bus_complete import main as bus_geometry


def pose(R,t):
    m=A.Matrix()
    for i in range(3):
        for j in range(3):setattr(m,f'A{i+1}{j+1}',R[i][j])
    return A.Placement(A.Vector(*t),A.Rotation(m))


def main():
    tick=time.monotonic();reader=SavedShapes()
    dest=OUT/'n01-full-material-scene.json';bundle=OUT/'n01-full-material-scene.zip'
    assert not dest.exists() and not bundle.exists(),'Receive saved whole scene first'
    names={'plan':'n01-module-plan-r5.json','rear':'n01-shared-preflight-r5.json',
        'bank':'n01-compact-bank-plan-r2.json','motion':'motion-layout.json',
        'shared':'n01-shared-probe.json','cassette':'n01-cassette-world-probe.json',
        'backbone':'n01-common-backbone-preflight-r4.json'}
    files={k:OUT/n for k,n in names.items()};p={k:json.loads(path.read_text()) for k,path in files.items()}
    native=OUT/'FelineInteriorMotion.FCStd';assert sha(native)==p['bank']['source_native_sha256']
    scene={};roles={};kinds={};origins={};changed=set()
    report=dict(status='BUILDING_COMPLETE_CURRENT_MATERIAL_SCENE',selected=False,N01_complete=False,
        physical_pass=False,native_changed=False,contacts=[],reservation_contacts=[],errors=[],
        pairs=0,invalid_sources=[],nonmaterial_sources=[],parts=[],
        source_sha256={path.relative_to(ROOT).as_posix():sha(path) for path in files.values()},
        scope='All received cassette70 and Pi shared material against ALL retained modules, including lower U1/F0/AUX/WAGO. Existing cassette scoped36pose result is not this full assembly test.',
        full_harness_and_motion_verified=False,
        repeated_unchanged_case_motion=False,retired_scaffold_recipes=[],unmaterialized_scaffold_recipes=[])
    def save():
        report['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    def gate():
        if time.monotonic()-tick>240:raise TimeoutError('240s full-scene stage cap; retain snapshot')
    def add(n,s,role,kind,origin):
        assert n not in scene,n
        scene[n]=s;roles[n]=role;kinds[n]=kind;origins[n]=origin
    def load_bundle(meta,key,role,exclude=()):
        path=ROOT/meta[key];h=meta[key+'_sha256'];assert sha(path)==h,path
        with zipfile.ZipFile(path) as z:
            for row in meta['parts']:
                n=row['name']
                if n in exclude:continue
                data=z.read(row['entry']);assert hashlib.sha256(data).hexdigest()==row['sha256']
                s=Part.Shape();s.importBrepFromString(data.decode('utf-8'))
                add(n,s,role,row['kind'],path.relative_to(ROOT).as_posix());changed.add(n)
    load_bundle(p['cassette'],'bundle','CurrentCassette')
    replace=set(scene)
    load_bundle(p['shared'],'shared_probe','CurrentPiAndShared',exclude=replace)
    replace=set(scene)
    bus,bw,br,broot,bp=bus_geometry(geometry_only=True)
    for n,s in bus.items():add(n,s,'BUS','purchased', 'received_BUS_r3')
    for n,s in {**bw,**br,**{n:s for n,s in broot.items() if not n.startswith('InheritedRearPost')}}.items():
        add('CurrentBUS:'+n,s,'BUS','wire' if n in bw else 'reservation','received_BUS_r3')
    moved=p['rear']['changed_complete_receiving_groups'];rot=p['rear']['relative_rotations']
    for g in p['plan']['groups']:
        role=g['role']
        if role=='BUS':continue
        for n in g['objects']:
            gate()
            if n in replace:continue
            s=reader.shape(native,n)
            if role in moved:s.Placement=pose(rot.get(role,[[1,0,0],[0,1,0],[0,0,1]]),moved[role])*s.Placement
            if role=='JPWM':s.translate(A.Vector(-90,44,30))
            add(n,s,role,'purchased_or_retained_module','retained_current_R5')
    for key,r in p['bank']['relative_holder_poses'].items():
        T=pose(r['rotation_rows'],r['translation_mm'])
        for kind in ('Housing','IN','OUT','ATO'):
            n=f'Ref_Material_F_{key}_CP2_{kind}_0_0'
            scene[n].Placement=T*scene[n].Placement
    moving={n:(c,st) for c,g in p['motion']['membership'].items() for st,ns in g.items() for n in ns}
    for row in p['motion']['inventory']:
        n=row['object']
        if n in scene or row['kind']!='surface' or n.startswith('BatteryFrameHardware'):continue
        if n in moving:
            add(n,reader.shape(MODEL,n),'leg:'+':'.join(moving[n]),'moving_rest_material','retained_P0_world')
        elif n.startswith(('Print_P0_','Ref_Material_P0_','Battery','Print_CP2_TailRiser')):
            add(n,reader.shape(native,n),'P0_or_battery','retained_fixed_material','retained_P0_world')
    for i in range(1,5):add(f'BellyFoot{i}',reader.shape(OUT/'FelineBellyFeet.FCStd',f'BellyFoot{i}'),'BellyFeet','retained_fixed_material','received_four_native_feet')
    # Do not insert arbitrary filled boxes for shaped/holed parent recipes.
    # Materialize explicitly rectangular reservations only and mark the rest.
    retired=('LowerDeck','OutputWing','LowerDeckRoot','PiFuse','MainRaisedBridge','Standoff_MAIN','Standoff_BUS','SelectedSolderSpliceClip')
    for row in p['backbone']['recipes']:
        n=row['name'];key='StructureReserve:'+n
        if key in scene:continue
        if n.startswith(retired):report['retired_scaffold_recipes'].append(n);continue
        if 'low_mm' not in row:
            report['unmaterialized_scaffold_recipes'].append(n);continue
        lo,hi=row['low_mm'],row['high_mm']
        add(key,Part.makeBox(*(b-a for a,b in zip(lo,hi)),A.Vector(*lo)),
            'ScaffoldPlanning','rectangular_reservation','backbone_R4_rectangular_recipe_only')
    bounds={n:s.BoundBox for n,s in scene.items()};valid={n:s.isValid() and bool(s.Solids) for n,s in scene.items()}
    for n,s in scene.items():
        if not s.Solids:report['nonmaterial_sources'].append(n)
        elif not valid[n]:report['invalid_sources'].append(dict(object=n,role=roles[n],known_BUS_rotation_issue=roles[n]=='BUS'))
    save()
    with zipfile.ZipFile(bundle,'x',compression=zipfile.ZIP_DEFLATED) as z:
        for i,(n,s) in enumerate(scene.items()):
            gate();raw=s.exportBrepToString().encode('utf-8');entry=f'{i:04d}.brep';z.writestr(entry,raw);b=bounds[n]
            report['parts'].append(dict(name=n,entry=entry,role=roles[n],kind=kinds[n],origin=origins[n],valid=valid[n],solids=len(s.Solids),
                sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=[[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]],volume_mm3=s.Volume))
    report.update(bundle=bundle.relative_to(ROOT).as_posix(),bundle_sha256=sha(bundle),parts_count=len(scene))
    save();print('Complete scene saved',len(scene),'invalid',len(report['invalid_sources']),flush=True)
    try:
        targets={n:s for n,s in scene.items() if n not in changed and not roles[n].startswith('leg:')}
        for n in changed:
            for m,t in targets.items():
                gate()
                if not bounds[n].intersect(bounds[m]):continue
                report['pairs']+=1
                if not (valid[n] and valid[m]):
                    report['errors'].append(dict(a=n,b=m,error='Invalid/nonmaterial candidate pair is not clearance'));continue
                c=scene[n].common(t);assert c.isNull() or c.isValid(),(n,m)
                if c.Volume>1e-5:
                    key='reservation_contacts' if 'reservation' in kinds[n] or 'reservation' in kinds[m] else 'contacts'
                    b=c.BoundBox
                    report[key].append(dict(a=n,b=m,a_role=roles[n],b_role=roles[m],volume_mm3=c.Volume,
                        witness_bounds_mm=[[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]]))
                if report['pairs']%20==0:save()
        report['status']='FULL_CURRENT_MODULE_DEPENDENCY_REJECTED' if report['contacts'] or report['reservation_contacts'] or report['errors'] else 'FULL_CURRENT_MODULE_DEPENDENCY_CLEAR_UNMATERIALIZED_RECIPES_WIRING_TOOLS_OPEN'
    except Exception as exc:
        report['errors'].append(repr(exc));report['status']='FULL_CURRENT_MODULE_DEPENDENCY_INCOMPLETE'
    report['source_sha256'].update(reader.hashes)
    report['source_sha256'][Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
    report['new_scope_percent']=0
    save();print(json.dumps({k:report[k] for k in ('status','parts_count','pairs','worker_seconds')})+' actual='+str(len(report['contacts']))+' reservations='+str(len(report['reservation_contacts']))+' errors='+str(len(report['errors'])),flush=True)


if __name__=='__main__':main()
