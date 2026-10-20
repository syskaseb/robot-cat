"""One joint BAT/F0/POST proposal, no factory-length or assembly PASS.

The selected FHAC0002ZXJ has nominal89.5mm leads, not the historical
30/70mm cuts or older generic102mm. Body shape/ports/OD remain nominal
planning datums. Test both polarities and both F0 ends before mount detail.
"""
import hashlib,json,math,time,zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_main_hung_context import compose
from receive_feline_existing_lower_caps import current
from receive_feline_rrp_shared_height import load
from plan_feline_n01_shared import pipe
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from plan_feline_usb_service_bight import outer_margin
from feline_atomic_save import save_json


def path(p,t,steps,R):
    p=A.Vector(*p);t=A.Vector(*t);parts=[];length=0
    for kind,value in steps:
        start=p
        if kind=='line':
            p=p+t*value;length+=value
            parts.append(dict(kind='line',start=list(start),end=list(p)))
        else:
            n=A.Vector(*value);assert abs(n.dot(t))<1e-7
            p=start+R*t+R*n;mid=start+R*math.sin(math.pi/4)*t+R*(1-math.cos(math.pi/4))*n
            parts.append(dict(kind='arc',start=list(start),mid=list(mid),end=list(p),R_mm=R))
            t=n;length+=R*math.pi/2
    return dict(parts=parts,length_mm=length,end=list(p),end_tangent=list(t),R_mm=R)


def pose(s,centre,rotation,target):
    p=A.Placement(A.Vector(*target),rotation)*A.Placement(A.Vector(*centre),A.Rotation()).inverse()
    result=s.copy();result.Placement=p*result.Placement
    assert result.isValid() and result.Solids
    return result,p


def main():
    tick=time.monotonic();dest=OUT/'n01-BAT-F0-vertical-joint.json'
    assert not dest.exists(),'Receive saved candidate; no unchanged rerun'
    world,parts,meta,pins,docs=compose();print('CURRENT_WORLD_LOADED',round(time.monotonic()-tick,3),flush=True)
    mf=OUT/'n01-MTA-low-stop-cradles.json';mr=json.loads(mf.read_text())
    receipt=mf.with_name(mf.stem+'-scene.json');received=json.loads(receipt.read_text())
    assert not received['failures'] and len(received['completed_static'])==len(received['completed_motion'])==72
    for record in (mr,received):
        for p,h in record['source_sha256'].items():assert sha(ROOT/p)==h,p
    effective={n:s for n,s in parts.items() if n not in mr['retired']};effective.update(load(mr))
    _,ends,efiles=current();ends={r['id']:r for r in ends}
    old={'F0':'Ref_Material_F0_CP2_0_0','XT60':'Ref_Material_XT60_CP2_0_0','POST':'Ref_Material_PostF0Splice_CP2_0_0'}
    # Derive the shared source geometry from quarter-circle R12.4 and
    # the whole rear F0 bay, not from independent arbitrary wire targets.
    R=12.4;f0centre=[166.,0.,9.];xtmouth=[f0centre[0]-R-3,0.,-38.5]
    actors={};transforms={}
    actors[old['F0']],transforms['F0']=pose(parts[old['F0']],[68,0,-13.75],A.Rotation(A.Vector(1,1,0),A.Vector(0,0,1)),f0centre)
    actors[old['XT60']],transforms['XT60']=pose(parts[old['XT60']],[142.999996948242,0.000003051758,-35],A.Rotation(),[xtmouth[0]-11.95,0,-35])
    f0in=list(transforms['F0'].multVec(A.Vector(*ends['W075/retained0/end']['point_mm'])))
    f0out=list(transforms['F0'].multVec(A.Vector(*ends['W076/retained0/start']['point_mm'])))
    assert (A.Vector(*f0in)-A.Vector(166,0,-16.5)).Length<1e-4
    positive=path(xtmouth,[1,0,0],[('line',3),('turn',[0,0,1]),('line',f0in[2]-xtmouth[2]-R)],R)
    assert (A.Vector(*positive['end'])-A.Vector(*f0in)).Length<1e-4
    # The second factory lead turns toward the existing rear WAGO bay;
    # port2 is reserved jointly, not silently left in its old pose.
    output=path(f0out,[0,0,1],[('line',5.85),('turn',[0,-1,0])],R)
    post1=output['end'];postcentre=[post1[0],post1[1]-9.5,post1[2]-1.5]
    actors[old['POST']],transforms['POST']=pose(parts[old['POST']],[143.000000762939,-35,42],A.Rotation(A.Vector(0,0,1),180),postcentre)
    post2=list(transforms['POST'].multVec(A.Vector(*ends['W076/retained1/start']['point_mm'])))
    assert (transforms['POST'].multVec(A.Vector(*ends['W076/retained0/end']['point_mm']))-A.Vector(*post1)).Length<1e-4
    groundmouth=list(transforms['XT60'].multVec(A.Vector(*ends['W001/retained0/start']['point_mm'])))
    ground=path(groundmouth,[1,0,0],[('line',3),('turn',[0,1,0]),('turn',[0,0,1]),('line',9)],R)
    custom=path(post2,[0,1,0],[('line',.25),('turn',[-1,0,0]),('line',9)],25.2)
    recipes={'W075_factory':positive,'W076_factory':output,'W001_ground_prefix':ground,'W076_custom_prefix':custom}
    for n,r in recipes.items():actors[n]=pipe(r['parts'],2.1 if n=='W076_custom_prefix' else 1.55)
    # Supplied length minus strip/rework. Tolerance remains an explicit
    # delivery gate, never a claimed manufacturer's guaranteed minimum.
    budgets={n:dict(nominal_catalog_mm=89.5,curve_mm=recipes[n]['length_mm'],
        strip_mm=8.73 if n=='W075_factory' else 11.,rework_mm=10.,
        manufacturer_tolerance_unknown=True) for n in ('W075_factory','W076_factory')}
    for b in budgets.values():b['nominal_unused_mm']=b['nominal_catalog_mm']-b['curve_mm']-b['strip_mm']-b['rework_mm'];assert b['nominal_unused_mm']>=0
    for n in old.values():effective.pop(n)
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (mf,ROOT/mr['bundle'],receipt,ROOT/received['pair_rows'],*efiles,Path(__file__))})
    result=dict(status='RUNNING_JOINT_BAT_F0_PROPOSAL',source_sha256=pins,recipes=recipes,factory_length_budgets=budgets,
        actual_supplier_page='https://www.littelfuse.com/products/fuses-overcurrent-protection/fuse-holders-fuse-blocks-accessories/fuse-holders/in-line-fuse-holders/ato-fhac/fhac0002zxj',
        catalog_nominal_not_guaranteed_tolerance=True,selected_SKUs_changed=False,geometry={},checks={},failures=[],
        outer={},native_changed=False,N01_complete=False,physical_pass=False,
        missing=['independent full grips and roots','whole assembly/tool access','remaining shared123 capacity','sampled motion of changed proposal'],
        nominal_datums_NOT_supplier_verified=True,unchanged_MTA_overlay_explicit_not_canonical=True,
        historical920_NOT_extra_BAT_wire=True)
    archive=dest.with_suffix('.breps.zip')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for i,(n,s) in enumerate(actors.items()):
            raw=s.exportBrepToString().encode();entry=str(i)+'.brep';z.writestr(entry,raw)
            result['geometry'][n]=dict(entry=entry,sha256=hashlib.sha256(raw).hexdigest())
    result.update(bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive))
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3);save_json(dest,result)
    save();query=SolidQueries()
    # Receive all conflicts for this single frozen hypothesis, not one
    # witness followed by another almost identical construction.
    for n,s in actors.items():
        result['outer'][n]=outer_margin(s,docs['outer'])
        if not result['outer'][n]['ok']:result['failures'].append(n+'|outer')
        for m,t in effective.items():
            if bbox_lower_bound(s.BoundBox,t.BoundBox)>=1.25:continue
            a=s;b=t
            if m==world.bus['name']:
                a=s.copy();a.Placement=docs['inverse']*a.Placement;b=world.bus['original']
            if not b.Solids:
                result['checks'][n+'|'+m]=dict(ok=False,unreceived_wire_or_shell_profile=True);result['failures'].append(n+'|'+m);continue
            gap=query.distance(a,b);row=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
            if not row['ok']:
                _,points,_=a.distToShape(b);row['witness_mm']=[[list(x),list(y)] for x,y in points[:1]]
                result['failures'].append(n+'|'+m)
            result['checks'][n+'|'+m]=row
            if len(result['checks'])%10==0:save()
        save();print('RECEIVED',n,'failures',len(result['failures']),round(time.monotonic()-tick,3),flush=True)
    result['status']='JOINT_BAT_F0_REJECTED_NO_MOUNT_DETAIL' if result['failures'] else 'JOINT_BAT_F0_STATIC_PROPOSAL_ONLY_INTERNAL_GRIPS_MOTION_TOOLS_OPEN'
    save();print(result['status'],result['failures'],result['worker_seconds'],flush=True)


if __name__=='__main__':main()
