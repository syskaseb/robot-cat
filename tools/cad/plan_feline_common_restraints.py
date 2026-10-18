"""One full-material retention proposal, before native details or route middles.

Four9wire open cuffs/arms/straps, two power combs/roots,12case retainers,
larger24existing heads and all8lower module driver channels in one scene.
All new geometry is explicitly provisional planning material, not selected.
"""
import json
import math
import sys
import time
import zipfile
from pathlib import Path
import FreeCAD as A
import Part
import numpy as np
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import OUT,STAGES
from check_feline_all_current_lands import near
from check_feline_leg_body import placement
from check_feline_shared_space import tube_prefix


def main():
    coherent='--coherent-retention' in sys.argv
    tick=time.monotonic();dest=OUT/('n01-common-restraint-material-r2.json' if coherent else 'n01-common-restraint-material.json');assert not dest.exists()
    paths={k:OUT/n for k,n in dict(scene='n01-full-material-scene.json',lower='n01-lower-bay-world-probe.json',
        packet='n01-current-endpoint-packet-r3.json',lands='n01-reconciled-port-contracts-gate.json',
        qualified='n01-reconciled-port-contracts-qualified.json',motion='motion-layout.json').items()}
    p={k:json.loads(f.read_text()) for k,f in paths.items()}
    prior=json.loads((OUT/'n01-common-restraint-material.json').read_text()) if coherent else None
    report=dict(status='RUNNING_SHARED_RETENTION_MATERIAL',selected=False,N01_complete=False,physical_pass=False,
        native_changed=False,contacts=[],errors=[],outside=[],wall_failures=[],planned_unions=[],
        mating_pairs=[],root_unions=[],pairs=0,poses=[],driver_conflicts=[],parts=[],
        changed_cause='Whole cuff/comb channels+positive roots+12case retention+larger heads. No case or wire microshifts. Deep inline service on bench, not74routine WAGO disconnects.',
        project_fit_gates=['5x5x4heads based on retained4.8x4.5x3.5model, not supplier guarantee',
            'Nominal groove/jacket gap0.2mm and removable caps0.25mm, delivered fit remainsphase2',
            '0.2mm housing-to-insulatingstrap adjacency only; general bought-part/wire clearance1.25mm',
            'Cap levers accessible after removing cap on bench; not an in-situ quick-service claim'],
        quantities_candidate=dict(new_case_M2x12=16,new_case_M2nuts=16,new_wire_and_case_ties=10,
            existing_lower_wire_ties=24,new_electrical_parts=0,stock_selected=False),
        full89routes_headtail_USB_tools_skin_native_stock_open=True,
        source_sha256={f.relative_to(ROOT).as_posix():sha(f) for f in (*paths.values(),Path(__file__))})
    def save():
        report['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    def gate():
        if time.monotonic()-tick>300:raise TimeoutError('300s bounded whole-retention proposal; keep receipt')
    save()
    scene={};meta={}
    for key in ('scene','lower'):
        bundle=ROOT/p[key]['bundle'];assert sha(bundle)==p[key]['bundle_sha256']
        with zipfile.ZipFile(bundle) as z:
            for row in p[key]['parts']:
                if row.get('role')=='CurrentCassette':continue
                s=Part.Shape();s.importBrepFromString(z.read(row['entry']).decode('utf-8'))
                assert row['name'] not in scene
                scene[row['name']]=s;meta[row['name']]=row
    ends={e['id']:e for e in p['packet']['endpoints']};recipes=p['lands']['land_recipes']
    # Integrate the already received whole POST_F0 pose and nominal Pi mould.
    pose=p['packet']['changed_scene_groups']['POST_F0'];mat=A.Matrix()
    for i in range(3):
        for j in range(3):setattr(mat,f'A{i+1}{j+1}',pose['relative_rotation_rows'][i][j])
    c=A.Vector(*pose['centre_mm']);rot=A.Rotation(mat);tf=A.Placement(c-rot.multVec(c),rot)
    for n,s in scene.items():
        if meta[n].get('role')=='POST_F0':s.Placement=tf*s.Placement
    def box(lo,hi):return Part.makeBox(*(b-a for a,b in zip(lo,hi)),A.Vector(*lo))
    scene['NominalPiUSBCPowerMould']=box(*p['packet']['nominal_Pi_USB_C_mould']['bounds_mm'])
    meta['NominalPiUSBCPowerMould']=dict(kind='project_mating_reservation',role='Pi4')
    new={};kind={};owner={};mates={};ties={}
    def add(n,s,k,o,mate=()):
        assert s.isValid() and s.Solids,(n,'Invalid proposed material')
        new[n]=s;kind[n]=k;owner[n]=o;mates[n]=set(mate)
    def replace(n,s,o):
        old=scene.pop(n);meta.pop(n);add(n,s,'frame_reservation',o)
        return old
    def strap(name,axis,station,lo,hi,headlo,headhi,o):
        # Rectangle annulus in the two cross-section axes, full2.5mm strip.
        axes=[i for i in range(3) if i!=axis];a=[0.,0.,0.];b=[0.,0.,0.]
        a[axis]=station-1.25;b[axis]=station+1.25
        for i,u,v in zip(axes,lo,hi):a[i]=u;b[i]=v
        outer=box(a,b);aa=a.copy();bb=b.copy();aa[axis]-=.2;bb[axis]+=.2
        for i in axes:aa[i]+=.8;bb[i]-=.8
        band=outer.cut(box(aa,bb));add(name,band,'tie_reservation',o)
        add(name+'Head',box(headlo,headhi),'tie_reservation',o);ties[name]=name+'Head'
    if coherent:
        # USB was explicitly rooted in NineWireArmRR. Allocate that WHOLE
        # first branch around its newly completed cuff/band, not a tiny notch.
        fn='CurrentBUS:USB_DiagonalArm';end=np.array([132.4304752678421,-71.90814337545011,51.60996202870123])
        points=[np.array(q) for q in ([105,-36,64],[105,-60,58],[135.5,-60,58],[135.5,end[1],end[2]],end)]
        def beam(a,b,width):
            d=b-a;v=np.array([-d[1],d[0],0]);v=v/np.linalg.norm(v);profiles=[]
            for q in (a,b):
                vv=[A.Vector(*(q+v*u+[0,0,h])) for u,h in ((-width/2,-1.5),(width/2,-1.5),(width/2,1.5),(-width/2,1.5))]
                profiles.append(Part.makePolygon(vv+[vv[0]]))
            return Part.makeLoft(profiles,True,True)
        s=beam(points[0],points[1],6)
        for a,b in zip(points[1:],points[2:]):s=s.fuse(beam(a,b,4))
        for q in points[1:-1]:s=s.fuse(box((q-[3,3,1.5]).tolist(),(q+[3,3,1.5]).tolist()))
        s=s.removeSplitter();assert len(s.Solids)==1
        replace(fn,s,'UpperFrame');report['USB_whole_branch_path_mm']=[q.tolist() for q in points]
    # Enlarge only the head budget, not the received24wire seats/loops/routes.
    for n in list(scene):
        if not n.startswith('TieHead:'):continue
        b=scene[n].BoundBox;c=b.Center
        s=box([c.x-2.5,c.y-2.5,c.z-2],[c.x+2.5,c.y+2.5,c.z+2])
        o=meta[n]['owner'];scene.pop(n);meta.pop(n);add(n,s,'tie_reservation',o)
    # Four9mm open bundle cuffs, actual positive arm/root connections.
    for code in ('FL','FR','RL','RR'):
        ee=[e for e in ends.values() if e['group']=='NineWireCuff'+code];assert len(ee)==9
        points=np.array([e['point_mm'] for e in ee]);axis=np.array(ee[0]['departure_axis']);assert abs(axis[0])==1
        x0=min(points[0,0],points[0,0]+9*axis[0]);x1=x0+9;y=float(points[:,1].mean());z=float(points[:,2].mean())
        #10.3mm bundle plus0.4 clearance; primary sidewalls/bottom2mm.
        s=box([x0,y-7.35,z-7.35],[x1,y+7.35,z+7.35])
        cavity=box([x0-1,y-5.35,z-5.35],[x1+1,y+5.35,z+9])
        s=s.cut(cavity)
        armname='StructureReserve:NineWireArm'+code;arm=scene[armname].copy().cut(cavity)
        if code.startswith('R'):arm=arm.fuse(box([107.5,y-7.35 if y>0 else y+5.35,62.5],[109.5,y-5.35 if y>0 else y+7.35,65.5]))
        if code=='FR':arm=arm.fuse(box([-83,-43,62.5],[-66,-37,65.5]))
        slot=box([(x0+x1)/2-1.45,y-9,z+5.15],[(x0+x1)/2+1.45,y+9,z+6.35])
        if coherent:
            for a,b in ((y-8.55,y-7.35),(y+7.35,y+8.55)):
                arm=arm.cut(box([(x0+x1)/2-1.45,a,z-9],[(x0+x1)/2+1.45,b,z+7]))
        s=s.cut(slot);combined=s.fuse(arm).removeSplitter()
        assert len(combined.Solids)==1,(code,'Cuff has no positive arm connection')
        oldc=scene.pop('StructureReserve:NineWireCuff'+code);meta.pop('StructureReserve:NineWireCuff'+code)
        scene.pop(armname);meta.pop(armname)
        add('BundleCuff:'+code,combined,'frame_reservation','UpperFrame')
        head_y=[y+8.15,y+13.15] if y>0 else [y-13.15,y-8.15]
        mid=(x0+x1)/2
        strap('BundleTie:'+code,0,mid,[y-8.35,z-8.6],[y+8.35,z+6.15],
            [mid-2.5,head_y[0],z-2],[mid+2.5,head_y[1],z+2],'BundleTie:'+code)
        report['root_unions'].append(dict(part='BundleCuff:'+code,root='StructureReserve:Post'+('-69_1' if code=='FL' else '-69_-1' if code=='FR' else '105_1' if code=='RL' else '105_-1')))
        report['geometry_stage']='Four-cuff construction through '+code;save()
    # P_SYS fourchannel open comb. Keep full mouth/lead allocation.
    ee=[r for r in recipes if ends[r['id']]['group']=='WAGO:P_SYS_new'];assert len(ee)==4
    s=box([-4.45,-.1,44.2],[4.55,34.1,52.6])
    for r in ee:
        y=r['start_mm'][1];R=2.3
        cyl=Part.makeCylinder(R,11,A.Vector(5.55,y,48.5),A.Vector(-1,0,0))
        s=s.cut(cyl.fuse(box([-5.45,y-R,48.5],[5.55,y+R,54])))
    s=s.cut(box([-1.4,-2,50.6],[1.5,36,51.8]))
    for a,b in ((-4.45,-2.45),(2.55,4.55)):s=s.fuse(box([a,-.1,42.52],[b,33.5,44.4]))
    s=s.removeSplitter();assert len(s.Solids)==1
    replace('P_SYS_CommonRelief',s,'UpperFrame')
    strap('PSYSTie',0,.05,[-.9,43.2],[34.9,51.6],[-2.45,-5.7,46.5],[2.55,-.7,50.5],'PSYSTie')
    report['root_unions'].append(dict(part='P_SYS_CommonRelief',root='StructureReserve:Crossmember0'))
    # MAIN complete head-side BAY in the planning strip, not a P0 cut.
    portal=box([-59.75,-28.3,80.3],[-31.15,-19.7,85.3])
    replace('StructureReserve:UpperStrip-1',scene['StructureReserve:UpperStrip-1'].cut(portal).removeSplitter(),'UpperFrame')
    ee=[r for r in recipes if ends[r['id']]['group']=='MAIN'];assert len(ee)==4
    s=box([-49,-27.25,79],[-32.4,-20.75,88])
    for r in ee:
        x=r['start_mm'][0];cyl=Part.makeCylinder(1.25,11,A.Vector(x,-24,89),A.Vector(0,0,-1))
        s=s.cut(cyl.fuse(box([x-1.25,-29,78],[x+1.25,-24,89])))
    main_shift=-.7 if coherent else 0
    s=s.cut(box([-50,-26.25,85.35+main_shift],[-31,-25.05,88.3+main_shift]))
    s=s.fuse(box([-49,-22.75,81.3],[-32.4,-17.7,84.3])).removeSplitter();assert len(s.Solids)==1
    replace('MAIN_CommonRelief',s,'UpperFrame')
    strap('MAINTie',2,86.8+main_shift,[-53.7,-26.05],[-31.4,-19.75],[-58.5,-26.05,84.8+main_shift],[-53.5,-21.05,88.8+main_shift],'MAINTie')
    report['root_unions'].append(dict(part='MAIN_CommonRelief',root='StructureReserve:UpperStrip-1'))
    report['geometry_stage']='Shared complete power combs and heads';save()
    # Eight removable inline caps/base shoes. Source-root driver axes allocated
    # first: outer joints have inboard screws, inner joints outboard screws.
    for n in list(scene):
        if meta[n].get('kind')!='actual_case' or not meta[n].get('owner','').endswith('_Joint'):continue
        case=scene[n];b=case.BoundBox;role=meta[n]['owner'];x,y,z=list(b.Center)
        panel='ForePanel' if x<20 else 'RearPanel';bias=(1 if y>0 else -1)*(-1 if abs(y)<25 else 1)
        edge=b.YMax if bias>0 else b.YMin;bolt_y=edge+bias*4.25
        base=box([b.XMin-1.25,b.YMin-.25,-42.2],[b.XMax+1.25,b.YMax+.25,b.ZMin])
        for a,c in ((b.XMin-1.25,b.XMin-.25),(b.XMax+.25,b.XMax+1.25)):
            base=base.fuse(box([a,b.YMin-.25,-42.2],[c,b.YMax+.25,-36.4]))
        ya,yb=sorted((edge-bias*.25,bolt_y+bias*3.5))
        base=base.fuse(box([x-8.5,ya,-42.2],[x+8.5,yb,b.ZMin]))
        cap_bottom=b.ZMax+.25;cap_top=cap_bottom+2
        sy0,sy1=(edge-1.25,edge+.75) if bias>0 else (edge-.75,edge+1.25)
        cap=box([b.XMin+1,sy0,cap_bottom],[b.XMax-1,sy1,cap_top]) if coherent else box([b.XMin+1,bolt_y-3.5,cap_bottom],[b.XMax-1,bolt_y+3.5,cap_top])
        spans=((b.XMin+2,b.XMin+4),(b.XMax-8,b.XMax-6)) if x<0 and abs(y)<25 else ((b.XMin+2,b.XMin+4),(b.XMax-4,b.XMax-2))
        for a,c in spans:
            ca=b.YMin-1.25 if bias>0 else b.YMin-2.75;cb=b.YMax+2.75 if bias>0 else b.YMax+1.25
            cap=cap.fuse(box([a,ca,cap_bottom],[c,cb,cap_top]))
            la,lb=(b.YMin-1.25,b.YMin-.25) if bias>0 else (b.YMax+.25,b.YMax+1.25)
            cap=cap.fuse(box([a,la,b.ZMax-1],[c,lb,cap_bottom+.2]))
        for j,bx in enumerate((x-5,x+5)):
            if coherent:cap=cap.fuse(box([bx-3.5,min(bolt_y-3.5,sy0),cap_bottom],[bx+3.5,max(bolt_y+3.5,sy1),cap_top]))
            boss=Part.makeCylinder(3.5,cap_bottom+42.2,A.Vector(bx,bolt_y,-42.2));base=base.fuse(boss)
            bore=Part.makeCylinder(1.15,20,A.Vector(bx,bolt_y,-43));base=base.cut(bore);cap=cap.cut(bore)
            pts=[A.Vector(bx+2.4*math.cos(i*math.pi/3),bolt_y+2.4*math.sin(i*math.pi/3),-38.3) for i in range(6)]
            base=base.cut(Part.Face(Part.Wire(Part.makePolygon(pts+[pts[0]]).Edges)).extrude(A.Vector(0,0,1.8)))
            shaft=Part.makeCylinder(1,12,A.Vector(bx,bolt_y,cap_top),A.Vector(0,0,-1))
            head=Part.makeCylinder(1.9,1.5,A.Vector(bx,bolt_y,cap_top))
            add('CapScrew:'+role+':'+str(j),shaft.fuse(head),'hardware',role+':Screw'+str(j))
            pts=[A.Vector(bx+2.3094*math.cos(i*math.pi/3),bolt_y+2.3094*math.sin(i*math.pi/3),-38.2) for i in range(6)]
            nut=Part.Face(Part.Wire(Part.makePolygon(pts+[pts[0]]).Edges)).extrude(A.Vector(0,0,1.6)).cut(Part.makeCylinder(.8,2,A.Vector(bx,bolt_y,-38.3)))
            add('CapNut:'+role+':'+str(j),nut,'hardware',role+':Screw'+str(j))
        base=base.removeSplitter();cap=cap.removeSplitter();assert len(base.Solids)==len(cap.Solids)==1,role
        add('CaseBase:'+role,base,'frame_reservation',panel,[n]);add('CaseCap:'+role,cap,'cap_reservation',role,[n])
        report['geometry_stage']='Complete inline retainers through '+role;save()
    # Four source-body bands with alternating inboard heads; no lever strap on
    # the eight inline joints. Full underside slots preserve panel continuity.
    for code in ('FL','FR','RL','RR'):
        n='Ref_Material_MTA_'+code+'_0_0';b=scene[n].BoundBox;x,y,z=list(b.Center);side=1 if y>0 else -1
        station=x-7 if side>0 else x+7;lo=[b.YMin-1,b.ZMin-1];hi=[b.YMax+1,b.ZMax+1]
        headlo=[station-2.5,b.YMin-6 if side>0 else b.YMax+1,z-2]
        headhi=[station+2.5,b.YMin-1 if side>0 else b.YMax+6,z+2]
        strap('CaseTie:'+code,0,station,lo,hi,headlo,headhi,'CaseTie:'+code)
        for panel in ('ForePanel','RearPanel'):
            pn='LowerBay:'+panel
            if pn in scene:replace(pn,scene[pn].copy(),panel)
            new[pn]=new[pn].cut(box([station-1.45,b.YMin-1.2,-45],[station+1.45,b.YMax+1.2,b.ZMax+1.2 if coherent else -41.8])).removeSplitter()
            assert new[pn].isValid() and len(new[pn].Solids)==1,pn
    # First land cylinders from the CURRENT received contracts, no obsolete
    # axes or collinear power-pair copies. Their restraints are checked too.
    for r in recipes:
        n='Land:'+r['id'];s=Part.makeCylinder(r['radius_mm'],r['straight_mm'],A.Vector(*r['start_mm']),A.Vector(*r['axis']))
        scene[n]=s;meta[n]=dict(kind='current_first_land',role=ends[r['id']]['group'],endpoint=r['id'])
    if coherent:
        bp=OUT/'n01-common-backbone-preflight-r4.json';bank=json.loads(bp.read_text());report['source_sha256'][bp.relative_to(ROOT).as_posix()]=sha(bp)
        report['bank_full_prefixes_added']=[]
        for row in bank['bend_allocations']:
            a=np.array(row['start_mm']);v=(np.array(row['end_mm'])-a-row['bend_R_mm']*np.array(row['bend']))/(row['land_mm']+row['bend_R_mm'])
            n='BankFullPrefix:'+row['id'];s=tube_prefix(a.tolist(),v.tolist(),row['radius_mm'],row['bend'],row['bend_R_mm'],row['land_mm'])
            add(n,s,'actual_wire',n);report['bank_full_prefixes_added'].append(row['id'])
    bounds={n:s.BoundBox for n,s in {**scene,**new}.items()}
    valid={n:s.isValid() and bool(s.Solids) for n,s in {**scene,**new}.items()}
    changed=set(new)
    if coherent:
        changed={n for n in new if n.startswith(('BundleCuff:FL','BundleCuff:FR','BundleCuff:RR','CurrentBUS:','MAIN_CommonRelief','MAINTie','CaseCap:','LowerBay:','BankFullPrefix:'))}
        previous={r['name']:r for r in prior['parts']}
        for n in set(new)-changed:
            b=bounds[n];bb=[[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]]
            assert np.max(np.abs(np.array(bb)-previous[n]['bounds_mm']))<1e-5,n
            assert abs(new[n].Volume-previous[n]['volume_mm3'])<1e-4,n
        report['unchanged_material_receipt_reused']=dict(source='n01-common-restraint-material.json',sha256=sha(OUT/'n01-common-restraint-material.json'),unchanged_parts=len(new)-len(changed),changed_parts=sorted(changed))
        report['prior_unchanged_contacts_classified_as_owned_print_unions']=[]
        for row in prior['contacts']:
            a,b=row['a'],row['b']
            if a in changed or b in changed:continue
            # Preserve negative observations. Reuse is allowed ONLY when the
            # exact pair is demonstrably the same planned printed owner.
            assert a in new and kind[a]=='frame_reservation',(a,b,'Unchanged unresolved contact')
            same=b in new and kind[b]=='frame_reservation' and owner[a]==owner[b]
            old=b in meta and (meta[b].get('owner')==owner[a] and meta[b]['kind'] in ('seat_reservation','frame_reservation','load_root_reservation') or owner[a]=='UpperFrame' and b.startswith('StructureReserve:'))
            assert same or old,(a,b,'Cannot turn unchanged failure into clearance')
            report['prior_unchanged_contacts_classified_as_owned_print_unions'].append(row)
        report['assembly_sequence_change']='Cut2labelled replaceableW026/W037 factory-joint ties before8lower root drivers. Two lower panels are tethered; full disconnection list still OPEN, not independent removal proof.'
        report['service_tie_replacements_candidate']=2
    def same_tie(a,b):return a in ties and ties[a]==b or b in ties and ties[b]==a
    def printed(k):return k in ('frame_reservation','cap_reservation')
    def check(n,s,m,t,pose=None):
        gate();bb=t.BoundBox if pose is not None else bounds[m]
        if not bounds[n].intersect(bb):return
        report['pairs']+=1;assert valid[n] and t.isValid(),(n,m,'Invalid actual candidate')
        c=s.common(t);assert c.isNull() or c.isValid(),(n,m)
        if c.Volume<=1e-5:return
        row=dict(a=n,b=m,pose=pose,volume_mm3=c.Volume)
        if pose is None:
            if coherent and n.startswith('BankFullPrefix:') and m=='Land:'+n.removeprefix('BankFullPrefix:'):
                report['mating_pairs'].append(row);return
            if same_tie(n,m) or m in new and kind[n]==kind[m]=='hardware' and owner[n]==owner[m]:report['mating_pairs'].append(row);return
            if m in new and kind[n]==kind[m]=='frame_reservation' and owner[n]==owner[m]:report['planned_unions'].append(row);return
            if m in scene and meta[m].get('role')=='ScaffoldPlanning' and kind[n]=='frame_reservation' and owner[n]=='UpperFrame':report['planned_unions'].append(row);return
            if coherent and m in scene and kind[n]=='frame_reservation':
                oldkind=meta[m]['kind'];oldowner=meta[m].get('owner')
                if oldowner==owner[n] and oldkind in ('seat_reservation','frame_reservation','load_root_reservation') or owner[n]=='UpperFrame' and m.startswith('StructureReserve:'):
                    report['planned_unions'].append(row);return
            if m.startswith('TieLoop:') and n.startswith('TieHead:') and n.removeprefix('TieHead:')==m.removeprefix('TieLoop:'):report['mating_pairs'].append(row);return
        report['contacts'].append(row)
    try:
        save()
        for n,s in new.items():
            if n not in changed:continue
            for m,t in scene.items():
                if meta[m].get('role','').startswith('leg:'):continue
                check(n,s,m,t)
        for i,(n,s) in enumerate(new.items()):
            for m,t in list(new.items())[i+1:]:
                if n in changed or m in changed:check(n,s,m,t)
        # Full eight assembly driver cylinders. Deep inline cap service is
        # intentionally performed after whole lower panel removal on bench.
        for x in (-80,-70,112,122):
            for y in (-22.5,22.5):
                tool=Part.makeCylinder(3,43,A.Vector(x,y,-48))
                for n,s in new.items():
                    if coherent and n in ('TieHead:Seat:W026:factory:1','TieHead:Seat:W037:factory:1'):continue
                    if not tool.BoundBox.intersect(bounds[n]):continue
                    gate();c=tool.common(s);assert c.isNull() or c.isValid()
                    if c.Volume>1e-5:report['driver_conflicts'].append(dict(axis_mm=[x,y],part=n,volume_mm3=c.Volume))
        reader=SavedShapes();outer=reader.shape(OUT/'central-cassette-envelope/FelineLayoutEnvelope.FCStd','TorsoEnvelope');shell=Part.makeCompound(outer.Shells)
        for n,s in new.items():
            gate();diff=s.cut(outer);assert diff.isNull() or diff.isValid(),n
            if diff.Volume>1e-5:report['outside'].append(dict(name=n,volume_mm3=diff.Volume))
            elif s.distToShape(shell)[0]<3.65-1e-5:report['wall_failures'].append(n)
            b=s.BoundBox;report['parts'].append(dict(name=n,kind=kind[n],owner=owner[n],solids=len(s.Solids),bounds_mm=[[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]],volume_mm3=s.Volume))
        for r in report['root_unions']:
            root=new.get(r['root'],scene.get(r['root']));c=new[r['part']].common(root)
            r['volume_mm3']=c.Volume;assert c.Volume>1e-5,(r,'No positive root')
        save();print('Common retention static',report['pairs'],'contacts',len(report['contacts']),'drivers',len(report['driver_conflicts']),flush=True)
        if any(report[k] for k in ('contacts','errors','outside','wall_failures','driver_conflicts')):report['status']='SHARED_RETENTION_REJECTED_NO_MOTION_RERUN'
        else:
            axes=json.loads((ROOT/'hardware/simulation/p0/e6-leg-compatibility.json').read_text())['axes'];motion=p['motion']
            moving={n:s for n,s in scene.items() if meta[n].get('role','').startswith('leg:')}
            for index,sample in enumerate(motion['poses'][:36]):
                for code,groups in motion['membership'].items():
                    aa=[next(a for a in axes if a['code']==code and a['stage']==stage) for stage in STAGES];tfs=placement(aa,sample['legs'][code]['angles_delta_degrees'])
                    for stage,names in groups.items():
                        for name in names:
                            gate();s=moving[name].copy();s.Placement=tfs[stage]*s.Placement
                            for n,t in new.items():check(n,t,name,s,index)
                report['poses'].append(index);save()
            report['status']='SHARED_RETENTION_MOTION_REJECTED' if report['contacts'] else 'SHARED_RETENTION_SCOPED_CLEAR_FULL_ROUTES_TOOLS_STOCK_NATIVE_OPEN'
        report['source_sha256'].update(reader.hashes)
    except Exception as exc:report['errors'].append(repr(exc));report['status']='SHARED_RETENTION_PARTIAL'
    save();print(json.dumps({k:report[k] for k in ('status','worker_seconds','pairs','errors')})+' contacts='+str(len(report['contacts'])),flush=True)


if __name__=='__main__':main()
