"""One complete source restraint proposal; typed fits, full prints and motion.

Save each exact pair and each whole-print proof. Resume missing work only;
do not replay MTA, source wire checks or successful unions after a slice.
"""
import argparse,gzip,hashlib,json,time,zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_source_restraint_plan import construct
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
    base,new,meta,groups,specs,bonds,*_=construct(revision)
    failures=[]
    for n,s in new.items():
        for other,t in {**base,**new}.items():
            if n==other or other in new and list(new).index(other)>list(new).index(n):continue
            limit=local_limit(n,other,meta,groups,specs,bonds)
            if limit is None:continue
            if bbox_lower_bound(s.BoundBox,t.BoundBox)>limit+1e-6:continue
            gap=s.distToShape(t)[0]
            common=s.common(t).Volume if limit==0 else 0.
            if gap<limit-1e-6 or common>1e-5:failures.append((n,other,round(gap,6),limit,round(common,6)))
    print('LOCAL_CHANGED_SOURCE',revision,len(new),'FAILURES',failures,flush=True)
    assert not failures


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
        base,new,nm,groups,specs,bonds,sr,_,_=construct(revision)
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
        result['print_union_proofs'][group]=dict(valid=valid,solids=len(s.Solids),envelope_mm=size,within250_margin=valid and max(size)<250,members=members)
        checks['wholeprint:'+group]=dict(ok=valid and max(size)<250,actual_whole_print_union=True)
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
    parser=argparse.ArgumentParser();parser.add_argument('--revision',choices=('r1','r2'),default='r1');parser.add_argument('--local-only',action='store_true');args=parser.parse_args()
    if args.local_only:local_check(args.revision)
    else:main(args.revision)
