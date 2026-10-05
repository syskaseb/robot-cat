"""Complete W001/W003 and straight W061 in the facing ground plan.

Preserve XT60 and BUS source datums; short diagonal BUS corridor avoids the
previous Y65 detour. Other ground wires and native mounts remain obligations.
"""
from datetime import datetime,timezone
import json,re,math
from pathlib import Path
from servo_fuse_inputs_r1 import save,sha
from w5_ground_bridge_plan import ports,ROOT
from w5_ground_network_plan import profile
from w5_s1_source_layout_r2 import CentreLine
from w5_s1_source_layout_r1 import add,mul

OUT=ROOT/'hardware/electronics/full-cat/w5-central-ground-routes-r1'

def recipes():
    p=ports(); rows=[]
    bus=ROOT/'hardware/electronics/full-cat/w5-bus-pair-r52-r4/intent.json'
    src=json.loads(bus.read_text(encoding='utf-8'))['source_lead_datums']['W003']
    for wire,port,n in [('W001','G1.1',[0,0,-1]),('W003','G2.4',[0,0,1])]:
        datum=p[port];c=CentreLine(datum['point_mm'],datum['outward_axis']);rad=profile(wire)['radius_mm']
        c.line(add(c.p,mul(c.t,6)));c.arc(n,radius=rad);c.line(add(c.p,mul(c.t,6)))
        t=c.p
        mid=([[55.5,75,70],[55.5,60,70],[t[0],t[1],70],t] if wire=='W001' else
            [src,[src[0],src[1],140],[t[0],t[1],140],t])
        rows.append(dict(wire=wire,a=dict(edges=c.edges),middle=mid,lead_in=True,
            radius_mm=rad,embedded_allowance_mm=19 if wire=='W001' else 11,
            trial_reserve_mm=10 if wire=='W001' else 30,limit_mm=150 if wire=='W001' else 300))
    return rows

def main():
    import FreeCAD as A,Part
    from w5_ground_network_r1 import from_recipe
    from w5_ground_entries_r1 import owners,RECEIVED
    from w5_exact_separation import separated
    from w5_ground_joint_layout_r4 import attached_ends
    begin=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists()
    fixed,pins=owners(A,Part,json.loads(RECEIVED.read_text(encoding='utf-8')))
    graph=ROOT/'hardware/electronics/power-platform/wiring-p0.json'
    affected={r['wire'] for r in attached_ends(json.loads(graph.read_text(encoding='utf-8')))}
    obligations=[]
    for k in list(fixed):
        if k.startswith(('ReceivedD/','ReceivedV/','R53BUS/G2shared/')) or any(re.search(r'(?<![A-Za-z0-9])'+re.escape(w)+r'(?![A-Za-z0-9])',k) for w in affected):
            obligations.append(k);del fixed[k]
    bridge=ROOT/'hardware/electronics/full-cat/w5-ground-facing-plan-r1/W061_BRIDGE_WORLD.brep'
    built={'W061':Part.read(str(bridge))};pins.append(bridge)
    lengths=[];files=[];hits=[];native=[];errors=[]
    for row in recipes():
        path,shape=from_recipe(A,Part,row);wire=row['wire'];built[wire]=shape
        for suffix,obj in [('WORLD',shape),('CENTERLINE_WORLD',path)]:
            dest=OUT/(wire+'_'+suffix+'.brep');obj.exportBrep(str(dest));files.append(dest)
        nominal=path.Length+row['embedded_allowance_mm']
        lengths.append(dict(wire=wire,path_mm=path.Length,nominal_mm=nominal,
            trial_blank_mm=math.ceil((nominal+row['trial_reserve_mm'])/10)*10,
            fits_limit=nominal<=150 if wire=='W001' else nominal+30<=300))
    printed={'SourceDeck','SourceCarrier','SourceCover','SourcePlatform','SourceBankLeft','BankRight','SourceWestHood','SourceEastHood'}
    for key,shape in built.items():
        for owner,other in [*fixed.items(),*((n,s) for n,s in built.items() if n<key)]:
            if owner in ('G1_NEW_BODY','G2_NEW_BODY') or not shape.BoundBox.intersect(other.BoundBox):continue
            if owner in printed:
                native.append(dict(wire=key,owner=owner,bounds_overlap_only=True));continue
            try:
                vol=sum(a.common(b).Volume for a in shape.Solids for b in other.Solids
                    if a.BoundBox.intersect(b.BoundBox) and not separated(a,b))
                if vol>1e-6:hits.append(dict(wire=key,owner=owner,volume_mm3=vol))
            except Exception as e:errors.append(dict(wire=key,owner=owner,error=str(e)))
        print('CENTRAL',key,len(hits),len(errors),flush=True)
    finish=datetime.now(timezone.utc)
    pins.extend((Path(__file__),graph,ROOT/'tools/electronics/w5_ground_bridge_plan.py',ROOT/'tools/electronics/w5_ground_network_r1.py',ROOT/'tools/electronics/w5_ground_network_plan.py'))
    save(OUT/'checks.json',dict(status='THREE_CENTRAL_GROUND_ROUTES_UNSELECTED',lengths=lengths,hits=hits,errors=errors,
        native_checks_pending=native,replacement_obligations=obligations,other_18_ground_routes_open=True,
        all_36_leg_routes_open=True,native_mounts_ready=False,selected=False,W5_complete=False,physical_pass=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in dict.fromkeys(pins)},
        files={p.relative_to(ROOT).as_posix():sha(p) for p in files},
        started_utc=begin.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-begin).total_seconds()))
    print('CENTRAL_RESULT',lengths,len(hits),len(errors),flush=True)

if __name__=='__main__':main()
