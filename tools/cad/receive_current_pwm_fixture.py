"""Receive saved E2 gates and test only unresolved fixture/tie interfaces."""
import json,time,sys
from pathlib import Path
sys.path.insert(0,str(Path(sys.executable).resolve().parent.parent/'lib'))
import finish_current_pwm_fixture as F
from open_deck_p0_plate import circle
A,Part,B,C,P=F.A,F.Part,F.B,F.C,F.P
OUT,ROOT,BASE=F.OUT,F.ROOT,F.BASE

def run():
    tick=time.monotonic();r=dict(status='E2_RECEIPT_PENDING',contacts=[],pairs=0,physical_pass=False)
    d=A.openDocument(str(OUT/'PWMBranchSelected.FCStd'))
    try:
      body,carrier=d.E2Fixture,d.UpperCarrier001
      # The nut pocket stops84.32, but a fully engaged M3x12 ends86.22.
      s=B.sketch(body,'E2ThreadEndClearancePlan',86.52)
      for x,y in B.AXES:circle(s,x,y,3.4)
      body.Tip=B.feature(body,'Pocket','E2ThreadEndClearance',s,2.2)
      # The fuse seats must also leave the complete lateral band path, not
      # merely its bottom return through the floor.
      B.pocket(body,'E2FuseBandSides',134.8,[(x,y,2.8,1.3) for x in (44.6,77.6) for y in (-11.1,-3.2)],4.1)
      # A1.2mm strap cannot fit a0.945mm channel. Give the complete return
      #1.5mm, retain1.5mm of plate floor, and place its bottom at76.32.
      d.E2BoardBandSlot.Length=1.5
      x,y0,y1,z0,z1=128,-12.7,-4.3,76.32,84.2
      d.Band_Board.Shape=C.box([x-1.25,y0,z0,x+1.25,y1,z1]).cut(C.box([x-1.4,y0+1.2,z0+1.2,x+1.4,y1-1.2,z1-1.2]))
      d.TieHead_Board.Shape=C.box([x-2.25,y0-3.5,(z0+z1)/2-2.4,x+2.25,y0,(z0+z1)/2+2.4])
      # Generate the whole channel from the installed band silhouette,
      # not the old nominal slot that missed its negative-Y side.
      B.pocket(carrier,'E2BoardFullBandPassage',77.72,[(x-1.5,y0-.3,3,y1-y0+.6)],1.5)
      d.recompute();r['native_validity']=F.validate(d,[carrier,body])
      material={body.Name:body.Shape,carrier.Name:carrier.Shape}
      for o in d.Objects:
        if o.TypeId!='Part::Feature' or not o.Name.startswith(('Band_','TieHead_','E2Bolt','E2Nut','E2Washer','E2Driver')):continue
        for n,t in material.items():
          if not C.near(o.Shape,t,0):continue
          v=sum(a.common(b).Volume for a in o.Shape.Solids for b in t.Solids);r['pairs']+=1
          if v>1e-5:r['contacts'].append(dict(a=o.Name,b=n,volume=v))
      # Assembly tools are used on the free upper plate, before Pi/BUS or
      # lower plate stacking. The plate itself still cannot obstruct a tool.
      r['driver_stage']='Unstacked UpperCarrier, before all boards and lower-module stacking; installation/fixture replacement requires this stage.'
      r['prior_receipt_sha256']=P.sha(OUT/'final-checks.json')
      r['unchanged_checks_reused']='final-checks: route/insulation versus retained scene, nine PCB bearing collars, native parameter/reopen and supplier models. Removed material only; no relocated wire or added fixture material.'
      r['worker_seconds']=round(time.monotonic()-tick,3)
      r['status']='E2_RECEIPT_REJECTED' if r['contacts'] else 'E2_RECEIPT_STATIC_PREPARED'
      dest=OUT/'received-checks.json';dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
      if not r['contacts']:
        d.saveAs(str(OUT/'PWMBranchReceived.FCStd'))
        r['model_sha256']=P.sha(OUT/'PWMBranchReceived.FCStd');dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
      print(json.dumps(r),flush=True)
    finally:
      for doc in list(A.listDocuments().values()):A.closeDocument(doc.Name)
if __name__=='__main__':run()
