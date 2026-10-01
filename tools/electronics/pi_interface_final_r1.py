"""Bounded final Pi interface: sleeves, stacks, combined native owners and lift.

Nominal printed preparation only. Supplier bodies remain explicit reserves.
Save source/report plan before any intersections. Never waive a bare-wire hit.
"""
import json,math
from pathlib import Path
import pi_wiring_complete_r1 as M
A,Part,ROOT=M.A,M.Part,M.ROOT
E=ROOT/'hardware/electronics/full-cat';C=ROOT/'hardware/cad/studies'
OUT=E/'pi-interface-final-r2';N=C/'pi-complete-native-r2'
DELTA_OE_ONLY=True
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def ring(x,y,z,di,do,h):
    return Part.makeCylinder(do/2,h,A.Vector(x,y,z)).cut(Part.makeCylinder(di/2,h,A.Vector(x,y,z)))
def hexagon(x,y,z,af,h,angle=0):
    rr=af/math.sqrt(3)
    points=[A.Vector(x+rr*math.cos(i*math.pi/3+angle),y+rr*math.sin(i*math.pi/3+angle),z) for i in range(7)]
    return Part.Face(Part.Wire(Part.makePolygon(points).Edges)).extrude(A.Vector(0,0,h))
def section(edge,start,end):
    # Arc length along the existing exact centreline; no guessed endpoint.
    return edge.Curve.toShape(edge.getParameterByLength(start),edge.getParameterByLength(end))
def fan(a,b):
    p,q=A.Vector(*a),A.Vector(*b);c=Part.BezierCurve()
    c.setPoles([p,A.Vector(p.x,p.y+(q.y-p.y)/3,p.z),A.Vector(q.x,q.y-(q.y-p.y)/3,q.z),q]);return c.toShape()
def main():
    OUT.mkdir(exist_ok=True)
    if (OUT/'checks.json').exists():
        rejected=read(OUT/'checks.json');assert rejected['status']=='OPEN'
        save('rejected-checks.json',rejected) # preserve failed diagnostic; never overwrite a complete selection
        if DELTA_OE_ONLY:
            assert rejected['affected_pairs']==2316 and all('XL07' in h['a'] or 'XL07' in h['b'] for h in rejected['hits'])
            save('baseline-before-oe-delta.json',rejected)
    native=read(N/'checks.json');assert native['reopen_recompute']
    plan=dict(parent='R32',native='pi-complete-native-r2',
        corrected_datums={'Pi_board_bottom_z_mm':52,'J8_housing_bottom_assumed_z_mm':55.6,'J8_wire_exit_assumed_z_mm':69.6,'J8_top_reserve_z_mm':69.85},
        previous_diagnostic_metadata_not_authoritative=['pi-wiring-complete-r13/gpio-datums.json fixed original Z metadata','pi-bus-mount-r3/plan.json washer OD4.3 / additional nuts','pi-power-usb-r4/checks.json old fan formula','pi-cable-caddy-r3/plan.json one park tie text'],
        mounting={'Pi':'4 M2.5x16, existing four nuts and washers reused; 7mm integral rise',
                  'BUS':'4 M2x12,4 nuts AF4 H1.6,4 DIN125 washers ID2.2 OD5 H0.3; native posts OD4.9, platform Ymax34',
                  'north_tray':'2 M3x10 replace 2 M3x8; reuse existing clamp nuts/washers',
                  'south_tray':'2 M3x8 unchanged'},
        sleeve_materials={'GPIO':'TE5052942064 RNF1003/32 black; expanded2.4, conservative project finishedOD2.5 includes wall reserve; 5 blanks15mm, 6mm insulation overlap, end Z153.8 below PCB underside154',
                          'MAIN':'Two RNF1003/32 inner sleeves on separate2mm bare necks, outer OD2.2; one COMMON RNF1003/8 black expanded9.5/recovered4.8 boot over both insulated leads, conservative capsule width7.6. One15mm outer blank with6mm intact-insulation overlap; NOT two interfering3/16 sleeves.'},
        solder='GPIO preserve Pi factory crimp, trim cassette end only. MAIN strip5mm:3mm through pad plus2mm exposed upper neck. Shrink off PETG before final fastening, strain on insulation not pad. Actual wall/insert dimensions phase2.',
        minimum_bends_mm={'GPIO_insulated':10,'GPIO_short_solder_takeoff':2,'power':18,'power_black_return':21.2,'USB':24},
        conservative_fan_radius_bounds_mm={'GPIO_start':41**2/(6*27.55),'GPIO_OE':40**2/(6*6),'power_red':59**2/(6*29.3),'power_black_first':59.1**2/(6*29.6),'power_black_last':29.4**2/(6*3.2),'USB_first':30.5**2/(6*6.4),'USB_last':50**2/(6*(64-61.169521705))},
        tie_allocation={'GPIO':6,'Pi_power_USB_and_MAIN':4,'USB_loose_park':2},
        tools='Tray screws before wiring; unplug Pi power and release both power-wire ties before removal, move free lead out of key corridor. Tool clearance below is against fixed parts, not the obstructing still-fixed Pi lead.',
        E2_route_override='XP02 module loop shifted+3mm at north return withR11.1 preserved; first34.7mm/bundle/boardtakeoff unchanged. Actual150mm factory budget recomputed here. R32 original routes immutable.',
        provisional=['Pi populated connector height, factory plug bounding reserves and wire ODs','Shrink fitted OD/wall','PETG/fastener delivered fit','USB surplus is loose storage reserve, not exact connected coil path'],
        physical_pass=False,new_stls=0,CP_PI_complete=False)
    save('interface.json',plan)
    owners={n:M.load(N/(n+'_WORLD.brep')) for n in ('PiTray','Deck','Carrier','BUSBracket')}
    owners['BUS']=M.load(E/'pi-bus-mount-r3/OfficialBus_PCB_WORLD.brep')
    owners['Cover']=M.load(C/'head-yaw-end-restraints-r1/CoverYawEndSeat.brep')
    reader=M.SavedShapes();entry=ROOT/read(ROOT/'hardware/cad/current-assembly.json')['entry'];o=reader.doc(entry);members={x.get('value') for x in M.prop(o['RobotCatAssembly24'],'Group').findall('.//Link')}
    for n in ('SideLeft22','SideRight22','FrameFront20','FrameRear20'):owners[n]=M.world_shape(reader,entry,o,n,members)
    owners['R4']=reader.shape(C/'battery-p0/r4/chassis/BottomPlateP0.FCStd','Plate')
    owners['BatteryR4']=reader.shape(C/'battery-p0/r4/electronics/BatteryCarrierP0.FCStd','Carrier')
    owners['MAINMount']=reader.shape(C/'main-p0-mount/r5/MainP0Mount.FCStd','Adapter');owners['MAINMount'].translate(A.Vector(105.82,8.16,52))
    pop=read(E/'pwm-carrier-r3/population.json');pcbshape=M.box([67.41,-25.4,154,110.59,25.4,155.6002])
    holes=[Part.makeCylinder(float(p['drill'])/2,2,A.Vector(float(p['x'])+89,float(p['y']),153.9)) for g in pop['board']['groups'] for p in g['pads']]
    owners['PWM_PCB_conservative_outline']=pcbshape.cut(Part.makeCompound(holes))
    clamp=C/'pi4-tray-body-mount-r1/PiTrayClampAssembly.FCStd'
    for n in reader.doc(clamp):
        if n.startswith(('View_upper_','View_lower_')):owners[n]=reader.shape(clamp,n)
    wires={}
    for folder,pat in [('pi-wiring-complete-r13','XL*DESIGN.brep'),('pi-power-usb-r4','*DESIGN.brep')]:
        for p in (E/folder).glob(pat):wires[p.stem]=M.load(p)
    paths=list((E/'head-connected-feeds-r8').glob('XB*.brep'))+list((E/'head-connected-feeds-r8').glob('XS*.brep'))
    for folder in ('tail-central-routes-r3','tail-ground-direct-r1','pwm-service-r2','head-pwm-bare-takeoffs-r3'):
        paths += [p for p in (E/folder).glob('*DESIGN.brep') if p.stem!='CarrierTailPWMEntry_DESIGN']
    paths += [E/p for p in ('aux-converter-routes-r5/XA02_DESIGN.brep','aux-converter-routes-r5/XA04_DESIGN.brep','aux-converter-routes-r2/XA03_DESIGN.brep','xa05-main-aux-return-r2/XA05_DESIGN.brep','xa06-ground-bridge-r1/XA06_DESIGN.brep','xb11-upstream-route-r3/XB11_DESIGN.brep')]
    retained={p.parent.name+'/'+p.stem:M.load(p) for p in paths}
    yy=16.4661534083945;hh=math.sqrt(11.1**2-(11.1-5.4)**2);low=yy-2*hh
    rededges=[Part.makeLine(A.Vector(119,-34.7,151.5),A.Vector(119,0,151.5)),fan([119,0,151.5],[122,yy,151.5]),
        M.B.arc([110.9,16.4661534083945,151.5],[122,16.4661534083945,151.5],[110.9,27.5661534083945,151.5]),
        M.B.arc([110.9,16.4661534083945,151.5],[110.9,27.5661534083945,151.5],[99.8,16.4661534083945,151.5]),
        M.B.arc([88.7,yy,151.5],[99.8,yy,151.5],[94.4,yy-hh,151.5]),
        M.B.arc([100.1,low,151.5],[94.4,yy-hh,151.5],[89,low,151.5]),
        Part.makeLine(A.Vector(89,low,151.5),A.Vector(89,-10.43,151.5))]
    for k in list(retained):
        if k.startswith('pwm-service-r2/XP02_module_') and '_bare_' not in k:del retained[k]
    for i,e in enumerate(rededges):
        key='pwm-service-r2/XP02_module_'+str(i)+'_DESIGN';retained[key]=M.tube(e,1.05)
        e.exportBrep(str(OUT/('XP02_module_'+str(i)+'_CENTERLINE.brep')));retained[key].exportBrep(str(OUT/('XP02_module_'+str(i)+'_DESIGN.brep')))
    redneed=sum(e.Length for e in rededges)+4.6709963268+6+10
    assert redneed<=145,redneed
    plan['E2_override_budget']={'factory_min_mm':145,'new_module_insulated_mm':sum(e.Length for e in rededges),'required_mm':redneed,'margin_mm':145-redneed,
        'fan_radius_bounds_mm':[yy**2/(6*3)],'return_arc_radius_mm':11.1,'bare_end_unchanged':True,'service_slack_embedded_not_added_twice':True}
    save('interface.json',plan)
    ties={p.parent.name+'/'+p.stem:M.load(p) for folder in ('pi-gpio-integrated-r10','pi-cable-caddy-r3') for p in (E/folder).glob('*.brep') if ('tie_' in p.stem or p.stem.startswith(('Pi_power_','Pi_USB_','BUS_USB_','MAIN_output_','USB_park_')))}
    for k,s in list(ties.items()):
        if 'XL05_board_tie_' in k and k[-1] in '012':
            b=s.BoundBox;bb=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
            if k.endswith('_2'):bb[2]+=.6
            bb[5]+=.6;ties[k]=M.box(bb);ties[k].exportBrep(str(OUT/(k.split('/')[-1]+'.brep')))
    sleeves={};covered={}
    for name in ('XL01','XL10','XL07','XL05','XL06'):
        folder=E/'pi-wiring-complete-r13'
        files=sorted(folder.glob(name+'_insulated_*CENTERLINE.brep'),key=lambda p:int(p.stem.split('_')[2]))
        last=M.load(files[-1]).Edges[0];assert last.Length>=6
        bare0=M.load(folder/(name+'_bare_0_CENTERLINE.brep')).Edges[0]
        bare1=M.load(folder/(name+'_bare_1_CENTERLINE.brep')).Edges[0]
        pad=bare1.valueAt(bare1.LastParameter);oldend=last.valueAt(last.LastParameter)
        sign=1 if oldend.y>pad.y else -1
        end=A.Vector(pad.x,pad.y+sign*2,151.5 if name=='XL07' else oldend.z)
        if name=='XL07':
            first=last.valueAt(last.FirstParameter);neck=A.Vector(end.x+3,7.61,153.28)
            curve=Part.BezierCurve();delta=neck-first
            curve.setPoles([first,A.Vector(first.x,first.y+delta.y/3,first.z),A.Vector(neck.x,neck.y-delta.y/3,neck.z),neck])
            wires[files[-1].stem.replace('_CENTERLINE','_DESIGN')]=M.tube(curve.toShape(),.7)
            curve.toShape().exportBrep(str(OUT/'XL07_insulated_10_CENTERLINE.brep'))
            last=fan(list(neck),list(end))
        else:last=Part.makeLine(last.valueAt(last.FirstParameter),end)
        if name=='XL10':
            start=last.valueAt(last.FirstParameter)
            upper=fan(list(start),[104.24,28,153.25]);level=Part.makeLine(A.Vector(104.24,28,153.25),A.Vector(104.24,17,153.25));lower=fan([104.24,17,153.25],[104.24,2,151.5])
            for j,e in enumerate((upper,level,lower)):
                wires['XL10_insulated_lift_'+str(j)+'_DESIGN']=M.tube(e,.7);e.exportBrep(str(OUT/('XL10_insulated_lift_'+str(j)+'_CENTERLINE.brep')))
            last=Part.makeLine(A.Vector(104.24,2,151.5),end)
        centre=A.Vector(pad.x,end.y,end.z+2)
        bendend=A.Vector(pad.x,pad.y,end.z+2)
        newbare=[M.B.arc(list(centre),list(end),list(bendend)),Part.makeLine(bendend,pad)]
        key='XL07_insulated_11_DESIGN' if name=='XL07' else files[-1].stem.replace('_CENTERLINE','_DESIGN')
        wires[key]=M.tube(last,.7)
        for i,e in enumerate(newbare):wires[name+'_bare_'+str(i)+'_DESIGN']=M.tube(e,math.sqrt(.14/math.pi))
        last.exportBrep(str(OUT/('XL07_insulated_11_CENTERLINE.brep' if name=='XL07' else files[-1].name)))
        for i,e in enumerate(newbare):e.exportBrep(str(OUT/(name+'_bare_'+str(i)+'_CENTERLINE.brep')))
        parts=[M.tube(section(last,last.Length-6,last.Length),1.25)]
        for edge in newbare:
            a=edge.valueAt(edge.FirstParameter);b=edge.valueAt(edge.LastParameter)
            if max(a.z,b.z)<=153.8+1e-6:parts.append(M.tube(edge,1.25))
            elif min(a.z,b.z)<153.8:
                # All final bare edges here are circular R1 or vertical line.
                low,high=0.,edge.Length
                for _ in range(40):
                    mid=(low+high)/2;z=edge.valueAt(edge.getParameterByLength(mid)).z
                    if z<153.8:low=mid
                    else:high=mid
                parts.append(M.tube(section(edge,0,(low+high)/2),1.25))
        sleeves[name+'_sleeve']=parts[0].multiFuse(parts[1:]);covered[name+'_sleeve']=name
        if name=='XL07':
            # One continuous profile avoids a boolean seam between the inclined
            # terminal fan and its R2 solder bend. Same radius/centreline.
            spine=Part.Wire([section(last,last.Length-6,last.Length),newbare[0],section(newbare[1],0,153.8-bendend.z)])
            e=spine.Edges[0];profile=Part.Wire([Part.makeCircle(1.25,e.valueAt(e.FirstParameter),e.tangentAt(e.FirstParameter))])
            sleeves[name+'_sleeve']=spine.makePipeShell([profile],True,False)
    boot_parts=[]
    for name in ('PI5V','PI_GND'):
        edge=M.load(E/'pi-power-usb-r4'/(name+'_0_CENTERLINE.brep')).Edges[0];assert edge.Length>2
        # Replace old diagnostic full insulation at the actual solder pad.
        wires[name+'_0_DESIGN']=M.tube(section(edge,2,edge.Length),1.5)
        wires[name+'_pad_bare_DESIGN']=M.tube(section(edge,0,2),math.sqrt(.823/math.pi))
        nextedge=M.load(E/'pi-power-usb-r4'/(name+'_1_CENTERLINE.brep')).Edges[0]
        sleeves[name+'_pad_inner']=M.tube(section(edge,0,2),1.1);covered[name+'_pad_inner']=name
        boot_parts += [M.tube(section(edge,2,edge.Length),2.05),M.tube(section(nextedge,0,max(0,8-edge.Length)),2.05)]
    sleeves['MAIN_pair_outer_boot']=boot_parts[0].multiFuse(boot_parts[1:]);covered['MAIN_pair_outer_boot']=('PI5V','PI_GND')
    hits=[];pairs=0
    for n,s in sleeves.items():
        print('Insulation validation: '+n,flush=True)
        assert s.Solids and all(a.isValid() and not a.check(True) for a in s.Solids),n
    def check(n,a,m,b):
        nonlocal pairs
        if DELTA_OE_ONLY and 'XL07' not in n and 'XL07' not in m:return
        if not a.BoundBox.intersect(b.BoundBox):return
        for i,s in enumerate(a.Solids):
            for j,t in enumerate(b.Solids):
                pairs+=1;v=s.common(t).Volume
                if v>1e-6:hits.append(dict(a=n,b=m,sa=i,sb=j,volume_mm3=v))
    for n,a in wires.items():
        for m,b in {**owners,**retained}.items():
            if n=='BUS_USB_C_body' and m=='BUS':continue # intentional inserted plug
            check(n,a,m,b)
    def group(n):return n.split('_')[0] if n.startswith(('XL','PI5V','PI_GND')) else 'USB' if n.startswith(('USB_BUS','Pi_USB_A','BUS_USB_C')) else n
    for i,n in enumerate(wires):
        for m in list(wires)[i+1:]:
            if group(n)==group(m):continue
            if ('Pi_power_body' in (n,m)) and (n.startswith(('PI5V','PI_GND')) or m.startswith(('PI5V','PI_GND'))):continue
            check(n,wires[n],m,wires[m])
    for n,a in retained.items():
        if n.startswith('pwm-service-r2/XP02_module_') and '_bare_' not in n:
            for m,b in {**owners,**ties,**retained}.items():
                if m.startswith('pwm-service-r2/XP02_module_'):continue
                check(n,a,m,b)
    for n,a in sleeves.items():
        a.exportBrep(str(OUT/(n+'.brep')))
        for m,b in {**owners,**retained,**ties,**wires}.items():
            names=covered[n] if isinstance(covered[n],tuple) else (covered[n],)
            if any(m.startswith(k+'_') for k in names):continue # its own sleeved conductor
            check(n,a,m,b)
    for i,n in enumerate(sleeves):
        for m in list(sleeves)[i+1:]:check(n,sleeves[n],m,sleeves[m])
    # Cross-owner check omitted by the earlier caddy diagnostic.
    for i,n in enumerate(('PiTray','Deck','Carrier','BUSBracket')):
        for m in ('PiTray','Deck','Carrier','BUSBracket')[i+1:]:check(n,owners[n],m,owners[m])
    pcb= M.box([-19,-28,52,66,28,53.6]);axes=[(x,y) for x in (-15.5,42.5) for y in (-24.5,24.5)]
    for x,y in axes:pcb=pcb.cut(Part.makeCylinder(1.45,3,A.Vector(x,y,51)))
    owners['Pi_PCB_footprint']=pcb
    stacks=[];metal={};tools={}
    def addstack(label,x,y,under,L,d,hd,hh,washer,nutz,af,nh,toolr,angle=0):
        wz=under-washer[2]
        parts={'shaft':Part.makeCylinder(d/2,L,A.Vector(x,y,under-L)),
               'head':Part.makeCylinder(hd/2,hh,A.Vector(x,y,under)),
               'washer':ring(x,y,wz,*washer), 'nut':hexagon(x,y,nutz,af,nh,angle)}
        tools[label+'_tool']=Part.makeCylinder(toolr,18,A.Vector(x,y,under+hh))
        for k,a in parts.items():
            metal[label+'_'+k]=a
            for m,b in owners.items():check(label+'_'+k,a,m,b)
            for m,b in {**wires,**sleeves,**ties}.items():check(label+'_'+k,a,m,b)
        stacks.append(dict(label=label,axis=[x,y],underhead_z=under,length=L,tip_z=under-L,nut_bottom_z=nutz,nut_height=nh,nominal_full_nut_engagement=under-L<=nutz,protrusion=nutz-(under-L)))
    for i,(x,y) in enumerate(axes):addstack('Pi'+str(i),x,y,54.1,16,2.5,4.5,2.5,[2.7,6,.5],40.2,5,2,3)
    for x in (-12,61):
        for y in (-36,36):addstack('Tray'+str(x)+'_'+str(y),x,y,49.5 if y>0 else 47.5,10 if y>0 else 8,3,5.5,3,[3.2,7,.5],39.72,5.5,2.4,3,math.pi/6)
    bus=read(E/'pi-bus-mount-r3/plan.json')
    for i,(x,y) in enumerate(bus['board_mount_axes_mm']):addstack('BUS'+str(i),x,y,60.3,12,2,3.8,2,[2.2,5,.3],49.8,4,1.6,2.2)
    for n,a in tools.items():
        for m,b in {**owners,**wires,**sleeves,**ties}.items():
            if n.startswith('Tray') and m.startswith(('PI5V_','PI_GND_','MAIN_pair_outer_boot')):continue # unplug/release these movable leads first; not attached-wire clearance
            check(n,a,m,b)
    # Actual tray boundary-face sweeps after BUS bracket / plugs / J8 removed.
    lift_hits_start=len(hits);prisms=0;tray=owners['PiTray']
    targets={n:s for n,s in owners.items() if n not in ('PiTray','BUSBracket','BUS','Cover','Pi_PCB_footprint')}
    for i,face in enumerate(tray.Faces):
        prism=face.extrude(A.Vector(0,0,15))
        if prism.Solids and prism.Volume>1e-8:
            prisms+=1
            for m,b in targets.items():check('TrayLiftFace'+str(i),prism,m,b)
    result=dict(status='PI_NOMINAL_INTERFACE_COMPLETE_CANDIDATE' if not hits else 'OPEN',hits=hits,affected_pairs=pairs,
        mount_stacks=stacks,tool_corridors=len(tools),continuous_tray_lift_mm=15,lift_prisms=prisms,lift_hits=hits[lift_hits_start:],
        insulation_ends=7,additional_ties=12,E2_override_budget=plan['E2_override_budget'],tool_cable_release_required=True,new_stls=0,physical_pass=False,selected=False,
        reused_unchanged_screen=DELTA_OE_ONLY,unchanged_baseline_affected_pairs=rejected['affected_pairs'] if DELTA_OE_ONLY else None,
        baseline_checks_sha256=M.sha(OUT/'baseline-before-oe-delta.json') if DELTA_OE_ONLY else None,
        delta_scope='Only OE upper/terminal fan and sleeve changed: upper endpoint Z153.25->153.28. Every prior hit involves OE and is rechecked, not waived. All other fixed parts/stacks/lift/paths unchanged.' if DELTA_OE_ONLY else None,
        remaining=['One selected print/quantity set and inspected PNG','Actual delivered populated board/plug/shrink/PETG fit belongs to phase2'],
        sources={**reader.hashes,'tools/electronics/pi_interface_final_r1.py':M.sha(Path(__file__))})
    save('checks.json',result)
    meshes=[]
    for n,a in {**{n:s for n,s in owners.items() if n in ('PiTray','BUSBracket','BUS','Pi_PCB_footprint')},**wires,**sleeves,**metal}.items():
        vs,fs=a.tessellate(.45);meshes.append(dict(name=n,vertices=[list(v) for v in vs],triangles=fs))
    save('preview-geometry.json',meshes)
    print(json.dumps({k:v for k,v in result.items() if k not in ('sources',)},ensure_ascii=True),flush=True)
if __name__=='__main__':main()
