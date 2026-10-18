"""Abandon the rejected fore bulkhead: full central Pi occupied-edge wedge.

One source-pinned planning hypothesis, not native mount or N01 completion.
Fasteners reverse about their actual PCB hole axes, with selected hardware
unchanged. GPIO grips are after the bend; source housing fit is provisional.
"""
import hashlib
import json
import time
import zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT, sha
from plan_feline_layout import OUT
from feline_current_scene import load, box
from check_feline_shared_space import tube_prefix
from check_feline_all_current_lands import near
from plan_feline_front_service_split import line_tube


def packed(path):
    data=json.loads(path.read_text());bundle=ROOT/data['bundle']
    assert sha(bundle)==data['bundle_sha256']
    shapes={};rows={}
    with zipfile.ZipFile(bundle) as z:
        for r in data['parts']:
            raw=z.read(r['entry']);assert hashlib.sha256(raw).hexdigest()==r['sha256']
            s=Part.Shape();s.importBrepFromString(raw.decode());shapes[r['name']]=s;rows[r['name']]=r
    return data,shapes,rows


def main():
    tick=time.monotonic();dest=OUT/'n01-central-pi-wedge.json';assert not dest.exists()
    parent=OUT/'n01-front-service-split-plan.json';p,proposal,rows=packed(parent)
    contract=OUT/'n01-pi-full-port-contract.json';pi=json.loads(contract.read_text())
    scene,meta,_,_,pins,_=load()
    for n in p['retired_planning_parts']:scene.pop(n);meta.pop(n)
    localpath=OUT/'n01-selected-local-head-tail-sources.json';local,locals_,localrows=packed(localpath)
    for n,s in locals_.items():
        if not s.Solids:continue
        if localrows[n]['role']=='HeadElectricalYaw':s.translate(A.Vector(0,0,35))
        scene[n]=s;meta[n]=localrows[n]
    assert len(scene)==911
    oldrot=A.Rotation(A.Vector(0,1,0),90)*A.Rotation(A.Vector(1,0,0),180)
    old=A.Placement(A.Vector(-125,0,86.15)-oldrot.multVec(A.Vector(0,0,47.72)),oldrot)
    rot=A.Rotation(A.Vector(1,0,0),-10)
    pose=A.Placement(A.Vector(0,0,84)-rot.multVec(A.Vector(0,0,47.72)),rot)
    pi_shapes={};pi_rows={};ends={};gpio={};fasteners=[]
    def put(n,s,kind='reservation'):
        assert s.isValid() and len(s.Solids)==1,n
        pi_shapes[n]=s;pi_rows[n]=dict(name=n,group='PiWedge',kind=kind)
    for n,r in list(rows.items()):
        if r['group']!='PiBulkhead':continue
        s=proposal.pop(n);rows.pop(n)
        if not n.startswith('Ref_Material_Pi4'):continue
        s.Placement=old.inverse()*s.Placement
        if 'NominalPCB' not in n:
            centre=s.BoundBox.Center;axis=A.Vector(centre.x,centre.y,48.52)
            flip=A.Rotation(A.Vector(1,0,0),180)
            s.Placement=A.Placement(axis-flip.multVec(axis),flip)*s.Placement
            fasteners.append(dict(name=n,hole_axis_source_mm=list(axis),same_hardware_reversed=True))
        s.Placement=pose*s.Placement;put(n,s,'proposal_material')
    for r in pi['parts']+pi['additional_reservations']:
        s=box(*r['source_bounds_mm']);s.Placement=pose*s.Placement;put('PiBudget:'+r['role'],s)
    usb=pi['USB_A_data_plug_budget'];s=box(*usb['source_bounds_mm']);s.Placement=pose*s.Placement
    put('PiBudget:USB_A_data_boot',s)
    def prefix(n,q,d,b,r,R,first):
        end=q+d*(first+R)+b*R;finish=end+b*9
        put(n,tube_prefix(list(q),list(d),r,list(b),R,first),'proposal_wire')
        put(n+':grip',line_tube(list(end),list(finish),r),'proposal_wire')
        ends[n]=dict(point_mm=list(q),departure_axis=list(d),bend_direction=list(b),
            R_mm=R,first_straight_mm=first,after_turn_grip_mm=[list(end),list(finish)])
        return pi_shapes[n].fuse(pi_shapes[n+':grip'])
    for e in pi['GPIO_endpoints']:
        source=A.Vector(*e['point_mm'])-A.Vector(0,0,50.38)
        q=pose.multVec(source);d=rot.multVec(A.Vector(0,0,1))
        b=rot.multVec(A.Vector(.6 if e['endpoint'] in ('PI.H6','PI.H11') else -.6,.8,0))
        gpio[e['endpoint']]=prefix('PiGPIO:'+e['endpoint'],q,d,b,.7,10,1.5)
    q=pose.multVec(A.Vector(*usb['source_wire_mouth_mm']))
    prefix('PiUSBData',q,A.Vector(1,0,0),A.Vector(0,-1,0),2.5,30,3)
    for wid,mouth in pi['full_selected_USB_C_receiver']['free_wire_mouths_mm'].items():
        prefix('PiPower:'+wid,pose.multVec(A.Vector(*mouth)),A.Vector(1,0,0),A.Vector(0,1,0),1.55,12.4,9)
    fixed={n:s for n,s in scene.items() if not meta[n].get('role','').startswith('leg:')}
    world={**fixed,**proposal,**pi_shapes};bounds={n:s.BoundBox for n,s in world.items()}
    result=dict(status='RUNNING_CENTRAL_PI_OCCUPIED_EDGE_GATE',selected=False,N01_complete=False,physical_pass=False,
        whole_layout_qualified=False,source_parent=parent.relative_to(ROOT).as_posix(),
        central_PCB_bottom_datum_mm=[0,0,84],tilt_about_X_degrees=-10,fastener_reversal=fasteners,
        end_overrides=ends,source_sha256={**pins,parent.relative_to(ROOT).as_posix():sha(parent),
            contract.relative_to(ROOT).as_posix():sha(contract),localpath.relative_to(ROOT).as_posix():sha(localpath),
            Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        actual_clearance_failures=[],reservation_holds=[],errors=[],completed_queries=[],GPIO_pair_gaps=[],
        open=['All20WAGO shared plan, retained R2 wire failures not waived',
            'Mount roots/tool paths and exact roof containment before N01',
            'Full middles/stock/native/motion remain later deliverables'],
        source_fit_assumptions=['1.5mm GPIO entry before R10; 9mm grip AFTER turn',
            'Official footprint height plus conservative occupied housing; delivered fit gate'],
        maximum_proposed_Z_mm=max(s.BoundBox.ZMax for s in pi_shapes.values()))
    bundle=dest.with_suffix('.zip');outrows=[]
    with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
        for n,s in pi_shapes.items():
            entry=f'{len(outrows):04}.brep';raw=s.exportBrepToString().encode();z.writestr(entry,raw)
            outrows.append(dict(pi_rows[n],entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    result.update(parts=outrows,bundle=bundle.relative_to(ROOT).as_posix(),bundle_sha256=sha(bundle))
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    def kind(n):
        if n in pi_rows:return pi_rows[n]['kind']
        if n in rows:return rows[n]['kind']
        r=meta[n];return 'reservation' if 'reservation' in r.get('kind','') or r.get('role')=='ScaffoldPlanning' else 'material'
    def wire(n):return kind(n)=='proposal_wire' or n.startswith(('BankFullPrefix:','End:','Factory:')) or n in ('W043','W077','W078')
    def query(n,m,minimum):
        if time.monotonic()-tick>150:raise TimeoutError('150s gate; completed queries saved')
        if not world[m].isValid():result['errors'].append(dict(name=m,error='Invalid BRep, no acceptance'));return
        gap=world[n].distToShape(world[m])[0]
        r=dict(a=n,b=m,gap_mm=gap,required_mm=minimum)
        result['completed_queries'].append(r)
        if gap<minimum-1e-5:
            (result['reservation_holds'] if kind(n)=='reservation' or kind(m)=='reservation' else result['actual_clearance_failures']).append(r)
        if len(result['completed_queries'])%10==0:save()
    save()
    try:
        for i,(n,s) in enumerate(gpio.items()):
            for m,t in list(gpio.items())[i+1:]:
                gap=s.distToShape(t)[0];result['GPIO_pair_gaps'].append(dict(a=n,b=m,gap_mm=gap))
                assert gap>=.2-1e-5,(n,m,gap)
        for n,s in pi_shapes.items():
            for m in world:
                if m in pi_shapes or not near(bounds[n],bounds[m],1.25):continue
                query(n,m,.2 if wire(n) and wire(m) else 1.25)
            # Only genuine new wire-to-own hardware/other port interfaces;
            # exclude intentionally occupied housing at the first endpoint.
            if wire(n):
                for m in pi_shapes:
                    if wire(m) or m.endswith(('GPIO1992OccupiedHousing','GPIO_header')):continue
                    if near(bounds[n],bounds[m],1.25):query(n,m,1.25)
            print('Received',n,len(result['completed_queries']),flush=True);save()
        result['status']='CENTRAL_PI_WEDGE_REJECTED' if result['actual_clearance_failures'] or result['reservation_holds'] or result['errors'] else 'CENTRAL_PI_OCCUPIED_EDGE_STATIC_CLEAR_WHOLE_PLAN_OPEN'
    except Exception as e:result['status']='PARTIAL_CENTRAL_PI_WEDGE';result['errors'].append(repr(e))
    save();print(json.dumps(dict(status=result['status'],parts=len(pi_shapes),pairs=len(result['completed_queries']),
        failures=len(result['actual_clearance_failures']),holds=len(result['reservation_holds']),errors=result['errors'],
        maximum_Z_mm=result['maximum_proposed_Z_mm'],seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':main()
