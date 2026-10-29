"""Selected T18I stock planning envelopes for the RL source assembly.

Returns complete bands/heads and piece budgets, not exact moulded nylon or
supplier fit approval. Both case belt planes use their actual native pad datum.
"""
import FreeCAD as A
import Part
import numpy as np
from scipy.spatial import ConvexHull
import plan_rl_source_restraints_20261029 as RLnative
from feline_t18i_selected_head import source as selected_head_source


def build(doc, clamps, rest):
    selected_head_source()  # Recheck pinned manufacturer drawing receipts.
    Fixture29,RL29Meta,restMotion=doc,{'clamps':clamps},rest
    axis_u=np.array([0.,.9902680687415703,-.13917310096006663])
    from scipy.spatial import ConvexHull
    Stock29={};Stock29Pieces={};Stock29Meta={};Stock29Tick=0
    def offset_convex(poly,amount):
     poly=np.array(poly);edges=np.roll(poly,-1,axis=0)-poly; normals=np.column_stack([edges[:,1],-edges[:,0]])/np.linalg.norm(edges,axis=1)[:,None]
     result=[]
     for i in range(len(poly)):
      prev=(i-1)%len(poly);matrix=np.array([normals[prev],normals[i]])
      result.append(np.linalg.solve(matrix,np.array([np.dot(normals[prev],poly[i]),np.dot(normals[i],poly[i])])+amount))
     return np.array(result)
    def stock_ring(key,owner,origin,E,F,U,poly,heads):
     origin,E,F,U=map(np.array,[origin,E,F,U]);assert abs(np.dot(E,U))<1e-7 and abs(np.dot(F,U))<1e-7 and abs(np.dot(E,F))<1e-7;poly=np.array(poly);outer=offset_convex(poly,1.2)
     def profile(points):
      vs=[A.Vector(*(origin+x*E+y*F-1.25*U)) for x,y in points];return Part.Face(Part.makePolygon(vs+[vs[0]]))
     band=profile(outer).cut(profile(poly)).extrude(A.Vector(*(2.5*U)))
     Stock29[key+'Band']=band
     pieces=[]
     for i in range(len(poly)):
      j=(i+1)%len(poly);pieces.append(profile([poly[i],poly[j],outer[j],outer[i]]).extrude(A.Vector(*(2.5*U))))
     assert abs(sum(x.Volume for x in pieces)-band.Volume)<1e-5
     Stock29Pieces[key+'Band']=pieces
     centres=[]
     for j,edge_index in enumerate(heads):
      a,b=outer[edge_index],outer[(edge_index+1)%len(outer)]; tangent=(b-a)/np.linalg.norm(b-a);normal=np.array([tangent[1],-tangent[0]])
      mid=(a+b)/2;N=normal[0]*E+normal[1]*F;T=tangent[0]*E+tangent[1]*F
      head=Part.makeBox(4.3,5.3,5.0);head.Placement=RLnative.pose(N,T,U,origin+mid[0]*E+mid[1]*F-2.65*T-2.5*U)
      Stock29[key+'Head'+str(j)]=head;Stock29Pieces[key+'Head'+str(j)]=[head];centres.append(list(head.CenterOfMass))
     loop=sum(np.linalg.norm(np.roll(outer,-1,axis=0)-outer,axis=1));piece=loop/len(heads)
     Stock29Meta[key]=dict(owner=owner,sku='111-02370',ties=len(heads),loop_mm=float(loop),working_each_mm=float(piece),untrimmed_each_mm=float(piece+25),working_limit100_pass=bool(piece<=100),stock145_pass=bool(piece+25<=145),heads_mm=[4.3,5.3,5.0],heads_centres=centres,planning_envelope_not_exact_nylon=True,trim_tail_after_tension=True)
    for key in ['RL1','RL2','RL3']:
     c=RL29Meta['clamps'][key];origin=(np.array(c['start'])+c['end'])/2
     poly=[[-7.85,-4.25],[7.85,-4.25],[7.85,5.7],[-7.85,5.7]] if key=='RL1' else [[-7.85,-5.7],[7.85,-5.7],[7.85,4.25],[-7.85,4.25]]
     stock_ring(key+'Cap','Hip' if key=='RL1' else 'Knee',origin,c['E'],c['F'],c['U'],poly,[3 if key=='RL1' else 1])
    stock_ring('HipSGuide','Hip',[151.24385796,84.6862915,71],[.5,.5,-2**-.5],[-.5,-.5,-2**-.5],[-2**-.5,2**-.5,0],[[-7.85,-4.25],[7.85,-4.25],[7.85,4.25],[-7.85,4.25]],[3])
    for key,actor,axis,origin in [('HipParent','Ref_Material_P0_Part__Feature022_0_0',[1.,0,0],[145.5,0,0]),('KneeParent','Ref_Material_P0_Part__Feature064_0_0',axis_u,[154,75,0])]:
     if key=='KneeParent':origin=list(Fixture29.getObject('RL29Knee2Leg0').Placement.Base)
     U=np.array(axis);U/=np.linalg.norm(U)
     if key=='HipParent':E=np.array([0.,1.,0.]);seat=Fixture29.getObject('RL29HipSeat').Shape
     else:E=np.array(list(Fixture29.getObject('RL29KneeSeat').Dir));seat=Fixture29.getObject('RL29KneeSeat').Shape
     E-=np.dot(E,U)*U;E/=np.linalg.norm(E);F=np.cross(U,E);origin=np.array(origin)
     plane=Part.makePlane(200,200,A.Vector(*(origin-100*E-100*F)),A.Vector(*U),A.Vector(*E))
     pts=[]
     for shape in [restMotion[actor],seat]:
      sec=shape.section(plane)
      for edge in sec.Edges:
       for v in edge.discretize(Deflection=.15):
        p=np.array(list(v))-origin;pts.append([np.dot(p,E),np.dot(p,F)])
     pts=np.unique(np.round(pts,6),axis=0);h=ConvexHull(pts);poly=offset_convex(pts[h.vertices],.2)
     # Two complete selected heads, placed on opposing broad sides.
     edges=np.roll(poly,-1,axis=0)-poly
     longest=int(np.argmax(np.linalg.norm(edges,axis=1)));opposite=int(np.argmax(np.linalg.norm((poly+np.roll(poly,-1,axis=0))/2-(poly[longest]+poly[(longest+1)%len(poly)])/2,axis=1)))
     stock_ring(key,'Hip' if key=='HipParent' else 'Knee',origin,E,F,U,poly,[longest,opposite])
    for key,s in Stock29.items():assert s.isValid() and s.Volume>0,key
    return Stock29,Stock29Pieces,Stock29Meta
