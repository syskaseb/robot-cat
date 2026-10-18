"""Read-only source-solid scene for changed wires and component interfaces."""
import itertools
import json
import numpy as np
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import OUT,MODEL,STAGES,transforms
from feline_current_candidate_scene import current
from receive_feline_global_case_candidates import placement,bounds_near
from check_feline_all_current_lands import near
from feline_solid_distance import distance


class Scene:
    def __init__(self):
        self.parts,self.meta,self.templates,self.pins,self.bus,_,_,_=current()
        self.reader=SavedShapes();env=OUT/'central-cassette-envelope/FelineLayoutEnvelope.FCStd'
        self.outer=self.reader.shape(env,'TorsoEnvelope');self.bounds={n:s.BoundBox for n,s in self.parts.items()}
        motionfile=OUT/'motion-layout.json';motion=json.loads(motionfile.read_text())
        axesfile=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';axes=json.loads(axesfile.read_text())['axes']
        self.rest={};self.motion=[];self.posed={}
        for code,groups in motion['membership'].items():
            aa=[next(a for a in axes if a['code']==code and a['stage']==stage) for stage in STAGES]
            tfs=[transforms(aa,p['legs'][code]['angles_delta_degrees']) for p in motion['poses'][:36]]
            for stage,names in groups.items():
                for name in names:
                    source=self.reader.shape(MODEL,name);self.rest[name]=source;bb=source.BoundBox
                    corners=np.array(list(itertools.product((bb.XMin,bb.XMax),(bb.YMin,bb.YMax),(bb.ZMin,bb.ZMax))))
                    for i in range(36):
                        r,t=tfs[i][STAGES.index(stage)];v=corners@r.T+t
                        self.motion.append(dict(name=name,code=code,stage=stage,pose=i,r=r,t=t,bounds=[v.min(0),v.max(0)]))
        self.pins.update(self.reader.hashes)
        for p in (MODEL,motionfile,axesfile,__import__('pathlib').Path(__file__)):
            self.pins[p.relative_to(ROOT).as_posix()]=sha(p)

    def wire(self,n):
        r=self.meta[n]
        return bool(r.get('wire_owner')) or r.get('kind') in ('wire','actual_wire','proposal_wire') or n.startswith(('End:','BankFullPrefix:','Factory:','CustomPrefix:')) or n in ('W043','W077','W078')

    def receive(self,shape,wire=False):
        """First named actual gap failure, plus all completed source pairs."""
        assert shape.isValid() and shape.Solids
        queries=[];outside=shape.cut(self.outer)
        assert outside.isNull() or outside.isValid()
        if outside.Volume>1e-5:return dict(kind='actual_outside',volume_mm3=outside.Volume),queries
        gap=float(shape.distToShape(self.outer.Shells[0])[0]);queries.append(dict(scope='true_outer',gap_mm=gap,minimum_mm=3.25))
        if gap<3.25-1e-5:return dict(kind='actual_outer_gap',gap_mm=gap),queries
        bb=shape.BoundBox;bounds=[np.array([bb.XMin,bb.YMin,bb.ZMin]),np.array([bb.XMax,bb.YMax,bb.ZMax])]
        for n,s in self.parts.items():
            minimum=.2 if wire and self.wire(n) else 1.25
            if not near(bb,self.bounds[n],minimum):continue
            if not s.Solids:return dict(kind='curve_jacket_owner_hold',source=n),queries
            q=shape
            if n==self.bus['name']:
                q=shape.copy();q.Placement=self.bus['inverse']*q.Placement;s=self.bus['original']
            if not s.isValid():return dict(kind='invalid_source_hold',source=n),queries
            gap=distance(q,s);queries.append(dict(scope='static_solid_children',source=n,gap_mm=gap,minimum_mm=minimum))
            if gap<minimum-1e-5:
                r=self.meta[n];reserved='reservation' in r.get('kind','') or r.get('role')=='ScaffoldPlanning' or n.startswith(('StructureReserve:','PiBudget:')) or n=='RetainedMAINCutForeCap'
                return dict(kind='reservation_hold' if reserved else 'actual_static_gap',source=n,gap_mm=gap,minimum_mm=minimum),queries
        for p in self.motion:
            if not bounds_near(bounds,p['bounds']):continue
            key=p['name'],p['pose']
            if key not in self.posed:
                original=self.rest[p['name']]
                if not original.isValid() or not original.Solids:return dict(kind='invalid_motion_source_hold',source=p['name']),queries
                s=original
                if np.linalg.norm(p['r']-np.eye(3))>1e-12 or np.linalg.norm(p['t'])>1e-7:
                    s=original.copy();s.Placement=placement(p['r'],p['t'])*s.Placement
                if not s.isValid():return dict(kind='invalid_posed_source_hold',source=p['name'],pose=p['pose']),queries
                b=s.BoundBox;actual=np.array([[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]])
                assert np.all(actual[0]>=p['bounds'][0]-1e-5) and np.all(actual[1]<=p['bounds'][1]+1e-5),'Motion source frame mismatch'
                self.posed[key]=s
            gap=distance(shape,self.posed[key]);queries.append(dict(scope='motion36_solid_children',source=p['name'],pose=p['pose'],stage=p['stage'],gap_mm=gap,minimum_mm=1.25))
            if gap<1.25-1e-5:return dict(kind='actual_sampled_motion_gap',source=p['name'],pose=p['pose'],stage=p['stage'],gap_mm=gap),queries
        return None,queries
