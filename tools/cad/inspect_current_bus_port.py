"""Bind the official D/V/G photograph to actual supplier header pin geometry.

Pin columns come from metal below the PCB, not a casing bbox split into thirds.
The factory mating plug dimensions and received revision still require fit.
"""
import json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(sys.executable).resolve().parent.parent/'lib'))
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,SavedShapes,sha
BASE=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype'
OUT=BASE/'body-harness-checkpoint'
SOURCE=ROOT/'hardware/electronics/full-cat/pi-bus-primary-r1'

def run():
    tick=time.monotonic();ports={};reader=SavedShapes()
    model=BASE/'mounting-checkpoint/CurrentBoardMounts.FCStd'
    raw=Part.read(str(SOURCE/'PCB.brep'))
    # Derive the transform from the actual retained supplier solid, not a
    # second hand-maintained board placement. Invalid compound is datums ONLY.
    placement=reader.shape(model,'BUSsupplier0').Placement*raw.Solids[0].Placement.inverse()
    for index in (0,1,2):
        before=raw.Solids[index].copy();before.Placement=placement*before.Placement
        saved=reader.shape(model,'BUSsupplier'+str(index))
        assert (before.Solids[0].CenterOfMass-saved.Solids[0].CenterOfMass).Length<1e-6
        assert abs(before.Volume-saved.Volume)<1e-6
    pins={model,SOURCE/'PCB.brep'}
    for name in ('H3','H5'):
        f=SOURCE/(name+'.brep');pins.add(f);s=Part.read(str(f));assert s.isValid()
        b=s.BoundBox
        slab=Part.makeBox(b.XLength+2,b.YLength+2,.1,A.Vector(b.XMin-1,b.YMin-1,-2))
        tails=s.common(slab);assert tails.isValid() and len(tails.Solids)==3,(name,len(tails.Solids))
        columns=[]
        for role,q in zip(('D','V','G'),sorted(tails.Solids,key=lambda q:q.CenterOfMass.x)):
            centre=q.CenterOfMass;xy=[centre.x,centre.y]
            point=placement.multVec(A.Vector(*xy,b.ZMax))
            columns.append(dict(role=role,raw_tail_section_centre_xy_mm=xy,
                world_header_top_reference_mm=list(point),
                reference_is_not_mating_plug_contact_or_exit=True,tail_section_volume_mm3=q.Volume))
        ports[name]=dict(valid_supplier_shape=True,pin_columns=columns,
            supplier_header_top_raw_z_mm=b.ZMax)
    cf=SOURCE/'catalog.json';pins.add(cf);catalog=json.loads(cf.read_text())
    usb=next(q for q in catalog['parts'] if q['name']=='Type_C1')
    dc=next(q for q in catalog['parts'] if q['name']=='DC1')
    assert (usb['bounds'][0]+usb['bounds'][3])>(dc['bounds'][0]+dc['bounds'][3])
    photo=OUT/'BUS-official-interface.webp';pins.add(photo)
    result=dict(status='OFFICIAL_PHOTO_AND_SUPPLIER_PIN_COLUMNS_BOUND_PLUG_FIT_OPEN',
        ports=ports,placement_translation_mm=list(placement.Base),rotation_z_deg=90,
        primary_photo_url='https://docs.waveshare.com/assets/images/Bus_Servo_Adapter%28A%29-interface-introduction-a9c1c2c311eaf43dc359366562e4db91.webp',
        primary_page_url='https://docs.waveshare.com/Bus_Servo_Adapter_A',
        binding_basis='Official top-side image: USB lower-right, DC lower-left; both top3pin headers D/V/G in increasing board X. Actual supplier model has matching USB/DC orientation and three separate metal tail sections. This is manufacturer-revision binding, NOT cable-colour or reverse plug-view inference.',
        installed_candidate_header='H5',V_contact_and_wire_removed_before_installation=True,
        placement_bound_to_current_native_supplier_solids=[0,1,2],
        received_revision_keyed_plug_fit_continuity_Cu_OD_and_actual_exit_verified=False,
        selected=False,W5_complete=False,physical_pass=False,worker_seconds=time.monotonic()-tick,
        source_sha256={f.relative_to(ROOT).as_posix():sha(f) for f in pins|{Path(__file__)}})
    (OUT/'BUS-port-binding.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result),flush=True)
    return result

if __name__=='__main__':run()
