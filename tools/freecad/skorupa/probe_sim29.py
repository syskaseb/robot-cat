"""Tiny throwaway native-solver diagnostic. Never saves or edits user CAD."""
import sys
import FreeCAD as A, Part
sys.path.insert(0,A.getHomePath()+'Mod/Assembly')
import JointObject
d=A.newDocument('DisposableSimulationProbe29')
asm=d.addObject('Assembly::AssemblyObject','Assembly')
g=asm.newObject('Assembly::JointGroup','Joints')
parts=[]
for n in ['Parent','Child']:
    p=asm.newObject('App::Part',n);o=p.newObject('Part::Feature',n+'Solid');o.Shape=Part.makeBox(1,1,1);parts.append(p)
ground=g.newObject('App::FeaturePython','Ground');JointObject.GroundedJoint(ground,parts[0])
j=g.newObject('App::FeaturePython','Rev');JointObject.Joint(j,1)
j.Detach1=True;j.Detach2=True;j.Reference1=(parts[0],['','']);j.Reference2=(parts[1],['',''])
j.Placement1=j.Placement2=A.Placement(A.Vector(171,-6,91),A.Rotation())
sim=asm.newObject('App::FeaturePython','Test');sim.addExtension('App::GroupExtensionPython')
for n in ['aTimeStart','bTimeEnd','cTimeStepOutput','fGlobalErrorTolerance']:sim.addProperty('App::PropertyFloat',n)
sim.fGlobalErrorTolerance=1e-6
sim.aTimeStart=0;sim.bTimeEnd=1;sim.cTimeStepOutput=.05
motion=asm.newObject('App::FeaturePython','Motion')
motion.addProperty('App::PropertyXLinkSubHidden','Joint');motion.Joint=(j,[''])
motion.addProperty('App::PropertyEnumeration','MotionType');motion.MotionType=['Angular','Linear'];motion.MotionType='Angular'
motion.addProperty('App::PropertyString','Formula');motion.Formula=sys.argv[1] if len(sys.argv)>1 else '0.1*sin(2*pi*time)';sim.Group=[motion]
d.recompute();print('solve',asm.solve(), 'formula',motion.Formula,flush=True)
print('generate',asm.generateSimulation(sim),'frames',asm.numberOfFrames(),flush=True)
