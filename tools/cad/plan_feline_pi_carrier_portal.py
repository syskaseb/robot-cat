"""Coupled Pi occupied-edge and carrier topology, after first wedge rejection."""
import json
import time
import zipfile
import hashlib
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_central_pi_wedge import packed
from plan_feline_front_service_split import line_tube
from feline_current_scene import load,box
from check_feline_all_current_lands import near
from check_feline_shared_space import tube_prefix


def main():
    tick=time.monotonic();dest=OUT/'n01-pi-carrier-portal.json';assert not dest.exists()
    oldpath=OUT/'n01-central-pi-wedge.json';old,pishapes,pirows=packed(oldpath)
    pp=ROOT/old['source_parent'];parent,others,rows=packed(pp)
    for n in list(others):
        if rows[n]['group']=='PiBulkhead':others.pop(n);rows.pop(n)
    scene,meta,_,_,pins,_=load()
    for n in parent['retired_planning_parts']:scene.pop(n);meta.pop(n)
    localpath=OUT/'n01-selected-local-head-tail-sources.json';_,ls,lr=packed(localpath)
    for n,s in ls.items():
        if not s.Solids:continue
        if lr[n]['role']=='HeadElectricalYaw':s.translate(A.Vector(0,0,35))
        scene[n]=s;meta[n]=lr[n]
    retired=['StructureReserve:UpperStrip1','StructureReserve:UpperStrip-1']
    for n in retired:
        assert 'reservation' in meta[n].get('kind',''),(n,meta[n])
        scene.pop(n);meta.pop(n)
    oldr=A.Rotation(A.Vector(1,0,0),-10)
    oldpose=A.Placement(A.Vector(0,0,84)-oldr.multVec(A.Vector(0,0,47.72)),oldr)
    rot=A.Rotation(A.Vector(0,0,1),180)*A.Rotation(A.Vector(1,0,0),-12)
    pose=A.Placement(A.Vector(50,0,84)-rot.multVec(A.Vector(0,0,47.72)),rot)
    delta=pose*oldpose.inverse()
    for n,s in list(pishapes.items()):
        if n.startswith(('PiUSBData','PiPower:')):pishapes.pop(n);pirows.pop(n);continue
        s.Placement=delta*s.Placement
    ends={}
    for n,e in old['end_overrides'].items():
        if not n.startswith('PiGPIO:'):continue
        ends[n]=dict(e,point_mm=list(delta.multVec(A.Vector(*e['point_mm']))),
            departure_axis=list(delta.Rotation.multVec(A.Vector(*e['departure_axis']))),
            after_turn_grip_mm=[list(delta.multVec(A.Vector(*q))) for q in e['after_turn_grip_mm']])
    def put(n,s,kind='reservation',group='PiWedge'):
        assert s.isValid() and len(s.Solids)==1,n
        pishapes[n]=s;pirows[n]=dict(name=n,group=group,kind=kind)
    def prefix(n,q,d,b,r,R,first):
        end=q+d*(first+R)+b*R;tip=end+b*9
        put(n,tube_prefix(list(q),list(d),r,list(b),R,first),'proposal_wire')
        put(n+':grip',line_tube(list(end),list(tip),r),'proposal_wire')
        ends[n]=dict(point_mm=list(q),departure_axis=list(d),R_mm=R,first_straight_mm=first,
            after_turn_grip_mm=[list(end),list(tip)],bend_direction=list(b))
    contract=OUT/'n01-pi-full-port-contract.json';pi=json.loads(contract.read_text())
    prefix('PiUSBData',pose.multVec(A.Vector(*pi['USB_A_data_plug_budget']['source_wire_mouth_mm'])),
        A.Vector(-1,0,0),A.Vector(0,-1,0),2.5,30,3)
    for wid,q in pi['full_selected_USB_C_receiver']['free_wire_mouths_mm'].items():
        prefix('PiPower:'+wid,pose.multVec(A.Vector(*q)),A.Vector(-1,0,0),A.Vector(0,1,0),1.55,12.4,9)
    # Connected planning portals: lap actual current four post envelopes,
    # not new isolated stems. MAIN's fore cap remains, Pi PCB area is vacated.
    for side in (-1,1):
        rail=box([-83 if side<0 else -72,side*32-1.5,78],[108,side*32+1.5,81])
        spans=[([-83,-43,78],[-77,-30.5,81]),([102,-33.5,78],[108,-17,81])] if side<0 else [([-72,17,78],[-66,33.5,81]),([102,17,78],[108,33.5,81])]
        for lo,hi in spans:rail=rail.fuse(box(lo,hi))
        if side<0:rail=rail.fuse(box([-83,-31,78],[-27.5,-10,84.3]))
        put('PiPortal:'+str(side),rail.removeSplitter(),'reservation','PiPortal')
    fixed={n:s for n,s in scene.items() if not meta[n].get('role','').startswith('leg:')}
    world={**fixed,**others,**pishapes};bounds={n:s.BoundBox for n,s in world.items()}
    result=dict(status='RUNNING_PI_PORTAL_SHARED_GATE',selected=False,N01_complete=False,physical_pass=False,
        source_parent=pp.relative_to(ROOT).as_posix(),retired_additional_parts=retired,
        PCB_bottom_datum_mm=[50,0,84],rotation_rows=[[getattr(rot.toMatrix(),f'A{i+1}{j+1}') for j in range(3)] for i in range(3)],
        endpoint_overrides=ends,actual_clearance_failures=[],reservation_holds=[],known_invalid_supplier_holds=[],
        errors=[],completed_queries=[],own_named_mates=[],portal_post_laps=[],
        source_sha256={**pins,oldpath.relative_to(ROOT).as_posix():sha(oldpath),pp.relative_to(ROOT).as_posix():sha(pp),
            localpath.relative_to(ROOT).as_posix():sha(localpath),contract.relative_to(ROOT).as_posix():sha(contract),
            Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        whole_scene_motion_tools_roots_and_remaining_WAGO_still_open=True,
        inherited_GPIO_pair_clearance_rigid_invariant_min_mm=min(r['gap_mm'] for r in old['GPIO_pair_gaps']),
        max_Z_mm=max(s.BoundBox.ZMax for s in pishapes.values()))
    def kind(n):
        if n in pirows:return pirows[n]['kind']
        if n in rows:return rows[n]['kind']
        r=meta[n];return 'reservation' if 'reservation' in r.get('kind','') or r.get('role')=='ScaffoldPlanning' else 'material'
    def wire(n):return kind(n)=='proposal_wire' or n.startswith(('BankFullPrefix:','End:','Factory:')) or n in ('W043','W077','W078')
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    bundle=dest.with_suffix('.zip');outrows=[]
    with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
        for n,s in pishapes.items():
            raw=s.exportBrepToString().encode();entry=f'{len(outrows):04}.brep';z.writestr(entry,raw)
            outrows.append(dict(pirows[n],entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    result.update(parts=outrows,bundle=bundle.relative_to(ROOT).as_posix(),bundle_sha256=sha(bundle));save()
    try:
        seen=set()
        for n,s in pishapes.items():
            for m,t in world.items():
                key=tuple(sorted((n,m)))
                if n==m or key in seen or not near(bounds[n],bounds[m],1.25):continue
                if m in pishapes and not wire(n):continue
                if m in pishapes and wire(m):continue
                if m in pishapes and m.endswith(('GPIO1992OccupiedHousing','GPIO_header')):continue
                seen.add(key)
                if time.monotonic()-tick>180:raise TimeoutError('180s scoped gate')
                if not t.isValid():
                    result['known_invalid_supplier_holds'].append(dict(a=n,b=m,not_clearance=True));continue
                gap=s.distToShape(t)[0];minimum=.2 if wire(n) and wire(m) else 1.25
                r=dict(a=n,b=m,gap_mm=gap,required_mm=minimum);result['completed_queries'].append(r)
                # Named mould mouths are occupied interfaces, not air gaps.
                mate=(n=='PiUSBData' and m=='PiBudget:USB_A_data_boot') or (n in ('PiPower:W079','PiPower:W080') and m=='PiBudget:RetainedK1474Boot')
                postmate=n.startswith('PiPortal:') and m.startswith('StructureReserve:PCBpost')
                if mate:result['own_named_mates'].append(r)
                elif postmate:
                    r['lap_mm3']=s.common(t).Volume;assert r['lap_mm3']>0
                    result['portal_post_laps'].append(r)
                elif gap<minimum-1e-5:
                    (result['reservation_holds'] if kind(n)=='reservation' or kind(m)=='reservation' else result['actual_clearance_failures']).append(r)
                if len(result['completed_queries'])%10==0:save()
            print('Received',n,len(result['completed_queries']),flush=True);save()
        result['status']='PI_PORTAL_SHARED_GATE_REJECTED' if result['actual_clearance_failures'] or result['reservation_holds'] or result['errors'] else 'PI_PORTAL_STATIC_CLEAR_LIMITED_SCOPE'
    except Exception as e:result['status']='PARTIAL_PI_PORTAL_GATE';result['errors'].append(repr(e))
    save();print(json.dumps(dict(status=result['status'],pairs=len(result['completed_queries']),
        failures=len(result['actual_clearance_failures']),holds=len(result['reservation_holds']),
        invalid_holds=result['known_invalid_supplier_holds'],errors=result['errors'],max_Z_mm=result['max_Z_mm'],seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':main()
