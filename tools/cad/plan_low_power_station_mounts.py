"""Four under-rail supports for the actual current low power stations.

One shared topology: clamp the retained P0 rail without drilling; the lower
jaw owns the ledge and low backing face. No wire loading through WAGO glue.
"""
import json,math,time,zipfile
from pathlib import Path
import FreeCAD as A
import Part
from plan_current_main_sources import ROOT,BASE,OUT,SHA
from current_prototype_harness_scene import W

def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
def fuse(parts):
    s=parts[0]
    for t in parts[1:]:s=s.fuse(t)
    return s.removeSplitter()

def scene():
    targets={};curves={};archive=BASE/'current-view-60-20261012.zip'
    with zipfile.ZipFile(archive) as z:
        for e in json.loads(z.read('index.json'))['entries']:
            s=Part.Shape();s.importBrepFromString(z.read(e['file']).decode())
            if 'radius_mm' in e:curves[e['label']]=(s,e['radius_mm'])
            else:targets[e['label']]=s
    return targets,curves,archive

def allocate(targets):
    pads=[];hardware={};parts={};stations=[]
    for leg,side in [('FL',1),('FR',-1),('RL',1),('RR',-1)]:
        name=leg+'_P';bb=targets[name].BoundBox
        x=(bb.XMin+bb.XMax)/2;y=(bb.YMin+bb.YMax)/2
        yy=abs(y)
        assert abs(bb.ZMin-.5)<1e-5 and yy>65,(name,'Changed station datum')
        def B(a,b,c,d,e,f):
            lo,hi=sorted((side*b,side*e));return [a,lo,c,d,hi,f]
        # The current E1 floor reaches Y-42: rail bearing starts at45,
        # not the obsolete broad39mm foot. Rear wall faces INWARD so the
        # retained FR station atY-93 still stays within the200mm body width.
        top=[B(x-10,45,38.52,x+10,61,43.52)]
        lower=[B(x-10,45,-5,x+10,61,-2),
               B(x-8,55,-5,x+8,yy+4,-2),
               B(x-16,yy-8,-2,x+16,yy+5.5,.25),
               B(x-16,yy-8,-2,x+16,yy-5,6),
               B(x-16,yy-5,-2,x-15.5,yy+5.5,3),
               B(x+15.5,yy-5,-2,x+16,yy+5.5,3)]
        for kind,rows in [('TopClamp',top),('StationShoe',lower)]:
            n=leg+kind;s=fuse([box(b) for b in rows])
            for dx in (-4,4):s=s.cut(Part.makeCylinder(1.7,60,A.Vector(x+dx,side*55,-12)))
            parts[n]=s.removeSplitter()
            pads.extend(dict(owner=n,name='Pad'+str(i),bounds_mm=b) for i,b in enumerate(rows))
        # Both adhesive surfaces stop at the lower casing. No binding crosses
        # a lever; actual glue compatibility/peel and delivered fit are gates.
        parts[leg+'BottomBond']=box(B(x-13.5,yy-4,.25,x+13.5,yy+4,.5))
        parts[leg+'BackBond']=box(B(x-10,yy-5,.5,x+10,yy-4.5,5.5))
        for dx in (-4,4):
            q=A.Vector(x+dx,side*55,-10.98)
            hardware[leg+'Bolt'+str(dx)]=Part.makeCylinder(1.5,55,q).fuse(Part.makeCylinder(2.75,3,A.Vector(q.x,q.y,44.02)))
            for tag,z in [('UpperWasher',43.52),('LowerWasher',-5.5)]:
                hardware[leg+tag+str(dx)]=Part.makeCylinder(3.5,.5,A.Vector(q.x,q.y,z)).cut(Part.makeCylinder(1.6,.5,A.Vector(q.x,q.y,z)))
            polygon=[A.Vector(q.x+3.2*math.cos(i*math.pi/3),q.y+3.2*math.sin(i*math.pi/3),-7.9) for i in range(7)]
            hardware[leg+'Nut'+str(dx)]=Part.Face(Part.makePolygon(polygon)).extrude(A.Vector(0,0,2.4)).cut(Part.makeCylinder(1.5,2.4,A.Vector(q.x,q.y,-7.9)))
        stations.append(dict(name=name,clamp_axes_mm=[[x-4,side*55],[x+4,side*55]],
            load_path='WAGO lower casing -> two provisional adhesive patches -> shoe/under-rail jaw -> P0 side rail; top clamp and two M3x55 close stack',
            adhesive_area_mm2=[216,100],wire_strain_relief='OPEN separately, no wire strain transferred to adhesive',
            stack=dict(underhead_z_mm=44.02,bolt_tip_z_mm=-10.98,nut_bottom_z_mm=-7.9,tip_past_nut_mm=3.08),
            assembly=['No power sources. Fit lower shoe below rail; install upper clamp and washers/bolts with nuts below before case or wires.',
                      'Fit delivered casing on dry shoe; confirm all five levers and markings remain free. Adjust only this replaceable shoe if supplier casing differs.',
                      'Use the previously proposed removable adhesive retention only after compatibility/peel trial; support case while operating a lever.',
                      'Deep removal: free wire ends without pulling casing, remove adhesive and case, then undo two exposed M3 stacks. No instant-service promise.']))
    return parts,hardware,dict(pads=pads,stations=stations,new_prints=8,
        hardware_nominal={'M3x55':8,'M3nut':8,'M3washer':16},
        provisional=['Nominal M3 hardware/head envelopes; exact SKU/stack tolerance in K2',
          '0.25mm bottom/0.5mm rear bond lines are project allocations, not measured adhesive properties',
          'Delivered WAGO lower casing and lever clearance; PETG rail fit/creep, clamp load, peel retention in phase2'],
        remaining=['Separate insulation grips/full five-port fans','Remaining eight D/G station mounts','Full moving legs/head mount replacement/whole W5/stock'],
        selected=False,W5_complete=False,physical_pass=False)

def run():
    tick=time.monotonic();targets,curves,archive=scene();parts,hardware,p=allocate(targets)
    new={**parts,**hardware};report=dict(contacts=[],errors=[],pairs=0)
    def test(n,s,m,t,rad=0):
        if not W.near(s,t,rad+.001):return
        report['pairs']+=1
        if not s.isValid() or not t.isValid():report['errors'].append([n,m]);return
        if rad:
            gap=s.distToShape(t)[0]
            if gap<rad-1e-4:report['contacts'].append(dict(part=n,other=m,gap_mm=gap))
        elif s.distToShape(t)[0]<1e-5:
            v=s.common(t).Volume
            if v>1e-5:report['contacts'].append(dict(part=n,other=m,volume_mm3=v))
    for n,s in new.items():
        for m,t in targets.items():
            if t.Solids:test(n,s,m,t)
        for m,(t,rad) in curves.items():test(n,s,m,t,rad)
        print('checked',n,'contacts',len(report['contacts']),flush=True)
    names=list(new)
    for i,n in enumerate(names):
        for m in names[i+1:]:test(n,new[n],m,new[m])
    p.update(report,status='LOW_POWER_STATION_MOUNT_STATIC_CLEAR_MOTION_NATIVE_OPEN' if not report['contacts'] and not report['errors'] else 'REJECTED_LOW_POWER_STATION_MOUNT',
        source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in (archive,Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,3))
    (OUT/'low-power-station-mounts-plan.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:p[k] for k in ('status','pairs','contacts','errors','worker_seconds')}),flush=True)

if __name__=='__main__':run()
