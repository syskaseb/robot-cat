"""Correct derived bed placement and check exact local design S-bends, not real leads."""
import hashlib,json,math
from pathlib import Path
import FreeCAD as A
import Mesh,MeshPart,Part
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/aux-splice-shelf-r2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
def volume(s):return sum(p.Volume for p in s.Solids)

def main():
    p=json.loads((OUT/'plan.json').read_text(encoding='utf-8'))
    g=json.loads((OUT/'geometry.json').read_text(encoding='utf-8'))
    assert g['nominal_clear'] and g['plan_sha256']==sha(OUT/'plan.json')
    d=A.openDocument(str(OUT/'AuxSpliceShelfR2.FCStd'))
    try:
        d.recompute();s=d.getObject('Shelf').Shape.copy()
        assert s.isValid() and len(s.Solids)==1
        b=s.BoundBox;flat=s.copy();flat.translate(A.Vector(-b.XMin,-b.YMin,-b.ZMin))
        stl=OUT/'AuxSpliceShelf_R2_candidate_x1.stl'
        old=Mesh.Mesh(str(stl));old_z=old.BoundBox.ZMin
        MeshPart.meshFromShape(Shape=flat,LinearDeflection=.05,AngularDeflection=.15,Relative=False).write(str(stl))
        m=Mesh.Mesh(str(stl));assert m.isSolid() and m.countComponents()==1 and abs(m.BoundBox.ZMin)<1e-7
        g['export_bed_correction']={'initial_min_z_mm':old_z,'corrected_min_z_mm':m.BoundBox.ZMin,
                                    'native_source_unchanged':True,'reason':'R2 plate102..105, inherited R1 export used minus103; corrected derived mesh only'}
        g['stl_sha256']=sha(stl)
        theta=math.acos(1-13/30);r=15
        curves=[];checks=[]
        for y,od,name in ((-78.25,3,'factory16AWG_DESIGN'),(-71.75,2.5,'HELU23502_DESIGN')):
            start=A.Vector(20,y,96.15)
            middle=A.Vector(20+r*math.sin(theta),y,96.15+r*(1-math.cos(theta)))
            end=A.Vector(20+2*r*math.sin(theta),y,109.15)
            mid1=A.Vector(20+r*math.sin(theta/2),y,96.15+r*(1-math.cos(theta/2)))
            center=A.Vector(end.x,y,109.15-r)
            mid2=A.Vector(center.x-r*math.sin(theta/2),y,center.z+r*math.cos(theta/2))
            final=A.Vector(50,y,109.15)
            path=Part.Wire([Part.Arc(start,mid1,middle).toShape(),Part.Arc(middle,mid2,end).toShape(),Part.makeLine(end,final)])
            profile=Part.Wire([Part.makeCircle(od/2,start,A.Vector(1,0,0))])
            tube=path.makePipeShell([profile],True,False)
            assert tube.isValid() and len(tube.Solids)==1
            hits={'shelf':volume(tube.common(s)),'F_HY_design':volume(tube.common(box(p['shifted_F_HY_bbox_mm']))),
                  'WAGO_closed_design':volume(tube.common(box(p['connector_closed_bbox_mm'])))}
            assert all(v<1e-5 for v in hits.values()),hits
            tube.exportBrep(str(OUT/(name+'.brep')))
            checks.append({'name':name,'od_design_mm':od,'centerline_radius_mm':r,'length_to_connector_face_mm':path.Length,
                           'strip_allowance_mm':11,'minimum_factory_lead_length_mm':84.5 if name.startswith('factory') else None,
                           'factory_available_after_route_and_strip_mm':84.5-path.Length-11 if name.startswith('factory') else None,
                           'local_positive_hits_mm3':hits,'actual_factory_exit_and_connector_port_confirmed':False})
            curves.append(tube)
        assert volume(curves[0].common(curves[1]))<1e-6
    finally:A.closeDocument(d.Name)
    d=A.openDocument(str(ROOT/'hardware/cad/studies/deck-aux-wago-r5/DeckAuxWagoR5.FCStd'))
    try:
        deck=d.getObject('Deck').Shape
        probe=s.copy();probe.translate(A.Vector(0,0,.01))
        contact_estimate=volume(probe.common(deck))/.01
        assert contact_estimate>400,contact_estimate
        g['contact_positive_offset_probe']={'offset_mm':.01,'area_estimate_mm2':contact_estimate,'not_clamp_or_load_test':True}
    finally:A.closeDocument(d.Name)
    g['local_wire_design_checks']=checks
    g['shelf_inner_window_mm']=[26,12]
    g['local_wire_actual_pass']=False
    g['source_sha256']={str(q.relative_to(ROOT)).replace('\\','/'):sha(q) for q in (Path(__file__),ROOT/'tools/cad/aux_splice_shelf_r1.py',ROOT/'tools/cad/aux_splice_shelf_r2.py')}
    (OUT/'geometry.json').write_text(json.dumps(g,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'stl_z':m.BoundBox.ZMin,'local_design_paths':checks,'deck_contact_area_estimate':contact_estimate}))

if __name__=='__main__':main()
