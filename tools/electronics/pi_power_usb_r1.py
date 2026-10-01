"""Complete nominal Pi power and USB paths. Source before long operations.

Power outputs leave MAIN to -X above the board rather than using the old
diagnostic R6 bends toward +X. No MAIN/P0 printed mount changes.
"""
import json,math
import pi_wiring_complete_r1 as M
A,Part,ROOT=M.A,M.Part,M.ROOT
OUT=ROOT/'hardware/electronics/full-cat/pi-power-usb-r1'
PI_RISE=0
GPIO_FOLDER='pi-gpio-integrated-r9'
GPIO_ROUTES='pi-wiring-complete-r12'
BUS_FOLDER='pi-bus-mount-r2'
POWER_FAN=False
CONCENTRIC_RETURN=False
USB_SOUTH_FAN=False
def rounded(points,r):return list(M.B.R.rounded([A.Vector(*p) for p in points],r).Edges)
def fan(a,b):
    c=Part.BezierCurve();c.setPoles([A.Vector(*a),A.Vector(a[0]+(b[0]-a[0])/3,a[1]+(b[1]-a[1])/3,a[2]),A.Vector(b[0]-(b[0]-a[0])/3,b[1]-(b[1]-a[1])/3,b[2]),A.Vector(*b)]);return c.toShape()
def main():
    OUT.mkdir(exist_ok=True);assert not (OUT/'checks.json').exists()
    plan=dict(parent_selection='one-batch-prototype-r31',GPIO='pi-gpio-integrated-r9',BUS='pi-bus-mount-r2',
        power_SKU='Joy-IT K-1474 EAN4250236828305,1m18AWG5A; 1pc shared with <=300mm MAIN input leftovers',
        power_ends={'red':'MAIN VOUT5.10V, direct pad solder','black':'MAIN GND_OUT, direct pad solder','USB-C':'Pi4 south-edge power only'},
        source_pad_centres=[[114.869,15.41,62.5748],[114.869,11.91,62.5748]],
        USB_SKU='Lanberg CA-USBO-10CU-0005-BK EAN5901969416237,500mm USB-A/C2.0; no cutting',
        USB_ends='Pi4 USB2 lower south block east edge to Waveshare25514 USB-C, USB modeB; BUS external power/ UART unused, D/G-only servo bus lead. No powered hub/backfeed.',
        dimensions_assumed={'power_single_strand_OD_mm':3,'power_pair_centres_mm':3.2,'USB_OD_mm':4,'USB_A_body_mm':[30,16,8],'USB_C_body_mm':[12,25,8]},
        note='Provisional plug bodies/OD and Pi connector height are project reserves, NOT manufacturer dimensions; actual delivery adjustment phase2.',
        new_stls=0,selected=False,CP_PI_complete=False,physical_pass=False,
        remaining=['Full restraint native construction','Factory USB excess storage','Supplier fastener/whole selection'])
    (OUT/'plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
    routes={
        'PI5V':rounded([[114.869,15.41,62.5748],[114.869,15.41,84.5],[35,15.41,84.5],[35,-80,84.5],[-9.4,-80,84.5],[-9.4,-80,48.2],[-9.4,-53,48.2]],18),
        'PI_GND':rounded([[114.869,11.91,62.5748],[114.869,11.91,88],[42,11.91,88],[42,-84,88],[-6.2,-84,88],[-6.2,-84,48.2],[-6.2,-53,48.2]],18)}
    if POWER_FAN:
        z=48.2+PI_RISE
        routes['PI5V']=rounded([[114.869,15.41,62.5748],[114.869,15.41,84.5],[60,15.41,84.5],[60,-3,84.5]],18)+[fan([60,-3,84.5],[60,-62,z])]+rounded([[60,-62,z],[60,-80,z],[-9.4,-80,z],[-9.4,-53,z]],18)
        routes['PI_GND']=rounded([[114.869,11.91,62.5748],[114.869,11.91,88],[56,11.91,88],[56,-6.1,88]],18)+[fan([56,-6.1,88],[56,-66.1,z])]+rounded([[56,-66.1,z],[56,-84.1,z],[-6.2,-84.1,z],[-6.2,-53,z]],18)
        if CONCENTRIC_RETURN:
            routes['PI_GND']=rounded([[114.869,11.91,62.5748],[114.869,11.91,88],[56,11.91,88],[56,-6.1,88]],18)
            routes['PI_GND'] += [fan([56,-6.1,88],[56,-65.2,z+3.2]),M.B.arc([38,-65.2,z+3.2],[56,-65.2,z+3.2],[38,-83.2,z+3.2]),fan([38,-83.2,z+3.2],[8.6,-83.2,z]),M.B.arc([8.6,-62,z],[8.6,-83.2,z],[-12.6,-62,z]),Part.makeLine(A.Vector(-12.6,-62,z),A.Vector(-12.6,-53,z))]
    usb=rounded([[96,-19,50.6+PI_RISE],[125,-19,50.6+PI_RISE],[125,-75,50.6+PI_RISE],[70,-75,50.6+PI_RISE]],24)
    usb+=[fan([70,-75,50.6+PI_RISE],[30,-75,61.169521705])]
    usb+=rounded([[30,-75,61.169521705],[-33.8900446757,-75,61.169521705],[-33.8900446757,-25.80421408,61.169521705]],24)
    if USB_SOUTH_FAN:
        z=50.6+PI_RISE
        usb=[Part.makeLine(A.Vector(96,-19,z),A.Vector(101,-19,z)),M.B.arc([101,-43,z],[101,-19,z],[125,-43,z]),
             fan([125,-43,z],[125,-73.5,64]),M.B.arc([101,-73.5,64],[125,-73.5,64],[101,-97.5,64]),
             fan([101,-97.5,64],[51,-97.5,61.169521705])]
        usb+=rounded([[51,-97.5,61.169521705],[-33.8900446757,-97.5,61.169521705],[-33.8900446757,-25.80421408,61.169521705]],24)
    routes['USB_BUS']=usb
    bodies={'Pi_power_body':M.box([-14.8,-53,44.2+PI_RISE,-.8,-28,52.2+PI_RISE]),
        'Pi_USB_A_body':M.box([66,-27,46.6+PI_RISE,96,-11,54.6+PI_RISE]),
        'BUS_USB_C_body':M.box([-39.89,-25.80421408,57.1695,-27.89,-.80421408,65.1695])}
    geo={};lengths={}
    for n,edges in routes.items():
        lengths[n]=sum(e.Length for e in edges)
        for i,e in enumerate(edges):
            s=M.tube(e,2 if n=='USB_BUS' else 1.5);name=f'{n}_{i}';geo[name]=s
            e.exportBrep(str(OUT/(name+'_CENTERLINE.brep')));s.exportBrep(str(OUT/(name+'_DESIGN.brep')))
    geo.update(bodies)
    r=M.SavedShapes();entry=ROOT/json.loads((ROOT/'hardware/cad/current-assembly.json').read_text(encoding='utf-8'))['entry'];o=r.doc(entry);members={x.get('value') for x in M.prop(o['RobotCatAssembly24'],'Group').findall('.//Link')}
    owners={n:M.world_shape(r,entry,o,n,members) for n in ('PiTray18','SideLeft22','SideRight22','FrameFront20','FrameRear20')}
    if PI_RISE:owners['PiTray18']=M.load(ROOT/'hardware/electronics/full-cat'/GPIO_ROUTES/'PiTray_DESIGN.brep')
    for n in ('Deck','Carrier'):owners[n]=M.load(ROOT/'hardware/electronics/full-cat'/GPIO_FOLDER/(n+'_DESIGN.brep'))
    owners['Cover']=M.load(ROOT/'hardware/cad/studies/head-yaw-end-restraints-r1/CoverYawEndSeat.brep')
    owners['BUSBracket']=M.load(ROOT/'hardware/electronics/full-cat'/BUS_FOLDER/'BusTrayBracket_DESIGN.brep')
    owners['BUS']=M.load(ROOT/'hardware/electronics/full-cat'/BUS_FOLDER/'OfficialBus_PCB_WORLD.brep')
    owners['MAINMount']=r.shape(ROOT/'hardware/cad/studies/main-p0-mount/r5/MainP0Mount.FCStd','Adapter');owners['MAINMount'].translate(A.Vector(105.82,8.16,52))
    for p in (ROOT/'hardware/electronics/full-cat'/GPIO_ROUTES).glob('XL*DESIGN.brep'):owners[p.stem]=M.load(p)
    clamps=ROOT/'hardware/cad/studies/pi4-tray-body-mount-r1/PiTrayClampAssembly.FCStd'
    for n in r.doc(clamps):
        if n.startswith(('View_upper_','View_lower_')):owners[n]=r.shape(clamps,n)
    for x in (-12,61):
        for y in (-36,36):
            owners[f'tray_M3_head_{x}_{y}']=Part.makeCylinder(2.75,3,A.Vector(x,y,49.5 if y>0 else 47.5))
    # Own plug inserted contacts/own wires meeting its boot intentionally touch.
    intentional={'BUS_USB_C_body':{'BUS'},'Pi_power_body':set(),'Pi_USB_A_body':set()}
    hits=[];pairs=0
    def check(n,a,m,b):
        nonlocal pairs
        if not a.BoundBox.intersect(b.BoundBox):return
        for i,s in enumerate(a.Solids):
            for j,t in enumerate(b.Solids):
                pairs+=1;v=s.common(t).Volume
                if v>1e-6:hits.append(dict(a=n,b=m,sa=i,sb=j,volume_mm3=v))
    for n,a in geo.items():
        for m,b in owners.items():
            if m in intentional.get(n,set()):continue
            check(n,a,m,b)
    keys=list(geo)
    def group(n):return 'PI_GND' if n.startswith('PI_GND_') else n.split('_')[0] if n.startswith('PI5V') else 'USB_BUS' if n.startswith('USB_BUS_') else n
    for i,n in enumerate(keys):
        for m in keys[i+1:]:
            if group(n)==group(m):continue
            if (n.startswith(('PI5V_','PI_GND_')) and m=='Pi_power_body') or (n.startswith('USB_BUS_') and m in ('Pi_USB_A_body','BUS_USB_C_body')):continue
            check(n,geo[n],m,geo[m])
    power_length=max(lengths['PI5V'],lengths['PI_GND'])+36
    R=.0175*2*(power_length/1000)/.823*1.1572
    result=dict(status='CANDIDATE' if not hits else 'OPEN',hits=hits,affected_pairs=pairs,centreline_lengths_mm=lengths,
        power_max_cut_mm=power_length,power_previous250mm_not_met=power_length>250,
        power_pair_R60_assumption_ohm=R,power_drop3A_V=3*R,remaining_connections_budget_ohm=(5.08-4.95)/3-R,
        power_factory1000_after_main300_margin_mm=1000-300-power_length,
        USB_requirement_mm=lengths['USB_BUS']+60+40,USB500_margin_mm=500-lengths['USB_BUS']-100,
        USB_fan_radius_lower_bound_mm=40**2/(6*abs(61.169521705-50.6-PI_RISE)),
        power_fan_radius_bounds_mm=[59**2/(6*(84.5-48.2-PI_RISE)),60**2/(6*(88-48.2-PI_RISE))] if POWER_FAN else[],physical_pass=False,new_stls=0,CP_PI_complete=False)
    (OUT/'checks.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    meshes=[]
    for n,a in {**geo,**{k:v for k,v in owners.items() if k in ('PiTray18','BUS','BUSBracket','MAINMount')}}.items():
        vs,fs=a.tessellate(.35);meshes.append(dict(name=n,vertices=[list(v) for v in vs],triangles=fs))
    (OUT/'preview-geometry.json').write_text(json.dumps(meshes)+'\n',encoding='utf-8')
    print(json.dumps(result),flush=True)
if __name__=='__main__':main()
