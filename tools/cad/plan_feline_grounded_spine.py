"""One grounded internal spine candidate, BEFORE detailed module adapters.

Existing8 upper M2frame holes are distinct from bottom belly-foot clamp holes.
Do not assume the retired old platform exists. No board is called mounted by
this scaffold alone; all current modules/69known wire approaches are included.
"""
import json,time,math,sys
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import OUT
from check_feline_shared_space import tube_prefix
from datetime import datetime as task_datetime,timezone as task_timezone


def main():
    tick=time.monotonic();reader=SavedShapes()
    native_meta=json.loads((OUT/'interior-native-checks.json').read_text());native=ROOT/native_meta['native']
    assert sha(native)==native_meta['native_sha256']
    planfile=OUT/'module-layout.json';plan=json.loads(planfile.read_text());motion=json.loads((OUT/'motion-layout.json').read_text());scenario=None
    if '--receiver-scenario' in sys.argv:
        scenario=json.loads((OUT/'motion-receivers-checks.json').read_text())
        assert scenario['native_built'] and scenario['fresh_reopen']
        native=ROOT/scenario['native'];assert sha(native)==scenario['native_sha256']
        planfile=ROOT/scenario['module_plan'];plan=json.loads(planfile.read_text())
    names=[n for g in plan['groups'] for n in g['objects']]
    for row in motion['inventory']:
        n=row['object']
        if n not in names and row['kind']=='surface' and (row['label'].startswith(('P0_','tail/')) or n.startswith(('Print_P0_','Print_CP2_TailRiser','Battery'))):
            if not n.startswith('BatteryFrameHardware'):names.append(n)
    names += [f'BellyFoot{i}' for i in range(1,5)]+[f'FrameHardwareNew{i}' for i in range(8)]
    scene={n:reader.shape(native,n) for n in names}
    integrated='--integrated-tail-roots' in sys.argv
    roots=[];pieces={};recipes=[];retained_risers={};root_reuse={}
    def box(name,low,high):
        x,y,z=low;xx,yy,zz=high
        s=Part.makeBox(xx-x,yy-y,zz-z,A.Vector(x,y,z));pieces[name]=s
        recipes.append(dict(name=name,kind='box',bounds_mm=[low,high]));return s
    for front,xlo,xhi,frame_name,anchors in [
        (True,-68.5 if integrated else -89.5,-66 if integrated else -87,'Ref_Material_P0_FrameFront20_0_0',(-80,-70)),
        (False,104 if integrated else 107,106.5 if integrated else 109.5,'Ref_Material_P0_FrameRear20_0_0',(112,122))]:
        label='Front' if front else 'Rear'
        foot_xlo=-89.5 if front else (104 if integrated else 107);foot_xhi=-66 if front else 126
        for sign in (-1,1):
            y=sign*22.5;name=label+('Left' if sign>0 else 'Right')+'Foot'
            foot=box(name,[foot_xlo,y-4,37.02],[foot_xhi,y+4,40.02])
            for hx in anchors:
                foot=foot.cut(Part.makeCylinder(1.1,5,A.Vector(hx,y,36)))
                radius=4.3/math.sqrt(3)
                pts=[A.Vector(hx+radius*math.cos(math.radians(30+60*i)),y+radius*math.sin(math.radians(30+60*i)),38.22) for i in range(6)]
                tool=Part.Face(Part.Wire(Part.makePolygon(pts+[pts[0]]).Edges)).extrude(A.Vector(0,0,2))
                foot=foot.cut(tool)
            if integrated and not front:
                suffixes=('', '002') if sign<0 else ('001','003')
                old_risers={('Print_CP2_TailRiser'+suffix):scene['Print_CP2_TailRiser'+suffix] for suffix in suffixes}
                retained_risers.update(old_risers);base=Part.makeCompound(list(old_risers.values()))
                # Rear bores are already occupied. Preserve both exact risers
                # and their original fasteners, integrate a forward wing,
                # and screen ONLY newly added material against retained parts.
                foot=foot.fuse(base).removeSplitter();root_reuse[name]=dict(originals=list(old_risers),base=base,whole=foot)
                pieces[name]=foot.cut(base)
            else:pieces[name]=foot
            assert foot.isValid() and len(foot.Solids)==1
            recipes[-1].update(upper_frame_M2_axes_mm=[[hx,y] for hx in anchors],through_hole_diameter_mm=2.2,
                nominal_nut_pockets=dict(across_flats_mm=4.3,z_mm=[38.22,40.22]))
            box(label+('Left' if sign>0 else 'Right')+'Upright',[xlo,y-4,39.92],[xhi,y+4,84])
            frame=scene[frame_name];topfaces=[f for f in frame.Faces if abs(f.optimalBoundingBox().ZMin-37.02)<1e-5 and abs(f.optimalBoundingBox().ZMax-37.02)<1e-5]
            footfaces=[f for f in foot.Faces if abs(f.optimalBoundingBox().ZMin-37.02)<1e-5 and abs(f.optimalBoundingBox().ZMax-37.02)<1e-5]
            bearing=sum(a.common(b).Area for a in topfaces for b in footfaces)
            holes=[]
            for hx in anchors:
                found=[]
                for f in frame.Faces:
                    c=f.Surface
                    if not isinstance(c,Part.Cylinder) or abs(c.Radius-1.025)>1e-5 or abs(c.Axis.z)<.9999:continue
                    b=f.optimalBoundingBox()
                    if math.hypot(c.Center.x-hx,c.Center.y-y)<1e-5 and abs(b.ZMin-35.52)<1e-5 and abs(b.ZMax-37.02)<1e-5:found.append(f)
                assert len(found)==1,(frame_name,hx,y,'Actual upper frame bore not found')
                holes.append(dict(axis_mm=[hx,y],diameter_mm=2.05,z_mm=[35.52,37.02]))
            assert bearing>90,(name,bearing)
            roots.append(dict(part=name,frame=frame_name,bearing_area_mm2=bearing,upper_bores=holes,
                lower_belly_clamp_hardware_unchanged=True,reuses_original_tail_risers=bool(integrated and not front)))
        box(label+'CrossCap',[xlo,-74,83],[xhi,74,85])
    for sign in (-1,1):
        y=sign*8;box('CentralRail'+('Left' if sign>0 else 'Right'),[-68.5 if integrated else -89.5,y-1.5,75],[106.5 if integrated else 109.5,y+1.5,85])
    # Nominal hardware is separately checked. EightM2x6 freed by the belly
    # foot conversion may be reused; nuts/washers are still stock candidates.
    for root in roots:
        if root['reuses_original_tail_risers']:continue
        for hx,y in [r['axis_mm'] for r in root['upper_bores']]:
            stem=Part.makeCylinder(1,6,A.Vector(hx,y,35.22));head=Part.makeCylinder(1.9,2,A.Vector(hx,y,33.22))
            washer=Part.makeCylinder(2.5,.3,A.Vector(hx,y,35.22)).cut(Part.makeCylinder(1.1,.3,A.Vector(hx,y,35.22)))
            radius=4/math.sqrt(3);pts=[A.Vector(hx+radius*math.cos(math.radians(30+60*i)),y+radius*math.sin(math.radians(30+60*i)),38.22) for i in range(6)]
            nut=Part.Face(Part.Wire(Part.makePolygon(pts+[pts[0]]).Edges)).extrude(A.Vector(0,0,1.6)).cut(Part.makeCylinder(1,1.6,A.Vector(hx,y,38.22)))
            pieces[f'UpperM2_{hx}_{y}']=Part.makeCompound([stem.fuse(head),washer,nut])
    prefixfile=OUT/'prefix-allocation.json';factoryfile=OUT/'factory-routes.json'
    prefixes=json.loads(prefixfile.read_text());factory=json.loads(factoryfile.read_text());wires={};rows={r['id']:r for r in prefixes['specifications']}
    for p in (prefixfile,factoryfile):assert native_meta['reused_qualified_interface_receipts'][p.relative_to(ROOT).as_posix()]==sha(p)
    omitted=[]
    for key,k in prefixes['allocation'].items():
        r=rows[key];bend=next(c['bend'] for c in prefixes['domains'][key] if c['option']==k)
        if scenario and r['role'] in plan['motion_receiving_changes']:omitted.append(key);continue
        wires[key]=tube_prefix(r['point'],r['direction'],r['radius'],bend,12.4)
    if scenario:factory={'routes':scenario['factory_routes']}
    for row in factory['routes']:
        edges=[]
        for e in row['parts']:
            a,b=A.Vector(*e['start']),A.Vector(*e['end']);edges.append(Part.makeLine(a,b) if e['kind']=='line' else Part.Arc(a,A.Vector(*e['mid']),b).toShape())
        w=Part.Wire(edges);e=w.Edges[0];p=e.valueAt(e.FirstParameter);t=e.tangentAt(e.FirstParameter)
        wires['Factory:'+row['wire']]=w.makePipeShell([Part.Wire([Part.makeCircle(row['radius_mm'],p,t)])],True,False)
    report=dict(status='ONE_GROUNDED_SPINE_PRECHECK_RUNNING',selected=False,physical_pass=False,
        recipes=recipes,frame_roots=roots,contacts=[],clearance_failures=[],errors=[],pairs=0,
        geometry_count=len(pieces),native_built=False,boards_called_mounted=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (native,planfile,prefixfile,factoryfile,Path(__file__))},
        omitted_stale_relocated_approaches=omitted,known_wire_pieces_checked=len(wires),full_wiring_checked=False,
        stock_candidate={'reuse_released_M2x6':8,'additional_M2nuts':8,'additional_M2washers':8},
        open=['Native editable receiver','Whole36pose moving leg check','Board-specific mounts/fastener stacks',
            'Bank fixture retention and ATO service','Panel attachment tabs','Stock/assembly/load test'])
    if integrated:
        report.update(topology='Front columns at inboard edge clear S0. Rear occupied frame bores reuse exact4tail risers/fasteners; integrated forward wings clear retained TailBridge, not a second bolt stack through occupied holes.',
            original_tail_riser_reuse={k:dict(originals=v['originals'],unchanged_original_volume_mm3=v['base'].Volume) for k,v in root_reuse.items()},
            newly_added_delta_screen=True,stock_candidate={'reuse_released_M2x6':4,'additional_M2nuts':4,'additional_M2washers':4,'rear_original_fasteners_retained':True})
    dest=OUT/('grounded-spine-integrated-plan.json' if integrated else 'grounded-spine-plan.json');deadline=task_datetime.fromisoformat('2026-10-17T07:30:00+00:00')
    def save():
        report['worker_seconds']=round(time.monotonic()-tick,3);dest.write_text(json.dumps(report,indent=2)+'\n')
    bounds={n:s.BoundBox for n,s in {**pieces,**scene,**wires}.items()};save()
    for pn,p in pieces.items():
        for n,s in {**scene,**wires}.items():
            if task_datetime.now(task_timezone.utc)>=deadline:
                report['status']='GROUNDED_SPINE_PRECHECK_DEADLINE_PARTIAL';save();return
            gap=1.25 if n in wires else 0;ba,bb=bounds[pn],bounds[n]
            sep=sum(max(0,a-b,c-d)**2 for a,b,c,d in [(ba.XMin,bb.XMax,bb.XMin,ba.XMax),(ba.YMin,bb.YMax,bb.YMin,ba.YMax),(ba.ZMin,bb.ZMax,bb.ZMin,ba.ZMax)])
            if sep>gap*gap:continue
            report['pairs']+=1
            try:
                c=p.common(s)
                if not c.isNull() and not c.isValid():raise ValueError('Invalid exact intersection')
                if c.Volume>1e-5:report['contacts'].append(dict(piece=pn,other=n,wire=n in wires,volume_mm3=c.Volume))
                elif gap:
                    distance=p.distToShape(s)[0]
                    if distance<gap-1e-5:report['clearance_failures'].append(dict(piece=pn,wire=n,gap_mm=distance,required_mm=gap))
            except Exception as exc:report['errors'].append(dict(piece=pn,other=n,error=str(exc)))
        save();print('Grounded spine',pn,'hits',len(report['contacts']),'gaps',len(report['clearance_failures']),flush=True)
    report['source_sha256'].update(reader.hashes)
    report['status']='ONE_GROUNDED_SPINE_CURRENT_STATIC_PARTIAL_WIRES_CLEAR_NATIVE_MOTION_OPEN' if not any(report[k] for k in ('contacts','clearance_failures','errors')) else 'GROUNDED_SPINE_COMMON_PLAN_REJECTED'
    save();print(json.dumps({k:report[k] for k in ('status','pairs','worker_seconds')}),flush=True)


if __name__=='__main__':main()
