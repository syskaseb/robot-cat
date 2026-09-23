"""Isolated, read-only E1 prototype checks; never saves source CAD."""
from pathlib import Path
import json,sys,itertools,math
import pilot
import author_ears as task

def write(name,data):
    task.OUT.mkdir(parents=True,exist_ok=True)
    (task.OUT/name).write_text(json.dumps(data,indent=2),encoding='utf-8',newline='\n')

def common(a,b):
    return abs(a.common(b).Volume) if a.BoundBox.intersect(b.BoundBox) else 0.

def sampled_distance(a,b):
    """Bidirectional vertex + 64 surface samples; not a Hausdorff certificate."""
    import Part
    worst=0.
    for s,t in [(a,b),(b,a)]:
        verts=[v.Point for v in s.Vertexes]
        mesh=s.tessellate(.15)[0];stride=max(1,len(mesh)//64)
        for p in verts+list(mesh[::stride]):
            worst=max(worst,Part.Vertex(p).distToShape(t)[0])
    return worst

def module():
    import FreeCAD as A, Part
    assert not A.GuiUp and not A.listDocuments()
    d=pilot.document(A,task.MODULE);d.recompute()
    shapes={n:d.getObject(n).Shape for n in task.PHYSICAL}
    report={'file_sha256':{task.MODULE.relative_to(pilot.ROOT).as_posix():pilot.sha(task.MODULE)},'new_geometry':{},'intersections':[],'mounts':[],'print_ready':False}
    for n,s in shapes.items():
        try:s.check(True);check=True
        except Exception as e:check=str(e)
        box=s.optimalBoundingBox(False,False)
        report['new_geometry'][n]={'valid':s.isValid(),'strict_bop':check,'solids':len(s.Solids),'volume_mm3':s.Volume,'bbox_mm':[box.XLength,box.YLength,box.ZLength]}
    try:d.getObject('InheritedRearHead').Shape.check(True);legacy=True
    except Exception as e:legacy=str(e)
    report['inherited_rear_head_strict_bop']=legacy
    report['legacy_geometry_gate']='FAIL: inherited rear head BOP defects retained, not print approved'
    for a,b in itertools.combinations(shapes,2):
        vol=common(shapes[a],shapes[b])
        if vol>1e-4:report['intersections'].append([a,b,vol])
    print('geometry',report['new_geometry'],'intersections',report['intersections'],flush=True)
    # Contact cross-section probes and complete shaft / nominal nut engagement.
    for side,y in [('L',-32),('R',32)]:
        for i,x,seat,nutz in [(0,-122,163.5,173.5),(1,-112,157.5,167.5)]:
            ring=Part.makeCylinder(2.1,.02,A.Vector(x,y,seat)).cut(Part.makeCylinder(1.2,.02,A.Vector(x,y,seat)))
            nutring=Part.makeCylinder(1.9,.02,A.Vector(x,y,nutz-.02)).cut(Part.makeCylinder(1.2,.02,A.Vector(x,y,nutz-.02)))
            # Driver enters through the open head split, then travels upward.
            driver=Part.makeCylinder(1.7,12,A.Vector(x,y,seat-14))
            # Orthogonal insertion route from front opening, below boss.
            entry=Part.makeCylinder(1.7,x+130,A.Vector(-130,y,seat-8),A.Vector(1,0,0))
            nut=shapes[f'EarNut{side}{i}']
            # Side-load the nut with the detached ear before mounting it.
            moves=[]
            for dx in ([18,12,6,3,0] if i==0 else [6,4,2,0]):
                ns=nut.copy();ns.translate(A.Vector(dx,0,0));moves.append(common(ns,shapes['Ear'+side]))
            report['mounts'].append({'side':side,'index':i,'axis_mm':[x,y],'seat_z':seat,'nut_z':nutz,
                'head_bearing_mm2':common(ring,shapes['RearHead'])/.02,
                'nut_bearing_mm2':common(nutring,shapes['Ear'+side])/.02,
                'nominal_nut_engagement_mm':1.6,'protrusion_mm':seat+12-nutz-1.6,
                'driver_rear_shell_overlap_mm3':common(driver,shapes['RearHead']),
                'front_entry_rear_shell_overlap_mm3':common(entry,shapes['RearHead']),
                'nut_insertion_intersections_mm3':moves})
    sketches=[o for o in d.Objects if o.TypeId=='Sketcher::SketchObject']
    report['sketches']=[{'name':s.Name,'fully_constrained':s.FullyConstrained,'solve':s.solve()} for s in sketches]
    # Measure actual linked native dimensional change and complete restoration.
    params=d.getObject('EarParameters');base={n:s.Volume for n,s in shapes.items()}
    probes=[]
    for name,value in [('HoleRadius',1.3),('WidthScale',1.02),('HeightScale',1.02)]:
        old=getattr(params,name);setattr(params,name,value);d.recompute(None,True,True)
        delta={n:d.getObject(n).Shape.Volume-v for n,v in base.items() if n in ['EarL','EarR','RearHead']}
        valid=all(d.getObject(n).Shape.isValid() and len(d.getObject(n).Shape.Solids)==1 for n in ['EarL','EarR','RearHead'])
        setattr(params,name,old);d.recompute(None,True,True)
        error=max(abs(d.getObject(n).Shape.Volume-v) for n,v in base.items())
        relative_error=max(abs(d.getObject(n).Shape.Volume-v)/max(v,1) for n,v in base.items())
        # Near-coincident Boolean differences on these trimmed lofts can return
        # the entire solid despite strict BOP-valid operands (observed OCCT 7.8).
        # Do not present that as an exact equivalence pass. Use measured surface
        # samples, full vertex checks, volume and strict BOP as a limited test.
        distances={n:sampled_distance(shapes[n],d.getObject(n).Shape) for n in ['EarL','EarR']}
        restored_strict={}
        for n in ['EarL','EarR']:
            try:d.getObject(n).Shape.check(True);restored_strict[n]=True
            except Exception as e:restored_strict[n]=str(e)
        probes.append({'parameter':name,'value':value,'delta_mm3':delta,'valid':valid,'restore_volume_error_mm3':error,'restore_relative_volume_error':relative_error,'restored_sample_distance_mm':distances,'restoration_method':'All vertices + bidirectional ~64 surface samples per ear <0.0001 mm; volume quadrature within 2 ppm; strict BOP. Not exact Boolean/Hausdorff proof','restored_strict_bop':restored_strict})
    report['parameters']=probes;report['cad_saved']=False
    report['tool_sha256']=pilot.sha(Path(__file__))
    write('module.json',report)
    print(json.dumps({'mounts':report['mounts'],'parameters':probes}),flush=True)
    for n in list(A.listDocuments()):A.closeDocument(n)
    assert all(r['strict_bop'] is True and r['solids']==1 for n,r in report['new_geometry'].items() if n!='RearHead')
    assert report['new_geometry']['RearHead']['strict_bop']==legacy
    assert not report['intersections']
    assert all(s['fully_constrained'] and s['solve']==0 for s in report['sketches'])
    assert all(p['valid'] and p['restore_relative_volume_error']<2e-6 and max(p['restored_sample_distance_mm'].values())<1e-4 and all(x is True for x in p['restored_strict_bop'].values()) for p in probes)
    assert all(min(r['head_bearing_mm2'],r['nut_bearing_mm2'])>5 and max(r['nut_insertion_intersections_mm3'])<1e-4 and r['driver_rear_shell_overlap_mm3']<1e-4 and r['front_entry_rear_shell_overlap_mm3']<1e-4 for r in report['mounts'])

if __name__=='__main__':module()
