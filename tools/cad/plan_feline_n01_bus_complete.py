"""One nominal BUS plan including BOTH D/G and straight USB-C mating space.

Vendor board geometry stays exact. Plug/OD/bend/clip budgets are explicitly
provisional, not supplier dimensions. One read-only actual-material screen;
no detailed native build, purchasing, electrical or physical PASS.
"""
import json
import time
import sys
from pathlib import Path
import FreeCAD as A
import Part
import numpy as np
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import OUT,BASE,MODEL,STAGES
from plan_feline_n01_shared import pipe
from plan_feline_factory_links import routes
from check_feline_shared_space import tube_prefix
from check_feline_leg_body import placement
from plan_feline_n01_coupled_pi_bus import Route

def pose(R,t):
    m=A.Matrix()
    for i in range(3):
        for j in range(3):setattr(m,f'A{i+1}{j+1}',R[i][j])
    return A.Placement(A.Vector(*t),A.Rotation(m))

def bb(s):
    b=s.BoundBox;return [[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]]

def main():
    tick=time.monotonic();reader=SavedShapes();dogleg='--outside-cable-arm' in sys.argv
    rooted=dogleg or '--rooted-branches' in sys.argv
    dest=OUT/('n01-bus-both-plugs-plan-r3.json' if dogleg else 'n01-bus-both-plugs-plan-r2.json' if rooted else 'n01-bus-both-plugs-plan.json')
    assert not dest.exists(),'Receive previous result; no unchanged rerun'
    files=[OUT/n for n in ('n01-module-plan-r5.json','n01-shared-preflight-r5.json','n01-compact-bank-plan-r2.json',
        'n01-common-backbone-preflight-r4.json','motion-layout.json','current-mount-axis-inventory.json')]
    gplan,rear,bank,backbone,motion,axis_inventory=[json.loads(p.read_text()) for p in files]
    binding_path=BASE/'body-harness-checkpoint/BUS-port-binding.json';binding=json.loads(binding_path.read_text())
    catpath=ROOT/'hardware/electronics/full-cat/pi-bus-primary-r1/catalog.json';catalog=json.loads(catpath.read_text())
    native=OUT/'FelineInteriorMotion.FCStd';assert sha(native)==bank['source_native_sha256']
    R=np.array([[0,0,-1],[-1,0,0],[0,1,0]],float)
    old=np.mean(next(g['candidate_bounds_mm'] for g in gplan['groups'] if g['role']=='BUS'),axis=0)
    centre=np.array([126,0,75]);trans=centre-R@old;T=pose(R,trans)
    report=dict(status='RUNNING',selected=False,N01_complete=False,physical_pass=False,native_changed=False,
        relative_BUS_pose=dict(rotation_rows=R.tolist(),translation_mm=trans.tolist(),centre_mm=centre.tolist()),
        contacts=[],reservation_overlaps=[],errors=[],pairs=0,poses=[],outside=[],
        routes=[],roots=[],source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in files+[binding_path,catpath,Path(__file__)]},
        scope='Complete purchased BUS pose, nominal H5D/G mating and both prefixes/shared relief, nominal straight USB-C plug and cable R30/afterbend9mm, actual4holes, rooted support reservations. Not whole80nets or physical mating proof.',
        provisional={'H5_exit_above_header_mm':14.05,'H5_mating_box_mm':[9,12.9,15.05],
            'USB_C_overmould_mm':[12,22,8],'USB_cable_OD_mm':5,'USB_static_R_mm':30,
            'all_are_project_reserves_not_manufacturer_dimensions':True},
        USB_selected='LanbergCA-USBO-10CU-0005-BK0.5m straightUSB-A/C, no angle adapter/no changed cable',
        USB_Pi_A_plug_full_middle_and_remaining_length_open=True)
    def save():
        report.update(worker_seconds=round(time.monotonic()-tick,3),updated_utc=__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat())
        dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    def gate():
        if time.monotonic()-tick>240:
            report['status']='TIME_BOUNDED_PARTIAL';save();raise TimeoutError('240s cap')
    scene={};roles={};bus={};fixedbounds={};valid={}
    def check(an,a,bn,b,scope,reservation=False):
        gate()
        if an not in fixedbounds:fixedbounds[an]=a.BoundBox
        if bn not in fixedbounds:fixedbounds[bn]=b.BoundBox
        if not fixedbounds[an].intersect(fixedbounds[bn]):return
        report['pairs']+=1
        try:
            for n,s in ((an,a),(bn,b)):
                if n not in valid:valid[n]=s.isValid() and bool(s.Solids)
                assert valid[n],n+' invalid material'
            c=a.common(b);assert c.isNull() or c.isValid()
            if c.Volume>1e-5:report['reservation_overlaps' if reservation else 'contacts'].append(
                dict(a=an,b=bn,scope=scope,volume_mm3=c.Volume,witness_bounds_mm=bb(c)))
        except Exception as exc:report['errors'].append(dict(a=an,b=bn,scope=scope,error=str(exc)))
    cd={'JPWM':[-90,44,30],'W041_Joint':[0,15,3],'W042_Joint':[0,-15,3]}
    effective=json.loads(json.dumps(gplan))
    for g in effective['groups']:
        if g['role'] in cd:g['translation_mm']=(np.array(g['translation_mm'])+cd[g['role']]).tolist()
    for g in gplan['groups']:
        role=g['role']
        for n in g['objects']:
            gate();s=reader.shape(native,n)
            if role in rear['changed_complete_receiving_groups']:
                rr=rear['relative_rotations'].get(role,np.eye(3).tolist())
                s.Placement=pose(rr,rear['changed_complete_receiving_groups'][role])*s.Placement
            if role in cd:s.translate(A.Vector(*cd[role]))
            if role=='BUS':s.Placement=T*s.Placement;bus[n]=s
            scene[n]=s;roles[n]=role
    for key,p in bank['relative_holder_poses'].items():
        P=pose(p['rotation_rows'],p['translation_mm'])
        for kind in ('Housing','IN','OUT','ATO'):
            n=f'Ref_Material_F_{key}_CP2_{kind}_0_0';scene[n].Placement=P*scene[n].Placement
    stages={n for g in motion['membership'].values() for ns in g.values() for n in ns}
    for row in motion['inventory']:
        n=row['object']
        if n not in scene and row['kind']=='surface' and (n in stages or n.startswith(('Print_P0_','Ref_Material_P0_','Battery','Print_CP2_TailRiser'))):
            if not n.startswith('BatteryFrameHardware'):scene[n]=reader.shape(native,n)
    for i in range(1,5):scene[f'BellyFoot{i}']=reader.shape(native,f'BellyFoot{i}')
    fixedwires={}
    for row in backbone['bend_allocations']:
        p=np.array(row['start_mm']);q=np.array(row['end_mm']);b=np.array(row['bend']);r=row['bend_R_mm'];l=row['land_mm']
        fixedwires[row['id']]=tube_prefix(p,(q-p-r*b)/(l+r),row['radius_mm'],b,r,l)
    for row in routes(effective):fixedwires['Factory:'+row['wire']]=pipe(row['parts'],row['radius_mm'])
    for row in backbone['allocations']:
        if row['owner'].startswith('NineWireCuff'):
            fixedwires[row['id']]=Part.makeCylinder(1.55,9,A.Vector(*row['point_mm']),A.Vector(*row['bodyward_axis']))
    wires={};reserves={};roots={}
    def box(n,lo,hi,root=False):
        s=Part.makeBox(*(np.array(hi)-lo),A.Vector(*lo))
        (roots if root else reserves)[n]=s
        if root:report['roots'].append(dict(name=n,low_mm=lo,high_mm=hi))
        return s
    endpoints=[]
    for row in binding['ports']['H5']['pin_columns']:
        if row['role']=='V':continue
        h=T.multVec(A.Vector(*row['world_header_top_reference_mm'])+A.Vector(0,0,42))
        e=h+T.Rotation.multVec(A.Vector(0,0,14.05))
        path=Route([e.x,e.y,e.z],[-1,0,0]).turn([0,-1,0],10).line(9).record('BUS.'+row['role'],1.55)
        wires[path['wire']]=pipe(path['parts'],path['radius_mm']);report['routes'].append(path)
        endpoints.append(dict(role=row['role'],header_reference=[h.x,h.y,h.z],nominal_exit=[e.x,e.y,e.z]))
    report['H5']=dict(ports=endpoints,V_contact_removed=True,actual_mating_fit_open=True)
    d,g=endpoints;de=np.array(d['nominal_exit']);ge=np.array(g['nominal_exit'])
    # One2lane relief; electrodes are not joined. Both full9mm lands retained.
    bx=de[0]-10;by=de[1]-10;bz=(de[2]+ge[2])/2
    box('DGSharedRelief',[bx-3.95,by-9,de[2]-3.95],[bx+3.95,by,ge[2]+3.95])
    box('H5MatingReserve',[d['header_reference'][0]-14.05,de[1]-6.45,de[2]-3.95],
        [d['header_reference'][0]+1,de[1]+6.45,ge[2]+3.95])
    # Actual vendor USB-C metal socket defines its OUTER mating face, not a
    # guessed centre of the entire PCB. World basis explicitly composed once.
    c=next(p for p in catalog['parts'] if p['name']=='Type_C1');lo,hi=np.array(c['bounds'][:3]),np.array(c['bounds'][3:])
    raw=[(lo[0]+hi[0])/2,lo[1],(lo[2]+hi[2])/2]
    original=pose([[0,-1,0],[1,0,0],[0,0,1]],binding['placement_translation_mm'])
    mouth=T.multVec(original.multVec(A.Vector(*raw))+A.Vector(0,0,42))
    u=np.array([mouth.x,mouth.y,mouth.z]);report['USB_C_mating_face_mm']=u.tolist()
    box('USB_C_Overmould',[u[0]-6,u[1]-22,u[2]-4],[u[0]+6,u[1],u[2]+4])
    r=Route((u+[0,-22,0]).tolist(),[0,-1,0]).line(3).turn([0,0,-1],30).line(9).record('USB_CableFirst',2.5)
    report['routes'].append(r);wires['USB_CableFirst']=pipe(r['parts'],r['radius_mm'])
    p=np.array(r['end_mm']);box('USB_AfterBendRelief',[p[0]-4.9,p[1]-4.9,p[2]],[p[0]+4.9,p[1]+4.9,p[2]+9])
    # Actual4 PCB holes, normal now-X. Carrier roots go to existing common
    # rear-post proposal; positive union is checked, not claimed as strength.
    ax=next(r for r in axis_inventory['groups'] if r['role']=='BUS')['unique_axes']
    holepts=[]
    for row in ax:
        x,y=row['axis_world_xy_mm'];v=T.multVec(A.Vector(x,y,90.72));holepts.append(v)
    pcbback=float(np.mean([v.x for v in holepts]));ys=[v.y for v in holepts];zs=[v.z for v in holepts]
    plate=box('BUS_Backplate',[pcbback+2,min(ys)-3,min(zs)-(6 if rooted else 3)],
        [pcbback+5,max(ys)+3,max(zs)+3],True)
    for i,v in enumerate(holepts):
        plate=plate.cut(Part.makeCylinder(1.2,5,A.Vector(pcbback+1,v.y,v.z),A.Vector(1,0,0)))
        roots['BUS_Standoff'+str(i)]=Part.makeCylinder(3,2,v,A.Vector(1,0,0)).cut(Part.makeCylinder(1.2,2,v,A.Vector(1,0,0)))
    roots['BUS_Backplate']=plate
    if rooted:
        box('BUS_FrameCrossbar',[101,-23,49],[107,23,52],True)
        box('BUS_CentralLowerRoot',[104,-4,49],[pcbback+5,4,52],True)
        box('BUS_UpperPositiveRoot',[102,21,79],[pcbback+5,27,82],True)
        box('BUS_BackplatePositiveEar',[pcbback+2,14,79],[pcbback+5,27,82],True)
    else:
        for y in (-18.5,18.5):box('BUS_LowerRoot'+str(y),[102,y-3,52],[pcbback+5,y+3,55],True)
        box('BUS_UpperPositiveRoot',[102,17,79],[pcbback+5,23,82],True)
    box('DG_LowerRoot',[102,-3,52],[108,23,55],True)
    box('DG_Upstand',[bx+3.65,by-8.5,54],[bx+9.65,by-3.25,bz],True)
    # USB relief support remains below the whole wire end, no filled box
    # crossing the cable. Common frame-root reservations stay explicit.
    if rooted:
        # Short flat branch from the retained full structural9wire arm,
        # not a1.4mm wire pilot and not a long bar through the rear frame.
        start=np.array([105,-36,64]);end=np.array([p[0]+6.27,p[1],p[2]+4.5])
        def flatbeam(a,b,width):
            delta=b-a;normal=np.array([-delta[1],delta[0],0]);normal/=np.linalg.norm(normal)
            sections=[]
            for v in (a,b):
                vs=[A.Vector(*(v+normal*aa+np.array([0,0,bb]))) for aa,bb in
                    ((-width/2,-1.5),(width/2,-1.5),(width/2,1.5),(-width/2,1.5))]
                sections.append(Part.makePolygon(vs+[vs[0]]))
            return Part.makeLoft(sections,True,True)
        if dogleg:
            q1=np.array([135.5,-60,58]);q2=np.array([135.5,p[1],p[2]+4.5])
            end=np.array([p[0]+3.9,p[1],p[2]+4.5])
            beam=flatbeam(start,q1,6).fuse(flatbeam(q1,q2,4)).fuse(flatbeam(q2,end,4))
            for q,w in ((q1,6),(q2,4)):
                beam=beam.fuse(Part.makeBox(w,w,3,A.Vector(*(q-[w/2,w/2,1.5]))))
            beam=beam.removeSplitter()
            report['USB_outside_arm_path_mm']=[v.tolist() for v in (start,q1,q2,end)]
            report['USB_outside_arm_cause']='After2rooting rejections, route around the COMPLETE cable via2outer knuckles; no direct diagonal through its final tangent cylinder. USB pose/path unchanged.'
        else:beam=flatbeam(start,end,6)
        assert beam.isValid() and len(beam.Solids)==1
        roots['USB_DiagonalArm']=beam
        parent=Part.makeBox(6,30,3,A.Vector(102,-50,62.5))
        for row in backbone['allocations']:
            if row['owner']=='NineWireCuffRR':
                pv=A.Vector(*row['point_mm']);dv=A.Vector(*row['bodyward_axis'])
                parent=parent.cut(Part.makeCylinder(1.8,11,pv-dv,dv))
        # LogicalRR has negativeY in the current physical mapping; assert
        # actual frame/arm coordinates rather than inferring by its label.
        contact=beam.common(parent);assert contact.isValid() and contact.Volume>1e-4
        report['USB_root_parent']=dict(owner='NineWireArmRR',source='common-backbone-r4',
            full_parent_box_mm=[[102,-50,62.5],[108,-20,65.5]],root_contact_volume_mm3=contact.Volume,
            start_mm=start.tolist(),end_mm=end.tolist(),section_mm=[6,3],
            parent_is_still_a_scoped_planning_body_not_native_release=True)
        report['roots'].append(dict(name='USB_DiagonalArm',start_mm=start.tolist(),end_mm=end.tolist(),section_mm=[6,3]))
    else:
        box('USB_XRoot',[102,-23,35],[p[0]+11,-17,38],True)
        box('USB_FrameRiser',[102,-23,35],[108,-17,45.72],True)
        box('USB_YRoot',[p[0]+5,-74,35],[p[0]+11,-20,38],True)
        box('USB_Upstand',[p[0]+4.6,p[1]-2.5,35],[p[0]+10.6,p[1]+2.5,p[2]+5],True)
    report['PCB_axes_mm']=[[v.x,v.y,v.z] for v in holepts]
    report['hardware_candidate']='Retain4M2board stacks; exact length/nut/head placement and stock reconciliation still N03. Not a new selected SKU.'
    # roots touch common posts by positive volume, but those posts are still
    # only the previously screened backbone plan, not finished native parts.
    for sign in (-1,1):box('InheritedRearPost'+str(sign),[102,sign*20-3,42.72],[108,sign*20+3,85],True)
    report['frame_root_basis']='Inherited common-backbone-r4 rear-post -> lower rail -> four free-span frame clamps. Physical fastener/strength proof remains OPEN.'
    if rooted:
        priorpath=OUT/'n01-bus-both-plugs-plan.json';prior=json.loads(priorpath.read_text())
        assert not prior['contacts'] and not prior['errors']
        assert prior['relative_BUS_pose']==report['relative_BUS_pose'] and prior['routes']==report['routes']
        for pp,h in prior['source_sha256'].items():
            if pp!='tools/cad/plan_feline_n01_bus_complete.py':assert sha(ROOT/pp)==h,pp
        report['unchanged_received_scope']=dict(report=priorpath.relative_to(ROOT).as_posix(),sha256=sha(priorpath),
            case_and_complete_nominal_prefixes_reused=True,
            reason='Identical exact vendor source/pose and routes. All prior hits are only root reservations changed below.',
            actual_mating_still_provisional=True)
        report['source_sha256'][priorpath.relative_to(ROOT).as_posix()]=sha(priorpath)
        if dogleg:
            priorrootpath=OUT/'n01-bus-both-plugs-plan-r2.json';pr=json.loads(priorrootpath.read_text())
            assert not pr['contacts'] and not pr['errors'] and len(pr['reservation_overlaps'])==1
            hit=pr['reservation_overlaps'][0];assert hit['a']=='USB_DiagonalArm' and hit['b']=='USB_CableFirst'
            report['source_sha256'][priorrootpath.relative_to(ROOT).as_posix()]=sha(priorrootpath)
            report['unchanged_root_scope_reused']=dict(report=priorrootpath.relative_to(ROOT).as_posix(),sha256=sha(priorrootpath),
                only_changed='USB_DiagonalArm replaced by outside dogleg; all other roots, plugs and prefixes identical')
    save()
    for n,s in ({} if rooted else {**bus,**wires}).items():
        for bn,b in scene.items():
            if roles.get(bn)=='BUS':continue
            check(n,s,bn,b,'new_BUS_or_nominal_wire_vs_actual_static_material')
        for bn,b in fixedwires.items():check(n,s,bn,b,'new_BUS_or_nominal_wire_vs_bank_MTA_and36boundaries')
    for n,s in {**reserves,**roots}.items():
        if n.startswith('InheritedRearPost'):continue # unchanged scoped R4 proof
        if rooted and n in reserves:continue # received unchanged plug/relief footprints
        if dogleg and n!='USB_DiagonalArm':continue # received all other exact root checks
        for bn,b in scene.items():
            if n.startswith('BUS_Standoff') and roles.get(bn)=='BUS':continue
            if n=='H5MatingReserve' and roles.get(bn)=='BUS':continue
            check(n,s,bn,b,'proposed_root_or_plug_reservation_vs_actual_material',True)
        for bn,b in fixedwires.items():check(n,s,bn,b,'proposed_root_or_plug_reservation_vs_existing_wire',True)
        for bn,b in wires.items():
            if n=='DGSharedRelief' and bn.startswith('BUS.'):continue
            if n=='USB_AfterBendRelief' and bn=='USB_CableFirst':continue
            if n=='H5MatingReserve' and bn.startswith('BUS.'):continue
            if n=='USB_C_Overmould' and bn=='USB_CableFirst':continue
            check(n,s,bn,b,'proposed_root_vs_new_complete_prefix',True)
    report['source_sha256'].update(reader.hashes)
    report['status']='BUS_SHARED_PLAN_REJECTED' if report['contacts'] or report['reservation_overlaps'] or report['errors'] else 'BUS_STATIC_PLAN_CLEAR_MOTION_ENVELOPE_USB_MIDDLE_TOOLS_OPEN'
    save();print(json.dumps(dict(status=report['status'],pairs=report['pairs'],contacts=len(report['contacts']),reservations=len(report['reservation_overlaps']),errors=len(report['errors']),seconds=report['worker_seconds'])),flush=True)

if __name__=='__main__':main()
