"""One Pi harness construction, sourced J8 datums and affected route checks.

Run in FreeCAD Python with tools/cad and tools/electronics on sys.path.
Keeps R31 and previous evidence immutable. No physical qualification.
"""
from pathlib import Path
import json
import math
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT, SavedShapes, prop, sha
from check_p0_leg_geometry import world_shape
import head_complete_yaw_transitions_r1 as B

OUT = ROOT/'hardware/electronics/full-cat/pi-wiring-complete-r1'
REF = ROOT/'hardware/reference/pi-interface-2026-10-01'
FACTORY_LENGTH = 300
PORTAL_BUILDER = None
ROUTE_STYLE = 'side-entry'
LANE_START=45
LANE_STEP=2
UNDERBOARD_LOW={'XL05'}
FANNED_AXES=None
FANNED_LOW=125.6
LANE_OVERRIDES={}
TOP_OVERRIDES={}
OUTSIDE_OVERRIDES={}
OE_NORTH_FAN=False
OE_FAN_OFFSET=4
PI_RISE=0
FAN_HEIGHT=45

def save(name, data):
    (OUT/name).write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def load(path):
    s = Part.Shape(); s.read(str(path)); return s

def box(b):
    return Part.makeBox(b[3]-b[0], b[4]-b[1], b[5]-b[2], A.Vector(*b[:3]))

def bbox(s):
    b=s.BoundBox; return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]

def dxf_entities(path):
    lines=path.read_text(encoding='utf-8').splitlines()
    assert len(lines)%2 == 0
    active=False; kind=''; data=[]
    for code,value in zip(lines[::2],lines[1::2]):
        code,value=code.strip(),value.strip()
        if code=='0':
            if active and kind: yield kind,data
            kind=value; data=[]
            if value=='ENDSEC': active=False
        else:
            if code=='2' and value=='ENTITIES': active=True
            data.append((code,value))

def j8():
    entities=list(dxf_entities(REF/'pi4-mechanical.dxf'))
    circles=[]; square_lines=[]
    for kind,pairs in entities:
        d=dict(pairs)
        if d.get('8')!='PINS_TOP': continue
        if kind=='CIRCLE' and abs(float(d.get('40',0))-.8)<1e-8:
            x,y=float(d['10']),float(d['20'])
            if y>50 and x<58: circles.append((x,y))
        if kind=='LINE':
            a=[float(d.get(k,0)) for k in ('10','20')]
            b=[float(d.get(k,0)) for k in ('11','21')]
            if all(7<x<10 and 50<y<53 for x,y in (a,b)): square_lines.append([a,b])
        if kind=='LWPOLYLINE' and d.get('70')=='1':
            xs=[float(v) for c,v in pairs if c=='10']
            ys=[float(v) for c,v in pairs if c=='20']
            vertices=list(zip(xs,ys))
            if len(vertices)==4 and all(7<x<10 and 50<y<53 for x,y in vertices):
                square_lines += [[vertices[i],vertices[(i+1)%4]] for i in range(4)]
    assert len(circles)==39 and len(set(circles))==39, circles
    assert len(square_lines)==4, square_lines
    square_points=[p for line in square_lines for p in line]
    sx=(min(p[0] for p in square_points)+max(p[0] for p in square_points))/2
    sy=(min(p[1] for p in square_points)+max(p[1] for p in square_points))/2
    assert abs(sx-8.37)<1e-8 and abs(sy-51.23)<1e-8
    points={}
    for column in range(20):
        for row in range(2):
            x,y=8.37+2.54*column,51.23+2.54*row
            if column or row: assert any(abs(x-a)<1e-8 and abs(y-b)<1e-8 for a,b in circles)
            points[2*column+row+1]=[x-19,y-28,62.6+PI_RISE]
    return points,dict(source='Official Pi4 mechanical DXF PINS_TOP:39 circular pads plus square pin1',
        square_pin1_board_xy_mm=[sx,sy],header_pitch_mm=2.54,
        board_to_world_translation_mm=[-19,-28,45],
        housing='Pololu1992: nominal50.8 +/-0.30 by5.10 by14.0 +/-0.25 mm',
        housing_bottom_z_assumption_mm=48.6,housing_top_z_assumption_mm=62.6,
        z_basis='Project mated height assumption: PCB1.6, header plastic2mm; not sourced female insertion measurement',
        terminal_exit_max_z_for_clearance_mm=62.85,physical_pass=False)

def tube(edge,radius):
    p=edge.valueAt(edge.FirstParameter)
    return Part.Wire([edge]).makePipeShell([Part.Wire([Part.makeCircle(radius,p,edge.tangentAt(edge.FirstParameter))])],True,False)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists(), 'Preserve generated evidence; use a new revision'
    pins,datums=j8(); save('gpio-datums.json',dict(datums=datums,pins=pins))
    iface=json.loads((ROOT/'hardware/electronics/full-cat/pi-logic-interface-r1/interface.json').read_text(encoding='utf-8'))
    population=json.loads((ROOT/'hardware/electronics/full-cat/pwm-carrier-r3/population.json').read_text(encoding='utf-8'))
    terminals={r['ref']:r for r in population['terminals']}
    specs=[('XL01',1,'LOGIC3V3.in'),('XL10',6,'G_LOGIC.in'),('XL07',11,'OE.in')]
    endpoints={name:[89+terminals[ref]['x'],terminals[ref]['y'],155.6002] for name,_,ref in specs}
    headers=json.loads((ROOT/'hardware/electronics/full-cat/board-interfaces-r1/interfaces.json').read_text(encoding='utf-8'))['adafruit815']['logic_headers']
    for name,pad in [('XL05','3'),('XL06','4')]:
        d=next(r for r in headers if r['connector']=='JP3' and r['pad']==pad)
        endpoints[name]=[-59+d['xy_mm'][0],-12.7+d['xy_mm'][1],155.6]
    specs += [('XL05',3,'PCA.JP3.3'),('XL06',5,'PCA.JP3.4')]
    plan=dict(status='SOURCE_BEFORE_WHOLE_GPIO_ROUTING',parent_selection='one-batch-prototype-r31',
        scope='Five complete Pi-to-cassette paths; power/USB and insulation anchors to integrate before checkpoint',
        endpoints_mm=endpoints,GPIO_pins=[p for _,p,_ in specs],
        wire=('Pololu1841 brown26AWG300mm' if FACTORY_LENGTH==300 else 'Pololu1871 brown26AWG600mm'),
        design_wire_OD_assumption_mm=1.4,design_radius_mm=10,
        cut_rule='Dry-fit, preserve Pi factory crimp. +30mm at one removable Pi end, +6mm board strip/trim. Do not count two detachable ends.',
        actual_OD_and_insert_height_phase2=True,new_stls=0,selected=False,physical_pass=False,
        CP_PI_complete=False,remaining=['Routes/clearance/length','Two insulation restraints per branch','Power and USB','Selection and quantities'])
    save('plan.json',plan)
    r=SavedShapes();entry=ROOT/json.loads((ROOT/'hardware/cad/current-assembly.json').read_text(encoding='utf-8'))['entry'];obj=r.doc(entry)
    members={x.get('value') for x in prop(obj['RobotCatAssembly24'],'Group').findall('.//Link')}
    owners={n:world_shape(r,entry,obj,n,members) for n in ('PiTray18','BusAdapter','SideLeft22','SideRight22','FrameFront20','FrameRear20')}
    paths={'Deck':'hardware/cad/studies/tail-direct-deck-r1/DeckTailDirectReturn.brep',
           'Carrier':'hardware/cad/studies/tail-central-carrier-r1/CarrierTailCentralPWM_WORLD.brep',
           'Cover':'hardware/cad/studies/head-yaw-end-restraints-r1/CoverYawEndSeat.brep'}
    for name,path in paths.items(): owners[name]=load(ROOT/path)
    # These are the exact Deck/Carrier selected by R31; do not use a newer
    # unselected PWM diagnostic descendant as if it had already been accepted.
    for i in range(4): owners['P0Support'+str(i)]=r.shape(ROOT/'hardware/cad/studies/open-deck-p0/r3/OpenDeckSupports.FCStd','Support'+str(i))
    clamps=ROOT/'hardware/cad/studies/pi4-tray-body-mount-r1/PiTrayClampAssembly.FCStd'
    for n in r.doc(clamps):
        if n.startswith(('View_upper_','View_lower_')): owners[n]=r.shape(clamps,n)
    portal_evidence = PORTAL_BUILDER(owners) if PORTAL_BUILDER else None
    housing=box([-11.9,21.95,48.6+PI_RISE,38.9,27.05,62.85+PI_RISE])
    rows=[];geometry=[('J8_housing_nominal',housing)];routes=[]
    for index,(name,pin,ref) in enumerate(specs):
        start=pins[pin];end=endpoints[name]
        # One outside north-side riser, with independent lanes/straight board tails.
        lane=LANE_OVERRIDES.get(name,LANE_START+index*LANE_STEP)
        prefix=[];suffix=[];direction=1
        if ROUTE_STYLE == 'underboard-complete':
            axis=start[0];low=82.6+index*3;top=149 if name in UNDERBOARD_LOW else 151.5
            top=TOP_OVERRIDES.get(name,top)
            if FANNED_AXES:
                axis=FANNED_AXES[name]
                c=Part.BezierCurve();c.setPoles([A.Vector(*start),A.Vector(start[0],start[1],start[2]+FAN_HEIGHT/3),
                      A.Vector(axis,start[1],start[2]+2*FAN_HEIGHT/3),A.Vector(axis,start[1],start[2]+FAN_HEIGHT)])
                prefix=[c.toShape()];route_start=[axis,start[1],start[2]+FAN_HEIGHT];low=FANNED_LOW
            elif name=='XL06':
                axis+=5.08
                c=Part.BezierCurve();c.setPoles([A.Vector(*start),A.Vector(start[0],start[1],start[2]+20/3),
                      A.Vector(axis,start[1],start[2]+40/3),A.Vector(axis,start[1],start[2]+20)])
                prefix=[c.toShape()]
                route_start=[axis,start[1],start[2]+20]
                low=102.6
            else:route_start=start
            points=[route_start,[axis,start[1],low],[axis,lane,low],[axis,lane,top]]
            if name=='XL07' and OE_NORTH_FAN:
                top=153.25;direction=1
                points[-1]=[axis,lane,top]
                points += [[end[0]+OE_FAN_OFFSET,lane,top],[end[0]+OE_FAN_OFFSET,end[1]+41,top]]
                c=Part.BezierCurve();c.setPoles([A.Vector(end[0]+OE_FAN_OFFSET,end[1]+41,top),A.Vector(end[0]+OE_FAN_OFFSET,end[1]+41-40/3,top),A.Vector(end[0],end[1]+1+40/3,top),A.Vector(end[0],end[1]+1,top)])
                suffix=[c.toShape()]
            elif name in ('XL05','XL07'):
                direction=-1;outside=OUTSIDE_OVERRIDES.get(name,-80 if name=='XL05' else 115)
                points += [[outside,lane,top],[outside,end[1]-21,top],
                           [end[0],end[1]-21,top],[end[0],end[1]-1,top]]
            else:points += [[end[0],lane,top],[end[0],end[1]+1,top]]
        elif ROUTE_STYLE == 'top-entry':
            low=82.6+index*3; top=169+index*3
            points=[start,[start[0],start[1],low],[start[0],lane,low],
                    [start[0],lane,top],[end[0],lane,top],
                    [end[0],end[1],top],[end[0],end[1],158.6]]
        else:
            points=[start,[start[0],start[1],82.6],[start[0],lane,82.6],
                    [start[0],lane,151.5],[end[0],lane,151.5],[end[0],end[1]+1,151.5]]
        edges=prefix+list(B.R.rounded([A.Vector(*p) for p in points],10).Edges)+suffix
        bare=([Part.makeLine(A.Vector(end[0],end[1],158.6),A.Vector(*end))]
              if ROUTE_STYLE == 'top-entry' else
              [B.arc([end[0],end[1]+direction,top+1 if ROUTE_STYLE=='underboard-complete' else 152.5],
                     [end[0],end[1]+direction,top if ROUTE_STYLE=='underboard-complete' else 151.5],
                     [end[0],end[1],top+1 if ROUTE_STYLE=='underboard-complete' else 152.5]),
               Part.makeLine(A.Vector(end[0],end[1],top+1 if ROUTE_STYLE=='underboard-complete' else 152.5),A.Vector(*end))])
        length=sum(e.Length for e in edges)
        bare_length=sum(e.Length for e in bare)
        routes.append(dict(wire=name,pi_pin=pin,board_landing=ref,start_mm=start,end_mm=end,
            insulated_route_mm=length,bare_tail_mm=bare_length,strip_trim_mm=6,Pi_service_reserve_mm=30,
            required_factory_length_mm=length+bare_length+36,nominal_factory_length_mm=FACTORY_LENGTH,
            factory_margin_mm=FACTORY_LENGTH-length-bare_length-36,minimum_bend_mm=10))
        for role,es,rad in [('insulated',edges,.7),('bare',bare,math.sqrt(.129/math.pi))]:
            for i,e in enumerate(es):
                shape=tube(e,rad);assert shape.isValid() and len(shape.Solids)==1
                shape.exportBrep(str(OUT/f'{name}_{role}_{i}_DESIGN.brep'))
                e.exportBrep(str(OUT/f'{name}_{role}_{i}_CENTERLINE.brep'))
                geometry.append((f'{name}_{role}_{i}',shape))
                for owner,s in owners.items():
                    if not shape.BoundBox.intersect(s.BoundBox):continue
                    for j,solid in enumerate(s.Solids):
                        v=shape.common(solid).Volume
                        if v>1e-6: rows.append(dict(wire=name,role=role,segment=i,owner=owner,solid=j,volume_mm3=v))
    wire_hits=[]
    wire_shapes=[(n,s) for n,s in geometry if n!='J8_housing_nominal']
    for i,(n,s) in enumerate(wire_shapes):
        for m,t in wire_shapes[i+1:]:
            if n.split('_')[0]==m.split('_')[0] or not s.BoundBox.intersect(t.BoundBox):continue
            v=s.common(t).Volume
            if v>1e-6:wire_hits.append(dict(a=n,b=m,volume_mm3=v))
    housing_hits=[]
    for name,s in owners.items():
        for j,solid in enumerate(s.Solids):
            v=housing.common(solid).Volume
            if v>1e-6:housing_hits.append(dict(owner=name,solid=j,volume_mm3=v))
    sources=dict(r.hashes)
    for path in list(paths.values())+['hardware/electronics/full-cat/pi-logic-interface-r1/interface.json','hardware/electronics/full-cat/pwm-carrier-r3/population.json','hardware/electronics/full-cat/board-interfaces-r1/interfaces.json']:
        sources[path]=sha(ROOT/path)
    for p in REF.iterdir():
        if p.is_file():sources[p.relative_to(ROOT).as_posix()]=sha(p)
    save('checks.json',dict(status='WHOLE_GPIO_ROUTE_CANDIDATE_NOT_SELECTED',routes=routes,
        material_hits=rows,wire_wire_hits=wire_hits,housing_hits=housing_hits,owner_bounds={n:bbox(s) for n,s in owners.items()},
        source_sha256=sources,portal_evidence=portal_evidence,physical_pass=False,
        new_stls=portal_evidence.get('new_stls',0) if portal_evidence else 0,CP_PI_complete=False,
        required_remaining=['Latest Carrier descendant, wire-wire separation and whole restraint construction','Power/USB integration']))
    meshes=[]
    for name,s in geometry+list(owners.items()):
        if name in ('Cover',):continue
        vs,fs=s.tessellate(.35);meshes.append(dict(name=name,vertices=[list(v) for v in vs],triangles=fs))
    save('preview-geometry.json',meshes)
    print(json.dumps(dict(routes=routes,material_hits=rows,wire_wire_hits=wire_hits,housing_hits=housing_hits)),flush=True)

if __name__=='__main__':main()
