"""Independent triangle check of inherited shell and new AUX passages. No repair.

Export with FreeCAD Python; --check with trimesh/manifold Python. Intermediate
STLs are diagnostic only, not robot print assets.
"""
from pathlib import Path
import hashlib
import json
import sys
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'hardware/skorupa/v35'
BASE=OUT/'shape-cache/mesh-proof-final'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def export():
    import FreeCAD as A
    import Part
    import MeshPart
    from aux35 import MASTER,SOURCE,SOURCE_SHA,ADDITIONS,instance
    master_digest=sha(MASTER);d=A.openDocument(str(MASTER))
    BASE.mkdir(parents=True,exist_ok=True)
    old=Part.Shape();old.read(str(SOURCE/'shape-cache/ShellMounted20.brep'))
    shapes={'SourceShell':old,'Shell35':instance(d,'Shell35')}
    deck=Part.Shape();deck.read(str(SOURCE/'shape-cache/Part__Feature038.brep'))
    shapes.update(SourceDeck=deck,Deck35=instance(d,'Deck35'))
    for n,(src,parent,material,xyz) in ADDITIONS.items():
        if n.startswith(('AuxPost35_','AuxGap35_','AuxBolt35_','AuxNut35_')):
            shapes[n]=instance(d,src,xyz)
    shapes['AuxEnvelope']=Part.makeBox(40.64,20.32,11.5748,A.Vector(89.2,-24,52))
    for i,x in enumerate([75.54,131.5]):shapes['Wire'+str(i)]=Part.makeBox(12,10,6,A.Vector(x,-18.8,55))
    rows=[]
    for n,s in shapes.items():
        print('MESH',n,flush=True)
        is_shell=n in ('SourceShell','Shell35')
        mesh=MeshPart.meshFromShape(Shape=s if is_shell else s.cleaned(),LinearDeflection=.03 if is_shell else .005,AngularDeflection=.1 if is_shell else .03,Relative=False)
        p=BASE/(n+'.stl');mesh.write(str(p))
        rows.append(dict(name=n,sha256=sha(p),brep_volume_mm3=s.Volume,linear_deflection_mm=.03 if is_shell else .005,angular_deflection_rad=.1 if is_shell else .03))
    assert sha(MASTER)==master_digest
    (BASE/'index.json').write_text(json.dumps(dict(master_sha256=master_digest,source_checkpoint_sha256=SOURCE_SHA,
        meshes=rows),indent=2),encoding='utf8',newline='\n')

def check():
    import trimesh
    import numpy as np
    index=json.loads((BASE/'index.json').read_text())
    assert sha(OUT/'AuxPower35.FCStd')==index['master_sha256']
    meshes={};rows=[]
    for r in index['meshes']:
        p=BASE/(r['name']+'.stl');assert sha(p)==r['sha256']
        m=trimesh.load_mesh(p,process=True);meshes[r['name']]=m
        counts=np.bincount(m.edges_unique_inverse,minlength=len(m.edges_unique))
        row=dict(r,is_volume=bool(m.is_volume),watertight=bool(m.is_watertight),winding=bool(m.is_winding_consistent),
                 nonmanifold_edges=int(sum(counts!=2)),mesh_volume_mm3=float(m.volume))
        rows.append(row);print(row,flush=True)
    intersections=[]
    if all(r['is_volume'] and r['nonmanifold_edges']==0 for r in rows):
        for n in meshes:
            if n in ('SourceShell','Shell35','SourceDeck','Deck35'):continue
            m=trimesh.boolean.intersection([meshes['Shell35'],meshes[n]],engine='manifold',check_volume=True)
            intersections.append(dict(parts=['Shell35',n],volume_mm3=float(m.volume)))
        added=trimesh.boolean.difference([meshes['Shell35'],meshes['SourceShell']],engine='manifold',check_volume=True)
        removed=trimesh.boolean.difference([meshes['SourceShell'],meshes['Shell35']],engine='manifold',check_volume=True)
        delta=dict(added_mm3=float(added.volume),removed_mm3=float(removed.volume))
        added_deck=trimesh.boolean.difference([meshes['Deck35'],meshes['SourceDeck']],engine='manifold',check_volume=True)
        removed_deck=trimesh.boolean.difference([meshes['SourceDeck'],meshes['Deck35']],engine='manifold',check_volume=True)
        deck_delta=dict(added_mm3=float(added_deck.volume),removed_mm3=float(removed_deck.volume))
    else:delta=None;deck_delta=None
    passed=(bool(intersections) and all(r['volume_mm3']<.02 for r in intersections)
            and delta is not None and deck_delta is not None and deck_delta['added_mm3']<.01
            and abs(deck_delta['removed_mm3']-13.5716802635)<.01)
    report=dict(master_sha256=index['master_sha256'],source_checkpoint_sha256=index['source_checkpoint_sha256'],
        meshes=rows,intersections=intersections,subtractive_change=delta,deck_subtractive_change=deck_delta,
        required_clearance_passed=passed,shell_mesh_difference_gate_passed=bool(delta and delta['added_mm3']<.5),
        shell_mesh_difference_gate_limit_mm3=.5,mechanical_release=False,
        shell_difference_note='The coarse global shell difference remains a separate failed/uncertain diagnostic, NOT reclassified as clearance success. Exact BRep subtractive check is independently required for shell. Cleaned 0.005mm global shell remesh was stopped for excessive runtime/memory; no fine-shell result claimed.',
        scope=__doc__,method='trimesh process=True (merge coincident STL vertices), manifold boolean, no hole filling, welding tolerance changes or repair')
    (OUT/'mesh-proof.json').write_text(json.dumps(report,indent=2),encoding='utf8',newline='\n')
    print(json.dumps(report,indent=2),flush=True)
    assert passed,'Independent mesh proof incomplete; keep report'

if __name__=='__main__':
    check() if '--check' in sys.argv else export()
