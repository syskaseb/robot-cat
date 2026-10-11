"""Whole24-end bank boundary assessment before detailed input/leg routing.

R47 purchased holders/ends remain; old bank plastics are not retained CP2
mounts. Identify actual existing material blocking nominal axial departures.
This does not select reliefs, qualify factory wire, or award W5.
"""
import json,time
from pathlib import Path
from current_body_harness_context import ROOT,OUT,W,Part,context,clipped

def run():
    tick=time.monotonic();source=OUT/'owner-plan.json';p=json.loads(source.read_text())
    ends={}
    for row in p['body_conductors']:
        for e in row['historical_ends']:
            n=e.get('native','') or ''
            if n.startswith(('F_L','F_R')) and n.endswith(('_CP2_IN','_CP2_OUT')):
                assert n not in ends,n
                ends[n]=e
    assert len(ends)==24
    reader,pins,targets,retained=context();pins.update((Path(__file__),source))
    r=dict(status='WHOLE_BANK_BOUNDARY_ASSESSMENT_ONLY',selected=False,W5_complete=False,physical_pass=False,
      end_count=24,departures=[],contacts=[],pairs=0,
      output_wire_OD_basis='2.1mm provisional envelope ONLY, delivered34172 OD/area remain unknown',
      input_wire_OD_basis='LAPP0107001 nominal3.1mm;9mm straight grip is project requirement, not a manufacturer seating datum',
      preserved='All selected W1/head/tail/E2 and source guides; no material changed or contact masked',
      open=['Choose one whole bank/foundation relief and retention load path before routing','Actual supplier seating, crimps and delivered cable fit','All native parts, full routing/service/stock'])
    bounds=lambda s:[s.BoundBox.XMin,s.BoundBox.YMin,s.BoundBox.ZMin,s.BoundBox.XMax,s.BoundBox.YMax,s.BoundBox.ZMax]
    for n,e in sorted(ends.items()):
        start=e['point_mm'];axis=e['departure'];end=[a+9*b for a,b in zip(start,axis)]
        c=Part.Wire([Part.makeLine(W.A.Vector(*start),W.A.Vector(*end))]);rr=1.55 if n.endswith('_IN') else 1.05
        assert n in targets,n
        r['departures'].append(dict(name=n,mouth_mm=start,axis=axis,straight_end_mm=end,
          nominal_radius_mm=rr,actual_terminal_box_mm=bounds(targets[n]),mouth_material_distance_mm=Part.Vertex(W.A.Vector(*start)).distToShape(targets[n])[0]))
        for m,t in targets.items():
            if not t.Solids:continue
            cc=clipped(c,True,3) if m==n else c
            if not W.near(cc,t,rr):continue
            assert t.isValid() and cc.isValid(),(n,m)
            r['pairs']+=1;d,pairs,_=cc.distToShape(t)
            if d<rr-1e-4:
                r['contacts'].append(dict(a=n,b=m,distance_mm=d,required_mm=rr,
                  obstacle_box_mm=bounds(t),witness_mm=[list(v) for v in pairs[0]] if pairs else None))
        for m,(t,rad) in retained.items():
            if not W.near(c,t,rr+rad):continue
            r['pairs']+=1;d,pairs,_=c.distToShape(t)
            if d<rr+rad-1e-4:r['contacts'].append(dict(a=n,b=m,distance_mm=d,required_mm=rr+rad))
    r['worker_seconds']=round(time.monotonic()-tick,3)
    r['source_sha256']={**reader.hashes,**{x.relative_to(ROOT).as_posix():W.sha(x) for x in pins}}
    (OUT/'bank-boundary-assessment.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(ends=24,pairs=r['pairs'],contacts=r['contacts'],seconds=r['worker_seconds'])),flush=True)

if __name__=='__main__':run()
