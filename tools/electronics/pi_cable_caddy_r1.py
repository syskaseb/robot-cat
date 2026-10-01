"""Integral tray cable seats/park bay and one MAIN-output seat on Deck.

Preserves original four Pi bores/nut pockets and all clamp volumes.
Factory USB surplus is a bounded loose-coil reserve, not a fake connected torus.
"""
import json,math
import pi_wiring_complete_r1 as M
A,Part,ROOT=M.A,M.Part,M.ROOT
OUT=ROOT/'hardware/electronics/full-cat/pi-cable-caddy-r1'
POWER_FOLDER='pi-power-usb-r3'
MAIN_POST_TOP=95
COIL_Y=-70
MAIN_NECK_X=86.75
COIL_TIE_Y=-70
def main():
    OUT.mkdir(exist_ok=True);assert not (OUT/'checks.json').exists()
    E=ROOT/'hardware/electronics/full-cat';C=ROOT/'hardware/cad/studies'
    owners={'PiTray':M.load(E/'pi-wiring-complete-r13/PiTray_DESIGN.brep'),
        'Deck':M.load(E/'pi-gpio-integrated-r10/Deck_DESIGN.brep'),'Carrier':M.load(E/'pi-gpio-integrated-r10/Carrier_DESIGN.brep'),
        'BUSBracket':M.load(E/'pi-bus-mount-r3/BusTrayBracket_DESIGN.brep'),
        'BUS':M.load(E/'pi-bus-mount-r3/OfficialBus_PCB_WORLD.brep'),'Cover':M.load(C/'head-yaw-end-restraints-r1/CoverYawEndSeat.brep')}
    r=M.SavedShapes();entry=ROOT/json.loads((ROOT/'hardware/cad/current-assembly.json').read_text(encoding='utf-8'))['entry'];o=r.doc(entry);members={x.get('value') for x in M.prop(o['RobotCatAssembly24'],'Group').findall('.//Link')}
    for n in ('SideLeft22','SideRight22','FrameFront20','FrameRear20'):owners[n]=M.world_shape(r,entry,o,n,members)
    owners['BatteryCarrierR4']=r.shape(C/'battery-p0/r4/electronics/BatteryCarrierP0.FCStd','Carrier')
    owners['R4']=r.shape(C/'battery-p0/r4/chassis/BottomPlateP0.FCStd','Plate')
    clamps=C/'pi4-tray-body-mount-r1/PiTrayClampAssembly.FCStd'
    relief=[]
    for n in r.doc(clamps):
        if n.startswith(('View_upper_','View_lower_')):
            owners[n]=r.shape(clamps,n);b=M.bbox(owners[n]);relief.append([v-.3 if i<3 else v+.3 for i,v in enumerate(b)])
    plate=[-18,-96,40,100,-23,43]
    adds={'PiTray':[
        [-14.1,-59.25,42,-7.9,-56.75,53.7],
        [94.5,-23,42,102.5,-15,47],[97.25,-21,46,99.75,-17,55.6]],
        'Deck':[[MAIN_NECK_X,17.2,82.7,MAIN_NECK_X+2.5,20,MAIN_POST_TOP],
                [86.75,14.6,82.7,MAIN_NECK_X+2.5,20,83],[86.75,10.9,86.3,MAIN_NECK_X+2.5,20,86.5]],
        'BUSBracket':[[-38,-40,49,-30,3,52],[-35.14,-36.25,52,-32.64,-33.75,59.169521705]]}
    cuts={'PiTray':[],'Deck':[],'BUSBracket':[]}
    ties={};own={}
    # Full rectangular band + head bounds; loop seams not counted as collisions.
    def loop_x(name,x0,x1,y,z0,z1,owner,clamps):
        boxes=[[x0-1.2,y-1.25,z0-1.2,x0,y+1.25,z1+1.2],
               [x1,y-1.25,z0-1.2,x1+1.2,y+1.25,z1+1.2],
               [x0,y-1.25,z0-1.2,x1,y+1.25,z0],
               [x0,y-1.25,z1,x1,y+1.25,z1+1.2],
               [x0-4.8,y-2.4,z1+1.3,x0,y+2.4,z1+4.8]]
        for i,b in enumerate(boxes):ties[name+'_'+str(i)]=M.box(b);own[name+'_'+str(i)]=clamps
        for x in (x0-.6,x1+.6):cuts[owner].append([x-.9,y-1.5,z0-2,x+.9,y+1.5,z1+5])
    def loop_y(name,x,y0,y1,z0,z1,owner,clamps):
        boxes=[[x-1.25,y0-1.2,z0-1.2,x+1.25,y0,z1+1.2],
               [x-1.25,y1,z0-1.2,x+1.25,y1+1.2,z1+1.2],
               [x-1.25,y0,z0-1.2,x+1.25,y1,z0],
               [x-1.25,y0,z1,x+1.25,y1,z1+1.2],
               [x-2.4,y1+1.3,z1+1.3,x+2.4,y1+6.1,z1+4.8]]
        for i,b in enumerate(boxes):ties[name+'_'+str(i)]=M.box(b);own[name+'_'+str(i)]=clamps
        for y in (y0-.6,y1+.6):cuts[owner].append([x-1.5,y-.9,z0-2,x+1.5,y+.9,z1+5])
    loop_x('Pi_power',-15.2,-6.8,-58,39.8,56.7,'PiTray',('PI5V','PI_GND'))
    loop_y('Pi_USB',98.5,-22,-16,39.8,59.6,'PiTray',('USB_BUS',))
    loop_x('BUS_USB',-37.7,-30.1,-35,48.8,63.169521705,'BUSBracket',('USB_BUS',))
    loop_y('MAIN_output',88,10.1,20.3,82.5,89.6,'Deck',('PI5V','PI_GND'))
    # One loose coil at >=R24: support annulus plus four legs, with one loose
    # band around the entire park (not tensioned onto plug/crimp/copper).
    ring=Part.makeCylinder(26,2,A.Vector(23,COIL_Y,64)).cut(Part.makeCylinder(22,2,A.Vector(23,COIL_Y,64)))
    park_posts=[[45.5,COIL_Y-1.5,42,48.5,COIL_Y+1.5,64],[-2.5,COIL_Y-1.5,42,.5,COIL_Y+1.5,64],[21.5,COIL_Y+22.5,42,24.5,COIL_Y+25.5,64],[21.5,COIL_Y-25.5,42,24.5,COIL_Y-22.5,64]]
    adds['PiTray']+=park_posts
    plan=dict(new_prints=['PiTray replacement x1','Deck replacement x1','BUSBracket new x1'],
        plateau_world=plate,plate_clamp_clearance_boxes_world=relief,adds_world=adds,cuts_world=cuts,
        USB_park={'centre_mm':[23,COIL_Y,68],'minimum_coil_radius_mm':24,'one_turn_capacity_mm':2*math.pi*24,
                  'purpose':'loose factory surplus only, not the connected wire route; adjust coil angle and free service ends after dry-fit',
                  'retention':'one T18I through two park edge slots, loose; actual surplus/drop/tie pressure phase2'},
        total_added_ties=6,remaining='Native exports, checks/insulation/fastener stacks, final single selection',
        physical_pass=False,selected=False,new_stls=0)
    # Loose park band crosses above reserve atZ70.2 and below platform;
    # full threading slots preserve enough edge land, no proprietary clip.
    loop_x('USB_park_left',-4.1,2.1,COIL_TIE_Y,39.8,70.2,'PiTray',('USB_BUS',))
    loop_x('USB_park_right',43.9,50.1,COIL_TIE_Y,39.8,70.2,'PiTray',('USB_BUS',))
    plan['cuts_world']=cuts
    (OUT/'plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
    addon=M.box(plate).cut(Part.makeCompound([M.box(b) for b in relief]))
    owners['PiTray']=owners['PiTray'].multiFuse([addon,ring]+[M.box(b) for b in adds['PiTray']])
    for n in ('Deck','BUSBracket'):owners[n]=owners[n].multiFuse([M.box(b) for b in adds[n]])
    for n in ('PiTray','Deck','BUSBracket'):
        owners[n]=owners[n].cut(Part.makeCompound([M.box(b) for b in cuts[n]]))
        assert owners[n].isValid() and len(owners[n].Solids)==1 and not owners[n].check(True),n
        owners[n].exportBrep(str(OUT/(n+'_DESIGN.brep')))
    wires={p.stem:M.load(p) for p in (E/POWER_FOLDER).glob('*DESIGN.brep')}
    for p in (E/'pi-wiring-complete-r13').glob('XL*DESIGN.brep'):wires[p.stem]=M.load(p)
    hits=[];pairs=0
    def check(n,a,m,b):
        nonlocal pairs
        if not a.BoundBox.intersect(b.BoundBox):return
        for i,s in enumerate(a.Solids):
            for j,t in enumerate(b.Solids):
                pairs+=1;v=s.common(t).Volume
                if v>1e-6:hits.append(dict(a=n,b=m,sa=i,sb=j,volume_mm3=v))
    for n,a in wires.items():
        for m,b in owners.items():
            if n=='BUS_USB_C_body' and m=='BUS':continue
            check(n,a,m,b)
    for n,a in ties.items():
        a.exportBrep(str(OUT/(n+'.brep')))
        for m,b in owners.items():check(n,a,m,b)
        for m,b in wires.items():
            if any(m.startswith(c+'_') for c in own[n]):continue # own insulated clamp only
            check(n,a,m,b)
    for n in ('PiTray','Deck','BUSBracket'):
        for m,b in owners.items():
            if n==m or m in ('PiTray','Deck','BUSBracket','BUS'):continue
            check(n,owners[n],m,b)
    for i,(n,a) in enumerate(ties.items()):
        for m,b in list(ties.items())[i+1:]:
            if n.rsplit('_',1)[0]==m.rsplit('_',1)[0]:continue
            check(n,a,m,b)
    coil_reserve=Part.makeTorus(24,2,A.Vector(23,COIL_Y,68))
    for m,b in owners.items():check('USB_coil_RESERVE',coil_reserve,m,b)
    result=dict(status='CADDY_GEOMETRY_CANDIDATE' if not hits else 'OPEN',hits=hits,affected_pairs=pairs,new_stls=0,new_ties=6,
        physical_pass=False,CP_PI_complete=False,original_clamps_preserved=True,USB_park_is_reserve_not_connected=True)
    (OUT/'checks.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    meshes=[]
    for n,a in {**wires,**ties,**{n:s for n,s in owners.items() if n in ('PiTray','Deck','BUSBracket','BUS')},'USB_coil_RESERVE':coil_reserve}.items():
        vs,fs=a.tessellate(.4);meshes.append(dict(name=n,vertices=[list(v) for v in vs],triangles=fs))
    (OUT/'preview-geometry.json').write_text(json.dumps(meshes)+'\n',encoding='utf-8')
    print(json.dumps(result),flush=True)
if __name__=='__main__':main()
