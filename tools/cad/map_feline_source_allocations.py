"""All-neighbour map of inherited local source geometry, no route trials.

Accept the already loaded immutable world so one source-family inspection
does not rebuild it for every question. Results never select N01 or a part.
"""
import hashlib,json,time,zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from plan_feline_pi_root_access import profile_gap


def receive(world,fixed,meta,pins,docs):
    tick=time.monotonic();sf=OUT/'n01-current-source-MTA-boundary-overlay.json';r=json.loads(sf.read_text())
    for p,h in r['source_sha256'].items():assert sha(ROOT/p)==h,p
    dest=OUT/'n01-inherited-local-source-neighbor-map.json'
    assert not dest.exists(),'Read existing all-neighbour map instead of repeating it'
    archive=ROOT/r['U1_local_bundle'];assert sha(archive)==r['U1_local_bundle_sha256'];actors={};kinds={}
    with zipfile.ZipFile(archive) as z:
        for row in r['U1_local_geometry']:
            raw=z.read(row['entry']);assert hashlib.sha256(raw).hexdigest()==row['sha256'];s=Part.Shape();s.importBrepFromString(raw.decode())
            actors[row['name']]=s;kinds[row['name']]=row
    checks={};query=SolidQueries();done=[];sources={**pins,sf.relative_to(ROOT).as_posix():sha(sf),Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))}
    def save():
        result=dict(status='INHERITED_LOCAL_SOURCE_ALL_NEIGHBORS_DIAGNOSIS_NOT_N01',source_sha256=sources,
            actual_geometry_hashes={n:hashlib.sha256(s.exportBrepToString().encode()).hexdigest() for n,s in actors.items()},
            completed=done,checks=checks,failures={k:v for k,v in checks.items() if not v['ok']},
            intended_holes_NOT_manufacturer_pinout_or_pad_fit=True,N01_complete=False,native_changed=False,
            physical_pass=False,worker_seconds=round(time.monotonic()-tick,3))
        save_json(dest,result)
    for n,s in actors.items():
        for other,t in {**fixed,**actors}.items():
            if n==other or other in actors and list(actors).index(other)>list(actors).index(n):continue
            a=kinds[n];b=kinds.get(other,meta.get(other,{}));mate=None;minimum=1.25
            if other in kinds and a['wire']==b['wire']:mate='same selected bare/jacket seam';minimum=0.
            elif other=='Ref_Material_PWM1608NominalPCB_0_0':
                mate='named selected carrier solder hole in nominal PCB, physical fit open' if a['kind']=='bare' else 'own insulated pad departure'
                minimum=0. if a['kind']=='bare' else .2
            elif a['kind']=='wire' and b.get('kind') in ('wire','proposal_wire','actual_wire','curve_profile_reservation'):minimum=.2
            if bbox_lower_bound(s.BoundBox,t.BoundBox)>minimum+1e-6:continue
            aa=s;bb=t
            if other==world.bus['name']:aa=s.copy();aa.Placement=docs['inverse']*aa.Placement;bb=world.bus['original']
            if not bb.Solids:
                radius=b.get('nominal_profile_radius_mm') or b.get('radius_mm')
                row=profile_gap(aa,bb,radius,minimum) if radius else dict(ok=False,unreceived_profile=True)
            else:
                gap=query.distance(aa,bb);row=dict(ok=gap>=minimum-1e-6,gap_mm=gap,minimum_mm=minimum,intended_mate=mate)
                if not row['ok']:row['witness_mm']=[[list(x),list(y)] for x,y in aa.distToShape(bb)[1][:1]]
            checks[n+'|'+other]=row
            if not row['ok']:print('WITNESS',n,other,row,flush=True)
        done.append(n);save();print('MAPPED',n,flush=True)
    save();print('ALL_LOCAL_SOURCES_MAPPED',len(done),len(checks),round(time.monotonic()-tick,3),flush=True)
