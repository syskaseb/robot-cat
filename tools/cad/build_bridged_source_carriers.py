"""Native histories for the received exact below-band carrier gate only."""
import json,time,zipfile
from pathlib import Path
import build_complete_source_carriers as B
P=B.P


def contact_area(a,b):
    # Solid.common(solid) discards a merely touching face in this OCC build:
    # two10mm cubes share100mm2, but their solid Boolean hasArea0/Volume0.
    # Measure exact FACE intersections, never infer area from distance0.
    bounds=B.ImmutableBounds();area=0
    for f in a.Faces:
        for g in b.Faces:
            if bounds.near(f,g,1e-6) and f.distToShape(g)[0]<1e-6:
                area+=f.common(g).Area
    return area


def run():
    tick=time.monotonic();gf=P.OUT/'source-carrier-port-bridges-material.json';g=json.loads(gf.read_text())
    assert g['status']=='SOURCE_CARRIER_PORT_BRIDGES_ACTUAL_CLEAR_NATIVE_OPEN' and not g['contacts'] and not g['errors']
    for n,h in g['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    fp=P.OUT/'leg-source-near-member-plan.json';family=json.loads(fp.read_text());cp=json.loads((P.OUT/'complete-source-carriers-plan.json').read_text())
    with zipfile.ZipFile(P.ROOT/'hardware/simulation/v35/inputs.zip') as z:members=json.loads(z.read('geometry.json'))['components']
    reader=B.H.P.SavedShapes();targets,_,_,_,_=B.current_scene(reader)
    shapes,codes,_,_=B.allocation(cp,family,targets,members);recipes={};areas=[]
    for n,r in g['recipes'].items():
        pads=r['pads'];cuts=list(r['cuts'])
        # An annular XY pocket is exactly the union of these four disjoint
        # rectangular strips. This reuses the existing native sketch builder.
        for ring in r['ring_cuts']:
            x,y,z,X,Y,Z=ring['outer'];a,b,_,c,d,_=ring['inner']
            cuts += [[x,y,z,X,b,Z],[x,d,z,X,Y,Z],[x,b,z,a,d,Z],[c,b,z,X,d,Z]]
        s=P.box(pads[0]['bounds_mm'])
        for row in pads[1:]:s=s.fuse(P.box(row['bounds_mm'])).removeSplitter()
        for v in cuts:s=s.cut(P.box(v)).removeSplitter()
        assert s.isValid() and len(s.Solids)==1 and not s.check(True),n
        shapes[n]=s;recipes[n]=dict(pads=pads,cuts=cuts)
        root=next(q for q in cp['roots'] if q['leg']+'SourceCarrier'==n)
        bond=shapes[root['leg']+'SourceCaseBond'];case=targets['P0_'+root['case']]
        ca=bond.common(case);cb=s.common(bond)
        case_area=contact_area(bond,case);cap_area=contact_area(s,bond)
        assert ca.Volume<1e-5 and cb.Volume<1e-5 and case_area>1 and cap_area>1,(n,'point-only root')
        areas.append(dict(part=n,bond_case_area_mm2=case_area,carrier_bond_area_mm2=cap_area))
        print('native carrier root face',areas[-1],flush=True)
    B.native(recipes,shapes,codes,g,gf,tick)
    rf=P.OUT/'complete-source-carriers-native.json';receipt=json.loads(rf.read_text())
    receipt['root_contact_faces']=areas
    receipt['source_sha256'][Path(__file__).relative_to(P.ROOT).as_posix()]=P.SHA(Path(__file__))
    receipt['port_interface']='Twelve unchanged9mm wire lands, below-band bridges and actual band/head clearance pockets'
    rf.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':run()
