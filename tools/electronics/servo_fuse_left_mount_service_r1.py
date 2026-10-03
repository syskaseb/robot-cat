"""Replace one entire left foot/bolt footprint, not the fixed splice roof.

R14: left foot moving upward hits FL cage roof at[-66,89,116,-60,95,118].
Keep the existing post; narrow the complete foot to its other side and put
the SAME M2x12/nut/washers on x=-51. Check support, tools and a conservative
continuous envelope of the changed foot against actual released owners.
"""
from pathlib import Path
from datetime import datetime,timezone
import sys,json,math,os
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-left-mount-service-r1'

def main():
    import FreeCAD as A
    import Part
    start=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True);assert not (OUT/'checks.json').exists()
    loader=ROOT/'tools/electronics/servo_fuse_bank_fixed_rr_lift_r14.py'
    raw=loader.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
    ctx=dict(__file__=str(loader),__name__='r14_definition');exec(compile(raw.rstrip()[:-len(tail)],str(loader),'exec'),ctx)
    code=ctx['code'];code=code[:code.index('    hits=[];errors=[];pairs=0')]+'    return owners,module,pins\n'
    code=code.replace('servo-fuse-bank-fixed-rr-lift-r14','servo-fuse-left-mount-service-r1')
    ns=dict(__file__=str(loader),__name__='read_current_released');exec(compile(code,str(loader),'exec'),ns)
    owners,module,pins=ns['main']();pins[loader.relative_to(ROOT).as_posix()]=sha(loader)
    V=A.Vector
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],V(*b[:3]))
    def cyl(x,y,z,r,h):return Part.makeCylinder(r,h,V(x,y,z))
    bank=module['BankLeft'];deck=owners['CandidateDeck']
    oldtool=box([-66.1,88.9,108.9,-47.9,97.1,113.1])
    footbox=[-59.5,89,109,-48,97,113];axis=[-51,92.5]
    hole=cyl(*axis,104.9,1.2,8.3);foot=box(footbox).cut(hole)
    remainder=bank.cut(oldtool);candidate=remainder.fuse(foot).cut(hole)
    connection=remainder.common(box([-59.5,89,112.9,-48,97,113.2])).Volume
    assert connection>0,connection
    cartpath=ROOT/'hardware/manufacturing/fixed-fastener-skus-r1/cart.json';pins[cartpath.relative_to(ROOT).as_posix()]=sha(cartpath)
    rows=json.loads(cartpath.read_text(encoding='utf-8'))['rows']
    bolt=next(r for r in rows if r['supplier_sku']=='0912A2-M020X012VISK')
    nut=next(r for r in rows if r['supplier_sku']=='SKL000381');washer=next(r for r in rows if r['supplier_sku']=='00125202')
    bd,nd,wd=[r['dimensions_mm'] for r in (bolt,nut,washer)];x,y=axis
    footprint=cyl(x,y,105.1,wd['OD']/2,3.8).cut(cyl(x,y,105,1.2,4.1))
    missing=footprint.cut(deck).Volume
    tip=113+wd['t']-bd['L'];underhead=113+wd['t'];nz=105-wd['t']-nd['H'];protrusion=nz-tip
    def ring(z):return cyl(x,y,z,wd['OD']/2,wd['t']).cut(cyl(x,y,z-.1,wd['ID']/2,wd['t']+.2))
    rad=nd['AF']/math.sqrt(3);pts=[V(x+rad*math.cos(k*math.pi/3),y+rad*math.sin(k*math.pi/3),nz) for k in range(6)]
    hardware=dict(Bolt=cyl(x,y,tip,1,bd['L']).fuse(cyl(x,y,underhead,bd['head_d']/2,bd['head_h'])),
        Washers=Part.makeCompound([ring(113),ring(105-wd['t'])]),
        Nut=Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(0,0,nd['H'])).cut(cyl(x,y,nz-.1,1,nd['H']+.2)))
    tools=dict(Allen=cyl(x,y,underhead+bd['head_h'],2,28),NutTool=cyl(x,y,nz-4,3.5,4).cut(cyl(x,y,nz-4.1,1.1,4.2)))
    hits=[];errors=[];pairs=0
    def check(phase,n,s,k,t):
        nonlocal pairs
        if not s.BoundBox.intersect(t.BoundBox):return
        pairs+=1
        try:
            c=s.common(t)
            if c.Volume>1e-5:hits.append(dict(phase=phase,part=n,owner=k,mm3=c.Volume,bounds_mm=[getattr(c.BoundBox,a) for a in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]))
        except Exception as e:errors.append(dict(phase=phase,part=n,owner=k,error=str(e)))
    print('LEFT_MOUNT_PREFLIGHT',os.getpid(),flush=True)
    # Small hardware is checked against the actual new drilled Deck and bank.
    drilled=deck.cut(hole)
    for n,s in dict(Foot=foot,**hardware).items():
        for k,t in owners.items():
            if k=='CandidateDeck':t=drilled
            check('installed_changed_mount',n,s,k,t)
        for k,t in module.items():
            if k=='BankLeft':
                if n=='Foot':continue
                t=candidate
            check('installed_changed_mount',n,s,k,t)
    for n,s in tools.items():
        for k,t in dict(owners,**module).items():
            if k=='CandidateDeck':t=drilled
            if k=='BankLeft':t=candidate
            check('released_tool_access',n,s,k,t)
    sweep=box([-59.5,89,109,-48,97,213])
    for k,t in owners.items():check('continuous_changed_foot_100mm','Foot',sweep,k,t)
    state=dict(valid=candidate.isValid(),solids=len(candidate.Solids),BOP=[str(v) for v in candidate.check(True) or []])
    valid=not hits and not errors and missing<1e-5 and protrusion>=bd['pitch'] and state['valid'] and state['solids']==1 and not state['BOP']
    candidate.exportBrep(str(OUT/'BankLeft_CANDIDATE.brep'));foot.exportBrep(str(OUT/'Foot_CANDIDATE.brep'))
    hole.exportBrep(str(OUT/'HoleTool.brep'))
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='LEFT_MOUNT_SERVICE_PREFLIGHT_CLEAR' if valid else 'LEFT_MOUNT_SERVICE_PREFLIGHT_REJECTED',selected=False,physical_pass=False,W5_complete=False,
        hits=hits,errors=errors,pairs=pairs,old_foot_removal_mm=[-66.1,88.9,108.9,-47.9,97.1,113.1],new_foot_mm=footbox,new_axis_mm=axis,old_axis_mm=[-63,92.5],
        washer_bearing_missing_mm3=missing,post_connection_mm3=connection,protruding_thread_mm=protrusion,state=state,
        added_prints=0,added_fasteners=0,added_wires=0,fastener_sources=[bolt,nut,washer],
        source_sha256=pins,script_sha256=sha(Path(__file__)),started_utc=start.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-start).total_seconds()))
    print('LEFT_MOUNT_PREFLIGHT_RESULT',valid,len(hits),missing,protrusion,hits,flush=True)
if __name__=='__main__':main()
