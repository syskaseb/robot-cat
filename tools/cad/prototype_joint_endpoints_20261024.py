"""One shared endpoint/assembly trial after LAYOUT24-C; not whole N01."""
import json,math,time,zipfile
from pathlib import Path
import FreeCAD as A
import Part
import prototype_layout_review_20261024 as base
from check_main_p0_placement import sha


def caps(shape):
    rows=[]
    for f in shape.Faces:
        if (type(f.Surface).__name__=='Plane' and len(f.Edges)==1 and
                type(f.Edges[0].Curve).__name__=='Circle'):
            rows.append(dict(point_mm=list(f.Edges[0].Curve.Center),
                radius_mm=f.Edges[0].Curve.Radius,outward=list(f.normalAt(0,0))))
    assert len(rows)==2, 'Receive actual two pipe caps; do not substitute a box'
    return rows


def free_station(scene,group,role):
    name=f'Station:{group}:wire:{group}.{role}'
    centre=scene[f'Station:{group}:case'].BoundBox.Center
    row=max(caps(scene[name]),key=lambda r:(A.Vector(*r['point_mm'])-centre).Length)
    return dict(row,actor=name,datum='received pipe free cap; capacity radius may exceed selected wire')


def local_groups(scene):
    groups={}
    for group,delta in [('D_RR',(0,24,0)),('G_AUX',(0,0,-20))]:
        for n,s in scene.items():
            if n.startswith('Station:'+group+':'):
                clone=s.copy();clone.translate(A.Vector(*delta));groups[n]=clone
    assert len(groups)==18
    return groups


def fore_groups(scene):
    """Changed architecture: ground block beside PWM/MAIN, not above fuses."""
    groups=local_groups(scene)
    old=scene['Station:G_AUX:case'].BoundBox.Center
    target=A.Vector(-85,-78,98)
    for n,s in scene.items():
        if n.startswith('Station:G_AUX:'):
            clone=s.copy();clone.rotate(old,A.Vector(0,0,1),-90)
            clone.translate(target-old);groups[n]=clone
    return groups


def open_upper_carrier(original):
    return original.copy().cut(Part.makeBox(25.3,16.5,6,A.Vector(3,-35.5,90)))


def early_groups(scene,out):
    """Keep reviewed cases; remove template lane/free-tip, keep full9 grooves."""
    profiles=json.loads((out/'n01-selected-piece-profile-contract.json').read_text())['portions']
    logical=json.loads((out/'n01-shared-end-plan.json').read_text())['endpoints']
    mapping={r['endpoint']:(r['wire'],r['portion_id']) for r in logical
             if r['endpoint'].startswith(('D_RR.','G_AUX.'))}
    result={};recipes={}
    def box(lo,hi):return Part.makeBox(*(hi[i]-lo[i] for i in range(3)),A.Vector(*lo))
    for group in ('D_RR','G_AUX'):
        case=scene[f'Station:{group}:case'].copy();case.translate(A.Vector(0,24,0))
        result[f'Station:{group}:case']=case;xs=[];rs=[]
        for role in range(1,6):
            tag=f'{group}.{role}';wire,portion=mapping[tag]
            old=free_station(scene,group,role)
            # Mouth lies on received case +Y face, not old pipe's artificial tip.
            x=old['point_mm'][0];y=case.BoundBox.YMax;z=98.;r=profiles[portion]['project_radius_mm']
            result[f'Station:{group}:wire:{tag}']=Part.makeCylinder(r,9.25,A.Vector(x,y,z),A.Vector(0,1,0))
            xs.append(x);rs.append(r)
        lo=min(x-r-2 for x,r in zip(xs,rs));hi=max(x+r+2 for x,r in zip(xs,rs));back=98-max(rs)-2
        a=case.BoundBox.YMax+.25;b=a+9
        pad=box((lo,a,back),(hi,b,98))
        for x,r in zip(xs,rs):pad=pad.cut(Part.makeCylinder(r+.15,11,A.Vector(x,a-1,98),A.Vector(0,1,0)))
        top=98+max(rs)+.15
        band=box((lo-1.2,a+3.25,back-1.2),(hi+1.2,a+5.75,top+1.2))
        band=band.cut(box((lo,a+3.15,back),(hi,a+5.85,top)))
        head=box((hi+1.2,a+2,95.35),(hi+5.5,a+7,100.65))
        if group=='D_RR':head.rotate(A.Vector((lo+hi)/2,0,98),A.Vector(0,1,0),180)
        for label,s in [('split_common_comb',pad),('band_budget',band),('head_budget',head)]:
            s.check(True);assert len(s.Solids)==1
            result[f'Station:{group}:{label}']=s
        recipes[group]=dict(grip_Y_mm=[a,b],grip_length_mm=9,open_top=True,
            grooves_not_rotated=True,head_side='outward-left proper180Y' if group=='D_RR' else 'outward-right',
            flexible_band_thread_direction_reversed_not_rigid_mirror=group=='D_RR',
            loop_centreline_conservative_mm=2*(hi-lo+top-back+2.4),
            head_take_up_allowance_mm=7,bench_pull_tail_allowance_mm=20,
            required_total_mm=2*(hi-lo+top-back+2.4)+27,selected_tie_nominal_mm=100,
            individual_pull_fit_and_tightening_phase2_OPEN=True)
        assert recipes[group]['required_total_mm']<100
    return result,recipes


def early_carrier(original):
    # Common open exit after both9mm lands; neither case seat is cut.
    body=original.copy().cut(Part.makeBox(57,20.5,6,A.Vector(3,-35.5,90)))
    body.check(True);assert len(body.Solids)==1
    return body


def west_exit_groups(scene,out):
    groups,clamps=early_groups(scene,out);pivot=A.Vector(15.625,-55,98)
    # Head goes to the exterior +Y side after the proper quarter-turn.
    groups['Station:D_RR:head_budget'].rotate(pivot,A.Vector(0,1,0),180)
    for n,s in groups.items():
        if n.startswith('Station:D_RR:'):s.rotate(pivot,A.Vector(0,0,1),90)
    clamps['D_RR']['head_side']='exterior +Y after proper90Z station rotation'
    return groups,clamps


def west_exit_carrier(original,groups):
    def box(lo,hi):return Part.makeBox(*(hi[i]-lo[i] for i in range(3)),A.Vector(*lo))
    body=early_carrier(original)
    body=body.fuse(box((4,-71.5,90),(27,-65.5,93)))
    b=groups['Station:D_RR:case'].optimalBoundingBox(False,False)
    body=body.cut(box((b.XMin-.3,b.YMin-.3,93),(b.XMax+.3,b.YMax+.3,104)))
    body=body.fuse(box((-3.125,-68.05,92.8),(5.875,-41.95,94.7)))
    body=body.cut(box((-10,-68.5,90),(-3.375,-41.5,96.5)))
    for n,s in groups.items():
        if n.endswith(':band_budget'):
            b=s.optimalBoundingBox(False,False)
            body=body.cut(box((b.XMin-.25,b.YMin-.25,b.ZMin-.25),
                              (b.XMax+.25,b.YMax+.25,b.ZMax+.25)))
    body.check(True)
    return body


def north_groups(scene,out):
    groups,clamps=early_groups(scene,out);pivot=A.Vector(15.625,-55,98)
    for n,s in groups.items():
        if n.startswith('Station:D_RR:'):
            s.rotate(pivot,A.Vector(0,0,1),90);s.translate(A.Vector(0,20,0))
    clamps['D_RR']['head_side']='exterior -Y after proper90Z, all grooves retained'
    return groups,clamps


def north_carrier(original,groups):
    def box(lo,hi):return Part.makeBox(*(hi[i]-lo[i] for i in range(3)),A.Vector(*lo))
    body=early_carrier(original)
    # Extend seat; GPIO occupied housing startsY=-17.582, leave1.418mm.
    body=body.fuse(box((4,-44,90),(27,-19,93)))
    b=groups['Station:D_RR:case'].optimalBoundingBox(False,False)
    body=body.cut(box((b.XMin-.3,b.YMin-.3,93),(b.XMax+.3,b.YMax+.3,104)))
    body=body.fuse(box((-3.125,-48.05,92.8),(5.875,-21.95,94.7)))
    body=body.cut(box((-10,-48.5,90),(-3.375,-21.5,96.5)))
    # Move the printed hanger behind all five exits, not around each wire.
    body=body.cut(box((-10.1,-35.1,90),(-5.9,-30.9,106.3)))
    body=body.fuse(box((-10,-55,90),(-6,-51,109.4)))
    body=body.fuse(box((-10,-53,106.2),(-6,-31,109.4)))
    for n,s in groups.items():
        if n.endswith(':band_budget'):
            b=s.optimalBoundingBox(False,False)
            body=body.cut(box((b.XMin-.25,b.YMin-.25,b.ZMin-.25),
                              (b.XMax+.25,b.YMax+.25,b.ZMax+.25)))
    body.check(True);assert len(body.Solids)==1
    return body


def two_level_carrier(original,groups):
    def box(lo,hi):return Part.makeBox(*(hi[i]-lo[i] for i in range(3)),A.Vector(*lo))
    body=original.copy().cut(box((3,-35.5,90),(28.3,-19,96)))
    lower=box((30.5,-90,70),(64,-65,73))
    porch=box((30.5,-70.5,71),(64,-45.5,75))
    b=groups['Station:G_AUX:case'].optimalBoundingBox(False,False)
    porch=porch.cut(box((b.XMin-.3,b.YMin-.3,73),(b.XMax+.3,b.YMax+.3,84)))
    body=body.fuse(lower).fuse(porch)
    for x0,x1 in [(31,35),(60,64)]:
        body=body.fuse(box((x0,-66,70),(x1,-62,93)))
    body=body.fuse(box((33,-90,72.7),(60,-88.8,77)))
    for n,s in groups.items():
        if n.startswith('Station:G_AUX:') and n.endswith((':band_budget',':head_budget')):
            b=s.optimalBoundingBox(False,False)
            body=body.cut(box((b.XMin-.25,b.YMin-.25,b.ZMin-.25),
                              (b.XMax+.25,b.YMax+.25,b.ZMax+.25)))
    body.check(True);assert body.isValid() and len(body.Solids)==1
    return body


def endpoint_map(out,scene,groups):
    logical=json.loads((out/'n01-shared-end-plan.json').read_text())
    profiles=json.loads((out/'n01-selected-piece-profile-contract.json').read_text())
    local={}
    for r in logical['endpoints']:
        role=r['endpoint'];group=role.split('.')[0]
        if group in ('D_RR','G_AUX'):
            local[r['wire']]=dict(portion_id=r['portion_id'],logical_endpoint=role,
                local=free_station(groups,group,role.split('.')[1]))
    remotes={'W011':free_station(scene,'D_FR',5),'W012':free_station(scene,'D_RL',5),
             'XA05':free_station(scene,'G2',5),'XA06':free_station(scene,'G_TAIL',1),
             'W060':free_station(scene,'G1',1)}
    for wire in ('W016','W017','W018'):
        n=f'RRFlat:{wire}/body/start'
        remotes[wire]=dict(min(caps(scene[n]),key=lambda r:r['point_mm'][0]),actor=n,
                          datum='received full9 source cuff free cap')
    for wire,n,axis in [('XA04','AuxEscape:XA04',2),('XB23','HP_positive_channel:XB23',0)]:
        remotes[wire]=dict(max(caps(scene[n]),key=lambda r:r['point_mm'][axis]),actor=n,
                          datum='received actual nominal source prefix distal cap')
    n='SelectedYaw:W2_local_XB13_1';target=A.Vector(-152,-55.75,-5.406217782649094)
    matches=[]
    for e in scene[n].Edges:
        for end,parameter,sign in [(e.Vertexes[0].Point,e.FirstParameter,-1),
                                   (e.Vertexes[-1].Point,e.LastParameter,1)]:
            if (end-target).Length<1e-6:matches.append(e.tangentAt(parameter)*sign)
    assert len(matches)==1
    remotes['XB13']=dict(point_mm=list(target),outward=list(matches[0]),actor=n,
                         datum='received placed curve endpoint and actual tangent')
    remotes['W078']=dict(point_mm=[-46.3,-24,48.1],outward=[1,0,0],actor='SpliceClip',
        datum='PROVISIONAL: .25mm beyond actual clip right face; replaces artificial3mm free tip; source full9 jacket/grip fit OPEN',
        source_grip_OPEN=True)
    main_y={'W079':-76.8875,'W080':-80.3875,'W060':-83.8875,'W078':-87.3875}
    for w,y in main_y.items():
        local[w]=dict(portion_id=w+'/retained0',logical_endpoint='MAIN',
            local=dict(point_mm=[5.7,y,96.55],outward=[1,0,0],actor='MAINexit',
                       datum='reviewed full9 common source saddle free cap'))
    rows={}
    for w,r in local.items():
        p=profiles['portions'][r['portion_id']]
        remote=remotes.get(w)
        if w in ('W079','W080'):
            y=46.618109634713775 if w=='W079' else 50.118109634713775
            remote=dict(point_mm=[74.7,y,101.6],outward=[1,0,0],actor='PAS',
                        datum='received PAS free cap; upstream factory prefix retained')
        assert remote is not None
        rows[w]=dict(r,remote=remote,selected_sku=p['selected_sku'],
            selected_physical_unit=p['selected_physical_unit'],radius_mm=p['project_radius_mm'],
            minimum_R_mm=p['minimum_project_R_mm'],
            straight_lower_bound_mm=(A.Vector(*r['local']['point_mm'])-
                                     A.Vector(*remote['point_mm'])).Length)
    assert len(rows)==14
    return dict(status='CURRENT_CAP_IDENTITIES_NOT_WHOLE_ROUTES',rows=rows,
        source_sha256={str(out/n):sha(out/n) for n in
                       ['n01-shared-end-plan.json','n01-selected-piece-profile-contract.json']},
        selected=False,N01_complete=False,physical_pass=False)


def down_fans(endpoint_map):
    shapes={};recipes={}
    for w,r in endpoint_map['rows'].items():
        if not r['logical_endpoint'].startswith(('D_RR.','G_AUX.')):continue
        p=r['local']['point_mm'];t=r['local']['outward']
        R=15 if r['logical_endpoint'].startswith('G_AUX.') else r['minimum_R_mm']
        q=[p[i]+t[i]*R-(R if i==2 else 0) for i in range(3)]
        parts=[base.tr.arc(p,t,q)]
        shapes[w]=base.solid(parts,r['radius_mm']);shapes[w].check(True)
        recipes[w]=dict(parts=parts,end=q,tangent=[0,0,-1],radius_mm=r['radius_mm'])
    return shapes,recipes


def under_gpio_lanes(endpoint_map,planes=None):
    """One S-bend per group: ahead of fuse housings, below occupied GPIO."""
    nominal={};packing={};recipes={}
    for w,r in endpoint_map['rows'].items():
        group=r['logical_endpoint'].split('.')[0]
        if group not in ('D_RR','G_AUX'):continue
        p=r['local']['point_mm'];R,z=(12.4,81.5) if group=='D_RR' else (15.,79.)
        if planes:z=planes[group]
        drop=p[2]-z;run=2*math.sqrt(R*drop-drop**2/4)
        t=r['local']['outward'];q=[p[0]+run*t[0],p[1]+run*t[1],z]
        parts=base.tr.biarc(p,t,q,t)
        assert min(v['radius'] for v in parts)>=R-1e-6
        nominal[w]=base.solid(parts,r['radius_mm'])
        packing[w]=base.solid(parts,r['radius_mm']+.5)
        nominal[w].check(True);packing[w].check(True)
        recipes[w]=dict(parts=parts,end=q,tangent=t,radius_mm=r['radius_mm'],
            packing_radial_mm=.5,group_plane_Z_mm=z,minimum_R_mm=R,
            source_grip9_unchanged=True,
            basis='Early9mm exit ahead of housingY=-39.25. S planes include .5mm packing below GPIO lowerZ86.95 and above metal terminal upperZ74.194.')
    return nominal,packing,recipes


def drr_chimney(endpoint_map):
    """Shared full-width bay in the9mm gap between F_R1 and F_R2."""
    nominal={};packing={};recipes={}
    for w,r in endpoint_map['rows'].items():
        if not r['logical_endpoint'].startswith('D_RR.'):continue
        p=r['local']['point_mm'];y=p[1];R=12.4
        a=[-10.6,y,98];b=[-23,y,85.6];c=[-23,y,45.75];d=[-10.6,y,33.35]
        parts=[base.tr.line(p,a),base.tr.arc(a,(-1,0,0),b),
               base.tr.line(b,c),base.tr.arc(c,(0,0,-1),d)]
        nominal[w]=base.solid(parts,r['radius_mm']);packing[w]=base.solid(parts,r['radius_mm']+.5)
        nominal[w].check(True);packing[w].check(True)
        recipes[w]=dict(parts=parts,end=d,tangent=[1,0,0],radius_mm=r['radius_mm'],
            source_grip9_unchanged=True,minimum_R_mm=R,packing_radial_mm=.5,
            basis='F_R1 housing rightX=-27.5; F_R2 leftX=-18.5; centreX=-23,9mm bay. Lower plane33.35 between strap28.7 and rail38.')
    return nominal,packing,recipes


def main_input_routes(endpoint_map):
    """Two shared outer-side input runs; keep R47 and Pi pedestal intact."""
    shapes={};recipes={};R=12.4
    for w in ('W060','W078'):
        row=endpoint_map['rows'][w];p=row['local']['point_mm'];y=p[1]
        a=[17.6,y,96.55];b=[30,y,84.15]
        parts=[base.tr.line(p,a),base.tr.arc(a,(1,0,0),b)]
        if w=='W078':
            c=[30,y,60.5];d=[17.6,y,48.1];e=[-21.5,y,48.1]
            f=[-33.9,y+R,48.1];g=[-33.9,-36.4,48.1];q=row['remote']['point_mm']
            parts += [base.tr.line(b,c),base.tr.arc(c,(0,0,-1),d),base.tr.line(d,e),
                      base.tr.arc(e,(-1,0,0),f),base.tr.line(f,g),
                      base.tr.arc(g,(0,1,0),q)]
        else:
            q=A.Vector(*row['remote']['point_mm'])
            # Last30deg arc follows the already received G1 cap tangent.
            h=q-A.Vector(0,R*(1-math.cos(math.pi/6)),R*.5)
            c=A.Vector(55.5,y,h.z);v=h-c;radius=v.Length/2;assert radius>=R
            u=v.normalize()
            bend=dict(kind='arc',start=list(c),end=list(h),tangent=[0,0,-1],
                bend=list(u),radius=radius,angle=math.pi,length=math.pi*radius,end_tangent=[0,0,1])
            f=[30,y,45]
            parts += [base.tr.line(b,f),*base.tr.biarc(f,(0,0,-1),list(c),(0,0,-1)),
                      bend,base.tr.arc(list(h),(0,0,1),list(q))]
        shapes[w]=base.solid(parts,row['radius_mm']);shapes[w].check(True)
        recipes[w]=dict(parts=parts,length_mm=base.tr.length(parts),radius_mm=row['radius_mm'],
            minimum_R_mm=min(p.get('radius',math.inf) for p in parts),
            source=row['local'],receiver=row['remote'],
            end_tangent=parts[-1]['end_tangent'],source_grip_and_receiver_prefix_unchanged=True,
            W078_source_grip_not_received=w=='W078')
    return shapes,recipes


def ground_routes(endpoints,entries,scene):
    """One north gallery and shared west/south approach, not pose enumeration."""
    shapes={};recipes={}
    def half(p,t,bend,R,end):
        return dict(kind='arc',start=p,end=end,tangent=t,bend=bend,radius=R,
                    angle=math.pi,length=math.pi*R,end_tangent=[-x for x in t])
    for w in ('XA04','XA05','XA06','XB13','XB23'):
        row=endpoints['rows'][w];parts=list(entries[w]['parts']);p=entries[w]['end']
        a=[p[0],0,79];parts.append(base.tr.line(p,a))
        if w=='XA06':
            b=[71.375,15,79];parts.append(base.tr.arc(a,(0,1,0),b))
            c=[83,15,79];d=[98,30,79]
            rise=95.595-79;run=2*math.sqrt(15*rise-rise**2/4)
            e=[98,71.5-run,79];f=[98,71.5,95.595];g=[128,71.5,95.595]
            parts += [base.tr.line(b,c),base.tr.arc(c,(1,0,0),d),base.tr.line(d,e),
                      *base.tr.biarc(e,(0,1,0),f,(0,1,0)),half(f,[0,1,0],[1,0,0],15,g),
                      base.tr.arc(g,(0,-1,0),row['remote']['point_mm'])]
        else:
            R=p[0]-22.375;b=[22.375,R,79];parts.append(base.tr.arc(a,(0,1,0),b))
            if w=='XA05':
                c=[-22.375,15,79];d=[-37.375,15,64];e=[-37.375,15,60.26];f=[-37.375,30,45.26]
                parts += [base.tr.line(b,c),base.tr.arc(c,(-1,0,0),d),base.tr.line(d,e),
                          base.tr.arc(e,(0,0,-1),f),base.tr.line(f,row['remote']['point_mm'])]
            elif w=='XA04':
                c=[-44,19.75,79];d=[-59,19.75,64];e=[-59,19.75,48.35];f=[-59,4.75,33.35]
                g=[-59,-80.27,33.35];h=[-44,-95.27,33.35];i=[131.43,-95.27,33.35]
                j=[146.43,-95.27,48.35];k=[146.43,-95.27,82.21];l=[146.43,-80.27,97.21]
                q=[146.43,-65.27,82.21]
                parts += [base.tr.line(b,c),base.tr.arc(c,(-1,0,0),d),base.tr.line(d,e),
                          base.tr.arc(e,(0,0,-1),f),base.tr.line(f,g),base.tr.arc(g,(0,-1,0),h),
                          base.tr.line(h,i),base.tr.arc(i,(1,0,0),j),base.tr.line(j,k),
                          base.tr.arc(k,(0,0,1),l),base.tr.arc(l,(0,1,0),q)]
                row=dict(row,remote=dict(point_mm=q,outward=[0,0,1],actor='AuxSource:XA04:jacket',
                    replaces_only='AuxEscape:XA04',received_source_grip_unchanged=True))
            else:
                q=row['remote']['point_mm'];t=[-v for v in row['remote']['outward']]
                if w=='XB13':
                    c=[-100,b[1],79];parts.append(base.tr.line(b,c))
                else:c=b
                parts += base.tr.biarc(c,(-1,0,0),q,t)
        minimum=min(p.get('radius',math.inf) for p in parts)
        assert minimum>=row['minimum_R_mm']-1e-6,(w,minimum)
        shapes[w]=base.solid(parts,row['radius_mm']);shapes[w].check(True)
        recipes[w]=dict(parts=parts,length_mm=base.tr.length(parts),minimum_R_mm=minimum,
            radius_mm=row['radius_mm'],source=row['local'],receiver=row['remote'],
            exact_source_cap_and_tangent=True,selected_sku=row['selected_sku'])
    return shapes,recipes


def read_archive(doc):
    result={};arc=doc['geometry_archive']
    assert sha(Path(arc['path']))==arc['sha256']
    with zipfile.ZipFile(arc['path']) as z:
        for name,r in arc['members'].items():
            s=Part.Shape();s.importBrepFromString(z.read(r['member']).decode());result[name]=s
    return result


def changed_checks(changed,current,metadata):
    from feline_solid_distance import bbox_lower_bound,distance
    from receive_feline_jpwm_whole_pose import solid_profile_target
    tick=time.monotonic();checked={};rows=[];errors=[]
    for a,s in changed.items():
        for b,original in current.items():
            if a==b:continue
            m=metadata.get(b,{})
            reserve=m.get('nominal_profile_radius_mm',0) if not original.Solids else 0
            if bbox_lower_bound(s.BoundBox,original.BoundBox)>1.25+reserve:continue
            if b not in checked:
                try:
                    other=original.copy() if original.Solids else solid_profile_target(original,m)
                    other.check(True);checked[b]=other
                except Exception as exc:
                    errors.append(dict(actor=b,error=str(exc).splitlines()[0]));checked[b]=None
            other=checked[b]
            if other is None:continue
            gap=distance(s.copy(),other.copy())
            common=s.copy().common(other.copy()).Volume if gap<1e-6 else 0
            kind=m.get('kind','UNKNOWN_RETAINED_ACTOR')
            if b.startswith(('Service:','ATOAccess:')):kind='access_reservation'
            elif b.startswith('PiBudget:'):kind='occupied_module_or_mating_reservation'
            elif b.startswith('Station:') and ':wire:' in b:kind='received_wire_capacity'
            rows.append(dict(new=a,existing=b,kind=kind,gap_mm=gap,common_mm3=common))
    return dict(rows=rows,errors=errors,seconds=time.monotonic()-tick,
        whole_scene_received=False,N01_complete=False,physical_pass=False)


def preserve_trial(out, shapes, receipt):
    """Save one explicitly UNSELECTED study, then strictly reopen every own shape."""
    tick=time.monotonic(); archive=out/'prototype-joint-endpoints-20261024.breps.zip'
    members={}
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for i,(name,s) in enumerate(shapes.items()):
            s.check(True)
            raw=s.exportBrepToString();raw=raw.encode() if isinstance(raw,str) else raw
            member=f'{i}.brep';z.writestr(member,raw)
            reopened=Part.Shape();reopened.importBrepFromString(raw.decode());reopened.check(True)
            box=reopened.optimalBoundingBox(False,False)
            members[name]=dict(member=member,solids=len(reopened.Solids),
                bounds_mm=[box.XMin,box.YMin,box.ZMin,box.XMax,box.YMax,box.ZMax],
                strict_reopen=True,volume_mm3=reopened.Volume)
    receipt['geometry_archive']=dict(path=str(archive),sha256=sha(archive),members=members)
    receipt['preserve_and_reopen_seconds']=time.monotonic()-tick
    receipt['generator_sha256']=sha(Path(__file__))
    receipt['selected']=False;receipt['N01_complete']=False;receipt['physical_pass']=False
    target=out/'prototype-joint-endpoints-20261024-result.json'
    target.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return receipt
