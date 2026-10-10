"""Single whole W4 fitted proposal, including support/tie silhouettes.

Historical failed plans remain unselected. This file is not a score update.
Factory input is reserved only; its full source approach remains in W5.
"""
import json,math,time
from pathlib import Path
import plan_current_tail_lower_bus as L
C=L.C;A,Part,P,ROOT,BASE,OUT=C.A,C.Part,C.P,C.ROOT,C.BASE,C.OUT
line,arc,shift,box,wire=L.line,L.arc,L.shift,L.box,C.wire
parent=L.build
AXES=[(-57,-35),(-14,-35)]

def build():
 p=parent();n=1.05/math.sqrt(3);zr=92-2*n;y=-41.875
 red=[line([-16,y,151.49],[-31,y,151.49])]
 red+=shift(red[-1]['end'],[-1,0,0],[0,-1,0],3.125)
 red+=[line(red[-1]['end'],[-65,-45,151.49]),arc([-65,-45,138.89],[-65,-45,151.49],[-77.6,-45,138.89]),
  line([-77.6,-45,138.89],[-77.6,-45,89.8]),arc([-65,-45,89.8],[-77.6,-45,89.8],[-65,-45,77.2]),line([-65,-45,77.2],[20,-45,77.2])]
 red+=shift(red[-1]['end'],[1,0,0],[0,0,1],zr-77.2)
 red+=[line(red[-1]['end'],[68,-45,zr])]
 p['routes']['XB32']['parts']=red
 # Full board-tail sleeve envelope, not just its2.1mm insulation, sets the
 # lower plane: carrier77.72 + sleeveR1.4 + nominalgap0.38 =79.5.
 sig=p['routes']['XS33']['parts'];sig=sig[:6]
 for part in sig:
  for key in ('start','mid','end'):
   if key in part:part[key][2]=79.5
 sig+=[line(sig[-1]['end'],[2.5,-49.5,79.5])]
 sig+=shift(sig[-1]['end'],[1,0,0],[0,0,1],95-79.5)
 sig+=shift(sig[-1]['end'],[1,0,0],[0,1,0],3.45)
 sig+=[line(sig[-1]['end'],[50,-46.05,95])]
 zg=92+n;sig+=shift(sig[-1]['end'],[1,0,0],[0,0,-1],95-zg)
 sig+=[line(sig[-1]['end'],[68,-46.05,zg])]
 p['routes']['XS33']['parts']=sig
 p['routes']['XS33_bare']['parts']=[arc([86.51,14.97,80.5],[86.51,14.97,79.5],[86.51,13.97,80.5]),line([86.51,13.97,80.5],[86.51,13.97,85.8202])]
 p['routes']['F_TY_input_prefix']=dict(parts=[line([-61,y,99.99],[-70,y,99.99]),
  arc([-70,y+6.5,99.99],[-70,y,99.99],[-76.5,y+6.5,99.99]),
  arc([-70,y+6.5,99.99],[-76.5,y+6.5,99.99],[-70,y+13,99.99]),line([-70,y+13,99.99],[-55,y+13,99.99])],radius=2)
 p['carrier_reliefs_mm']=[[83.51,25,77.9,89.51,30.3,81.5]]
 p['assembly']=['All energy sources physically removed, no energizing. Fit carrier nut traps and twoM3x10 stacks on bare upper carrier before boards.',
  'Bench solder/shrink complete three HELU tails/JR cut extension, knownB3 pad afterR3 only; factory servo250 intact. No unknownU1 external pad used.',
  'Lay stationary local interface on tail shelf and fit retained five local ties. Lay B3 under board before seating boards; fit independent B3 grip.',
  'Fit cradle, holder and both9mm factory insulation grips. Output8mm terminal allocation lies WITHIN last15mm factory segment, not extra beyond84.5mm minimum.',
  'Fit custom-red vertical grip, ground port5 vertical grip, then two ordinary replaceable casing bands. Do not assign port4, it carriesXL09.',
  'ATO service: sources absent, cut TWO casing bands, support body and open lid into reserved central tool space. Never pull wires or use the lid as a grip.',
  'For holder/cradle removal: free relevant source ends on bench, cut dedicated wire bands and remove holder first; only then access recessed cradle screws. No attached deformable-cable sweep is claimed.',
  'Tail module: all sources absent, freeG_TAIL.5, supportB3 board end, release local housing bands/JR, and loosen root hardware. Never pull the soldered board lead.']
 p['input_scope']='9mm factory input grip plus44.42mm source-prefix reservation; leave remaining input uncut until fullW5. No claim that the source approach/stockW5 is complete.'
 p['support_plan']=['One screw-removable FHAC cradle; two carrier-rooted nut posts and recessed2M3x10/2nuts/2washers.',
  'Matched carrier B3 outrigger/one actual internal-rim portal; independently gripped sleeved board tail.',
  'Matched E2 outside-arc hanging ground grip, preserves all selected E2 interfaces.',
  'Two factory insulation grips, custom-red vertical9mm grip, two cuttable body bands, ground/B3 grips:7newT18I, plus5retained localT18I.',
  'Both holder exits and ATO central service budget retained; no wire load through adhesive.']
 p['source_sha256'][Path(__file__).relative_to(ROOT).as_posix()]=P.sha(Path(__file__))
 return p

def union(parts):
 s=parts[0]
 for t in parts[1:]:s=s.fuse(t)
 return s.removeSplitter()

def channel(s,bounds):return s.cut(box(bounds)).removeSplitter()

def tie_x(x,y0,y1,z0,z1,head_north=True):
 band=box([x-1.25,y0,z0,x+1.25,y1,z1]).cut(box([x-1.4,y0+1.2,z0+1.2,x+1.4,y1-1.2,z1-1.2]))
 head=box([x-2.4,y1 if head_north else y0-4.5,(z0+z1)/2-1.75,x+2.4,y1+4.5 if head_north else y0,(z0+z1)/2+1.75])
 return band,head

def tie_z(z,x0,x1,y0,y1):
 band=box([x0,y0,z-1.25,x1,y1,z+1.25]).cut(box([x0+1.2,y0+1.2,z-1.4,x1-1.2,y1-1.2,z+1.4]))
 head=box([(x0+x1)/2-2.4,y1,z-1.75,(x0+x1)/2+2.4,y1+4.5,z+1.75])
 return band,head

def layout():
 p=build();carrier=union([box([x-4,y-4,77.72,x+4,y+4,82.99]) for x,y in AXES]+[
  box([51,39,74.72,59,54,77.72]),box([51,46.5,77.72,59,53.5,78.45])])
 # Recesses are exact band silhouettes plus0.2mm per side, not a cable axis.
 carrier=channel(carrier,[53.5,44.8,76.22,56.5,55.2,77.72])
 for x,y in AXES:
  carrier=carrier.cut(Part.makeCylinder(1.7,6,A.Vector(x,y,77)))
  # Side-loaded nut channels; exact native hex cavity is added in master.
  carrier=channel(carrier,[x-3,y-4,79.72,x+3,y+3,82.32])
 e2=union([box([49,-39,129.5,62,-34,132.3]),box([56.15,-48,119,59.5,-36,129.5])])
 cradle=union([box([-71,-52,82.99,0,-31,85.99]),box([-61,-52,85.99,-10,-31.75,89.99]),
  box([-70,-45.875,85.99,-61,-37.875,97.99]),box([-10,-45.875,85.99,-1,-37.875,97.99]),
  box([-70,-51,85.99,-62,-47,122]),box([-76.55,-51,122,-62,-41.125,125]),box([-76.55,-48.125,125,-73.55,-41.125,134])])
 for x in (-39,-30):cradle=channel(cradle,[x-1.5,-53.7,84.49,x+1.5,-30.1,90])
 for x in (-65.5,-5.5):
  cradle=channel(cradle,[x-1.5,-47.375,84.49,x+1.5,-36.375,85.99])
  for a,b in [(-47.375,-45.675),(-38.075,-36.375)]:cradle=channel(cradle,[x-1.5,a,84.49,x+1.5,b,103.59])
 for x,y in AXES:
  cradle=cradle.cut(Part.makeCylinder(1.7,3.5,A.Vector(x,y,82.8)))
  cradle=cradle.cut(Part.makeCylinder(3.7,4.2,A.Vector(x,y,85.99)))
 result=dict(CarrierW4Addition=carrier,E2W4Addition=e2,FTYCradle=cradle)
 for label,x in [('CaseA',-39),('CaseB',-30)]:
  result['Band_'+label],result['TieHead_'+label]=tie_x(x,-53.4,-30.35,84.69,113.39,False)
  # Heads below97.5mm housing plane, in the measured gaps between TE stems.
  result['TieHead_'+label]=box([x-2.4,-57.9,92.99,x+2.4,-53.4,96.49])
 for label,x in [('FactoryInput',-65.5),('FactoryOutput',-5.5)]:
  result['Band_'+label],result['TieHead_'+label]=tie_x(x,-47.075,-36.675,84.69,103.39)
 result['Band_Red'],result['TieHead_Red']=tie_z(129.5,-80.05,-71.95,-49.525,-39.725)
 result['Band_Ground'],result['TieHead_Ground']=tie_z(123.5,52.65,60.9,-49.4,-34.6)
 result['Band_B3'],result['TieHead_B3']=tie_x(55,45.1,54.9,76.32,81.95)
 # Hollow insulation material, not a conductor volume with a waiver.
 sleeve=Part.makeCylinder(3,26.5,A.Vector(-29.25,-41.875,151.49),A.Vector(1,0,0))
 sleeve=sleeve.cut(Part.makeCylinder(2.01,27,A.Vector(-29.5,-41.875,151.49),A.Vector(1,0,0)))
 result['OutputJointSleeve']=sleeve
 s=Part.makeCylinder(1.4,15,A.Vector(86.51,17,79.5),A.Vector(0,1,0))
 result['B3Insulation']=s.cut(Part.makeCylinder(1.051,15.2,A.Vector(86.51,16.9,79.5),A.Vector(0,1,0)))
 assert all(s.isValid() and s.Solids for s in result.values())
 return result

def run():
 C.build=build;C.run('complete-received',lambda unused:layout())

if __name__=='__main__':run()
