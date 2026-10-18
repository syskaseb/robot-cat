"""Shared central and vertical galleries for all three constrained power kits.

Not a third isolated source-clock or case offset: P_REAR/G1/P_FRONT full
cases, all bends, caps, heads and roots vary together in the24-node choice.
All other received domains remain choices, not prematurely frozen positions.
"""
import hashlib
import itertools
import json
import subprocess
import time
from pathlib import Path
import numpy as np
from scipy.interpolate import RegularGridInterpolator
from scipy.spatial import cKDTree
from feline_flat_station_templates import build,compatible,compact,to_box,self_wire_gap,pier_supported,shared_rail_bounds
from feline_flat_s1_templates import candidates,source_pair_compatible

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'
PRIOR='48d7faca'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    tick=time.monotonic();dest=OUT/'n01-coupled-power-galleries.json';assert not dest.exists()
    oldpath=OUT/'n01-flat20-domains-joint.json';old=json.loads(oldpath.read_text())
    planfile=OUT/'n01-flat-station-architecture.json';plan=json.loads(planfile.read_text())
    fieldproof=OUT/'n01-flat20-field-joint.json';proof=json.loads(fieldproof.read_text())
    fieldfile=ROOT/proof['field'];assert sha(fieldfile)==proof['field_sha256']
    helper=ROOT/'tools/cad/feline_flat_station_templates.py'
    for n,h in old['source_sha256'].items():
        if n!=helper.relative_to(ROOT).as_posix():assert sha(ROOT/n)==h,n
    oldcode=subprocess.run(['git','show',PRIOR+':'+helper.relative_to(ROOT).as_posix()],cwd=ROOT,check=True,capture_output=True).stdout
    legacy={'__file__':str(helper)};exec(compile(oldcode.decode(),'<pinned prior template>','exec'),legacy)
    domains={};equivalent=0
    for ref,rows in old['domains'].items():
        station=next(s for s in plan['stations'] if s['ref']==ref);domains[ref]=[]
        for row in rows:
            args=(station,row['family'],row['side'],row['departure_X'],row['centre_mm'][0])
            oldm=legacy['build'](*args);m=build(*args)
            for k in ('points','radii','types','bounds'):assert np.array_equal(oldm[k],m[k]),(ref,k)
            assert len(m['boxes'])==len(oldm['boxes'])
            for a,b in zip(m['boxes'],oldm['boxes']):assert a['kind']==b['kind'] and np.array_equal(a['bounds'],b['bounds'])
            m['numeric_score']=row['numeric_score'];domains[ref].append(m);equivalent+=1
    sourcechoices,sourcepins=candidates()
    for ref,rows in old['S1_joint_domains'].items():
        bykey={(r['clock_target_degrees'],r['first_mm'],r['bend_degrees']):r for r in sourcechoices[ref]}
        domains[ref]=[]
        for row in rows:
            m=bykey[(row['clock_target_degrees'],row['first_mm'],row['bend_degrees'])]
            m['numeric_score']=row['numeric_score'];domains[ref].append(m)
    field=np.load(fieldfile,allow_pickle=False);axes=[field[k] for k in ('x','y','z')]
    fields={k:RegularGridInterpolator(axes,field[k+'_distance'],bounds_error=False,fill_value=0)
            for k in ('material','reservation','curve_hold','motion36','outer')}
    inside=RegularGridInterpolator(axes,field['inside'].astype(float),bounds_error=False,fill_value=0)
    service=RegularGridInterpolator(axes,field['service'].astype(float),method='nearest',bounds_error=False,fill_value=1)
    query=np.stack(np.meshgrid(*axes,indexing='ij'),axis=-1)
    for label in ('P_SYS','W043','S1'):
        values=cKDTree(field[label+'_context']).query(query.reshape(-1,3),workers=1)[0].reshape(query.shape[:3])
        fields[label+'_context']=RegularGridInterpolator(axes,values,bounds_error=False,fill_value=0)
    screen=dict(material=.2,reservation=.2,motion36=.2,outer=1,curve_hold=3.35,
                P_SYS_context=.2,W043_context=.2,S1_context=.2)
    rails=shared_rail_bounds()
    result=dict(status='RUNNING_COUPLED_POWER_GALLERIES',selected=False,N01_complete=False,physical_pass=False,
        changed_cause='Shared lateral central void and distinct vertical fan galleries for all3large power kits after coupled P_REAR/G1 conflict; all24nodes remain joint choices.',
        source_sha256={**proof['source_sha256'],**sourcepins,**{p.relative_to(ROOT).as_posix():sha(p) for p in
            (oldpath,planfile,fieldproof,fieldfile,helper,Path(__file__),OUT/'n01-flat20-coupled-conflict.json',OUT/'n01-flat20-actual-clamp-kits.json')}},
        prior_domain_geometry_equivalent_count=equivalent,old_default_geometry_exact_array_equivalence=True,
        reused_S1_source_domains={n:len(v) for n,v in domains.items() if n not in old['domains']},
        project_loose_numeric_screens_mm=screen,actual_airgaps_not_changed=True,
        numeric_proposal_not_solid_or_motion_qualification=True,
        all24actual_clamp_parts_stack_tools_and_carrier_root_connections_STILL_OPEN=True,
        full123portions246ends_and_materials_STILL_OPEN=True,
        domains={},new_domain_receipts=[],joint_assignment=None,errors=[])
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    def gate():
        if time.monotonic()-tick>180:raise TimeoutError('180s common power-gallery budget; completed source domains retained')
    def scores(template,xx):
        p0=template['points'];rr=template['radii'];tt=template['types'];count=len(p0);out=[]
        for start in range(0,len(xx),8):
            gate();cc=np.array([[x,0,0] for x in xx[start:start+8]]);p=p0[None,:,:]+cc[:,None,:];flat=p.reshape(-1,3)
            margins=np.full(len(cc),1e6);layers=['none']*len(cc)
            for label,interp in fields.items():
                val=(interp(flat).reshape(len(cc),count)-rr-screen[label]).min(1)
                for i,v in enumerate(val):
                    if v<margins[i]:margins[i]=float(v);layers[i]=label
            mask=inside(flat).reshape(len(cc),count).min(1)<.999
            margins[mask]=-1e6
            sv=service(flat).reshape(len(cc),count).max(1)
            for i,v in enumerate(sv):
                if v>.5 and margins[i]>=0:margins[i]=-.01;layers[i]='ATO_service'
            for rail in rails:
                for i in range(len(cc)):
                    val=float(np.min(to_box(p[i,tt!=3],rail)-rr[tt!=3]-.2))
                    if val<margins[i]:margins[i]=val;layers[i]='finite_common_rail'
            out.extend(zip(margins,layers))
        return out
    save()
    try:
        for ref in ('P_REAR','G1','P_FRONT'):
            station=next(s for s in plan['stations'] if s['ref']==ref)
            pitch=station['flat_dimensions_pitch_departure_thickness_mm'][0]
            # Same actual P0 inner-face datum for all three kits, not hand
            # offsets to one failing wire. Existing standard row also retained.
            abs_y=27-pitch/2-1.25;assert abs_y>0
            tested=0;received=0;rejected={};oldcount=len(domains[ref])
            for side,departure,y,bmode in itertools.product((-1,1),(-1,1),(0,abs_y,19.5),
                    ('OUTWARD_CONCENTRIC','UP_PARALLEL','INWARD_UP_PARALLEL')):
                if y==19.5 and bmode=='OUTWARD_CONCENTRIC':continue #Already received, not repeated.
                template=build(station,'inner',side,departure,0,side*y,bmode)
                if self_wire_gap(template)<-1e-6:
                    rejected['intrinsic_full_jacket_gap']=rejected.get('intrinsic_full_jacket_gap',0)+1;continue
                xx=list(range(-112,149,12))
                for x,(score,layer) in zip(xx,scores(template,xx)):
                    tested+=1
                    if score<0:rejected[layer]=rejected.get(layer,0)+1;continue
                    m=build(station,'inner',side,departure,x,side*y,bmode)
                    if not pier_supported(m):rejected['finite_pier_missing']=rejected.get('finite_pier_missing',0)+1;continue
                    m['numeric_score']=float(score);domains[ref].append(m);received+=1
            result['new_domain_receipts'].append(dict(ref=ref,new_tested=tested,new_received=received,
                old_domains_reused=oldcount,inner_void_datum_abs_Y_mm=abs_y,rejected=rejected))
            result['domains'][ref]=[compact(m) for m in domains[ref]];save()
            print(ref,'new gallery domains',received,'prior',oldcount,flush=True)
        memo={};visited=0
        def pair(a,i,b,j):
            key=(a,i,b,j) if a<b else (b,j,a,i)
            if key not in memo:
                aa,bb=domains[a][i],domains[b][j]
                memo[key]=source_pair_compatible(aa,bb) if aa.get('source_ring') or bb.get('source_ring') else compatible(aa,bb)
            return memo[key]
        def solve(chosen,remaining):
            nonlocal visited
            gate();visited+=1
            if visited>10000:raise TimeoutError('10000 common nodes; retain domains')
            if not remaining:return chosen
            viable={n:[i for i in rows if all(pair(n,i,a,j) for a,j in chosen.items())] for n,rows in remaining.items()}
            if any(not v for v in viable.values()):return None
            name=min(viable,key=lambda n:len(viable[n]));other={n:v for n,v in viable.items() if n!=name}
            for i in viable[name]:
                value=solve({**chosen,name:i},other)
                if value:return value
            return None
        assignment=solve({}, {n:list(range(len(v))) for n,v in domains.items()})
        result.update(joint_assignment=assignment,search_nodes=visited,numeric_mutual_pairs=len(memo))
        result['domains']={n:[compact(m) for m in v] for n,v in domains.items()}
        if assignment:
            result['chosen_templates']={n:compact(domains[n][i]) for n,i in assignment.items()}
            result['status']='COUPLED24_NUMERIC_GALLERY_PROPOSAL_REQUIRES_EXACT_WHOLE_RECEIVER'
        else:result['status']='COUPLED24_GALLERY_FAMILY_HAS_NO_JOINT_ASSIGNMENT'
    except Exception as e:result['errors'].append(repr(e));result['status']='PARTIAL_COUPLED_POWER_GALLERIES'
    save();print(json.dumps({k:result[k] for k in ('status','worker_seconds','joint_assignment','errors')}),flush=True)


if __name__=='__main__':main()
