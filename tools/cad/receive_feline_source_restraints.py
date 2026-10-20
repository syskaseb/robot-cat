"""One complete source restraint proposal; typed fits, full prints and motion.

Save each exact pair and each whole-print proof. Resume missing work only;
do not replay MTA, source wire checks or successful unions after a slice.
"""
import argparse,copy,gzip,hashlib,json,math,time,zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_source_restraint_plan import construct,source
from feline_main_hung_context import compose
from receive_feline_rrp_shared_height import load
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from plan_feline_pi_root_access import profile_gap
from receive_feline_global_case_candidates import placement
from plan_feline_usb_service_bight import outer_margin
from feline_atomic_save import save_json


def local_limit(n,other,meta,groups,specs,bonds):
    info=meta[n];oi=meta.get(other,{})
    if info['kind']=='PETG' and oi.get('kind')=='PETG' and info['print_group']==oi['print_group']:return None
    if {info['kind'],oi.get('kind')}=={'VHB4905','PETG'} and info['print_group']==oi['print_group']:return 0.
    for bond in bonds.values():
        if n==bond['patch'] and other in (bond['case'],bond['spine']):return 0.
        if n==bond['spine'] and other in (bond['patch'],bond['case']):return 0. if other==bond['patch'] else .2
    # POST's own two jackets leave this retained case at its nominal mouths.
    # Keep .2mm physical separation to its case-retention land, not a foreign
    # harness keepout. This NEVER applies to a different source/cable/print.
    if n in ('SourceBody:POST:spine','SourceBody:POST:patch') and other in ('W076_factory','W076_custom_prefix'):return .2
    if n.startswith('SourceGrip:'):
        key=n.split(':')[1]
        if other==specs[key]['wire']:return .2
        if other.startswith('SourceGrip:'+key+':'):
            suffixes={n.rsplit(':',1)[1],other.rsplit(':',1)[1]}
            return 0. if suffixes in ({'band','pad'},{'band','head'}) else .2
        if key=='F0OUT' and other=='Ref_Material_F0_CP2_0_0':return .2
        if key in ('POSTIN','POSTOUT') and other=='Ref_Material_PostF0Splice_CP2_0_0':return .2
    return 1.25


def local_check(revision):
    base,new,meta,groups,specs,bonds,*_=construct('r2' if revision=='r3' else revision)
    if revision in ('r4','r5'):
        m=json.loads((OUT/'n01-MTA-low-stop-cradles.json').read_text());base.update(load(m))
        groups['lower']+=m['print_groups']['LowerBay:RearPanel']
    failures=[]
    for n,s in new.items():
        for other,t in {**base,**new}.items():
            if n==other or other in new and list(new).index(other)>list(new).index(n):continue
            limit=local_limit(n,other,meta,groups,specs,bonds)
            if any(n in members and other in members for members in groups.values()):limit=None
            if limit is None:continue
            if bbox_lower_bound(s.BoundBox,t.BoundBox)>limit+1e-6:continue
            gap=s.distToShape(t)[0]
            common=s.common(t).Volume if limit==0 else 0.
            if gap<limit-1e-6 or common>1e-5:failures.append((n,other,round(gap,6),limit,round(common,6)))
    print('LOCAL_CHANGED_SOURCE',revision,len(new),'FAILURES',failures,flush=True)
    assert not failures


def receive_trimmed_fork(world,effective,meta,pins,docs,u1_sources,u1_files,case_bypass=False,head_aware=False):
    """Remove the known PCB corner only; reuse26 actors and monotone gaps.

    All14 current U1 sources enter the same gate. Preserve every original
    positive print joint: a smaller connected fork with identical joints
    cannot disconnect the previously proved connected whole print.
    Native detailed reconstruction remains N03, not this N01 space gate.
    """
    tick=time.monotonic();src=OUT/'n01-source-restraints-whole-r5.json';old=json.loads(src.read_text())
    name='SourceRoot:lowerSharedFork';pcbname='Ref_Material_PWM1608NominalPCB_0_0'
    assert old['failures']==[name+'|'+pcbname] and len(old['completed_static'])==26
    filename='n01-source-restraints-head-case-bypass.json' if head_aware else 'n01-source-restraints-case-bypass.json' if case_bypass else 'n01-source-restraints-current.json'
    dest=OUT/filename;assert not dest.exists()
    new=load(old);original=new[name];pcb=effective[pcbname].BoundBox;bb=original.BoundBox
    tool=Part.makeBox(pcb.XMax+1.25-bb.XMin+1,bb.YMax-(pcb.YMin-1.25)+1,bb.ZLength+2,
                      A.Vector(bb.XMin-1,pcb.YMin-1.25,bb.ZMin-1))
    cut=original.copy().cut(tool)
    if case_bypass:
        # The former downleg went THROUGH MTA_RR, not an obsolete alias.
        # Go ABOVE the complete cap and OUTSIDE its south face, then join
        # the already-rooted CaseBase below it. No guessed empty floor toe.
        from feline_source_restraint_plan import box,joined
        body=effective['Ref_Material_MTA_RR_0_0'].BoundBox
        cap=effective['CaseCap:W042_Joint'].BoundBox;base=effective['CaseBase:W042_Joint'].BoundBox
        shelf=box([bb.XMin,bb.YMin,-27.5],[48,-23,-25.5]).cut(tool)
        bodycut=box([body.XMin-1.25,body.YMin-1.25,-28.5],[54,-22,-24.5])
        shelf=shelf.cut(bodycut)
        innerY=cap.YMin-1.25;outerY=innerY-2;bridgeZ=cap.ZMax+1.25
        parent_faces=[f for f in effective['CaseBase:W042_Joint'].Faces
                      if type(f.Surface).__name__=='Plane' and abs(f.normalAt(0,0).y)>.99
                      and abs(f.CenterOfMass.y-base.YMin)<1e-5]
        assert len(parent_faces)==1,'Select the actual parent face, not its empty bbox corner'
        rootx=parent_faces[0].CenterOfMass.x
        bridgeYmax=bb.YMin+2
        neck=[box([46,bb.YMin,-27.5],[48,bridgeYmax,bridgeZ+2])]
        if head_aware:
            # First leave the WHOLE ground head beneath its old clear plane;
            # only then rise south of its full envelope. No Z-only retry.
            head=new['SourceGrip:GROUND:head'].BoundBox
            bridgeYmax=min(bb.YMin,head.YMin-1.25)
            neck=[box([46,bridgeYmax-2,-27.5],[48,bb.YMin+2,-25.5]),
                  box([46,bridgeYmax-2,-27.5],[48,bridgeYmax,bridgeZ+2])]
        cut=joined([shelf,*neck,
                    box([46,outerY,bridgeZ],[53,bridgeYmax,bridgeZ+2]),
                    box([51,outerY,base.ZMin],[53,innerY,bridgeZ+2]),
                    box([51,outerY,base.ZMin],[rootx+1,innerY,base.ZMin+2]),
                    box([rootx-1,outerY,base.ZMin],[rootx+1,base.YMin+2,base.ZMin+2])])
        assert cut.copy().common(effective['CaseBase:W042_Joint'].copy()).Volume>1.,'No actual bypass-root joint'
    assert cut.isValid() and len(cut.Solids)==1
    if not case_bypass:assert cut.copy().cut(original.copy()).Volume<1e-7
    removed=original.copy().cut(cut.copy());assert removed.isValid() and removed.Volume>0
    joint_proofs={}
    for n in old['print_groups']['lower']:
        if n==name:continue
        s=new.get(n,effective.get(n));assert s is not None,n
        if bbox_lower_bound(removed.BoundBox,s.BoundBox)>1e-6:continue
        common=removed.copy().common(s.copy());assert common.isNull() or common.isValid()
        if not case_bypass:assert common.Volume<1e-7,('Cut changes a previous print joint',n,common.Volume)
        joint_proofs[n]=dict(removed_joint_volume_mm3=common.Volume)
    new[name]=cut;ownmeta={r['name']:r for r in old['geometry']};query=SolidQueries()
    prior=json.loads(gzip.decompress((ROOT/old['pair_rows']).read_bytes()))
    checks={k:v for k,v in prior.items() if v['ok'] and (not case_bypass or name not in k.split('|'))}
    reused=len(checks);scene={**effective,**new,**u1_sources}
    source_inputs={**pins,**{f.relative_to(ROOT).as_posix():sha(f) for f in (src,ROOT/old['bundle'],ROOT/old['pair_rows'],Path(__file__),*u1_files)}}
    result=dict(status='RUNNING_CURRENT_SOURCE_FORK_STATIC_MOTION',source_sha256=source_inputs,
        completed_static=list(old['completed_static']),completed_motion=[],checks=checks,
        failures=[],reused_prior_positive_pairs=reused,subset_of_previous_root=not case_bypass,
        removed_free_corner_volume_mm3=removed.Volume,unchanged_previous_print_joint_proofs=joint_proofs,
        prior_lower_connected_print_proof=old['print_union_proofs']['lower'],
        current_lower_connectivity_proof='Whole union required below' if case_bypass else 'Connected1Solid subset fork, unchanged positive intersection regions with ALL other previously connected members',
        unchanged_upper_print_proof=old['print_union_proofs']['upper'],
        all14_U1_local_sources_included=len(u1_sources)==28,full_grips_common123_tools_assembly_OPEN=True,
        N01_complete=False,native_changed=False,physical_pass=False)
    assert result['all14_U1_local_sources_included']
    if case_bypass:
        members=[scene[n].copy() for n in old['print_groups']['lower']]
        full=members[0].multiFuse(members[1:]);assert full.isValid() and len(full.Solids)==1
        b=full.BoundBox;size=[b.XLength,b.YLength,b.ZLength];assert max(size)<250
        result['current_lower_connectivity_proof']=dict(actual_whole_union_valid=True,solids=1,envelope_mm=size,within250_margin=True)
        checks['wholeprint:lower']=dict(ok=True,actual_changed_whole_print_union=True)
    archive=dest.with_suffix('.breps.zip');geometry=[]
    with zipfile.ZipFile(ROOT/old['bundle']) as zold,zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for row in old['geometry']:
            row=dict(row);raw=cut.exportBrepToString().encode() if row['name']==name else zold.read(row['entry'])
            row['sha256']=hashlib.sha256(raw).hexdigest();z.writestr(row['entry'],raw);geometry.append(row)
    result.update(bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),geometry=geometry)
    def save():
        result.update(worker_seconds=round(time.monotonic()-tick,3),failures=[k for k,v in checks.items() if not v['ok']])
        save_json(dest,result)
    def check(n,s,other,t,limit=1.25):
        key=n+'|'+other
        if key in checks:return
        if bbox_lower_bound(s.BoundBox,t.BoundBox)>=limit:return
        a=s;b=t
        if other==world.bus['name']:a=s.copy();a.Placement=docs['inverse']*a.Placement;b=world.bus['original']
        if not b.Solids:
            md=meta.get(other,{});rad=md.get('nominal_profile_radius_mm') or md.get('radius_mm')
            row=profile_gap(a,b,rad,limit) if rad else dict(ok=False,unreceived_curve_profile=True)
        else:gap=query.distance(a,b);row=dict(ok=gap>=limit-1e-6,gap_mm=gap,minimum_mm=limit)
        checks[key]=row
        if not row['ok']:print('CURRENT_SOURCE_HOLD',key,row,flush=True)
    checks[name+'|outer']=outer_margin(cut,docs['outer']) if case_bypass else old['outline'][name]
    save()
    # Positive old distances survive a true subset; only the old failed pair
    # and previously unvisited neighbours need a new exact query.
    for other,s in scene.items():
        if other==name or other in old['print_groups']['lower']:continue
        limit=local_limit(name,other,ownmeta,old['print_groups'],old['independent_grips'],old['case_bonds'])
        if limit is not None:check(name,cut,other,s,limit)
    for n,s in new.items():
        for other,t in u1_sources.items():check(n,s,other,t)
    save()
    if result['failures']:result['status']='CURRENT_SOURCE_FORK_STATIC_HOLD';save();return result
    result['completed_static']=list(new)
    moving=[(p,A.BoundBox(*p['bounds'][0],*p['bounds'][1])) for p in world.motion]
    for n,s in new.items():
        for p,b in moving:
            if bbox_lower_bound(s.BoundBox,b)>=1.25:continue
            key=n+'|motion:'+p['name']+':'+str(p['pose'])
            if key in checks:continue
            tf=placement(p['r'],p['t']);q=s.copy();q.Placement=tf.inverse()*q.Placement
            gap=query.distance(q,world.rest[p['name']]);checks[key]=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
            if gap<1.25-1e-6:result['status']='CURRENT_SOURCE_FORK_MOTION_HOLD';save();return result
        result['completed_motion'].append(n);save();print('CURRENT_SOURCE36',n,flush=True)
    result['status']='SOURCE_RESTRAINTS_CURRENT_STATIC36_RECEIVED_N01_SHARED123_OPEN';save()
    print(result['status'],len(checks),result['worker_seconds'],flush=True)
    return result


def main(revision='r1'):
    tick=time.monotonic();dest=OUT/('n01-source-restraints-whole'+('' if revision=='r1' else '-'+revision)+'.json');pf=dest.with_suffix('.pairs.json.gz');archive=dest.with_suffix('.breps.zip')
    world,parts,meta,pins,docs=compose();mf=OUT/'n01-MTA-low-stop-cradles.json';m=json.loads(mf.read_text())
    effective={n:s for n,s in parts.items() if n not in m['retired']};effective.update(load(m))
    sf=OUT/'n01-F0-access-stack.json';motion=OUT/'n01-F0-access-stack-motion.json'
    foundation=OUT/'n01-channelled-foundation-static.json'
    inputs=(sf,ROOT/json.loads(sf.read_text())['bundle'],motion,mf,ROOT/m['bundle'],foundation,
        ROOT/'tools/cad/feline_source_restraint_plan.py',ROOT/'tools/cad/feline_source_saddles.py',
        ROOT/'tools/cad/receive_feline_positive_service_deck.py',Path(__file__))
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in inputs})
    parent=None
    if revision=='r3':
        previous=OUT/'n01-source-restraints-whole-r2.json';parent=json.loads(previous.read_text())
        assert parent['status']=='SOURCE_PRINT_UNION_HOLD' and parent['failures']==['wholeprint:upper']
        for p,h in parent['source_sha256'].items():
            if p!=Path(__file__).relative_to(ROOT).as_posix():assert pins[p]==h,('Changed geometry dependency',p)
        pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (previous,ROOT/parent['bundle'])})
    diagnostic=None
    if revision in ('r4','r5'):
        df=OUT/'n01-source-restraints-static-witnesses.json';diagnostic=json.loads(df.read_text())
        assert len(diagnostic['completed'])==27
        prior=OUT/'n01-source-restraints-whole-r3.json';prior_result=json.loads(prior.read_text())
        for p,h in diagnostic['source_sha256'].items():
            if p in pins:assert pins[p]==h,p
        pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (df,prior,ROOT/prior_result['bundle'])})
    checks={};query=SolidQueries()
    if dest.exists():
        result=json.loads(dest.read_text());assert result['source_sha256']==pins
        assert sha(archive)==result['bundle_sha256'] and sha(pf)==result['pair_rows_sha256']
        checks=json.loads(gzip.decompress(pf.read_bytes()))
        if result['failures'] or result['status']=='SOURCE_FULL_RESTRAINTS_STATIC36_RECEIVED_ASSEMBLY_COMMON123_OPEN':
            print('TERMINAL',result['status'],result['failures'],flush=True);return
        new={}
        with zipfile.ZipFile(archive) as z:
            for row in result['geometry']:
                raw=z.read(row['entry']);assert hashlib.sha256(raw).hexdigest()==row['sha256']
                s=Part.Shape();s.importBrepFromString(raw.decode());new[row['name']]=s
        # Current source kit is pinned by sf, so load without reconstruction.
        sr=json.loads(sf.read_text());base={}
        with zipfile.ZipFile(ROOT/sr['bundle']) as z:
            for n,row in sr['geometry'].items():
                raw=z.read(row['entry']);assert hashlib.sha256(raw).hexdigest()==row['sha256']
                s=Part.Shape();s.importBrepFromString(raw.decode());base[n]=s
        result.setdefault('previous_worker_seconds',[]).append(result['worker_seconds'])
    else:
        if parent:
            base,sr,_,_=source();new=load(parent);nm={row['name']:dict(row) for row in parent['geometry']}
            groups={g:[n for n in members if n in new] for g,members in parent['print_groups'].items()}
            specs=parent['independent_grips'];bonds=parent['case_bonds']
        else:base,new,nm,groups,specs,bonds,sr,_,_=construct(revision)
        # Keep full inherited physical print ownership, not just the nearest rail.
        lower=list(m['print_groups']['LowerBay:RearPanel'])
        # The channelled-foundation graph predates the RECEIVED portal2
        # substitution. Use actual current material paths, not that old pier.
        f=docs['retention_frame_graph'];upper={'CurrentFoundation:FoundationFlange:1'}
        def current_name(node):
            name=node.rsplit('/solid:',1)[0]
            return name if name=='BankPortal2:Carrier' else 'CurrentFoundation:'+name
        while True:
            expanded=set(upper)
            for edge in f['positive_joints']:
                a,b=current_name(edge['a']),current_name(edge['b'])
                if {a,b}&upper:expanded.update((a,b))
            if expanded==upper:break
            upper=expanded
        upper=sorted(upper)+['EarlyRR:comb:inner']
        missing=[n for n in lower+upper if n not in effective]
        assert not missing,('Current whole-print ownership missing',missing)
        pgroup=dict(lower=lower+groups['lower'],upper=upper+groups['upper'])
        geometry=[]
        with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
            for i,(n,s) in enumerate(new.items()):
                raw=s.exportBrepToString().encode();entry=str(i)+'.brep';z.writestr(entry,raw);geometry.append(dict(nm[n],name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
        result=dict(status='RUNNING_SOURCE_RESTRAINTS_LOCAL_PRINTS',source_sha256=pins,geometry=geometry,
            bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),print_groups=pgroup,print_union_proofs={},
            independent_grips=specs,case_bonds=bonds,completed_static=[],completed_motion=[],outline={},
            new_geometry_count=len(new),five_independent_T18I_full_heads=True,
            selected_case_only_VHB_extra_draw_mm=54,selected_roll_count_NOT_changed=1,
            assembly_and_all123_common_capacity_OPEN=True,N01_complete=False,native_changed=False,physical_pass=False)
        if diagnostic:
            prior_shapes=load(prior_result);unchanged=[]
            for n,s in new.items():
                a=s.copy().cut(prior_shapes[n].copy());b=prior_shapes[n].copy().cut(s.copy())
                assert (a.isNull() or a.isValid()) and (b.isNull() or b.isValid())
                if a.Volume+b.Volume<1e-5:unchanged.append(n)
            checks={k:v for k,v in diagnostic['checks'].items()
                    if v['ok'] and k.split('|')[0] in unchanged and (k.split('|')[1] not in new or k.split('|')[1] in unchanged)}
            # A group reassignment must not inherit a former same-print or
            # softer mating exemption against a now foreign print member.
            for key,row in list(checks.items()):
                n,other=key.split('|',1)
                same=any(n in members and other in members for members in result['print_groups'].values())
                limit=None if same else local_limit(n,other,{v['name']:v for v in geometry},result['print_groups'],specs,bonds)
                if limit is not None and row.get('minimum_mm',-1)<limit:checks.pop(key)
            result.update(reused_actual_geometry_identity=unchanged,reused_exact_pairs=len(checks))
            if result['print_groups']['upper']==prior_result['print_groups']['upper'] and all(n in unchanged for n in result['print_groups']['upper'] if n in new):
                result['print_union_proofs']['upper']=copy.deepcopy(prior_result['print_union_proofs']['upper'])
                checks['wholeprint:upper']=dict(ok=True,reused_identical_members_union_and_print_orientation=True)
        if parent:
            assert pgroup==parent['print_groups'],'Only reuse identical whole-print material members'
            result['reused_whole_print_geometry_from']=previous.relative_to(ROOT).as_posix()
            result['print_union_proofs']=copy.deepcopy(parent['print_union_proofs'])
            for group,proof in result['print_union_proofs'].items():
                assert proof['valid'] and proof['solids']==1
                x,y,z=proof['envelope_mm'];angle=45. if max(x,y)>250 else 0.
                c=abs(math.cos(math.radians(angle)));s=abs(math.sin(math.radians(angle)))
                envelope=[c*x+s*y,s*x+c*y,z]
                proof.update(print_rotation_about_Z_deg=angle,conservative_rotated_print_envelope_mm=envelope,
                             within250_margin=max(envelope)<250,union_not_requeried=True,
                             orientation_NOT_slicer_or_strength_approval=True)
                checks['wholeprint:'+group]=dict(ok=proof['within250_margin'],actual_whole_print_union=True,rotated_full_enclosing_box=True)
    effective.update(base);effective.update(new);ameta={row['name']:row for row in result['geometry']}
    def save(status=None):
        if status:result['status']=status
        pf.write_bytes(gzip.compress(json.dumps(checks,separators=(',',':')).encode(),mtime=0))
        result.update(checks=len(checks),failures=[k for k,v in checks.items() if not v['ok']],worker_seconds=round(time.monotonic()-tick,3),pair_rows=pf.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(pf));save_json(dest,result)
    save()
    for group,members in result['print_groups'].items():
        if group in result['print_union_proofs']:continue
        s=effective[members[0]].copy().multiFuse([effective[n].copy() for n in members[1:]])
        valid=s.isValid() and len(s.Solids)==1;b=s.BoundBox;size=[b.XLength,b.YLength,b.ZLength]
        angle=45. if max(size[:2])>250 else 0.;c=abs(math.cos(math.radians(angle)));sn=abs(math.sin(math.radians(angle)))
        oriented=[c*size[0]+sn*size[1],sn*size[0]+c*size[1],size[2]]
        result['print_union_proofs'][group]=dict(valid=valid,solids=len(s.Solids),envelope_mm=size,
            print_rotation_about_Z_deg=angle,conservative_rotated_print_envelope_mm=oriented,
            within250_margin=valid and max(oriented)<250,members=members,orientation_NOT_slicer_or_strength_approval=True)
        checks['wholeprint:'+group]=dict(ok=valid and max(oriented)<250,actual_whole_print_union=True)
        save();print('FULL_PRINT',group,result['print_union_proofs'][group]['solids'],size,flush=True)
        if not checks['wholeprint:'+group]['ok']:save('SOURCE_PRINT_UNION_HOLD');return
        if time.monotonic()-tick>220:save('PARTIAL_SOURCE_RESTRAINTS_SAVED');return
    def minimum(n,other):
        for members in result['print_groups'].values():
            if n in members and other in members:return None # proved whole valid1Solid, not foreign material
        return local_limit(n,other,ameta,result['print_groups'],result['independent_grips'],result['case_bonds'])
    def check(n,s,other,t,limit):
        if limit is None:return dict(ok=True,same_proved_whole_print=True)
        bound=bbox_lower_bound(s.BoundBox,t.BoundBox)
        if bound>=limit and (limit>0 or bound>1e-6):return None
        a=s;b=t
        if other==world.bus['name']:a=s.copy();a.Placement=docs['inverse']*a.Placement;b=world.bus['original']
        if not b.Solids:
            md=meta.get(other,{});radius=md.get('nominal_profile_radius_mm') or md.get('radius_mm')
            return profile_gap(a,b,radius,limit) if radius else dict(ok=False,unreceived_curve_profile=True)
        gap=query.distance(a,b);row=dict(ok=gap>=limit-1e-6,gap_mm=gap,minimum_mm=limit)
        if limit==0:
            c=a.copy().common(b.copy());assert c.isNull() or c.isValid();row.update(common_mm3=c.Volume,ok=row['ok'] and c.Volume<1e-5)
        if not row['ok']:
            _,pts,_=a.distToShape(b);row['witness_mm']=[[list(x),list(y)] for x,y in pts[:1]]
        return row
    names=list(new)
    for n,s in new.items():
        if n in result['completed_static']:continue
        if n not in result['outline']:
            result['outline'][n]=outer_margin(s,docs['outer']);checks[n+'|outer']=result['outline'][n]
            save()
            if not result['outline'][n]['ok']:save('SOURCE_RESTRAINT_OUTER_HOLD');return
        for other,t in effective.items():
            if other==n or other in new and names.index(other)>names.index(n):continue
            key=n+'|'+other
            if key in checks:continue
            row=check(n,s,other,t,minimum(n,other))
            if row is not None:checks[key]=row;save()
            if row is not None and not row['ok']:save('SOURCE_RESTRAINT_STATIC_ACTUAL_HOLD');print(result['status'],key,row,flush=True);return
            if time.monotonic()-tick>220:save('PARTIAL_SOURCE_RESTRAINTS_SAVED');return
        for other,t in world.rest.items():
            if bbox_lower_bound(s.BoundBox,t.BoundBox)>=1.25:continue
            key=n+'|rest:'+other
            if key not in checks:
                row=check(n,s,'rest:'+other,t,1.25)
                if row is not None:checks[key]=row;save()
            if key in checks and not checks[key]['ok']:save('SOURCE_RESTRAINT_REST_ACTUAL_HOLD');return
        result['completed_static'].append(n);save();print('STATIC',n,flush=True)
    for n,s in new.items():
        if n in result['completed_motion']:continue
        bb=s.BoundBox
        for p in world.motion:
            if bbox_lower_bound(bb,A.BoundBox(*p['bounds'][0],*p['bounds'][1]))>=1.25:continue
            key=n+'|motion:'+p['name']+':'+str(p['pose'])
            if key in checks:continue
            tf=placement(p['r'],p['t']);local=s.copy();local.Placement=tf.inverse()*local.Placement
            gap=query.distance(local,world.rest[p['name']]);checks[key]=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25);save()
            if not checks[key]['ok']:save('SOURCE_RESTRAINT_MOTION_ACTUAL_HOLD');print(result['status'],key,flush=True);return
            if time.monotonic()-tick>220:save('PARTIAL_SOURCE_RESTRAINTS_SAVED');return
        result['completed_motion'].append(n);save();print('MOTION36',n,flush=True)
    save('SOURCE_FULL_RESTRAINTS_STATIC36_RECEIVED_ASSEMBLY_COMMON123_OPEN')
    print(result['status'],len(checks),result['worker_seconds'],flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--revision',choices=('r1','r2','r3','r4','r5'),default='r1');parser.add_argument('--local-only',action='store_true');args=parser.parse_args()
    if args.local_only:local_check(args.revision)
    else:main(args.revision)
