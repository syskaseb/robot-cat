"""Two current nominal bottleneck certificates before another routing attempt."""
import json,os,time
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from feline_output_composed_context import compose
from compose_feline_output_boundaries import current,cap_at
from feline_selected_material_contract import load as profiles
from feline_terminal_escape import bound


def main():
    tick=time.monotonic();base,ends,files=current();index={r['id']:r for r in ends};contract,pf,bf=profiles()
    _,parts,meta,pins,_=compose();rows=[]
    for wire,owner,y in (('W045','CurrentFoundation:BankPier:4',32.),('W053','PiBudget:AdapterBody',51.5)):
        e=index[wire+'/custom/end'];q=np.asarray(e['routing_exit_mm']);d=np.asarray(e['routing_exit_axis']);assert np.linalg.norm(d-[0,-1,0])<1e-6
        p=A.Vector(q[0],y,q[2]);solid=parts[owner];assert solid.isValid() and len(solid.Solids)==1
        inside=solid.isInside(p,1e-7,True);boundary=Part.makeCompound(solid.Faces)
        distance=Part.Vertex(p).distToShape(boundary)[0];signed=-distance if inside else distance
        profile=contract['portions'][wire+'/custom'];r=bound(profile['minimum_project_R_mm'],q[1]-y,signed,profile['project_radius_mm'])
        r.update(wire=wire,endpoint=e['id'],current_actual_cap_mm=q.tolist(),outward_axis=d.tolist(),owner=owner,
            axial_witness_mm=list(p),axis_point_inside_actual_closed_material=inside,
            source_kind=meta[owner].get('kind'),nominal_budget_not_supplier_delivered_claim=True)
        rows.append(r);print(wire,owner,json.dumps(r),flush=True)
    sources=(*files,pf,bf,Path(__file__),ROOT/'tools/cad/feline_terminal_escape.py',ROOT/'tools/cad/feline_selected_material_contract.py')
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in sources})
    result=dict(status='TWO_CURRENT_TERMINAL_ESCAPE_BOUNDS_RECEIVED_NOT_WHOLE_N01',rows=rows,source_sha256=pins,
        conclusion='Change own support or pre-grip terminal fan topology if bound rejects; do not search more middle curves from the same cap/axis',
        selected_bought_parts_unchanged=True,physical_pass=False,N01_complete=False,worker_seconds=round(time.monotonic()-tick,3))
    save_json(OUT/'n01-terminal-escape-bottlenecks.json',result)
    print('Worker seconds',result['worker_seconds'],flush=True)


if __name__=='__main__':print('WORKER_PID',os.getpid(),flush=True);main()
