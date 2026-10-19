"""Canonical read-only planning scene, ordered overlays and current port pose.

Not a selected assembly or complete wiring. Keeps unknown/invalid suppliers
explicit; world-posed saved BReps are never placed a second time.
"""
import hashlib
import json
import zipfile
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT


def box(lo,hi):
    return Part.makeBox(*(b-a for a,b in zip(lo,hi)),A.Vector(*lo))


def load(negative_row=False,upper_rows=False):
    files={k:OUT/n for k,n in dict(scene='n01-full-material-scene.json',
        lower='n01-lower-bay-world-probe.json',common='n01-common-restraint-world-probe.json',
        extra='n01-remaining-selected-inventory.json',packet='n01-current-endpoint-packet-r3.json',
        ports='n01-twenty-wago-port-contract.json').items()}
    data={k:json.loads(f.read_text()) for k,f in files.items()};scene={};meta={};templates={}
    pins={f.relative_to(ROOT).as_posix():sha(f) for f in files.values()}
    retired={'StructureReserve:NineWire'+k+c for k in ('Cuff','Arm') for c in ('FL','FR','RL','RR')}
    for key in ('scene','lower','common','extra'):
        p=data[key];bundle=ROOT/p['bundle'];assert sha(bundle)==p['bundle_sha256']
        pins[bundle.relative_to(ROOT).as_posix()]=p['bundle_sha256']
        with zipfile.ZipFile(bundle) as z:
            for r in p['parts']:
                n=r['name']
                if r.get('role')=='CurrentCassette' or n in retired:continue
                raw=z.read(r['entry']);assert hashlib.sha256(raw).hexdigest()==r['sha256'],n
                s=Part.Shape();s.importBrepFromString(raw.decode('utf-8'))
                if key=='extra' and not r['placed_current']:
                    templates[r['role']]=(n,s,r);continue
                scene[n]=s;meta[n]=r
    pose=data['packet']['changed_scene_groups']['POST_F0'];m=A.Matrix()
    for i in range(3):
        for j in range(3):setattr(m,f'A{i+1}{j+1}',pose['relative_rotation_rows'][i][j])
    c=A.Vector(*pose['centre_mm']);rot=A.Rotation(m);tf=A.Placement(c-rot.multVec(c),rot)
    for n,s in scene.items():
        if meta[n].get('role')=='POST_F0':s.Placement=tf*s.Placement
    scene['NominalPiUSBCPowerMould']=box(*data['packet']['nominal_Pi_USB_C_mould']['bounds_mm'])
    meta['NominalPiUSBCPowerMould']=dict(role='Pi4',kind='project_mating_reservation')
    changes=[]
    if negative_row or upper_rows:
        for st in data['ports']['stations']:
            ref=st['ref']
            negative=ref in ('G_TAIL','G_AUX','P_AUX','G2','FL_P')
            positive=ref in ('D_FL','FL_G','FR_P','D_FR','FR_G')
            if not negative and not (upper_rows and positive):continue
            matches=[n for n,r in meta.items() if r.get('role')==st['current_group']]
            assert len(matches)==1,(ref,matches)
            n=matches[0];s=scene[n];centre=s.BoundBox.Center
            flip=ref in ('G_TAIL','G_AUX','P_AUX');rot=A.Rotation(A.Vector(0,0,1),180 if flip else 0)
            tf=A.Placement(centre+A.Vector(5 if upper_rows else 0,0,6.1)-rot.multVec(centre),rot)
            s.Placement=tf*s.Placement
            for p in st['occupied_ports']:
                p['point_mm']=list(tf.multVec(A.Vector(*p['point_mm'])))
                p['departure_axis']=list(rot.multVec(A.Vector(*p['departure_axis'])))
                assert abs(p['point_mm'][2]-46.1)<2e-5
                assert p['departure_axis'][1]*(1 if negative else -1)>.99
            changes.append(dict(ref=ref,name=n,flip_Z180=flip,mouth_Z_mm=46.1,
                occupied_ports=len(st['occupied_ports']),relative_placement=str(tf)))
        assert len(changes)==(10 if upper_rows else 5)
        if not upper_rows:assert sum(r['occupied_ports'] for r in changes)==22
    return scene,meta,templates,data,pins,changes


def record_active_datums():
    """Read current planning datums, NOT a new pose search or fit approval.

    Board faces and mounting axes come from source BRep. Connector boxes keep
    their original provenance; no reservation is promoted to supplier material.
    The orthographic overview shows ENVELOPES, not collision witnesses.
    """
    import time
    from html import escape
    from pathlib import Path
    from feline_common_space_context import current
    from compose_feline_current_end_register import pipe_mouth
    tick=time.monotonic()
    world,parts,meta,pins,docs=current()
    files={key:OUT/name for key,name in dict(
        ports='n01-pi-full-port-contract.json',
        bus='n01-bus-both-plugs-plan-r3.json',
        cable='n01-physical-cable-contract.json').items()}
    contracts={k:json.loads(p.read_text()) for k,p in files.items()}
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (*files.values(),Path(__file__))})
    def bounds(s):
        b=s.BoundBox
        return [[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]]
    def board(name,provenance):
        s=parts[name];assert s.isValid() and len(s.Solids)==1
        planes=sorted((f for f in s.Faces if type(f.Surface).__name__=='Plane'),key=lambda f:-f.Area)
        faces=[dict(area_mm2=f.Area,centre_mm=list(f.CenterOfMass),normal=list(f.normalAt(0,0))) for f in planes[:2]]
        holes=[]
        for f in s.Faces:
            if type(f.Surface).__name__!='Cylinder':continue
            c=f.Surface
            holes.append(dict(radius_mm=c.Radius,axis=list(c.Axis),point_on_axis_mm=list(c.Center)))
        return dict(name=name,provenance=provenance,bounds_mm=bounds(s),large_plane_faces=faces,
                    cylindrical_surfaces=holes,group_centre_is_not_PCB_datum=True)
    boards=[board('Ref_Material_Pi4NominalPCB_0_0','Retained nominal Pi PCB model, not supplier populated STEP'),
            board('Ref_Material_BUSsupplier0_0_0','Saved supplier CAD laminate in current BUS-r3 frame; revision fit gate retained')]
    port_basis={r['role']:r for r in contracts['ports']['parts']+contracts['ports']['additional_reservations']}
    records=[]
    for n,s in parts.items():
        if meta[n].get('group')!='PiUpper' and meta[n].get('role')!='BUS' and not n.startswith('CurrentBUS:'):continue
        basis=port_basis.get(n.removeprefix('PiBudget:')) if n.startswith('PiBudget:') else None
        records.append(dict(name=n,bounds_mm=bounds(s),kind=meta[n].get('kind'),
            provenance=basis['kind'] if basis else 'Project data-plug mould budget; not supplier geometry' if n=='PiBudget:USB_A_data_boot' else 'Saved scene source; see pinned source metadata',
            source_metadata={k:meta[n][k] for k in ('entry','sha256','origin','group','role') if k in meta[n]},
            source_contract_role=basis['role'] if basis else None,
            exact_queries_require_original_inverse_frame=n==world.bus['name']))
    mouths=[]
    for n,anchor in [(n,'PiBudget:GPIO1992OccupiedHousing') for n in parts if n.startswith('PiGPIO:') and not n.endswith(':grip')]+[(n,'PiBudget:RetainedK1474Boot') for n in ('PiPower:W079','PiPower:W080')]:
        mouths.append(dict(name=n,**pipe_mouth(parts[n],parts[anchor]),
            provenance='Saved project jacket cap, NOT manufacturer electrical pin'))
    for r in contracts['bus']['routes']:
        if r['wire'] not in ('BUS.D','BUS.G'):continue
        arc=r['parts'][0]
        edge=Part.Arc(*(A.Vector(*arc[k]) for k in ('start','mid','end'))).toShape()
        mouths.append(dict(name=r['wire'],point_mm=r['parts'][0]['start'],
            departure_axis=list(edge.tangentAt(edge.FirstParameter)),
            provenance='Retained BUS-r3 project jacket datum; mating/pinout not upgraded'))
    cable=contracts['cable']['usb']
    for key in ('pi_jacket_mouth_mm','bus_jacket_mouth_mm'):
        if key in cable:mouths.append(dict(name='USB:'+key,point_mm=cable[key],
            departure_axis=[-1,0,0] if key.startswith('pi_') else cable['bus_jacket_departure_axis'],
            provenance='Retained project mould-to-jacket boundary, not measured supplier datum'))
    assert len(mouths)==11 and len({tuple(r['point_mm']) for r in mouths})==11
    # Whole-space context is an overview of the EXISTING retained candidate,
    # not the rejected coupled trial and not a newly selected assembly.
    groups={}
    for n,s in parts.items():
        r=meta[n];g=r.get('group') or r.get('role') or n.split(':')[0]
        if g in ('',None):g='Other'
        bb=bounds(s)
        if g not in groups:groups[g]=[bb[0][:],bb[1][:],0]
        v=groups[g];v[0]=[min(a,b) for a,b in zip(v[0],bb[0])];v[1]=[max(a,b) for a,b in zip(v[1],bb[1])];v[2]+=1
    result=dict(status='ACTUAL_BOARD_DATUMS_AND_TYPED_BUDGETS_RECORDED_NOT_LAYOUT_SELECTION',
        current_frame='Retained current() planning scene; rejected two-level trial NOT adopted',
        boards=boards,Pi_BUS_parts=records,occupied_jacket_mouths=mouths,
        whole_scene_group_envelopes=groups,source_sha256=pins,
        USB_project_contract=cable,port_insertion_service_budget_mm=15,
        shared_portions=docs['ends']['physical_portions'],shared_ends=docs['ends']['ends'],
        actual_material_collision_not_inferred_from_boxes=True,
        selected=False,N01_complete=False,physical_pass=False,
        acceptance_open=['One whole feasible layout including full USB500/R30 and all seven Pi flexible ends',
                         'Shared capacity for all123/246, full grips/roots/tools/motion/contour',
                         'Moved interface exact verification; reuse unchanged receipts'],
        worker_seconds=round(time.monotonic()-tick,3))
    add_datum_constraints(result)
    dest=OUT/'n01-active-Pi-BUS-datums.json'
    if dest.exists():
        prior=json.loads(dest.read_text())
        result['previous_metadata_receipt']=dict(sha256=sha(dest),worker_seconds=prior['worker_seconds'],
            reason='Remove duplicate BUS USB mouth and include all departure axes; no geometric candidate changed')
    dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    # Dimensioned whole orthographic ENVELOPE overview: intentionally no false
    # detailed section or render claiming that these boxes are physical solids.
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1360" height="1200" viewBox="0 0 1360 1200">',
         '<rect width="1360" height="1200" fill="white"/>',
         '<g font-family="sans-serif" font-size="13"><text x="30" y="25">N01 current retained candidate: dimensioned envelopes, NOT a selected layout or collision proof</text>']
    colors=['#1976b0','#b06020','#32784a','#9b458c','#9c2828','#665500']
    # Show the full torso and external head; bounds remain in shared world mm.
    labelled={'PiUpper','BUS','BankLeft6Oprawek12Koncow','BankRight6Oprawek12Koncow','S0','S1','MAINUpper','PWM9685Shelf'}
    for view,(axis,base_y,title) in enumerate([(1,280,'TOP X/Y'),(2,970,'SIDE X/Z')]):
        svg.append(f'<text x="30" y="{base_y-(200 if view==0 else 530)}">{title}; world millimetres; dashed = group envelope</text>')
        for i,(g,v) in enumerate(sorted(groups.items())):
            lo,hi,count=v;x=30+(lo[0]+300)*2;y=base_y-hi[axis]*2;w=(hi[0]-lo[0])*2;h=(hi[axis]-lo[axis])*2
            if w<=0 or h<=0:continue
            color=colors[i%len(colors)] if g in labelled else '#aaa'
            svg.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="none" stroke="{color}" stroke-width="0.6" stroke-dasharray="3 3"><title>{escape(g)} ({count}): {escape(str(lo))} to {escape(str(hi))}</title></rect>')
            if g in labelled:svg.append(f'<text x="{x:.2f}" y="{y-3:.2f}" fill="{color}" font-size="10">{escape(g)}</text>')
        for b in boards:
            lo,hi=b['bounds_mm'];x=30+(lo[0]+300)*2;y=base_y-hi[axis]*2
            svg.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{(hi[0]-lo[0])*2:.2f}" height="{(hi[axis]-lo[axis])*2:.2f}" fill="none" stroke="#000" stroke-width="2"/>')
        for x in (-128,0,112,183.5):
            px=30+(x+300)*2
            svg.append(f'<path d="M{px},{base_y-175} V{base_y+115}" stroke="#ddd"/><text x="{px}" y="{base_y+132}">X{x:g}</text>')
    svg.extend(['<text x="30" y="1140">Black = actual nominal PCB envelopes. USB R30 / OD5 / free jacket452 are PROJECT assumptions;500 total is catalog.</text>',
                '<text x="30" y="1165">Full exact datums, board-face normals, holes, connector provenance and source hashes: n01-active-Pi-BUS-datums.json</text></g></svg>'])
    dest.with_suffix('.svg').write_text('\n'.join(svg),encoding='utf-8')
    print(json.dumps(dict(status=result['status'],seconds=result['worker_seconds'],boards=boards,
        part_records=len(records),jacket_mouths=len(mouths),groups=len(groups),N01_complete=False)),flush=True)


def add_datum_constraints(result):
    """Necessary LOCAL layer bounds, never a claim of globally free volume."""
    g=result['whole_scene_group_envelopes'];u=result['USB_project_contract']
    bank_top=max(g[n][1][2] for n in ('BankLeft6Oprawek12Koncow','BankRight6Oprawek12Koncow'))
    upper=('D_RR','FR_P','RR_P','RR_G','P_REAR','G_AUX')
    upper_floor=min(g[n][0][2] for n in upper)
    radius=u['project_OD_mm']/2;rigid_gap=1.25
    centre=[bank_top+radius+rigid_gap,upper_floor-radius-rigid_gap]
    file=OUT/'n01-fore-coil-service-deck-received.json';pose=json.loads(file.read_text())['Pi_pose']
    dz=pose['USB_mouth_mm'][2]-pose['target_PCB_centre_mm'][2]
    result['necessary_local_layer_constraints']=dict(
        bank_top_mm=bank_top,upper_station_floor_mm=upper_floor,upper_station_refs=list(upper),
        jacket_radius_mm=radius,rigid_gap_mm=rigid_gap,USB_axis_Z_interval_mm=centre,
        inverted_Pi_USB_mouth_minus_PCB_Z_mm=dz,
        necessary_inverted_Pi_PCB_Z_interval_mm=[z-dz for z in centre],
        source_inverted_pose_sha256=sha(file),
        scope='Only overlaps of these bank and upper-station footprints in the RETAINED candidate',
        NOT_globally_free_volume=True,
        unresolved_exclusions=['S0/key','MAIN whole stack','PWM shelf/root','Pi complete components and occupied connectors','BUS full components/boots/supports','Other wires/roots/motion/true curved skin'],
        lower_fore_station_variant_not_adopted_here=True,
        no_new_pose_chosen=True)


if __name__=='__main__':
    record_active_datums()
