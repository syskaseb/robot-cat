"""Affected GPIO versus retained harness/population and complete insulation restraints.

Construct the whole changed interface once; refuse selection on a real hit.
No physical force, temperature or dimensional qualification is implied.
"""
import json,math
from pathlib import Path
import pi_wiring_complete_r1 as M
A,Part,ROOT=M.A,M.Part,M.ROOT
OUT=ROOT/'hardware/electronics/full-cat/pi-gpio-integrated-r1'
ROUTES=ROOT/'hardware/electronics/full-cat/pi-wiring-complete-r5'
AXES=[(-10.63,45),(-5.55,47),(2.07,49),(-8.09,51),(-.47,53)]
ENDS=[(91.54,28,151.5),(104.24,2,151.5),(91.54,-16,151.5),(-57.095,-7,149),(-57.095,18,151.5)]
GROUP_UPSTREAM=False
GROUP_TIE_Z=137.3
GROUP_MAX_Y=54.5
def main():
    OUT.mkdir(exist_ok=True);assert not (OUT/'checks.json').exists()
    names=['XL01','XL10','XL07','XL05','XL06'];adds={'Deck':[],'Carrier':[]};cuts={'Deck':[],'Carrier':[]};ties={};own={}
    for i,((x,y),(ex,ey,ez),n) in enumerate(zip(AXES,ENDS,names)):
        z=116+i*3.7
        if not GROUP_UPSTREAM:adds['Deck'].append([x+1.2,y-1.25,105,x+3.6,y+1.25,z+1.25])
        # A horizontal loop around the vertical wire and its independent post.
        a,c=x-.9,x+3.9;b,t=y-1.5,y+1.5
        bands=[[a-1.2,b-1.2,z-1.25,a,t+1.2,z+1.25],
               [c,b-1.2,z-1.25,c+1.2,t+1.2,z+1.25],
               [a,b-1.2,z-1.25,c,b,z+1.25],[a,t,z-1.25,c,t+1.2,z+1.25],
               [a-4.8,b-5.7,z-1.75,a,b-1.2,z+1.75]]
        if not GROUP_UPSTREAM:
            for k,bb in enumerate(bands):ties[f'{n}_Pi_tie_{k}']=M.box(bb);own[f'{n}_Pi_tie_{k}']=n
        adds['Carrier'].append([ex-1.4,ey-1.25,144,ex+1.4,ey+1.25,ez-.7])
        a,c=ex-3.1,ex+3.1;bottom=143.4;top=ez+.7
        for sx in (a,c):cuts['Carrier'].append([sx-.9,ey-1.5,143,sx+.9,ey+1.5,155])
        bands=[[a-.6,ey-1.25,bottom-1.2,a+.6,ey+1.25,top+1.2],
               [c-.6,ey-1.25,bottom-1.2,c+.6,ey+1.25,top+1.2],
               [a-.6,ey-1.25,top,c+.6,ey+1.25,top+1.2],
               [a-.6,ey-1.25,bottom-1.2,c+.6,ey+1.25,bottom],
               [a-5.4,ey-2.4,bottom-4.7,a-.6,ey+2.4,bottom-1.2]]
        for k,bb in enumerate(bands):ties[f'{n}_board_tie_{k}']=M.box(bb);own[f'{n}_board_tie_{k}']=n
    if GROUP_UPSTREAM:
        z=GROUP_TIE_Z;t=GROUP_MAX_Y
        adds['Deck'].append([28.8,43.5,105,30.2,t,z+1.25])
        bands=[[7.9,42.3,z-1.25,9.1,t+1.2,z+1.25],[30.5,42.3,z-1.25,31.7,t+1.2,z+1.25],
               [9.1,42.3,z-1.25,30.5,43.5,z+1.25],[9.1,t,z-1.25,30.5,t+1.2,z+1.25],
               [4.3,37.8,z-1.75,9.1,42.3,z+1.75]]
        for k,bb in enumerate(bands):ties[f'GPIO_bundle_tie_{k}']=M.box(bb);own[f'GPIO_bundle_tie_{k}']='GPIO_bundle'
    plan=dict(source='Saved R5 GPIO centreline construction; R31 prints retained until complete selection',
        adds_world=adds,cuts_world=cuts,ties=6 if GROUP_UPSTREAM else 10,tie_sku='111-02370 T18I',new_skus=0,new_screws=0,
        new_stls=0,native_export_pending=True,physical_pass=False,selected=False,
        assembly='Thread board-end ties from underside before PCB mounting/soldering; mark every brown lead at both ends. Fit Pi housing before tightening post ties. Cut post ties, unplug J8 and both USB plugs before removing tray. Board-end restraints remain fixed.',
        clamping='Only insulation, never bare copper, crimp/contact or solder joint. Ties are replaceable; retention/edge finish/PETG creep are phase2 trials.')
    (OUT/'plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
    owners={n:M.load(ROUTES/(n+'_DESIGN.brep')) for n in ('Deck','Carrier')}
    for name,s in list(owners.items()):
        s=s.multiFuse([M.box(b) for b in adds[name]])
        if cuts[name]:s=s.cut(Part.makeCompound([M.box(b) for b in cuts[name]]))
        assert s.isValid() and len(s.Solids)==1,name
        owners[name]=s;s.exportBrep(str(OUT/(name+'_DESIGN.brep')))
    C=ROOT/'hardware/cad/studies';E=ROOT/'hardware/electronics/full-cat'
    owners['Cover']=M.load(C/'head-yaw-end-restraints-r1/CoverYawEndSeat.brep')
    owners['PWM_Carrier_candidate']=M.load(C/'pwm-board-end-restraint-r1/CarrierPWMService_WORLD.brep')
    # Only material added by the independent PWM candidate can create a new
    # GPIO conflict; inherited Carrier body was checked above with Pi portals.
    old=M.load(C/'tail-central-carrier-r1/CarrierTailCentralPWM_WORLD.brep')
    owners['PWM_Carrier_candidate']=owners['PWM_Carrier_candidate'].cut(old)
    paths=list((E/'head-connected-feeds-r8').glob('XB*.brep'))+list((E/'head-connected-feeds-r8').glob('XS*.brep'))
    for folder in ('tail-central-routes-r3','tail-ground-direct-r1','pwm-connector-branch-r7','head-pwm-bare-takeoffs-r3'):
        paths += [p for p in (E/folder).glob('*DESIGN.brep') if p.stem!='CarrierTailPWMEntry_DESIGN']
    paths +=[E/p for p in ('aux-converter-routes-r5/XA02_DESIGN.brep','aux-converter-routes-r5/XA04_DESIGN.brep','aux-converter-routes-r2/XA03_DESIGN.brep','xa05-main-aux-return-r2/XA05_DESIGN.brep','xa06-ground-bridge-r1/XA06_DESIGN.brep','xb11-upstream-route-r3/XB11_DESIGN.brep')]
    for p in paths:owners[p.parent.name+'/'+p.stem]=M.load(p)
    wires={p.stem:M.load(p) for p in ROUTES.glob('XL*DESIGN.brep')}
    hits=[];count=0
    def check(n,s,on,o):
        nonlocal count
        if not s.BoundBox.intersect(o.BoundBox):return
        for i,ss in enumerate(s.Solids):
            for j,oo in enumerate(o.Solids):
                count+=1;v=ss.common(oo).Volume
                if v>1e-6:hits.append(dict(a=n,b=on,a_solid=i,b_solid=j,volume_mm3=v))
    for n,s in wires.items():
        for on,o in owners.items():check(n,s,on,o)
    for n,s in ties.items():
        s.exportBrep(str(OUT/(n+'.brep')))
        for on,o in owners.items():check(n,s,on,o)
        for wn,w in wires.items():
            if wn.startswith(own[n]+'_insulated') or (own[n]=='GPIO_bundle' and '_insulated_' in wn):continue # own insulation clamping only
            check(n,s,wn,w)
    for i,(n,s) in enumerate(ties.items()):
        for on,o in list(ties.items())[i+1:]:
            if n.rsplit('_',1)[0]==on.rsplit('_',1)[0]:continue # joined loop/head
            check(n,s,on,o)
    result=dict(status='INTEGRATED_CANDIDATE' if not hits else 'INTEGRATED_OPEN',hits=hits,affected_pairs=count,
        new_stls=0,new_ties=6 if GROUP_UPSTREAM else 10,CP_PI_complete=False,physical_pass=False,
        source_sha256={p.relative_to(ROOT).as_posix():M.sha(p) for p in paths},
        remaining=['Native/export and one selected set','Power/USB/caddy and service','Actual tie/OD/insert height trials in phase2'])
    (OUT/'checks.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    geo=[]
    for n,s in {**wires,**ties,**{k:v for k,v in owners.items() if k in ('Deck','Carrier')}}.items():
        vs,fs=s.tessellate(.4);geo.append(dict(name=n,vertices=[list(v) for v in vs],triangles=fs))
    (OUT/'preview-geometry.json').write_text(json.dumps(geo)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='source_sha256'}),flush=True)
if __name__=='__main__':main()
