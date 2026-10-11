"""One current endpoint/ownership register, without accepting old CP2 datums.

This is a useful input to the remaining shared routing, not W5 completion.
Electrical aliases change only within the SAME rail; no net is merged.
"""
import copy,hashlib,json,math,time,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype'
OUT=BASE/'body-harness-checkpoint'
SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def plan():
    pins={Path(__file__)}
    def read(p):
        pins.add(p);return json.loads(p.read_text())
    owners=read(OUT/'owner-plan.json')
    leg=read(OUT/'leg-stations-plan.json');bank=read(OUT/'bank-input-plan.json')
    main=read(OUT/'main-source-plan.json');s1=read(OUT/'s1-output-plan.json')
    source=read(OUT/'source-receiving-plan.json')
    aux=read(BASE/'aux-wiring-checkpoint/whole-layout-plan.json')
    mta=read(OUT/'mta-interface-plan.json')
    holders={h['leg']:h for h in mta['holders']}
    archive=ROOT/'hardware/simulation/v35/inputs.zip';pins.add(archive)
    with zipfile.ZipFile(archive) as z:g=json.loads(z.read('geometry.json'))
    memberships={r['name']:r['stage'] for r in g['components']}
    rows={r['id']:dict(id=r['id'],roles=[r['a'],r['b']],material=r['material'],
      current_ends=copy.deepcopy(r['historical_ends']),actual_cut_mm=None,
      route_status='OPEN_NO_CURRENT_ROUTE',native_relief_complete=False) for r in owners['body_conductors']}
    # These are current whole-plan SAME-RAIL cavity assignments, not net changes.
    for e in rows['W065']['current_ends']:
        if e['role']=='P_REAR.1':e.update(role='P_REAR.5',point_mm=[29,-13,138])
    reassign={'W043':('P_SYS.2','P_SYS.5'),'W067':('P_SYS.3','P_SYS.2'),
      'W068':('P_SYS.4','P_SYS.3'),'W044':('P_REAR.2','P_REAR.3'),
      'W052':('P_REAR.3','P_REAR.2'),
      'W060':('G1.2','G1.4'),'W036':('G1.4','G1.2')}
    for wid,(old,new) in reassign.items():
        r=rows[wid];assert old in r['roles'];r['roles']=[new if a==old else a for a in r['roles']]
        for e in r['current_ends']:
            if e['role']==old:e['role']=new
        r['same_rail_port_reassignment']=dict(old=old,new=new)
    for r in rows.values():
        for e in r['current_ends']:
            role=e['role'];e['route_restraint_and_lever_qualified']=False
            if role in leg['ports']:
                e.update(copy.deepcopy(leg['ports'][role]));e['role']=role
                e['departure']=[0,0,1]
                e['basis']='Current shared lower receiving gallery, nominal envelope-derived project port, delivered fit gate'
            elif role.startswith('P_FRONT.'):
                e['point_mm']=main['P_FRONT']['ports'][role.split('.')[1]]
                e['departure']=[-1,0,0]
            elif role.startswith('P_SYS.'):
                e['point_mm']=source['P_SYS']['ports'][role.split('.')[1]]
                e['departure']=[0,1,0]
            elif role in ('P_REAR.2','P_REAR.3'):
                e['point_mm']=[29,6.5 if role.endswith('2') else 0,138]
                e['departure']=[1,0,0]
            elif role.startswith('G2.'):
                pose=aux['G2_pose'];x,y,z=e['point_mm'];px,py,pz=pose['pivot_mm'];dx,dy,dz=pose['translation_mm']
                a=math.radians(pose['yaw_deg'])
                e['point_mm']=[px+math.cos(a)*(x-px)-math.sin(a)*(y-py)+dx,
                               py+math.sin(a)*(x-px)+math.cos(a)*(y-py)+dy,z+dz]
                e['basis']='Current selected W1 G2 rotation+translation applied once to saved project datum'
                e['departure']=[1,0,0]
            elif role.startswith('G1.'):
                e.update(point_mm=[-89+6.5*(int(role.split('.')[1])-1),-73.75,100.99],departure=[0,1,0])
            elif role=='F_PI.in':e.update(point_mm=source['F_PI']['input_mm'],departure=[0,0,1])
            elif role=='F_PI.out':e.update(point_mm=source['F_PI']['output_mm'],departure=[0,0,-1])
            elif role=='SPLICE_PI.16':e.update(point_mm=source['F_PI']['output_factory_tip_mm'],departure=[1,0,0])
            elif role=='SPLICE_PI.18':e.update(point_mm=source['F_PI']['output_custom_tip_mm'],departure=[1,0,0])
            elif role.startswith('F_') and role.split('.')[0][2:] in holders:
                h=holders[role.split('.')[0][2:]];side='input' if role.endswith('.in') else 'output'
                e['point_mm']=h[side+'_mm'];e['basis']='Current four-holder BOTH-side nominal casing exit; full factory/custom joint recorded separately'
            if 'point_mm' in e:e['status']='CURRENT_PROJECT_DATUM_FIT_GATE_NOT_ROUTE'
    qualified={}
    for tag,p,keys in [('main-source',main,['routes']),('s1-output',s1,['routes']),
        ('source-receiving',source,['routes','factory_routes']),('leg-stations',leg,['routes']),
        ('bank-input',bank,['routes'])]:
        for key in keys:
            for name,r in p[key].items():
                if name=='W077_PREFIX':continue
                wid=name.split('_')[0];assert wid not in qualified,wid
                qualified[wid]=dict(plan=tag+'-plan.json',route=name,
                  guide_mm=sum(s['length_mm'] for s in r['parts']),
                  guide_endpoints_mm=[r['parts'][0]['start'],r['parts'][-1]['end']])
                rows[wid].update(route_status='SCOPED_NOMINAL_GUIDE_QUALIFIED_NATIVE_OPEN',guide=qualified[wid])
    for wid,r in rows.items():
        if wid not in qualified:continue
        # Bind full electrical endpoints separately from the inline custom
        # segment mouths. Eight factory+custom lengths must not be conflated.
        guide=qualified[wid];r['factory_segment']=None
        if guide['route'].endswith('_CUSTOM'):
            factory=leg['factory_override'] if wid=='W026' else mta['factory_routes'][wid+'_FACTORY']
            r['factory_segment']=dict(plan='leg-stations-plan.json' if wid=='W026' else 'mta-interface-plan.json',
              route='factory_override' if wid=='W026' else wid+'_FACTORY',
              guide_mm=sum(p['length_mm'] for p in factory['parts']),
              boundary_points_mm=[factory['parts'][0]['start'],factory['parts'][-1]['end']])
        else:
            points=guide['guide_endpoints_mm']
            for e in r['current_ends']:
                e['point_mm']=min(points,key=lambda p:math.dist(p,e['point_mm']))
    looms=[]
    for loom in owners['leg_looms']:
        r=copy.deepcopy(loom);stage=memberships[r['pcb']]
        assert memberships[r['housing']]==stage
        _,code,moving_stage=stage.split('_');assert code==r['cad_code']
        r.update(moving_saved_stage=stage,
          crossed_axes=['Rev_'+code+'_'+s for s in ('Hip','Knee','Ankle')[:('Hip','Knee','Ankle').index(moving_stage)+1]],
          nominal_usable_factory_mm=None,physical_pin_cavity_order=None,
          project_connector_choice=0,route_status='OPEN_COUPLED_MOVING_LOOM',
          cable_OD_mm=None,copper_area_mm2=None,dynamic_min_radius_mm=None)
        # Inverted hip housing follows Hip; knee AND ankle housings follow Knee.
        # Never infer ownership from the servo's electrical stage name.
        for role,e in r['electrical'].items():
            wid=e['wire'];row=rows[wid];row['route_status']='OPEN_FACTORY_LOOM_'+r['loom']
            row['loom']=r['loom'];row['shared_factory_SKU']='SR-Cable-5264-3PIN-900mm-6PCS'
            row['electrical_cavity_order_known']=False
        looms.append(r)
    open_ids=[n for n,r in rows.items() if r['route_status']=='OPEN_NO_CURRENT_ROUTE']
    assert len(rows)==80 and len(qualified)==25 and len(looms)==12 and len(open_ids)==19
    ports={}
    for wid,r in rows.items():
        for e in r['current_ends']:
            assert e['role'] in r['roles'],(wid,e['role'],r['roles'])
            role=e['role']
            if role.startswith(('P_','G1.','G2.','D_','FL_G.','FR_G.','RL_G.','RR_G.','FL_P.','FR_P.','RL_P.','RR_P.')):
                assert role not in ports,(role,ports.get(role),wid)
                ports[role]=wid
    return dict(status='CURRENT_FULL_HARNESS_DATUM_REGISTER_NOT_W5',selected=False,W5_complete=False,physical_pass=False,
      body_conductors=list(rows.values()),body_count=80,body_end_count=160,
      qualified_nominal_guides=25,open_body_guides=open_ids,looms=looms,
      local_boundary_owners=owners['internal_boundary_owners'],occupied_body_ports=ports,
      source_scope=owners['legacy_source_scope'],
      topology='One current role register:25nominal guides,19remaining body guides,12moving factory looms/36cores,18local boundary owners. Same-rail remaps explicit; no partial W5 credit.',
      delivery_gates=['BUS actual keyed connector and D/G cavity binding, no bbox-centre pin',
        'Factory servo cable OD/area/length/dynamic bend and keyed cavity order',
        'Project motion allowance is not calibrated operating range',
        'All changed native grips/retention/installed service and global stock remain OPEN'],
      source_sha256={p.relative_to(ROOT).as_posix():SHA(p) for p in pins})

if __name__=='__main__':
    tick=time.monotonic();p=plan();p['planning_seconds']=time.monotonic()-tick
    (OUT/'harness-interfaces-plan.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:p[k] for k in ('body_count','body_end_count','qualified_nominal_guides','open_body_guides','planning_seconds')}))
