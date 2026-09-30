"""One rigid-yaw JR holder and a through Carrier lead exit, not whole wiring.

Factory wire/connector dimensions remain provisional reservations for phase2.
The holder restrains insulation/housing, never the electrical contacts.
"""
import sys,json,hashlib,tempfile,shutil
from pathlib import Path
import FreeCAD as A,Part,MeshPart
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
import xb11_upstream_route as R
from head_external_yaw_loop_r1 import mv
P=ROOT/'hardware/cad/studies/head-external-wire-support-r1'
C=ROOT/'hardware/electronics/full-cat/head-external-yaw-loop-r1'
OUT=ROOT/'hardware/cad/studies/head-jr-support-r5'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,v):(OUT/n).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def load(p):s=Part.Shape();s.read(str(p));return s
def build(name,source,adds,cuts):
    d=A.newDocument(name);base=d.addObject('PartDesign::Feature','PinnedYawFrameParent');base.Shape=source;f=base
    for i,(operation,b) in enumerate([('MultiFuse',b) for b in adds]+[('Cut',b) for b in cuts]):
        t=d.addObject('Part::Box','Tool'+str(i));t.Length=b[3]-b[0];t.Width=b[4]-b[1];t.Height=b[5]-b[2];t.Placement.Base=A.Vector(*b[:3])
        new=d.addObject('Part::'+operation,'Interface'+str(i))
        if operation=='Cut':new.Base=f;new.Tool=t;new.Refine=False
        else:new.Shapes=[f,t]
        d.recompute();f.Visibility=False;t.Visibility=False;f=new
    d.saveAs(str(OUT/(name+'.FCStd')));s=f.Shape.copy();assert s.isValid() and len(s.Solids)==1 and not s.check(True)
    # One intentional dimensional change, then restore exact baseline volume.
    t=d.getObject('Tool0');length=t.Length.Value;v=s.Volume;t.Length=length+.2;d.recompute();changed=f.Shape.Volume;assert abs(changed-v)>1e-5
    t.Length=length;d.recompute();assert abs(f.Shape.Volume-v)<1e-5;d.save();s=f.Shape.copy()
    s.exportBrep(str(OUT/(name+'.brep')))
    m=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
    if name.startswith('Fork'):m.transform(A.Placement(A.Vector(),A.Rotation(A.Vector(0,1,0),90)).toMatrix())
    bb=m.BoundBox;m.translate(-bb.XMin,-bb.YMin,-bb.ZMin);assert m.isSolid() and m.countComponents()==1
    m.write(str(OUT/(name+'_candidate_x1.stl')));dims=[m.BoundBox.XLength,m.BoundBox.YLength,m.BoundBox.ZLength];assert max(dims)+10<256
    final_name=f.Name
    A.closeDocument(d.Name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-jr-reopen-') as td:
        dest=Path(td)/(name+'.FCStd');shutil.copy2(OUT/(name+'.FCStd'),dest);d=A.openDocument(str(dest));d.recompute();q=d.getObject(final_name).Shape;assert abs(q.Volume-s.Volume)<1e-5 and not q.check(True);A.closeDocument(d.Name)
    return s,dict(valid=True,solids=1,strict_bop_errors=0,reopen_recompute_ok=True,parameter_probe_volumes=[v,changed,s.Volume],added_mm3=s.cut(source).Volume,removed_mm3=source.cut(s).Volume,stl_dimensions_mm=dims,stl_closed=True,stl_components=1)
def main():
    OUT.mkdir(exist_ok=True);assert not (OUT/'checks.json').exists()
    plan=dict(status='SOURCE_BEFORE_RIGID_YAW_JR_HOLDER',
      parent_files_sha256={str(p.relative_to(ROOT)):sha(p) for p in (P/'UpperForkWireArmSlotted.FCStd',P/'FrontRightWirePassage.brep',P/'CoverHeadWirePassage.brep',C/'Pitch_Carrier_REST.brep')},
      ownership='C_HP on integral UpperFork holder, same rigid yaw frame as pitch Carrier; not removable pitch shell. This explicitly supersedes the older Carrier-only connector location.',
      connector_design_bbox_mm=[-158,82,136,-146,112,146],connector_dimensions_basis='30x12x10 conservative mating-pair reservation, NOT actual measured JR housing',
      carrier_exit_cutter_mm=[-156,4,127.25,-145,23,129.65],
      fork_wire_windows_mm=[[-153,20.5,127.25,-138,32,129.65],[-136,58,127.25,-132,63,129.65]],
      load_path_note='Low cable windows do not cut the journal axis/bore. Their upperZ129.65 remains0.85mm below a conservative R5.5 bore bound atZ136. This is a geometric ligament only, not PETG strength/load qualification.',
      factory_lead_design_thin_exit_mm=[3.5,1.8],factory_lead_basis='Provisional flat3-wire profile only for Carrier exit; actual wire width/thickness and pad/exit orientation verify on delivered MG92B. Factory250mm cable never cut.',
      print='Two replacements PETG x1, no net installed-part increase; Fork broad side, Carrier open side up. Supports/profile in phase2, brim5 within256.',
      fasteners='No additional screws; two T18I through paired slots around JR housing, one tie each on insulated ends. Ordinary ties are cut and replaced for removal, not releasable. Five additional ties from existing bag100, not a new SKU.',
      assembly=['Fit revised bare Carrier before servo and head closure.','Lay factory lead through opened +Y exit; do not force JR housing through thin slot.','Fit mating JR pair in side cradle; label ground/center6V/PWM and verify disconnected pinout.','Two loose releasable ties retain housing; independently restrain insulation at both ends. No tie on solder/bare contact.','Route excess factory lead outside shell in generous loose curve before tightening. Coil/storage and two complete end transitions still to be constructed.'],
      new_stls=2,new_skus=0,new_screws=0,new_ties=5,physical_pass=False,phase1_complete=False)
    dump('plan.json',plan)
    fork0=load(P/'UpperForkWireArmSlotted.brep');carrier0=load(C/'Pitch_Carrier_REST.brep')
    adds=[[-136,58,126,-130,63,136],[-170,62,133,-130,80,136],[-170,79,133,-138,122,136],[-162,82,136,-158,112,141],[-146,82,136,-142,112,141],[-155,73,136,-149,79,138.5],[-155,115,136,-149,121,139],[-162,114,136,-158,120,184],[-160,116,181,-149,120,184],[-151,110,182,-135,118,184],[-145,112,184,-141,116,184.3]]
    cuts=[]
    for y in (76,86,108,118):
        for x in (-165,-140):cuts.append([x-1,y-2,133,x+1,y+2,136])
    slot_cuts=list(cuts)
    cuts += plan['fork_wire_windows_mm']
    coil_slots=[[-150,112,182,-148,116,184],[-138,112,182,-136,116,184]]
    cuts += coil_slots
    fork,fg=build('ForkJRHolder',fork0,adds,cuts);carrier,cg=build('PitchCarrierThroughLeadExit',carrier0,[],[plan['carrier_exit_cutter_mm']])
    rows=[];add=fork.cut(fork0)
    # New addition against shells: relative yaw cancels. Only three pitch poses.
    for pitch in (-10,0,5):
        for n,p in [('FrontRight',P/'FrontRightWirePassage.brep')]+[(n,C/(n+'_REST.brep')) for n in ('FrontLeft','Rear','Nose','EarL','EarR')]:
            s=mv(load(p),0,pitch)
            for i,t in enumerate(s.Solids):
                if R.overlap(t.BoundBox,add.BoundBox):rows.append(dict(target='new_holder',pitch=pitch,owner=n,solid=i,hit_mm3=R.volume(add.common(t))))
    for yaw in (-15,0,15):
        for n,p in [('Cover',P/'CoverHeadWirePassage.brep'),('Deck',C/'Deck_REST.brep')]:
            s=load(p);t=mv(add,yaw)
            if R.overlap(t.BoundBox,s.BoundBox):rows.append(dict(target='new_holder',yaw=yaw,owner=n,hit_mm3=R.volume(t.common(s))))
        tube=load(P/f'loop_yaw{yaw:+}.brep');t=mv(fork,yaw);rows.append(dict(target='existing_loop',yaw=yaw,owner='complete_new_fork',hit_mm3=R.volume(tube.common(t))))
    jr=R.box(plan['connector_design_bbox_mm']);rows.append(dict(target='JR_mating_reservation',owner='holder',hit_mm3=R.volume(jr.common(fork))))
    lead=R.box([-153.75,8.8,127.6,-150.25,23,129.4]);rows.append(dict(target='thin_factory_exit_reservation',owner='new_carrier',hit_mm3=R.volume(lead.common(carrier))))
    # Every pair of holes must actually pass through the plate; no out-of-body
    # slot counted as an attachment. Housing and insulated ends have separate stations.
    slot_checks=[]
    for b in slot_cuts:
        probe=R.box([b[0]+.1,b[1]+.1,132.5,b[3]-.1,b[4]-.1,136.5])
        plate=R.box([-170,62,133,-138,122,136])
        assert R.volume(probe.common(plate))>0 and R.volume(probe.common(fork))<1e-6
        slot_checks.append(dict(bbox_mm=b,through_plate=True,probe_hit_mm3=R.volume(probe.common(fork))))
    hits=[r for r in rows if r['hit_mm3']>1e-5]
    dump('checks.json',dict(status='JR_HOLDER_CANDIDATE' if not hits else 'REJECTED',geometry={'fork':fg,'carrier':cg},changed_pairs=rows,hits=hits,new_stls=2,physical_pass=False,phase1_complete=False,
      slot_checks=slot_checks,tie_stations_y_mm=[76,86,108,118],coil_slots_mm=coil_slots,
      coil_retention='One loose T18I around the upper slack loop at(-143,114,186.7697); seatZ184.3 keeps clearance to the conservative lead envelope. Do not preload or crush insulation.',
      remaining=['Actual factory loop slack/loose tie fit','Full service end transitions to yaw loop','Fixed yaw feed','Actual JR/wire delivery fit/pinout']))
    print(json.dumps(dict(status='JR_HOLDER_CANDIDATE' if not hits else 'REJECTED',hits=hits)),flush=True)
if __name__=='__main__':main()
