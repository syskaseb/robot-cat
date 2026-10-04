"""One complete XA05 corridor above the fixed rear terminal blocks.

Preserve bought blocks/P0 and both selected endpoints. Source endpoint S-bend
starts at G2; auxiliary endpoint descends before its original G_AUX mouth.
This is a changed-interface check, not a new bank or whole-robot audit.
"""
from datetime import datetime,timezone
from pathlib import Path
import sys,json,math
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics'),str(ROOT/'tools/cad')]
from servo_fuse_inputs_r1 import save,sha
from w5_s1_source_layout_r2 import CentreLine,add,mul,Y,Z,X
OUT=ROOT/'hardware/electronics/full-cat/w5-xa05-joint-repair-r1'


class Path15(CentreLine):
    def arc(self,normal,angle=math.pi/2,radius=15):
        return super().arc(normal,angle,radius)

    def shift(self,delta):
        from w5_s1_source_layout_r1 import norm,dot
        h=norm(delta);assert 0<h<30 and abs(dot(self.t,delta))<1e-8
        n=mul(delta,1/h);t=list(self.t);a=math.acos(1-h/30)
        self.arc(n,a);self.arc(add(mul(t,math.sin(a)),mul(n,-math.cos(a))),a)


def layout():
    c=Path15([123,9.5,113.5],Y)
    c.shift([0,0,17.5]);c.arc(mul(X,-1))
    c.line([79,c.p[1],131]);c.arc(mul(Y,-1))
    c.line([64,-42,131]);c.arc(X);c.shift([0,0,-17.5])
    c.line([110.5,-57,113.5])
    assert math.dist(c.p,[110.5,-57,113.5])<1e-7
    return dict(wire='XA05',a='P0G2.5',b='G_AUX.1',edges=c.edges,
        wire_SKU='HELU23501',OD_mm=2.5,min_fixed_R_mm=15,
        path_mm=sum(e['length_mm'] for e in c.edges),actual_cut_mm=None,
        nominal_trial_blank_mm=math.ceil((sum(e['length_mm'] for e in c.edges)+82)/10)*10,
        ends_preserved=True,blocks_unchanged=True,selected=False,physical_pass=False)


def main():
    import FreeCAD as A
    import Part
    from w5_r53_owners import installed
    begin=datetime.now(timezone.utc);assert not (OUT/'checks.json').exists()
    OUT.mkdir(parents=True,exist_ok=True);intent=layout();save(OUT/'intent.json',intent)
    owners,pins,omitted=installed(A,Part)
    old='hardware/electronics/full-cat/xa05-main-aux-return-r2/XA05_DESIGN.brep'
    assert old in owners;old_shape=owners.pop(old)
    edges=[];pieces=[];hits=[];errors=[];pairs=0
    for i,e in enumerate(intent['edges']):
        edge=Part.makeLine(A.Vector(*e['start']),A.Vector(*e['end'])) if e['kind']=='line' else Part.Arc(A.Vector(*e['start']),A.Vector(*e['mid']),A.Vector(*e['end'])).toShape()
        profile=Part.Wire([Part.makeCircle(1.25,edge.valueAt(edge.FirstParameter),edge.tangentAt(edge.FirstParameter))])
        shape=Part.Wire([edge]).makePipeShell([profile],True,False)
        assert shape.isValid() and len(shape.Solids)==1
        edges.append(edge);pieces.append(shape)
        for key,other in owners.items():
            if not shape.BoundBox.intersect(other.BoundBox):continue
            pairs+=1
            try:
                common=shape.common(other)
                if common.Volume>1e-5:
                    b=common.BoundBox
                    hits.append(dict(edge=i,owner=key,mm3=common.Volume,
                        bounds_mm=[getattr(b,n) for n in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]))
            except Exception as ex:errors.append(dict(edge=i,owner=key,error=str(ex)))
        print('XA05_EDGE',i,'hits',len(hits),flush=True)
    files=[]
    for name,shape in [('XA05_WORLD.brep',Part.makeCompound(pieces)),('CENTERLINE_WORLD.brep',Part.Wire(edges))]:
        p=OUT/name;shape.exportBrep(str(p));files.append(p)
    finish=datetime.now(timezone.utc)
    pins += [Path(__file__),ROOT/'tools/electronics/w5_s1_source_layout_r2.py',ROOT/'tools/electronics/w5_s1_source_layout_r1.py',ROOT/old]
    save(OUT/'checks.json',dict(status='XA05_ROUTE_REJECTED' if hits or errors else 'XA05_ROUTE_CLEAR_RESTRAINTS_OPEN',
        hits=hits,errors=errors,pairs=pairs,omitted_retired_carrier_aliases=omitted,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in pins},
        files={p.relative_to(ROOT).as_posix():sha(p) for p in [OUT/'intent.json',*files]},
        native_restraints_ready=False,selected=False,W1_complete=False,W5_complete=False,physical_pass=False,
        started_utc=begin.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-begin).total_seconds()))
    print('XA05_RESULT',pairs,len(hits),len(errors),flush=True)


if __name__=='__main__':main()
