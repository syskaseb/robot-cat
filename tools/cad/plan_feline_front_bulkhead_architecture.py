"""One changed whole topology; no height-grid, native details or fullN01 claim.

Pi in fore vertical bulkhead with BOTH occupied edges; ten down-facing side
stations and three vertical FHACs between stations. Case/factory/grip/frame
budgets planned together. Static material gates precede expensive motion.
"""
import hashlib
import itertools
import json
import math
import time
import zipfile
from pathlib import Path
import FreeCAD as A
import Part
from feline_current_scene import load, box
from check_feline_all_current_lands import near
from check_feline_shared_space import tube_prefix
from check_feline_leg_body import placement
from plan_feline_layout import OUT, STAGES
from check_main_p0_placement import ROOT,sha


def tf_from_centre(shape,centre,rotation):
    return A.Placement(A.Vector(*centre)-rotation.multVec(shape.BoundBox.Center),rotation)


def tube(curve,radius):
    first=curve.Edges[0];p=first.valueAt(first.FirstParameter)
    s=curve.makePipeShell([Part.Wire([Part.makeCircle(radius,p,first.tangentAt(first.FirstParameter))])],True,False)
    assert s.isValid() and len(s.Solids)==1
    return s


def main():
    tick=time.monotonic();dest=OUT/'n01-front-bulkhead-architecture.json';assert not dest.exists()
    scene,meta,templates,data,pins,_=load()
    sources={k:OUT/n for k,n in dict(pi='n01-pi-full-port-contract.json',
        local='n01-selected-local-head-tail-sources.json',extra='n01-all-extra-interface-contract.json',
        motion='motion-layout.json').items()}
    p={k:json.loads(f.read_text()) for k,f in sources.items()}
    pins.update({f.relative_to(ROOT).as_posix():sha(f) for f in (*sources.values(),Path(__file__))})
    groups={};kinds={};owners={};mates={};changed_ends={};retired={};newports=[]
    report=dict(status='RUNNING_ONE_FRONT_BULKHEAD_SHARED_TOPOLOGY',selected=False,N01_complete=False,
        physical_pass=False,complete_route_or_native_approval=False,source_sha256=pins,
        hard_clearance_mm=1.25,case_and_material_contacts=[],reservation_conflicts=[],errors=[],pairs=0,
        interface_changes=['WholePi Ry-90 forebulkhead, completeGPIO/power/data budget; not tinyR3mould',
            'Ten side stations DOWN,22mm initial stroke thenR12.4INBOARD and9mm independent grip',
            'Three FHAC vertical with six whole factory-to-custom/splice/independent grip budgets',
            'Head and all retained head local sources raised35mm together; original internals unchanged',
            'New envelope candidate198mm max, within200 limit, not native/print selected'],
        design=dict(Pi_PCB_source_origin_target_mm=[-108,0,-19.65],Pi_rotation_about_Y_degrees=-90,
            head_relative_raise_mm=35,side_station_centres_X_mm=[-50,-14,22,58,94],
            side_station_centres_Y_mm=[-67.5,67.5],side_station_centre_Z_mm=40,
            FHAC_centres={'F_HY':[-24,-83.5,32],'F_HP':[12,83.5,32],'F_TY':[48,-83.5,32]},
            FHAC_root_between_stations_X_mm={'F_HY':-32,'F_HP':4,'F_TY':40},
            Monitor_centre_mm=[50,68,0],F_PWM_centre_mm=[60,-76,-20]),
        preserved=['lower118/fourMTA/eightfactorysides','complete24bankquarters','W043/W077/W078',
            'all15drives/P0/E6/provisionalreplaceableMG92B','MAINnegativeupperstrip andactualdatums'],
        holds=['All89body+34extra external middles/lengths and every restraint load path/tool/removal sequence',
            'Newneck/core/head motion and exact revised skin containment',
            'Pi carrier roots on actual availableframeholes, all new native geometry/parameter/reopen/stock',
            'Yaw220mm plus30mm residual deliveryfit budget is NOT a modeled installed250mm coil',
            'Reservation overlap is not proof of real supplier contact; cannot silently accept it either'])
    def save():
        report['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    def gate():
        if time.monotonic()-tick>240:raise TimeoutError('240s integrated topology gate; preserve receipt')
    def add(group,name,s,kind='proposal_material',mate=()):
        assert s.isValid() and s.Solids,(name,'Invalid proposed shape')
        groups.setdefault(group,{})[name]=s;kinds[name]=kind;owners[name]=group;mates[name]=set(mate)
    def remove(n):
        retired[n]=meta[n];scene.pop(n);meta.pop(n)
    def material_kind(row):
        k=row.get('kind','');role=row.get('role','')
        return 'reservation' if 'reservation' in k or role=='ScaffoldPlanning' else 'material'
    try:
        # Keep all existing head mechanics but propose a whole rigid+35raise.
        # This invalidates its old body/root qualification, not its internals.
        for n in list(scene):
            if meta[n].get('role')=='HeadMechanism':
                s=scene[n].copy();s.translate(A.Vector(0,0,35));remove(n);add('HeadRaised',n,s)
        # Replace complete Pi pose and its obsolete *own* planning roots.
        rotate=A.Rotation(A.Vector(0,1,0),-90)
        current_origin=A.Vector(0,0,98.1)
        pi_tf=A.Placement(A.Vector(-108,0,-19.65)-rotate.multVec(current_origin),rotate)
        source_tf=A.Placement(A.Vector(-108,0,-19.65)-rotate.multVec(A.Vector(0,0,47.72)),rotate)
        for n in list(scene):
            if meta[n].get('role')=='Pi4':
                if n=='NominalPiUSBCPowerMould':remove(n);continue
                s=scene[n].copy();s.Placement=pi_tf*s.Placement;remove(n);add('PiBulkhead',n,s)
            elif n.startswith(('StructureReserve:PCBrootPi4','StructureReserve:PCBrailPi4')):remove(n)
        for r in p['pi']['parts']+p['pi']['additional_reservations']:
            s=box(*r['source_bounds_mm']);s.Placement=source_tf*s.Placement
            add('PiBulkhead','PiBudget:'+r['role'],s,'reservation')
        usb=p['pi']['USB_A_data_plug_budget'];s=box(*usb['source_bounds_mm']);s.Placement=source_tf*s.Placement
        add('PiBulkhead','PiBudget:USB_A_data_boot',s,'reservation')
        mouth=source_tf.multVec(A.Vector(*usb['source_wire_mouth_mm']));direction=rotate.multVec(A.Vector(1,0,0))
        # Short exit beforeR30, then9mm independent AFTER-bend grip. Avoid
        # requiring a fictitious extra9mm straight before every USB bend.
        add('PiBulkhead','PiBudget:USB_A_full_first_bend',tube_prefix(list(mouth),list(direction),2.5,[1,0,0],30,3),'reservation')
        report['Pi_USB_A_mouth_mm']=list(mouth)
        for e in p['pi']['GPIO_endpoints']:
            q=pi_tf.multVec(A.Vector(*e['point_mm']));d=pi_tf.Rotation.multVec(A.Vector(*e['departure_axis']))
            add('PiBulkhead','PiGPIO:'+e['endpoint'],tube_prefix(list(q),list(d),.7,[0,0,1],10),'reservation')
            changed_ends[e['endpoint']]=dict(point_mm=list(q),departure_axis=list(d))
        for name,q in p['pi']['full_selected_USB_C_receiver']['free_wire_mouths_mm'].items():
            q=source_tf.multVec(A.Vector(*q));d=rotate.multVec(A.Vector(1,0,0))
            changed_ends[name+'/Pi']=dict(point_mm=list(q),departure_axis=list(d))
            add('PiBulkhead','PiPower:'+name,tube_prefix(list(q),list(d),1.55,[1,0,0],12.4),'reservation')
        # Both side rows turn DOWN as an entire distribution architecture.
        for sign,refs in [(-1,['G_TAIL','G_AUX','P_AUX','G2','FL_P']),
                           (1,['D_FL','FL_G','FR_P','D_FR','FR_G'])]:
            for x,ref in zip(report['design']['side_station_centres_X_mm'],refs):
                st=next(st for st in data['ports']['stations'] if st['ref']==ref)
                n=next(n for n,r in meta.items() if r.get('role')==st['current_group'])
                rot=A.Rotation(A.Vector(1,0,0),90*sign)
                if ref in ('G_TAIL','G_AUX','P_AUX'):rot=rot*A.Rotation(A.Vector(0,0,1),180)
                s=scene[n].copy();tf=tf_from_centre(s,[x,sign*67.5,40],rot);s.Placement=tf*s.Placement
                remove(n);g='WG:'+ref;add(g,n,s)
                for e in st['occupied_ports']:
                    q=tf.multVec(A.Vector(*e['point_mm']));d=rot.multVec(A.Vector(*e['departure_axis']))
                    assert d.z<-.99,(ref,list(d))
                    bend=[0,-sign,0];radius=2.1 if ref=='P_AUX' else 1.55
                    wire=tube_prefix(list(q),list(d),radius,bend,12.4,22)
                    end=q+d*(22+12.4)+A.Vector(*bend)*12.4
                    add(g,'StationWire:'+e['endpoint'],wire,'proposal_wire')
                    land=Part.Wire([Part.makeLine(end,end+A.Vector(*bend)*9)])
                    add(g,'StationLand:'+e['endpoint'],tube(land,radius),'proposal_wire')
                    changed_ends[e['endpoint']]=dict(point_mm=list(q),departure_axis=list(d),
                        supported_after_turn_end_mm=list(end+A.Vector(*bend)*9))
                newports.append(dict(ref=ref,station_centre_mm=[x,sign*67.5,40],occupied=len(st['occupied_ports'])))
        # Vertical FHAC cases occupy the spaces beside/between stations. Both
        # factory pieces and actual lap/sleeve/custom grip lengths are present.
        factoryports={}
        for e in [e for r in p['extra']['sections'] for e in r['ends'] if e.get('local_point_mm') is not None]:
            factoryports[e['endpoint']]=e
        for role,c in report['design']['FHAC_centres'].items():
            _,s,_=templates[role];s=s.copy();rot=A.Rotation(A.Vector(0,1,0),-90)
            tf=tf_from_centre(s,c,rot);s.Placement=tf*s.Placement;add(role,role+':case',s)
            bb=s.BoundBox;sign=1 if c[1]>0 else -1;rootx=report['design']['FHAC_root_between_stations_X_mm'][role]
            bed='StructureReserve:BankBed'+str(sign)
            floor=box([bb.XMin-1,bb.YMin-1,bb.ZMin-2],[bb.XMax+1,bb.YMax+1,bb.ZMin])
            add(role,role+':floor',floor,'reservation')
            # Backer stands in a complete inter-station gap; floor/root include
            # overlap, not a floating post. Native body/mate still unselected.
            ya,yb=(70,73) if sign>0 else (-73,-70)
            rootya,rootyb=(65.75,73) if sign>0 else (-73,-65.75)
            add(role,role+':backer',box([rootx-1.5,ya,bb.ZMin-2],[rootx+1.5,yb,55]),'reservation')
            add(role,role+':bed_root',box([rootx-1.5,rootya,52],[rootx+1.5,rootyb,55]),'reservation',(bed,))
            for side in ('in','out'):
                e=factoryports[role+'.'+side];q=A.Vector(*c)+rot.multVec(A.Vector(*e['local_point_mm']))
                d=rot.multVec(A.Vector(*e['departure_axis']));bend=A.Vector(0,-sign,0)
                a=q+d*9;mid=a+d*(12.4/math.sqrt(2))+bend*(12.4*(1-1/math.sqrt(2)));b=a+d*12.4+bend*12.4
                tip=b+bend*10;curve=Part.Wire([Part.makeLine(q,a),Part.Arc(a,mid,b).toShape(),Part.makeLine(b,tip)])
                assert curve.Length<84.5
                add(role,role+':factory_'+side,tube(curve,2),'proposal_wire')
                add(role,role+':splice_'+side,tube(Part.Wire([Part.makeLine(tip-bend*14,tip+bend*6)]),2.4),'reservation')
                add(role,role+':custom_'+side,tube(Part.Wire([Part.makeLine(tip-bend*8,tip+bend*18)]),1.55),'proposal_wire')
                changed_ends[role+'.'+side]=dict(point_mm=list(q),departure_axis=list(d),
                    nominal_factory_guide_mm=curve.Length,custom_grip_line_mm=[list(tip+bend*9),list(tip+bend*18)],
                    factory100mm_is_assumption=True,lap_mm=8,sleeve_mm=20)
        for role,c in [('F_PWM',[60,-76,-20]),('Monitor5015',[50,68,0])]:
            _,s,_=templates[role];s=s.copy();rot=A.Rotation(A.Vector(1,0,0),90) if role=='Monitor5015' else A.Rotation()
            s.Placement=tf_from_centre(s,c,rot)*s.Placement;add(role,role+':case',s)
        # Current local head/tail geometry is not silently absent. Curves are
        # checked by profile-distance in the NEXT routing gate, not called
        # physical solids, while actual insulation/JR budgets are included here.
        local=p['local'];lb=ROOT/local['bundle'];assert sha(lb)==local['bundle_sha256'];pins[lb.relative_to(ROOT).as_posix()]=sha(lb)
        report['retained_local_curve_reservations']=[]
        with zipfile.ZipFile(lb) as archive:
            for r in local['parts']:
                raw=archive.read(r['entry']);assert hashlib.sha256(raw).hexdigest()==r['sha256']
                s=Part.Shape();s.importBrepFromString(raw.decode('utf-8'))
                if r['role']=='HeadElectricalYaw':s.translate(A.Vector(0,0,35))
                if s.Solids:
                    n=r['name'];scene[n]=s;meta[n]=r
                else:report['retained_local_curve_reservations'].append(r['name'])
        report['changed_endpoints']=changed_ends;report['station_ports']=newports;report['retired_planning_parts']=list(retired)
        report['proposed_group_parts']={g:list(ss) for g,ss in groups.items()};save()
        # Save the actual proposed whole geometry before any costly query, so
        # failed gates retain the exact cause and never require construction again.
        bundle=dest.with_suffix('.zip');rows=[]
        with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as archive:
            for g,ss in groups.items():
                for n,s in ss.items():
                    raw=s.exportBrepToString().encode('utf-8');entry=f'{len(rows):04}.brep';archive.writestr(entry,raw)
                    rows.append(dict(name=n,group=g,kind=kinds[n],entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
        report['bundle']=bundle.relative_to(ROOT).as_posix();report['bundle_sha256']=sha(bundle);report['parts']=rows;save()
        fixed={n:s for n,s in scene.items() if not meta[n].get('role','').startswith('leg:')}
        # Only changed groups against retained groups: unchanged pairs not repeated.
        obstacles={**fixed,**{n:s for g,ss in groups.items() for n,s in ss.items()}}
        obstacle_owner={n:'retained' for n in fixed};obstacle_owner.update(owners)
        boxes={n:s.BoundBox for n,s in obstacles.items()};seen=set()
        print('Whole architecture constructed',len(rows),'changed parts;',len(scene),'retained; no native',flush=True)
        for g,ss in groups.items():
            for n,s in ss.items():
                gate()
                if kinds[n]=='proposal_wire':continue # full wire/motion stage only after body gate
                for m,t in obstacles.items():
                    if obstacle_owner[m]==g or m in mates[n] or not near(s.BoundBox,boxes[m],1.25):continue
                    key=tuple(sorted((n,m)))
                    if key in seen:continue
                    seen.add(key);gate()
                    if not t.isValid() or not t.Solids:
                        report['errors'].append(dict(a=n,b=m,error='Invalid source geometry, not clearance'));continue
                    report['pairs']+=1;v=s.common(t);assert v.isNull() or v.isValid(),(n,m,'Invalid common')
                    distance=s.distToShape(t)[0]
                    if v.Volume>1e-5 or distance<1.25-1e-5:
                        other_kind=kinds[m] if m in kinds else material_kind(meta[m])
                        target=report['reservation_conflicts'] if 'reservation' in (kinds[n],other_kind) else report['case_and_material_contacts']
                        target.append(dict(a=n,b=m,volume_mm3=v.Volume,gap_mm=distance,group=g,
                            reservation_overlap_is_not_real_contact=(target is report['reservation_conflicts'])))
            save();print('Received group',g,'pairs',report['pairs'],'material failures',len(report['case_and_material_contacts']),
                'reservation holds',len(report['reservation_conflicts']),flush=True)
        report['status']='WHOLE_FRONT_BULKHEAD_STATIC_REJECTED' if report['case_and_material_contacts'] or report['reservation_conflicts'] or report['errors'] else 'WHOLE_FRONT_BULKHEAD_BODIES_NOMINATED_WIRES_MOTION_MOUNTS_OPEN'
        report['motion_not_run_before_failed_or_incomplete_static_wire_gate']=True
    except Exception as e:
        report['status']='PARTIAL_FRONT_BULKHEAD_GATE';report['errors'].append(repr(e))
    save();print(json.dumps({k:report[k] if k!='case_and_material_contacts' and k!='reservation_conflicts' else len(report[k]) for k in ('status','pairs','case_and_material_contacts','reservation_conflicts','errors','worker_seconds')}),flush=True)


if __name__=='__main__':main()
