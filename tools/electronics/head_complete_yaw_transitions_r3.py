"""Full end transition remedy: relocate clamped anchors beyond factory coil.

R2 exposed a Fork/coil support intersection and a real Cover port conflict.
This construction keeps the same JR/factory lead but makes two replacement
parts with integral tie seats. Only the changed interfaces are checked.
"""
import sys,json
from pathlib import Path
import head_complete_yaw_transitions_r1 as B
B.OUT=B.ROOT/'hardware/electronics/full-cat/head-complete-yaw-transitions-r3'
B.END_X=-10; B.END_Y=136; B.MOVING_Y=130; B.FLEX_LENGTH=260
sys.path.insert(0,str(B.ROOT/'tools/cad'))
import head_jr_support_r5 as CAD
NEW=B.ROOT/'hardware/cad/studies/head-yaw-end-restraints-r1'
B.INPUTS=list(B.CACHE.glob('*_REST.brep'))+[NEW/'ForkYawEndSeat.brep',NEW/'CoverYawEndSeat.brep',B.CAD/'PitchCarrierThroughLeadExit.brep',B.PORTS/'FrontRightWirePassage.brep']

def main():
    NEW.mkdir(exist_ok=True); assert not (NEW/'checks.json').exists()
    CAD.OUT=NEW
    fork0=B.load(B.CAD/'ForkJRHolder.brep');cover0=B.load(B.PORTS/'CoverHeadWirePassage.brep')
    fork_adds=[[-184,62,134,-168,134,138.5]]
    fork_cuts=[[-182,127,133,-180,133,140],[-174,127,133,-172,133,140]]
    cover_adds=[[-23,88,135,-19,134,139],[-23,130,135,-2,142,138.5]]
    cover_cuts=[[-15,92,120.5,-5,104,128],[-19,133,134,-17,139,140],[-4,133,134,-2,139,140]]
    plan=dict(status='SOURCE_BEFORE_COMPLETE_END_RESTRAINTS',
        fork_adds_mm=fork_adds,fork_tie_cuts_mm=fork_cuts,cover_adds_mm=cover_adds,cover_cuts_mm=cover_cuts,
        moving_anchor_rest_mm=[-177.2,130,141],fixed_anchor_mm=[-10,136,141],
        moving_length_mm=260,fixed_radius_mm=12.6,moving_radius_requirement_mm=31.5,
        tie_requirement='Two T18I from existing bag100, each around insulation bundle at its own integral seat. No clamp on JR contacts. Fixed end belongs to removable cover: unplug JR and cut support ties before lifting cover.',
        additions='Two replacement prints; no net installed part increase and no new screws/SKU. Former FixedDeckTie remains selected for later inner harness; not falsely substituted.',
        physical_pass=False,phase1_complete=False,
        inputs_sha256={p.relative_to(B.ROOT).as_posix():B.R.sha(p) for p in (B.CAD/'ForkJRHolder.brep',B.PORTS/'CoverHeadWirePassage.brep')})
    CAD.dump('plan.json',plan)
    if '--resume' not in sys.argv:
        fork,fg=CAD.build('ForkYawEndSeat',fork0,fork_adds,fork_cuts)
        cover,cg=CAD.build('CoverYawEndSeat',cover0,cover_adds,cover_cuts)
        CAD.dump('native-geometry.json',dict(fork=fg,cover=cg))
    else:
        def recover(name):
            d=B.A.openDocument(str(NEW/(name+'.FCStd'))); d.recompute()
            f=[x for x in d.Objects if x.Name.startswith('Interface')][-1]
            s=f.Shape.copy(); assert s.isValid() and len(s.Solids)==1 and not s.check(True)
            t=d.getObject('Tool0'); original=t.Length.Value;v=s.Volume
            t.Length=original+.2;d.recompute();changed=f.Shape.Volume;assert abs(changed-v)>1e-5
            t.Length=original;d.recompute();assert abs(f.Shape.Volume-v)<1e-5
            B.A.closeDocument(d.Name)
            return s,dict(valid=True,solids=1,strict_bop_errors=0,reopen_recompute_ok=True,
                          parameter_probe_volumes=[v,changed,v],recovery_from_saved_source=True)
        fork,fg=recover('ForkYawEndSeat');cover,cg=recover('CoverYawEndSeat')
        CAD.dump('native-geometry.json',dict(fork=fg,cover=cg))
    # The path runner loads these exact new shapes, not the unmodified parents.
    B.CAD=NEW; B.PORTS=NEW
    original_load=B.load
    def load(p):
        remap={'ForkJRHolder.brep':NEW/'ForkYawEndSeat.brep',
               'PitchCarrierThroughLeadExit.brep':B.ROOT/'hardware/cad/studies/head-jr-support-r5/PitchCarrierThroughLeadExit.brep',
               'CoverHeadWirePassage.brep':NEW/'CoverYawEndSeat.brep',
               'FrontRightWirePassage.brep':B.ROOT/'hardware/cad/studies/head-external-wire-support-r1/FrontRightWirePassage.brep'}
        return original_load(remap.get(p.name,p))
    B.load=load
    B.main()
    checks=json.loads((B.OUT/'checks.json').read_text()); rows=[]
    # Every new tie hole passes through its complete selected owner.
    for owner,shape,cuts in [('Fork',fork,fork_cuts),('Cover',cover,cover_cuts[1:])]:
        for b in cuts:
            s=B.R.box([b[0]+.1,b[1]+.1,b[2],b[3]-.1,b[4]-.1,b[5]])
            v=B.R.volume(s.common(shape)); assert v<1e-6
            rows.append(dict(owner=owner,tie_slot_mm=b,full_depth_clear=True,hit_mm3=v))
    CAD.dump('checks.json',dict(status='END_SEATS_CANDIDATE' if not checks['hits'] and checks['moving_radius_sample_bound_met'] else 'REJECTED',
        geometry={'fork':fg,'cover':cg},slot_checks=rows,route_checks_sha256=B.R.sha(B.OUT/'checks.json'),
        new_stls=2,quantities={'ForkYawEndSeat_candidate_x1.stl':1,'CoverYawEndSeat_candidate_x1.stl':1},
        new_ties=2,new_screws=0,new_skus=0,physical_pass=False,phase1_complete=False))

if __name__=='__main__': main()
