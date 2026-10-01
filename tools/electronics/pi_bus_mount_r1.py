"""Vendor PCB on a detachable tray-ear bracket, not the old BusAdapter box."""
import json,math
from pathlib import Path
import pi_wiring_complete_r1 as M
A,Part,ROOT=M.A,M.Part,M.ROOT
OUT=ROOT/'hardware/electronics/full-cat/pi-bus-mount-r1'
BODY_AXES=[(-12,-36),(-12,36)]
BASE_BOXES=[[-68,0,49,-23,33,52],[-68,33,47,-8,39,50],[-68,-39,47,-8,-33,50],[-26,-36,47,-23,36,52]]
TRAY_PATH=None
def move(s):
    s=s.copy();s.translate(A.Vector(-66,0,60));return s
def main():
    OUT.mkdir(exist_ok=True);assert not (OUT/'checks.json').exists()
    board=M.load(ROOT/'hardware/electronics/full-cat/pi-bus-primary-r1/Part__Feature.brep')
    pads=sorted({(round(f.Surface.Center.x,6)-66,round(f.Surface.Center.y,6)) for f in board.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-1.25)<1e-5})
    assert len(pads)==4
    adds=BASE_BOXES
    plan=dict(source='Official Waveshare25514 STEP, 2024-04-19; cached PCB117 physical solids',
        board_world_translation=[-66,0,60],board_mount_axes_mm=pads,PCB_bottom_z=58.4,
        body_fasteners='2 M3x10,2 retained-series M3 DIN934 nuts,2 washers3.2x7x0.5 at tray original ears; axes in body_mount_axes_mm',body_mount_axes_mm=BODY_AXES,
        PCB_fasteners='4 M2x12,4 M2 DIN934 AF4 H1.6,4 washers2.2x4.3x0.3, nominal DIN geometry; supplier SKU to fix before selection',
        printed_standoffs='4x OD5,ID2.4,z52..58.4; underside parts minZ56.4 clear base top52',
        assembly='Trap four M2 nuts from bottom, fasten bracket onto tray ears before Pi. Install BUS on four standoffs. Disconnect both USB ends and BUS D/G plug, undo two M3 bracket screws, remove BUS/bracket before tray lift. No need to remove soldered Pi logic leads from cassette.',
        new_prints=1,quantity=1,orientation='Bracket flat underside arms Z47 on bed; raised platform/short nut-pocket roofs inspect in phase2',
        PETG='Use existing PETG recipe; support/cantilever and M2 nut/bores samples in phase2; no slicer/physical PASS',
        selected=False,physical_pass=False)
    (OUT/'plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
    source=Part.makeCompound([M.box(b) for b in adds]);s=M.box(adds[0]).multiFuse([M.box(b) for b in adds[1:]])
    for x,y in pads:s=s.fuse(Part.makeCylinder(2.5,6.4,A.Vector(x,y,52)))
    cuts=[]
    for x,y in pads:
        cuts.append(Part.makeCylinder(1.2,16,A.Vector(x,y,46)))
        radius=4.3/math.sqrt(3)
        vs=[A.Vector(x+radius*math.cos(i*math.pi/3),y+radius*math.sin(i*math.pi/3),49) for i in range(6)]
        cuts.append(Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(A.Vector(0,0,2.4)))
    for x,y in BODY_AXES:cuts.append(Part.makeCylinder(1.7,5,A.Vector(x,y,46)))
    s=s.cut(Part.makeCompound(cuts));assert s.isValid() and len(s.Solids)==1 and not s.check(True)
    s.exportBrep(str(OUT/'BusTrayBracket_DESIGN.brep'))
    pcb=move(M.load(ROOT/'hardware/electronics/full-cat/pi-bus-primary-r1/PCB.brep'))
    pcb.exportBrep(str(OUT/'OfficialBus_PCB_WORLD.brep'))
    geo={'BusBracket':s,'OfficialBus':pcb}
    r=M.SavedShapes();entry=ROOT/json.loads((ROOT/'hardware/cad/current-assembly.json').read_text(encoding='utf-8'))['entry'];o=r.doc(entry);members={x.get('value') for x in M.prop(o['RobotCatAssembly24'],'Group').findall('.//Link')}
    owners={n:M.world_shape(r,entry,o,n,members) for n in ('PiTray18','SideLeft22','SideRight22','FrameFront20','FrameRear20')}
    if TRAY_PATH:owners['PiTray18']=M.load(ROOT/TRAY_PATH)
    owners['Pi_nominal_PCB']=M.box([-19,-28,45,66,28,46.6])
    for n,p in [('Deck','tail-direct-deck-r1/DeckTailDirectReturn.brep'),('Carrier','tail-central-carrier-r1/CarrierTailCentralPWM_WORLD.brep'),('Cover','head-yaw-end-restraints-r1/CoverYawEndSeat.brep')]:owners[n]=M.load(ROOT/'hardware/cad/studies'/p)
    clamps=ROOT/'hardware/cad/studies/pi4-tray-body-mount-r1/PiTrayClampAssembly.FCStd'
    for n in r.doc(clamps):
        if n.startswith(('View_upper_','View_lower_')):owners[n]=r.shape(clamps,n)
    hits=[]
    for n,a in geo.items():
        for m,b in owners.items():
            if not a.BoundBox.intersect(b.BoundBox):continue
            for i,ss in enumerate(a.Solids):
                for j,tt in enumerate(b.Solids):
                    v=ss.common(tt).Volume
                    if v>1e-6:hits.append(dict(a=n,b=m,sa=i,sb=j,volume_mm3=v))
    v=s.common(pcb).Volume
    if v>1e-6:hits.append(dict(a='bracket',b='BUS populated PCB',volume_mm3=v))
    result=dict(status='BRACKET_GEOMETRY_CANDIDATE' if not hits else 'OPEN',hits=hits,
        bracket=M.bbox(s),BUS=M.bbox(pcb),mount_axes=pads,new_stls=0,native_and_fastener_checks_pending=True,
        port_usb_mouth_world=[-33.8900446757,-.80421408,61.169521705],
        primary_source_sha256=M.sha(ROOT/'hardware/electronics/full-cat/pi-bus-primary-r1/catalog.json'),physical_pass=False)
    (OUT/'checks.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    meshes=[]
    for n,a in {**geo,**owners}.items():
        vs,fs=a.tessellate(.4);meshes.append(dict(name=n,vertices=[list(v) for v in vs],triangles=fs))
    (OUT/'preview-geometry.json').write_text(json.dumps(meshes)+'\n',encoding='utf-8')
    print(json.dumps(result),flush=True)
if __name__=='__main__':main()
