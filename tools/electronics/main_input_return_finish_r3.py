"""Final W060 strap reserve, no further native rebuild or circuit change.

An explicit small soft-insulation envelope contact remains provisional;
never label it collision-free or physical PASS. All rigid hits must clear.
"""
from datetime import datetime,timezone
import json,sys
from pathlib import Path
import main_input_return_r4 as R4
import body_ground_routes_r1 as M
R=R4.M;ROOT=M.ROOT
PRIOR=ROOT/'hardware/electronics/full-cat/main-input-return-finish-r2'
NATIVE=ROOT/'hardware/cad/studies/main-input-return-finish-r2'
OUT=ROOT/'hardware/electronics/full-cat/main-input-return-finish-r3'
CAD=ROOT/'hardware/cad/studies/main-input-return-finish-r3'
DECK_BREP=NATIVE/'Deck_WORLD.brep'
DECK_NATIVE=NATIVE/'DeckMainInput.FCStd'
DECK_CHECKS=None

def main():
    import FreeCAD as A
    import Part,MeshPart
    OUT.mkdir(exist_ok=True);CAD.mkdir(exist_ok=True);assert not (OUT/'checks.json').exists()
    begin=datetime.now(timezone.utc);prior=json.loads((PRIOR/'checks.json').read_text(encoding='utf-8'))
    assert all(v['relocated_reopen'] and v['strict_BOP_errors']==0 for v in prior['native_checks'].values())
    def load(p):s=Part.Shape();s.read(str(p));return s
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    deck=load(DECK_BREP);mount=load(NATIVE/'MAINMount_WORLD.brep')
    new=[box([126.75,-2.7,77,129.25,-1.5,94.4]),box([126.75,6,77,129.25,7.2,94.4]),
         box([126.75,-1.5,77,129.25,6,78.2]),box([126.75,-1.5,93.2,129.25,6,94.4]),box([125,7.2,92.2,131,12.2,96.2])]
    bands={f'MAIN_input_tie_{i}':s for i,s in enumerate(new)}
    owners,hashes=R.current_owners();owners.pop('Deck_R38');owners.pop('MAIN/Adapter')
    owners.update(NewDeck=deck,NewMAINMount=mount)
    for p in R.OUT.glob('W060_*_DESIGN.brep'):owners[p.stem]=load(p)
    for name in ('W060_neck_inner','W060_input_outer_boot'):owners[name]=load(NATIVE/(name+'_WORLD.brep'))
    rows=[r for r in prior['rows'] if not r['part'].startswith('MAIN_input_tie_')]
    for n,s in bands.items():
        for m,t in owners.items():
            for i,q in enumerate(s.Solids):
                for j,v in enumerate(t.Solids):
                    if q.BoundBox.intersect(v.BoundBox):rows.append(dict(part=n,owner=m,solid=i,owner_solid=j,hit_mm3=q.common(v).Volume))
    hits=[r for r in rows if r['hit_mm3']>1e-5]
    contact=[r for r in hits if r['part']=='W060_input_outer_boot' and r['owner']=='hardware/electronics/full-cat/pi-power-usb-r4/PI_GND_0_DESIGN.brep' and r['hit_mm3']<.2]
    blocking=[r for r in hits if r not in contact]
    for n,s in bands.items():s.exportBrep(str(CAD/(n+'_WORLD.brep')))
    end=datetime.now(timezone.utc)
    result=dict(status='REJECTED' if blocking else 'W060_READY_WITH_SOFT_CONTACT_RESERVE',
        hits=hits,blocking_hits=blocking,nominal_soft_contacts=contact,rows=rows,native_checks=prior['native_checks'],
        collision_free=False,geometry_gate='open' if contact else 'pass',
        contact_rule='Only this soft insulated sleeve/cable allowance. No bare copper, rigid support, fuse, connector or clamp interference accepted.',
        phase2_adjustment='Dry-fit actual OD and sleeve wall, trim15mm allowance to nominal8.01mm placement with >=6mm overlap. Gently separate insulated leads before tie tightening; do not bend on solder or defeat R6. If unavailable, replace this short removable input lead/sleeve, not P0.',
        route_length_mm=prior['route_length_mm'],nominal_blank_mm=220,outer_boot_intact_overlap_mm=prior['outer_boot_intact_overlap_mm'],
        source_sha256={**hashes,(PRIOR/'checks.json').relative_to(ROOT).as_posix():M.sha(PRIOR/'checks.json')},
        script_sha256=M.sha(Path(__file__)),replaced_print_jobs=2,new_print_jobs=0,
        physical_pass=False,W5_complete=False,started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds())
    if DECK_CHECKS:
        result['native_checks']['Deck']=json.loads(DECK_CHECKS.read_text(encoding='utf-8'))
        result['source_sha256'][DECK_CHECKS.relative_to(ROOT).as_posix()]=M.sha(DECK_CHECKS)
    for p in (DECK_BREP,DECK_NATIVE):result['source_sha256'][p.relative_to(ROOT).as_posix()]=M.sha(p)
    for p in NATIVE.iterdir():
        if p.is_file() and p.suffix in ('.FCStd','.brep'):result['source_sha256'][p.relative_to(ROOT).as_posix()]=M.sha(p)
    result['mesh_export_complete']=False
    M.save(OUT/'checks.json',result)
    if not blocking:
        dims={}
        mesh_checks={}
        for n,s in [('Deck',deck),('MAIN',mount)]:
            refined=s
            assert refined.isValid() and len(refined.Solids)==1
            assert abs(refined.Volume-s.Volume)<1e-5
            mesh=MeshPart.meshFromShape(Shape=refined,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
            mesh_checks[n]=dict(native_volume_mm3=s.Volume,refined_volume_mm3=refined.Volume,
                closed=mesh.isSolid(),components=mesh.countComponents(),refinement_geometry_unchanged=True)
            result['mesh_checks']=mesh_checks;M.save(OUT/'checks.json',result)
            assert mesh.isSolid() and mesh.countComponents()==1,mesh_checks[n]
            b=mesh.BoundBox;mesh.translate(-b.XMin,-b.YMin,-b.ZMin)
            dims[n]=[mesh.BoundBox.XLength,mesh.BoundBox.YLength,mesh.BoundBox.ZLength];assert max(dims[n])+10<=256
            mesh.write(str(CAD/(n+'_x1.stl')))
        result['dimensions_mm']=dims;result['mesh_export_complete']=True
    M.save(OUT/'checks.json',result)
    iface=json.loads((PRIOR/'interface.json').read_text(encoding='utf-8'))
    iface.update(status=result['status'],restraints_complete=not blocking,new_STL=2 if not blocking else 0,
        soft_contact_condition=result['phase2_adjustment'],nominal_soft_contacts=contact,collision_free=False,
        tie_MAIN_rule='Reserve moved toX128 beyond the root post; lower77/top94.4 encloses sloped wire without crossing it. Loose reserve, actual flexible wrap/tightening phase2.',
        insulation_blank_trimming='4mm inner blank trimmed to2mm neck;15mm outer allowance trimmed OFF PCB to actual placement, nominal8.01mm, >=6mm intact overlap. Do not assume15mm shrinks to8mm.',
        native_sources={'Deck':DECK_NATIVE.relative_to(ROOT).as_posix(),'MAIN':(NATIVE/'MainInputMount.FCStd').relative_to(ROOT).as_posix()})
    M.save(OUT/'interface.json',iface)
    geo=json.loads((PRIOR/'preview-geometry.json').read_text(encoding='utf-8'))
    geo=[r for r in geo if not r['name'].startswith('MAIN_input_tie_')]
    for n,s in bands.items():
        vs,ts=s.tessellate(.4);geo.append(dict(name=n,vertices=[list(v) for v in vs],triangles=ts))
    M.save(OUT/'preview-geometry.json',geo)
    print(json.dumps(dict(status=result['status'],blocking_hits=blocking,soft_contacts=contact,pairs=len(rows))),flush=True)

if __name__=='__main__':
    sys.path.insert(0,str(ROOT/'tools/cad'));main()
