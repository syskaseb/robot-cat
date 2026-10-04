"""One common source-cage access layout: native Carrier and Cover openings.

No block, source wire, restraint or roof mount moves. Supplier PDFs give
closed-body dimensions, not hinge datums: opening sectors and finger space
are explicit prototype allowances. Delivered lever/hand fit is phase2.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, math, shutil, tempfile
from servo_fuse_inputs_r1 import save, sha

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'hardware/electronics/full-cat/w5-source-cage-access-native-r1'
CAD = ROOT/'hardware/cad/studies/w5-source-cage-access-native-r1'
PARENTS = [ROOT/'hardware/cad/studies/w5-source-grips-native-r2/SourceCarrierInsulationGrips.FCStd',
           ROOT/'hardware/cad/studies/w5-source-roof-native-r5/SourceProtectiveHoods.FCStd']
WINDOWS = {
    'Carrier': [(-91.5,4,139.8,-47.5,32,171.5), (-46,-14,139.8,-2,14,171.5), (7,-22,139.8,35,22,171.5)],
    'Cover': [(-91.5,10.5,118,-47.5,31,240), (-46,-14,118,-2,14,240), (7,-22,118,35,22,240)],
}


def main():
    import FreeCAD as A, Part, MeshPart
    from w5_source_grips_native_r1 import current_owners
    begin=datetime.now(timezone.utc); assert not (OUT/'checks.json').exists()
    OUT.mkdir(parents=True,exist_ok=True); CAD.mkdir(parents=True,exist_ok=True)
    parents=[A.openDocument(str(p)) for p in PARENTS]
    d=A.newDocument('SourceCageServiceWindows'); target=CAD/'SourceCageServiceWindows.FCStd'; d.saveAs(str(target))
    par=d.addObject('App::VarSet','AccessParameters'); par.addProperty('App::PropertyLength','ExtraClearance'); par.ExtraClearance=0
    finals={}; original={}
    for label,parent,objname in (('Carrier',parents[0],'SourceGripsFinished'),('Cover',parents[1],'SourceRoofCoverFinished')):
        link=d.addObject('App::Link','Received'+label); link.setLink(parent.getObject(objname)); link.LinkPlacement=parent.getObject(objname).Placement
        original[label]=link.Shape.copy(); tools=[]
        for i,b in enumerate(WINDOWS[label]):
            q=d.addObject('Part::Box',label+'ServiceWindow'+str(i))
            q.Length=b[3]-b[0]; q.Width=b[4]-b[1]; q.Height=b[5]-b[2]; q.Placement.Base=A.Vector(*b[:3])
            q.setExpression('Length',str(b[3]-b[0])+' mm + 2 * AccessParameters.ExtraClearance')
            q.setExpression('Width',str(b[4]-b[1])+' mm + 2 * AccessParameters.ExtraClearance')
            q.setExpression('Placement.Base.x',str(b[0])+' mm - AccessParameters.ExtraClearance')
            q.setExpression('Placement.Base.y',str(b[1])+' mm - AccessParameters.ExtraClearance')
            tools.append(q)
        c=d.addObject('Part::Compound',label+'AccessTools'); c.Links=tools
        f=d.addObject('Part::Cut','SourceAccess'+label+'Finished'); f.Base=link; f.Tool=c; f.Refine=False; finals[label]=f
    print('SOURCE_ACCESS_NATIVE_RECOMPUTE',flush=True); d.recompute(); d.save()
    volumes={label:f.Shape.Volume for label,f in finals.items()}
    assert all(f.Shape.isValid() and len(f.Shape.Solids)==1 for f in finals.values())
    assert all(volumes[label]<original[label].Volume for label in finals)
    # Preserve all four existing source seats and all four roof posts exactly.
    added_seats=Part.read(str(ROOT/'hardware/electronics/full-cat/w5-source-grips-native-r2/ADDED_SEATS_WORLD.brep'))
    added_posts=Part.read(str(ROOT/'hardware/electronics/full-cat/w5-source-roof-native-r3/AddedPosts_WORLD.brep'))
    for label,protected in (('Carrier',added_seats),('Cover',added_posts)):
        for b in WINDOWS[label]:
            tool=Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
            for solid in protected.Solids:
                if solid.BoundBox.intersect(tool.BoundBox):
                    assert solid.common(tool).Volume<1e-5,(label,'changed bearing or source seat')
    par.ExtraClearance=.2; d.recompute(); assert all(f.Shape.Volume<volumes[label] for label,f in finals.items())
    par.ExtraClearance=0; d.recompute(); assert all(abs(f.Shape.Volume-volumes[label])<1e-5 for label,f in finals.items()); d.save()
    owners,pins=current_owners(A,Part); owners['SourceCarrier']=finals['Carrier'].Shape.copy(); owners['SourceCover']=finals['Cover'].Shape.copy()
    for wire in ('W064','W065','W067','W068'):
        p=ROOT/f'hardware/electronics/full-cat/w5-source-grips-native-r2/{wire}_T18I_WORLD.brep'; owners[wire+'_band']=Part.read(str(p)); pins.append(p)
    for key in ('source-switch-restraints-r2/P_SYS_seat_DESIGN','source-switch-restraints-r2/P_SYS_tie_DESIGN'):
        owners.pop(key)
    hits=[]; errors=[]; pairs=0; access=[]
    def check(label,s,own):
        nonlocal pairs
        for key,t in owners.items():
            if key==own: continue  # own purchased-body hinge/contact only
            for a in s.Solids:
                for b in t.Solids:
                    if not a.BoundBox.intersect(b.BoundBox): continue
                    pairs+=1
                    try:
                        v=a.common(b).Volume
                        if v>1e-5: hits.append(dict(access=label,owner=key,mm3=v))
                    except Exception as exc: errors.append(dict(access=label,owner=key,error=str(exc)))
    for label,own,z,slots in (
        ('P_SYS','P_SYS_received',142,[(x,18,x,11,0,1) for x in (-84,-76.5,-69,-61.5,-54)]),
        ('P_FRONT','P_FRONT_design',120,[(x,0,x,7,0,-1) for x in (-39,-31.5,-24,-16.5,-9)]),
        ('P_REAR','P_REAR_selected_raised_design',135,[(21,y,28,y,-1,0) for y in (-13.6,-6.8,0,6.8,13.6)])):
        for i,(cx,cy,px,py,dx,dy) in enumerate(slots):
            pivot=A.Vector(px,py,z+.05)
            def point(a): return pivot+A.Vector(dx*14*math.cos(a),dy*14*math.cos(a),14*math.sin(a))
            a,m,b=[point(math.radians(angle)) for angle in (0,55,110)]
            face=Part.Face(Part.Wire([Part.makeLine(pivot,a),Part.Arc(a,m,b).toShape(),Part.makeLine(b,pivot)]))
            side=A.Vector(2.5 if dy else 0,2.5 if dx else 0,0)
            sector=face.extrude(side*2); sector.translate(-side)
            finger=Part.makeCylinder(6,240-z,A.Vector(cx,cy,z+.1))
            before=len(hits)+len(errors); check(label+str(i)+'_lever_allowance',sector,own); check(label+str(i)+'_finger_allowance',finger,own)
            access.append(dict(block=label,slot=i+1,prototype_sector_and_finger_clear=len(hits)+len(errors)==before,
                               supplier_hinge_measured=False))
        print('SOURCE_CAGE_ACCESS',label,pairs,len(hits),len(errors),flush=True)
    dims={}; closed=False; reopened=False
    for label,f in finals.items():
        f.Shape.exportBrep(str(CAD/(label+'_WORLD.brep')))
    if not hits and not errors:
        for label,f in finals.items():
            mesh=MeshPart.meshFromShape(Shape=f.Shape,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
            assert mesh.isSolid() and mesh.countComponents()==1
            bb=mesh.BoundBox; dims[label]=[bb.XLength,bb.YLength,bb.ZLength]
            brim=6 if label=='Carrier' else 10
            assert bb.XLength+brim<=256 and bb.YLength+brim<=256 and bb.ZLength<=256
            mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin); mesh.write(str(CAD/(label+'_UNSELECTED_x1.stl')))
        closed=True
    deps=list(dict.fromkeys(Path(q.FileName) for q in A.listDocuments().values() if q.FileName and Path(q.FileName)!=target))
    for name in list(A.listDocuments()): A.closeDocument(name)
    if not hits and not errors:
        with tempfile.TemporaryDirectory(prefix='robot-cat-source-access-') as td:
            tmp=Path(td)
            for p in [target,*deps]:
                dest=tmp/p.relative_to(ROOT); dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,dest)
            rd=A.openDocument(str(tmp/target.relative_to(ROOT))); rd.recompute()
            assert all(abs(rd.getObject('SourceAccess'+label+'Finished').Shape.Volume-volumes[label])<1e-5 for label in finals)
            assert all(Path(q.FileName).is_relative_to(tmp) for q in A.listDocuments().values()); reopened=True
    pins += [Path(__file__),*PARENTS,*deps,
             ROOT/'hardware/electronics/full-cat/w5-source-grips-native-r2/ADDED_SEATS_WORLD.brep',
             ROOT/'hardware/electronics/full-cat/w5-source-roof-native-r3/AddedPosts_WORLD.brep',
             ROOT/'hardware/reference/power-distribution-2026-09-23/WAGO-221-615.pdf']
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='SOURCE_CAGE_ACCESS_NATIVE_PROVISIONAL_CLEAR' if not hits and not errors else 'SOURCE_CAGE_ACCESS_REJECTED',
        pairs=pairs,hits=hits,errors=errors,ports=access,windows_mm=WINDOWS,
        parameter_probe_mm=[0,.2,0],solids_per_part=1,closed_STLs=closed,relocated_reopen=reopened,
        final_valid=True,full_final_strict_BOP_tested=False,subtractive_no_added_material=True,
        protected_Carrier_seats_and_roof_posts_preserved=True,dimensions_mm=dims,
        prototype_allowance=dict(sector_radius_mm=14,angle_deg=110,width_mm=5,finger_diameter_mm=12,
                                supplier_dimensioned_hinge=False,actual_hand_and_lever_fit_phase2=True),
        print_notes='Carrier world+Zup; Cover pinned native export on original base, brim5. Phase2 supports/service-edge deburr, PETG bearing/creep and delivered lever fit. No slicer or strength claim.',
        new_prints=0,replacement_prints=2,new_fasteners=0,all_source_routes_and_restraints_unchanged=True,
        whole_source_assembly_complete=False,selected=False,W5_complete=False,physical_pass=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in dict.fromkeys(pins)},
        files={p.relative_to(ROOT).as_posix():sha(p) for p in CAD.iterdir() if p.suffix in ('.FCStd','.brep','.stl')},
        started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds()))


if __name__=='__main__': main()
