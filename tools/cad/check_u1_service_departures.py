"""Changed-only exact gate for two U1 service departures.

All eleven other full conductors and all28 grip lands are frozen. Reuse the
pinned30-pair current-service gate ONLY after verifying that its three hits
belong exclusively to the two replaced curves. BUS release remains upstream.
"""
import copy,json,math,time
from pathlib import Path
import FreeCAD as A
import Part
import plan_u1_service_departures as D
import plan_u1_power_grips as P
import plan_current_main_pi_wiring as M
from check_u1_socket_service import sweep
from check_u1_common_routes import self_screen
ROOT,OUT,SHA=P.ROOT,P.OUT,P.SHA


def inherited_gate(g):
    assert not g['errors'] and not g['reservation_resolutions']
    assert g['pairs']==30 and g['reused_prior_pairs']==372
    assert len(g['contacts'])==3 and all(h['b'] in ('XL01','XL09') for h in g['contacts'])
    for n,h in g['source_sha256'].items():assert SHA(ROOT/n)==h,n


def clipped_terminal(parts,radius):
    result=copy.deepcopy(parts);last=result[-1]
    assert last['kind']=='line' and last['end']==[37.5,-39.75,141.0]
    # Only the known axial engagement at the unbored reference entry face.
    delta=[a-b for a,b in zip(last['start'],last['end'])];length=math.sqrt(sum(x*x for x in delta))
    end=[b+(radius+.01)*a/length for a,b in zip(delta,last['end'])]
    result[-1]=M.line(last['start'],end)
    return result


def near(a,b,r):
    bounds=a.BoundBox;bounds.enlarge(r);return bounds.intersect(b.BoundBox)


def clipped_own_join(parts,bare,clearance):
    """Trim only the intended straight insulation-to-copper junction."""
    result=copy.deepcopy(parts)
    bare_ends=(bare[0]['start'],bare[-1]['end'])
    at_start=any(math.dist(result[0]['start'],q)<1e-7 for q in bare_ends)
    at_end=any(math.dist(result[-1]['end'],q)<1e-7 for q in bare_ends)
    assert at_start != at_end,'Expected exactly one shared terminal'
    index=0 if at_start else -1;segment=result[index]
    assert segment['kind']=='line' and segment['length_mm']>clearance
    start,end=segment['start'],segment['end'];u=[(b-a)/segment['length_mm'] for a,b in zip(start,end)]
    if at_start:start=[a+clearance*x for a,x in zip(start,u)]
    else:end=[b-clearance*x for b,x in zip(end,u)]
    result[index]=M.line(start,end)
    return result


def run():
    tick=time.monotonic();pf=OUT/'u1-service-departures-plan.json'
    p=json.loads(pf.read_text());assert p['status']=='TWO_OUTWARD_SERVICE_ROUTES_SAMPLED_ONLY_EXACT_GATE_OPEN'
    assert set(p['replacements'])=={'XL01','XL09'}
    for n,h in p['source_sha256'].items():assert SHA(ROOT/n)==h,n
    oldfile=OUT/'u1-current-service-checks.json';old=json.loads(oldfile.read_text());inherited_gate(old)
    frozen_file=OUT/'u1-common-wiring-plan.json';frozen=json.loads(frozen_file.read_text())
    reader,pins,targets,curves=P.latest_scene();pins.update((pf,oldfile,frozen_file))
    nativefile=OUT/'u1-power-grips-native.json';native=json.loads(nativefile.read_text());model=ROOT/native['native']
    assert SHA(model)==native['native_sha256'];pins.update((nativefile,model))
    for n in ('LowerCarrier001','E2Fixture','MAINGrip'):targets[n]=reader.shape(model,n)
    targets.update({'Power/'+n:s for n,s in P.allocation()['bands'].items()})
    targets.update(P.main_hardware())
    print('Service replacement scene',round(time.monotonic()-tick,3),flush=True)
    result=dict(status='PENDING',pairs=0,contacts=[],errors=[],reservation_resolutions=[],self_proximity={},
                lengths={},selected=False,physical_pass=False,E1_complete=False,W5_complete=False,
                inherited_service_pairs=30,inherited_original_service_pairs=372,
                unchanged_complete_conductors=11,all28_grip_lands_preserved=True)
    replacements={}
    for n,r in p['replacements'].items():
        oldroute=frozen['complete_routes'][n]
        assert r['parts'][0]==oldroute['parts'][0] and r['parts'][-1]==oldroute['parts'][-1],n
        c=P.wire(r['parts']);assert c.isValid(),n;replacements[n]=(c,r['radius']);curves.pop(n)
        points=[]
        for edge in c.Edges:
            pp=[list(v) for v in edge.discretize(Distance=.25)];points.extend(pp if not points else pp[1:])
        proximity=self_screen(points,2*r['radius'])
        if proximity:result['self_proximity'][n]=proximity
        assert abs(c.Length-r['guide_mm'])<max(.1,.001*r['guide_mm'])
        extra=36 if n=='XL01' else 6
        assert c.Length+extra<=r['nominal_blank_mm'] and r['nominal_blank_mm']<=600
        result['lengths'][n]=dict(exact_guide_mm=c.Length,nominal_blank_mm=r['nominal_blank_mm'],
                                actual_cut_mm=None,project_static_min_R_mm=r['min_fixed_radius_mm'])
    def distance(n,c,m,s,required,reservation=False):
        if not near(c,s,required):return
        result['pairs']+=1
        try:
            assert s.isValid(),m;gap=c.distToShape(s)[0]
            if gap<required-1e-5:
                result['reservation_resolutions' if reservation else 'contacts'].append(
                    dict(a=n,b=m,distance_mm=gap,required_mm=required))
        except Exception as e:result['errors'].append(dict(a=n,b=m,error=str(e)))
    for n,(c,r) in replacements.items():
        for m,s in targets.items():
            cc=P.wire(clipped_terminal(p['replacements'][n]['parts'],r)) if n=='XL09' and m=='G_TAIL' else c
            distance(n,cc,m,s,r)
        for m,(s,rr) in curves.items():
            cc=c
            if m.startswith(n+'/') and m.endswith('/bare'):
                cc=P.wire(clipped_own_join(p['replacements'][n]['parts'],frozen['bare'][m[:-5]]['parts'],r+rr+.01))
            distance(n,cc,m,s,r+rr)
        print('Changed full conductor',n,result['pairs'],len(result['contacts']),round(time.monotonic()-tick,3),flush=True)
    distance('XL01',replacements['XL01'][0],'XL09',replacements['XL09'][0],1.4)
    service=D.service_shapes(reader)
    ret=OUT/'U1SocketRetainer.FCStd'
    for n in reader.doc(ret):
        if n.startswith('Foam'):service[n]=sweep(reader.shape(ret,n))
    for n,(c,r) in replacements.items():
        for m,s in service.items():distance(n,c,'Service/'+m,s,r,m.startswith(('C1_','C2_')))
    result.update(status='TWO_ROUTES_STATIC_AND_U1_WITHDRAWAL_NOMINAL_CLEAR' if not any(result[k] for k in
                      ('contacts','errors','reservation_resolutions','self_proximity')) else 'SERVICE_REPLACEMENTS_REJECTED',
                  limitations=['Unchanged30/372 service pairs reused only with pinned sources and replaced-wire exception verified.',
                               'All sources absent; ENTIRE disconnected BUS cable removed first. Upstream H5/WAGO release still OPEN.',
                               'Self screen0.25mm and sampled curvature are not physical/continuous bend approval.',
                               'Changed E2 board-tail insulation, full wiring stock and whole selection still OPEN.'],
                  source_sha256={**reader.hashes,**{f.relative_to(ROOT).as_posix():SHA(f) for f in
                      pins|{Path(__file__),Path(D.__file__),ROOT/'tools/cad/check_u1_common_routes.py',ROOT/'tools/cad/check_u1_socket_service.py'}}},
                  worker_seconds=round(time.monotonic()-tick,3))
    (OUT/'u1-service-departures-checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='source_sha256'}),flush=True)


if __name__=='__main__':run()
