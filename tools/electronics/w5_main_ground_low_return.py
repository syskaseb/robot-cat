"""Whole MAIN return below G2, preserving its received board approach.

The new route stays outside RL_P and cooling before crossing below the
G2body. Its R10 is a prototype allowance, not a supplier guarantee. Only
the copied MAIN tail may occupy the existing common boot; the new section
is tested against that boot too. The bare pad interface remains unchanged.
"""
from pathlib import Path
from datetime import datetime,timezone
import json
import math
import w5_received_central_scope as received
import w5_central_shared_routes as scope
from w5_s1_source_layout_r2 import CentreLine
from w5_parallel_connection import connect
from w5_bus_low_s_material import build
from servo_fuse_inputs_r1 import save,sha

OUT=scope.ROOT/'hardware/electronics/full-cat/w5-main-ground-low-return-r1'
BOOT='main-positive-complete-r8/MAIN_input_common_boot_DESIGN'


def recipe(family):
    start=family['ends']['W060']['edges'][0]['start']
    c=CentreLine(start,[0,1,0]);c.line([start[0],start[1]+6,start[2]])
    c.arc([0,0,-1],radius=10);c.arc([1,0,0],radius=10)
    pre_tail=[122.5,0,105]
    c.edges.extend(connect(c.p,pre_tail,[1,0,0],10));c.p=pre_tail;c.t=[1,0,0]
    c.arc([0,0,-1],radius=10)
    assert math.dist(c.p,[132.5,0,95])<1e-7 and math.dist(c.t,[0,0,-1])<1e-7
    return dict(wire='W060',edges=c.edges,OD_mm=3,radius_mm=10,
        start=start,target=c.p,radius_supplier_qualified=False,
        retained_tail_radius_bound_mm=6,retained_tail_not_R10=True)


def main():
    import FreeCAD as A,Part
    from main_input_return_r4 import M
    start=datetime.now(timezone.utc)
    assert not (OUT/'checks.json').exists()
    OUT.mkdir(parents=True,exist_ok=True)
    fixed,printed,ends,family,rows,pins,reused,replaced=received.load(A,Part)
    obstacles={**fixed,**{w:s for w,s in ends.items() if w!='W060'}}
    row=recipe(family);front_path,front_shape=build(A,Part,row)
    curve=Part.BezierCurve();curve.setPoles([A.Vector(*p) for p in M.POLES])
    tail_edge=curve.toShape();pad_edge=Part.makeLine(A.Vector(*M.POLES[-1]),A.Vector(*M.B.PAD))
    assert (front_path.Edges[-1].valueAt(front_path.Edges[-1].LastParameter)-tail_edge.valueAt(tail_edge.FirstParameter)).Length<1e-7
    assert (front_path.Edges[-1].tangentAt(front_path.Edges[-1].LastParameter)-tail_edge.tangentAt(tail_edge.FirstParameter)).Length<1e-7
    tail_bits=[]
    for edge,radius in ((tail_edge,1.5),(pad_edge,math.sqrt(.823/math.pi))):
        shape=Part.Wire([edge]).makePipeShell([Part.Wire([Part.makeCircle(radius,edge.valueAt(edge.FirstParameter),edge.tangentAt(edge.FirstParameter))])],True,False)
        assert shape.isValid() and len(shape.Solids)==1 and not shape.check(True)
        tail_bits.append(shape)
    front_hits=scope.contacts(front_shape,obstacles,Part)
    inherited_internal=[];tail_hits=[]
    for i,shape in enumerate(tail_bits):
        for hit in scope.contacts(shape,obstacles,Part):
            if hit['owner']==BOOT or (i==1 and hit['owner']=='MAIN/SupplierFamilyReference'):
                inherited_internal.append(dict(part=i,**hit,reason='unchanged received tail inside its boot / bare board pad'))
            else:tail_hits.append(dict(part=i,**hit))
    shape=Part.makeCompound([front_shape,*tail_bits]);path=Part.Wire([*front_path.Edges,tail_edge,pad_edge])
    files=[]
    for suffix,s in (('WORLD',shape),('CENTERLINE',path)):
        p=OUT/('W060_'+suffix+'.brep');s.exportBrep(str(p));files.append(p)
    finish=datetime.now(timezone.utc)
    pins += [Path(__file__),Path(scope.__file__),Path(received.__file__),
        scope.ROOT/'tools/electronics/w5_bus_low_s_material.py',scope.ROOT/'tools/electronics/w5_parallel_connection.py',
        scope.ROOT/'tools/electronics/w5_s1_source_layout_r1.py',scope.ROOT/'tools/electronics/w5_s1_source_layout_r2.py',
        scope.ROOT/'tools/electronics/main_input_return_r4.py',scope.ROOT/'tools/electronics/main_input_return_r3.py',
        scope.ROOT/'tools/electronics/main_input_return_r1.py',scope.ROOT/'tools/electronics/w5_exact_separation.py']
    save(OUT/'checks.json',dict(status='WHOLE_MAIN_GROUND_LOW_RETURN',recipe=row,front_hits=front_hits,
        retained_tail_foreign_hits=tail_hits,retained_tail_internal_contacts=inherited_internal,
        complete=not front_hits and not tail_hits,errors=[],body_mm=path.Length,nominal_mm=path.Length+17,
        trial_blank_mm=math.ceil((path.Length+17+30)/10)*10,retained_MAIN_poles=M.POLES,retained_MAIN_pad=M.B.PAD,
        printed_pending=sorted(printed),replacement_obligations=replaced,native_complete=False,selected=False,physical_pass=False,
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds(),
        source_sha256={p.relative_to(scope.ROOT).as_posix():sha(p) for p in dict.fromkeys(pins)},
        files={p.relative_to(scope.ROOT).as_posix():sha(p) for p in files}))
    print('MAIN_GROUND_LOW_DONE',len(front_hits),len(tail_hits),round(path.Length,3),flush=True)


if __name__=='__main__':main()
